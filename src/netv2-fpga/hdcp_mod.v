/*
 Integration notes.

 0x74 DDC traffic format (from i2c_snoop.v):
     LSB  Bksv  MSB
 00: ae 80 12 db fa 00 00 00 00 00 00 00 00 00 00 00
 10: ed 90 b4 5c 0f 00 00 00 46 84 e5 6c 78 b6 53 f5
     lSB  Aksv  MSB          LSB     An          MSB
  
1. Km is computed by the host, based on observations of Aksv/Bksv.
   Note that Km is different for every source/sink combo but stays
   constant for a given pairing. Note endianness of records.
 
2. An (session key) is recovered on a per-session basis.
 
3. When the 14th byte of i2c_snoop (MSB of Aksv) is written, cipher
   initialization is triggered. This is the Aksv14_write signal.
   Consider refactor to pass on as an interrupt to SoC to compute
   Km dynamically, to avoid HPD re-flash/re-sync. Computations
   must complete within 100ms.
 
Things to check on integration:
  - line_end pulses on the last pixel (not after the last pixel)
    This means the line_end pulse can't be a simple de & ~de computation.
    Options include anticipating de length based on video mode, or digging
    the de signal out from an earlier pipeline stage.
 
  - hdcp_ena will come from the TERC4/control signal state machine
    and needs to be asserted whenever TERC4 islands occur, or when video
    data is present (this comes from looking at the guardbands & CTL signals)
 
  - ctl_code is the 4-bit control code that rides on the r/g channels (b has
    hsync/vsync). Necessary for EESS detection.
 
  - de, hsync, vsync are the video timing signals
 
  - Km_valid is status feedback from the CPU to indicate when the Km has
    been computed by the host and is in fact valid.
 
 */

module hdcp_mod (
		 input wire 	    clk, // pixclk
		 input wire 	    rst,
		 input wire 	    de,
		 input wire 	    hsync, // positive active
		 input wire 	    vsync,
		 input wire 	    line_end, // need to double check the purpose but nominally de && (sdata == CTRLTOKEN*)
		 input wire 	    hpd, // high == no cable present
		 input wire 	    Aksv14_write, // strobe to indicate ksv was written
		 input wire [63:0]  An,
		 input wire [55:0]  Km,
		 input wire 	    Km_valid,
		 input wire 	    hdcp_ena,
		 input wire [3:0]   ctl_code, // control code
		 output wire [23:0] cipher_stream,
//		 output wire [17:0] hdcp_debug,
//		 output wire [12:0] cipher_debug,
//		 output wire [7:0]  An_debug,
//		 output wire [7:0]  Km_debug,
		 output wire 	    stream_ready
		 );

   reg         Km_rdy0;
   reg         Km_rdy1;
   reg 	       Km_rdy2;
   wire        Km_ready;
   reg 	       hdcp_requested;

   // confirm the correct byte ordering
//   assign An_debug = An[63:56];
//   assign Km_debug = Km[55:48];
   
   wire       vsync_rising;
   reg 	      vsync_v2;
   always @(posedge clk) begin
      vsync_v2 <= vsync;
   end
   assign vsync_rising = vsync & !vsync_v2;
   
   ///////
   // HDCP
   ///////
   // HDCP initialization procedure
   //
   // 1. Sniff An, KSV going across the wire
   // 2. Generate private key table for one of the KSV's
   // 3. Perform the Km computation using derived private key table
   // 4. Enter An, Km into the register for the HDCP cipher
   // 5. Initiate the authentication (pulse hdcpBlockCipher_init and 
   //    authentication high one cycle simultaneously)
   // 6. Wait until stream_ready is high
   //
   // Now begins the main loop:
   // There is an ambiguity in the spec. Either a rekey operation happens immediately
   // (since this happens during vertical retrace), or not. Either way, this is roughly
   // what happens.
   //
   // 1. If hdcp_ena activates (or of de and data island enable), advance cipher
   // 2. If vertical sync happens, pulse hdcpBlockCipher_init one cycle and wait 
   //    until stream_ready; return to 1
   // 3. If horizontal sync happens, pulse hdcpRekeyCipher once cycle, wait until
   //    stream_ready; return to 1
   //
   // That's it. So the only question is if vsync "happens" immediately after an authentication.
   // The test vectors would suggest this is the case but I can't find it in the state machine
   // diagrams, so perhaps good to try both options...?
   parameter HDCP_UNPLUG      = 18'b1 << 0;  // 1
   parameter HDCP_WAIT_AKSV   = 18'b1 << 1;  // 2
   parameter HDCP_AUTH_PULSE  = 18'b1 << 2;  // 4
   parameter HDCP_AUTH        = 18'b1 << 3;  // 8
   parameter HDCP_AUTH_WAIT   = 18'b1 << 4;  // 10
   parameter HDCP_AUTH_VSYNC_PULSE  = 18'b1 << 5;  // 20
   parameter HDCP_AUTH_VSYNC        = 18'b1 << 6;  // 40
   parameter HDCP_AUTH_VSYNC_WAIT   = 18'b1 << 7;  // 80
   parameter HDCP_WAIT_1001   = 18'b1 << 8;  // 100
   parameter HDCP_WAIT_1001_END = 18'b1 << 9;  // 200
   parameter HDCP_VSYNC       = 18'b1 << 10; // 400
   parameter HDCP_VSYNC_PULSE = 18'b1 << 11; // 800
   parameter HDCP_VSYNC_WAIT  = 18'b1 << 12; // 1000
   parameter HDCP_READY       = 18'b1 << 13; // 2000
   parameter HDCP_REKEY       = 18'b1 << 14; // 4000
   parameter HDCP_REKEY_WAIT  = 18'b1 << 15; // 8000
   parameter HDCP_WAIT_KMRDY  = 18'b1 << 16; // 10000
//   parameter HDCP_REKEY_PULSE = 18'b1 << 17; // 20000 

   parameter HDCP_nSTATES = 17;
   
   reg [(HDCP_nSTATES-1):0]     HDCP_cstate = {{(HDCP_nSTATES-1){1'b0}}, 1'b1};
   reg [(HDCP_nSTATES-1):0]     HDCP_nstate;

   reg 				auth_mode;
   reg 				hdcp_init;
   wire 			hdcp_stream_ena;

   reg 				active_line;
   wire 			hdcp_rekey;
   
   reg 				hsync_v, hsync_v2;

//   assign hdcp_debug = HDCP_cstate;
   assign hdcp_is_ready = (HDCP_cstate == HDCP_READY);

   reg 				le_pipe;

   assign hdcp_rekey = line_end;

   always @ (posedge clk) begin
      if( rst == 1'b1 ) begin
	 active_line <= 1'b0;
	 hsync_v <= 1'b0;
	 hsync_v2 <= 1'b0;
      end else begin
	 hsync_v <= hsync;
	 hsync_v2 <= hsync_v;
	 
	 if( de ) begin
	    active_line <= 1'b1;
	 end else if( !hsync_v & hsync_v2 ) begin // hsync falling
	    active_line <= 1'b0;
	 end
      end
   end
   
   always @ (posedge clk) begin
      if ( hpd | rst )
	HDCP_cstate <= HDCP_UNPLUG; 
      else
	if( Aksv14_write ) begin
	   HDCP_cstate <= HDCP_AUTH_PULSE; // hack for tivo series 3
	end else begin
	   HDCP_cstate <=#1 HDCP_nstate;
	end
   end

   always @ (*) begin
      case (HDCP_cstate) //synthesis parallel_case full_case
	HDCP_UNPLUG: begin
	   HDCP_nstate = hpd ? HDCP_UNPLUG : HDCP_WAIT_AKSV;
	end
	HDCP_WAIT_AKSV: begin
	   // wait until the 14th byte is written to the HDCP register set
	   // this is the MSB of AKsv, and this triggers an authentication event
	   HDCP_nstate = Aksv14_write ? HDCP_AUTH_PULSE : HDCP_WAIT_AKSV;
//	   HDCP_nstate = Aksv14_write ? HDCP_WAIT_KMRDY : HDCP_WAIT_AKSV;
	   // in this implementation, skipe the HDCP_WAIT_KMRDY state
	end

	// this state is unreachable
	HDCP_WAIT_KMRDY: begin
	   HDCP_nstate = Km_ready ? HDCP_AUTH_PULSE : HDCP_WAIT_KMRDY;
	end
	
	////////
	// maybe put a state here to wait for Km to become ready
	// but for now, we assume host has pre-loaded Km. Km is fixed for every Tx/Rx HDMI pair.
	// So once you have computed it, it can be pre-loaded even before the transaction happens.
	// One way around this is to snag AKsv, Bksv; and if they are a new pair, compute Km 
	// and load it; and then override hpd high for a second to force a re-key *only* if
	// this is new pair. Thus, the first time you plug in a new device you *might* see it
	// flicker once, but it would never happen again, but I think typically you would
	// not notice because the screen would stay dark the entire time.
	//
	// --> above is the wait KMRDY state. The way this should work now is:
	// 1. Aksv is written, byte 14 triggers an interrupt to the CPU.
	// 2. CPU derives Km, writes Km, sets Km ready
	// 3. state machine then moves on to initiate auth pulse
	//
	////////
	HDCP_AUTH_PULSE: begin
	   HDCP_nstate = HDCP_AUTH;
	end
	HDCP_AUTH: begin
	   HDCP_nstate = stream_ready? HDCP_AUTH : HDCP_AUTH_WAIT;
	end
	HDCP_AUTH_WAIT: begin
	   HDCP_nstate = stream_ready ? HDCP_AUTH_VSYNC_PULSE : HDCP_AUTH_WAIT;
	end

	// this is a special vsync-update state just for after auth
	// because I don't know if there is more than 1 vsync period between
	// the conclusion of auth and the first 1001 assertion
	// if there is, then we end up unsynchronized on the Mi state
	HDCP_AUTH_VSYNC_PULSE: begin
	   HDCP_nstate = HDCP_AUTH_VSYNC;
	end
	HDCP_AUTH_VSYNC: begin
	   HDCP_nstate = stream_ready ? HDCP_AUTH_VSYNC : HDCP_AUTH_VSYNC_WAIT;
	end
	HDCP_AUTH_VSYNC_WAIT: begin
	   HDCP_nstate = stream_ready ? HDCP_WAIT_1001 : HDCP_AUTH_VSYNC_WAIT;
	end

	// our primary wait state
	HDCP_WAIT_1001: begin
	   HDCP_nstate = (vsync && (ctl_code[3:0] == 4'b1001)) ? 
			 HDCP_WAIT_1001_END : HDCP_WAIT_1001;
	end
	HDCP_WAIT_1001_END: begin
	   HDCP_nstate = (vsync && (ctl_code[3:0] == 4'b1001)) ?
			 HDCP_WAIT_1001_END : HDCP_READY;
	end
	

	HDCP_VSYNC_PULSE: begin
	   HDCP_nstate = HDCP_VSYNC;
	end
	HDCP_VSYNC: begin
	   HDCP_nstate = stream_ready ? HDCP_VSYNC : HDCP_VSYNC_WAIT;
	end
	HDCP_VSYNC_WAIT: begin
	   HDCP_nstate = stream_ready ? HDCP_WAIT_1001 : HDCP_VSYNC_WAIT;
	end

	// our primary cipher state
	HDCP_READY: begin
	   // Core assumption: the only way stream becomes un-ready during
	   // HDCP_READY is due to the external rekey event. vsync_rising
	   // will never result in this triggering because it itself must
	   // transition this state machine to a new state before stream_ready
	   // changes; and furthermore, stream_ready is guaranteed to be high
	   // upon return to this state.
	   HDCP_nstate = (stream_ready == 1'b0) ? HDCP_REKEY_WAIT : 
			 vsync_rising ? HDCP_VSYNC_PULSE :
			 HDCP_READY;
	end

	HDCP_REKEY: begin
	   HDCP_nstate = stream_ready ? HDCP_REKEY : HDCP_REKEY_WAIT;
	end
	HDCP_REKEY_WAIT: begin
	   HDCP_nstate = stream_ready ? HDCP_READY : HDCP_REKEY_WAIT;
	end
      endcase // case (HDCP_cstate)
   end

//   assign Km_ready = !Km_rdy2 & Km_rdy1; // rising edge pulse
   assign Km_ready = Km_rdy2; // for now make it level triggered ("cheezy mode")
		     
   always @ (posedge clk ) begin
      if( rst | hpd ) begin
	 auth_mode <=#1 1'b0;
	 hdcp_init <=#1 1'b0;
	 hdcp_requested <=#1 1'b0;
	 
	 Km_rdy0 <= 1'b0;
	 Km_rdy1 <= 1'b0;
	 Km_rdy2 <= 1'b0;
      end else begin
	 Km_rdy0 <= Km_valid;
	 Km_rdy1 <= Km_rdy0;
	 Km_rdy2 <= Km_rdy1;

	 case (HDCP_cstate) //synthesis parallel_case full_case
	   HDCP_UNPLUG: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b0;
	      hdcp_requested <=#1 1'b0;
	   end
	   HDCP_WAIT_AKSV: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b0;
	      hdcp_requested <=#1 1'b0;
	   end
	   
	   HDCP_WAIT_KMRDY: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b0;
	      hdcp_requested <=#1 1'b0;
	   end
	   
	   HDCP_AUTH_PULSE: begin
	      auth_mode <=#1 1'b1;
	      hdcp_init <=#1 1'b1; // pulse just one cycle
	      hdcp_requested <=#1 1'b0;
	   end
	   HDCP_AUTH: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b0;
	      hdcp_requested <=#1 1'b0;
	   end
	   HDCP_AUTH_WAIT: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b0;
	      hdcp_requested <=#1 1'b0;
	   end

	   HDCP_AUTH_VSYNC_PULSE: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b1;  // pulse init, but not with auth_mode
	      hdcp_requested <=#1 1'b0;
	   end
	   HDCP_AUTH_VSYNC: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b0;
	      hdcp_requested <=#1 1'b0;
	   end
	   HDCP_AUTH_VSYNC_WAIT: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b0;
	      hdcp_requested <=#1 1'b0;
	   end
	   
	   HDCP_WAIT_1001: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b0;
	      hdcp_requested <=#1 1'b0;
	   end
	   HDCP_WAIT_1001_END: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b0;
	      hdcp_requested <=#1 1'b0;
	   end
	   
	   HDCP_VSYNC_PULSE: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b1;  // pulse init, but not with auth_mode
	      hdcp_requested <=#1 1'b1;
	   end
	   HDCP_VSYNC: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b0;
	      hdcp_requested <=#1 1'b1;
	   end
	   HDCP_VSYNC_WAIT: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b0;
	      hdcp_requested <=#1 1'b1;
	   end
	   
	   HDCP_READY: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b0;
	      hdcp_requested <=#1 1'b1;
	   end
	   
	   HDCP_REKEY: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b0;
	      hdcp_requested <=#1 1'b1;
	   end
	   HDCP_REKEY_WAIT: begin
	      auth_mode <=#1 1'b0;
	      hdcp_init <=#1 1'b0;
	      hdcp_requested <=#1 1'b1;
	   end
	 endcase // case (HDCP_cstate)
      end // else: !if( ~rstbtn_n | hpd )
   end // always @ (posedge tx0_pclk)
   
   
   wire stream_ready;
   hdcp_cipher  cipher (
		.clk(clk),
		.reset(rst),
		.Km(Km),
		.An(An),
		.hdcpBlockCipher_init(hdcp_init),
		.authentication(auth_mode),
		.hdcpRekeyCipher(hdcp_rekey),
		.hdcpStreamCipher(hdcp_ena && (HDCP_cstate == HDCP_READY)),
		.pr_data(cipher_stream),
		.stream_ready(stream_ready)
//		.cipher_debug(cipher_debug)
		);
endmodule // hdcp_mod
