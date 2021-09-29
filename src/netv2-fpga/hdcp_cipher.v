//////////////////////////////////////////////////////////////////////////////
// Copyright (c) 2011, Andrew "bunnie" Huang
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without modification, 
// are permitted provided that the following conditions are met:
//
//  * Redistributions of source code must retain the above copyright notice, 
//    this list of conditions and the following disclaimer.
//  * Redistributions in binary form must reproduce the above copyright notice, 
//    this list of conditions and the following disclaimer in the documentation and/or 
//    other materials provided with the distribution.
//
//    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY 
//    EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES 
//    OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT 
//    SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
//    INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
//    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR 
//    PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
//    WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
//    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
//    POSSIBILITY OF SUCH DAMAGE.
//
//////////////////////////////////////////////////////////////////////////////

`timescale 1 ns / 1 ps

// generates a stream of hdcp cipher data
module hdcp_cipher(
		   input wire    clk,
		   input         reset,
		   
		   input [55:0]  Km,              // shared secret value
		   input [63:0]  An,              // session random number

		   input         hdcpBlockCipher_init, // pulsed only one cycle
		   input         authentication,  // pulsed one cycle same time as above
		   input         hdcpRekeyCipher, // pulsed one cycle to initiate rekey
		   input         hdcpStreamCipher,// advance cipher state one clock
		   output [23:0] pr_data,         // pseudorandom data output
		   output reg    stream_ready     // asserted when stream is ready (after init seq)
//		   output [12:0] cipher_debug
		   );

   wire 			 lfsr_out;
   wire [23:0] 			 ostream;
   wire [83:0] 			 Bo_wire;

   parameter INIT =       12'b1 << 0;   // 1
   parameter BLOCK_1 =    12'b1 << 1;   // 2
   parameter BLOCK_2 =    12'b1 << 2;   // 4
   parameter BLOCK_3 =    12'b1 << 3;   // 8
   parameter BLOCK_4 =    12'b1 << 4;   // 10
   parameter BLOCK_5 =    12'b1 << 5;   // 20
   parameter BLOCK_6 =    12'b1 << 6;   // 40
   parameter BLOCK_7 =    12'b1 << 7;   // 80
   parameter BLOCK_8 =    12'b1 << 8;   // 100
   parameter BLOCK_9 =    12'b1 << 9;   // 200 
   parameter GET_M   =    12'b1 << 10;  // 400
   parameter STREAM  =    12'b1 << 11;  // 800
   parameter REKEY   =    12'b1 << 12;  // 1000 (optimized to 0)
   parameter nSTATES = 13;
   
   reg [(nSTATES-1):0] cstate = {{(nSTATES-1){1'b0}},1'b1};
   reg [(nSTATES-1):0] nstate;

//   assign cipher_debug = cstate;
   
//   `define SIMULATION 1
`ifdef SIMULATION
   // synthesis translate_off
   reg [8*20:1] 	     state_ascii = "INIT               ";
   always @(cstate) begin
      if      (cstate == INIT     )  state_ascii <= "INIT               ";
      else if (cstate == BLOCK_1  )  state_ascii <= "BLOCK_1            ";
      else if (cstate == BLOCK_2  )  state_ascii <= "BLOCK_2            ";
      else if (cstate == BLOCK_3  )  state_ascii <= "BLOCK_3            ";
      else if (cstate == BLOCK_4  )  state_ascii <= "BLOCK_4            ";
      else if (cstate == BLOCK_5  )  state_ascii <= "BLOCK_5            ";
      else if (cstate == BLOCK_6  )  state_ascii <= "BLOCK_6            ";
      else if (cstate == BLOCK_7  )  state_ascii <= "BLOCK_7            ";
      else if (cstate == BLOCK_8  )  state_ascii <= "BLOCK_8            ";
      else if (cstate == BLOCK_9  )  state_ascii <= "BLOCK_9            ";
      else if (cstate == GET_M    )  state_ascii <= "GET_M              ";
      else if (cstate == STREAM   )  state_ascii <= "STREAM             ";
      else if (cstate == REKEY    )  state_ascii <= "REKEY              ";
      else state_ascii                           <= "WTF                ";
   end
   // synthesis translate_on
`endif //  `ifdef SIMULATION

   reg [5:0] 	       statecnt;
   reg 		       rekey;
   reg 		       load_block;
   reg 		       load_56; // load 56 or 80 bits...
   reg 		       load_lfsr;
   reg 		       advance_lfsr;
   reg 		       advance_block;
   reg [83:0] 	       Ks;
   reg [83:0] 	       Ki;
   reg [63:0] 	       Mi;
   reg 		       load_ks;
   reg 		       auth_mode;
   reg [83:0] 	       Kmod;
      
   always @ (posedge clk or posedge reset) begin
      if (reset)
	cstate <= INIT;
            else
	cstate <=#1 nstate;
   end
   
   hdcp_lfsr  lfsr( .clk(clk), .reset(reset),
		    .iv(auth_mode ? Ks[55:0] : Ki[55:0]),
		    .init_iv(load_lfsr),
		    .advance(advance_lfsr),
		    .onebit(lfsr_out));

   hdcp_block block( .clk(clk), .reset(reset),

		     .load(load_block),
		     .B(auth_mode ? {20'b0,An} : {20'b0,Mi}),
		     .K(Kmod),
		     .Bo(Bo_wire),
		     .rekey(rekey),
		     .lfsr_in(lfsr_out),
		     .ostream(ostream),
		     .advance(advance_block));
   assign pr_data = ostream;

   always @ (*) begin
      case ({auth_mode,load_56}) //synthesis parallel_case full_case
	2'b00: begin  // not auth mode, load 84 bits
	   Kmod = Ki;
	end
	2'b01: begin  // not auth mode, but load 56 bits only
	   Kmod = {28'b0,Ks[55:0]};
	end
	2'b10: begin // auth mode, load 84 bits
	   Kmod = Ks;
	end
	2'b11: begin // auth mode, load only 56 bits
	   Kmod = {28'b0,Km[55:0]};
	end
      endcase // case ({auth_mode,load_56})
   end // always @ (*)

   
   always @ (*) begin
      case (cstate) //synthesis parallel_case full_case
	INIT: begin
	   nstate = hdcpBlockCipher_init ? BLOCK_1 : INIT;
	end
	BLOCK_1: begin
	   nstate = BLOCK_2;
	end
	BLOCK_2: begin
	   nstate = (statecnt >= 6'd47) ? BLOCK_3: BLOCK_2;
	end
	BLOCK_3: begin
	   nstate = BLOCK_4;
	end
	BLOCK_4: begin
	   nstate = BLOCK_5;
	end
	BLOCK_5: begin
	   nstate = BLOCK_6;
	end
	BLOCK_6: begin
	   nstate = BLOCK_7;
	end
	BLOCK_7: begin
	   nstate = BLOCK_8;
	end
	BLOCK_8: begin
	   nstate = (statecnt >= 6'd55) ? BLOCK_9: BLOCK_8;
	end
	BLOCK_9: begin
	   nstate = GET_M;
	end
	GET_M: begin
	   nstate = STREAM;
	end
	STREAM: begin
	   if( hdcpBlockCipher_init ) begin
	      nstate = BLOCK_1;
	   end else if( hdcpRekeyCipher ) begin
	      nstate = REKEY;
	   end else begin
	      nstate = STREAM;
	   end
	end
	REKEY: begin
	   if( hdcpBlockCipher_init ) begin
	      nstate = BLOCK_1;
	   end else begin
	      nstate = (statecnt >= 6'd55) ? STREAM : REKEY;
	   end
	end
      endcase // case (cstate)
   end
   
   always @ (posedge clk or posedge reset) begin
      if( reset ) begin
	 statecnt <=#1 6'b0;
	 rekey <=#1 1'b0;
	 load_block <=#1 1'b0;
	 advance_lfsr <=#1 1'b0;
	 advance_block <=#1 1'b0;
	 load_ks <=#1 1'b0;
	 auth_mode <=#1 1'b0;
	 stream_ready <=#1 1'b0;
	 load_56 <=#1 1'b0;
      end else begin
	 case (cstate) // synthesis parallel_case full_case
	   INIT: begin
	      statecnt <=#1 6'b0;
	      rekey <=#1 1'b0;
	      load_block <=#1 1'b0;
	      advance_lfsr <=#1 1'b0;
	      advance_block <=#1 1'b0;
	      load_ks <=#1 1'b0;
	      auth_mode <=#1 authentication;
	      load_lfsr <=#1 1'b0;
	      stream_ready <=#1 1'b0;
	      load_56 <=#1 1'b0;
	   end
	   BLOCK_1: begin
	      statecnt <=#1 6'b0;   
	      rekey <=#1 1'b0;
	      load_block <=#1 1'b1; // load B & K regs of block module
	      advance_lfsr <=#1 1'b0;
	      advance_block <=#1 1'b0;
	      load_ks <=#1 1'b0;
	      auth_mode <=#1 auth_mode;
	      load_lfsr <=#1 1'b0;
	      stream_ready <=#1 1'b0;
	      load_56 <=#1 1'b1;
	   end
	   BLOCK_2: begin
	      statecnt <=#1 statecnt + 1; // 48 clocks
	      rekey <=#1 1'b0;
	      load_block <=#1 1'b0;
	      advance_lfsr <=#1 1'b0;
	      advance_block <=#1 1'b1;
	      load_ks <=#1 1'b0;
	      auth_mode <=#1 auth_mode;
	      load_lfsr <=#1 1'b0;
	      stream_ready <=#1 1'b0;
	      load_56 <=#1 1'b0;
	   end
	   BLOCK_3: begin
	      statecnt <=#1 0;
	      rekey <=#1 1'b0;
	      load_block <=#1 1'b0;
	      advance_lfsr <=#1 1'b0;
	      advance_block <=#1 1'b0;
	      load_ks <=#1 1'b1;  // save Ks, Ki, and B=>K
	      auth_mode <=#1 auth_mode;
	      load_lfsr <=#1 1'b0;
	      stream_ready <=#1 1'b0;
	      load_56 <=#1 1'b0;
	   end
	   BLOCK_4: begin
	      statecnt <=#1 0;
	      rekey <=#1 1'b0;
	      load_block <=#1 1'b0;
	      advance_lfsr <=#1 1'b0;
	      advance_block <=#1 1'b0;
	      load_ks <=#1 1'b1; // dup of above
	      auth_mode <=#1 auth_mode;
	      load_lfsr <=#1 1'b0;
	      stream_ready <=#1 1'b0;
	      load_56 <=#1 1'b0;
	   end
	   BLOCK_5: begin
	      statecnt <=#1 0;
	      rekey <=#1 1'b0;
	      load_block <=#1 1'b1;   // reload block cipher
	      advance_lfsr <=#1 1'b0;
	      advance_block <=#1 1'b0;
	      load_ks <=#1 1'b0;
	      auth_mode <=#1 auth_mode;
	      load_lfsr <=#1 1'b0;
	      stream_ready <=#1 1'b0;
	      load_56 <=#1 1'b0;
	   end
	   BLOCK_6: begin
	      statecnt <=#1 0;
	      rekey <=#1 1'b0;   
	      load_block <=#1 1'b0;
	      advance_lfsr <=#1 1'b0;
	      advance_block <=#1 1'b0;
	      load_ks <=#1 1'b0;
	      auth_mode <=#1 auth_mode;
	      load_lfsr <=#1 1'b1;    // init lfsr
	      stream_ready <=#1 1'b0;
	      load_56 <=#1 1'b0;
	   end
	   BLOCK_7: begin
	      statecnt <=#1 0;
	      rekey <=#1 1'b1;         // assert rekey
	      load_block <=#1 1'b0;
	      advance_lfsr <=#1 1'b0;
	      advance_block <=#1 1'b0;
	      load_ks <=#1 1'b0;
	      auth_mode <=#1 auth_mode;
	      load_lfsr <=#1 1'b0;
	      stream_ready <=#1 1'b0;
	      load_56 <=#1 1'b0;
	   end
	   BLOCK_8: begin
	      statecnt <=#1 statecnt + 1; // 56 clocks
	      rekey <=#1 1'b1; 
	      load_block <=#1 1'b0;
	      advance_lfsr <=#1 1'b1;
	      advance_block <=#1 1'b1;
	      load_ks <=#1 1'b0;
	      auth_mode <=#1 auth_mode;
	      load_lfsr <=#1 1'b0;
	      stream_ready <=#1 1'b0;
	      load_56 <=#1 1'b0;
	   end
	   BLOCK_9: begin
	      statecnt <=#1 0;
	      rekey <=#1 1'b0;    // de-assert rekey
	      load_block <=#1 1'b0;
	      advance_lfsr <=#1 1'b0;
	      advance_block <=#1 1'b0;
	      load_ks <=#1 1'b0;
	      auth_mode <=#1 auth_mode;
	      load_lfsr <=#1 1'b0;
	      stream_ready <=#1 1'b0;
	      load_56 <=#1 1'b0;
	   end // case: BLOCK_9
	   GET_M: begin   // one cycle wait to get M register loaded properly
	      statecnt <=#1 0;
	      rekey <=#1 1'b0;
	      load_block <=#1 1'b0;
	      advance_lfsr <=#1 1'b0;
	      advance_block <=#1 1'b0;
	      load_ks <=#1 1'b0;
	      auth_mode <=#1 1'b0;
	      load_lfsr <=#1 1'b0;
	      stream_ready <=#1 1'b0;
	      load_56 <=#1 1'b0;
	   end
	   STREAM: begin
	      if( !hdcpBlockCipher_init && hdcpRekeyCipher ) begin
		 // start the rekey immediately to meet timing requirements (copy of REKEY state here)
		 statecnt <=#1 statecnt + 1;
		 rekey <=#1 1'b1;
		 load_block <=#1 1'b0;
		 advance_lfsr <=#1 1'b1;
		 advance_block <=#1 1'b1;
		 load_ks <=#1 1'b0;
		 auth_mode <=#1 auth_mode;
		 load_lfsr <=#1 1'b0;
		 stream_ready <=#1 1'b0;
		 load_56 <=#1 1'b0;
	      end else begin // if ( !hdcpBlockCipher_init && hdcpRekeyCipher )
		 // default stream state
		 statecnt <=#1 0;
		 rekey <=#1 1'b0;
		 load_block <=#1 1'b0;
		 advance_lfsr <=#1 hdcpStreamCipher;
		 advance_block <=#1 hdcpStreamCipher;
		 load_ks <=#1 1'b0;
		 auth_mode <=#1 authentication;
		 load_lfsr <=#1 1'b0;
		 stream_ready <=#1 1'b1;
		 load_56 <=#1 1'b0;
	      end
	   end
	   REKEY: begin
	      statecnt <=#1 statecnt + 1;
	      rekey <=#1 1'b1;
	      load_block <=#1 1'b0;
	      advance_lfsr <=#1 1'b1;
	      advance_block <=#1 1'b1;
	      load_ks <=#1 1'b0;
	      auth_mode <=#1 auth_mode;
	      load_lfsr <=#1 1'b0;
	      stream_ready <=#1 1'b0;
	      load_56 <=#1 1'b0;
	   end
	 endcase // case (cstate)
      end
   end // always @ (posedge clk or posedge reset)
   
   always @(posedge clk or posedge reset) begin
      if( reset ) begin
	 Ks <= 80'b0;
	 Ki <= 80'b0;
      end else begin
//	 if( hdcpBlockCipher_init ) begin
//	    Ks <= (authentication | auth_mode) ? {28'b0,Km} : Ks;
//	    Ki <= 80'b0;
//	 end else if( load_ks && auth_mode ) begin
	 if( load_ks && auth_mode ) begin
	    Ks <= Bo_wire;
	    Ki <= 80'b0;
	 end else if( load_ks && !auth_mode ) begin
	    Ks <= Ks;
	    Ki <= Bo_wire;
	 end else begin
	    Ks <= Ks;
	    Ki <= Ki;
	 end
      end
   end // always @ (posedge clk or posedge reset)
      
   always @(posedge clk or posedge reset) begin
      if( reset ) begin
	 Mi <= 80'b0;
      end else begin
	 if( (cstate == BLOCK_8) || (cstate == BLOCK_9) || (cstate == GET_M) ) begin
	    Mi[15:0] <= ostream[15:0];
	    Mi[31:16] <= Mi[15:0];
	    Mi[47:32] <= Mi[31:16];
	    Mi[63:48] <= Mi[47:32];
	 end else begin
	    Mi <= Mi;
	 end
      end // else: !if( reset )
   end // always @ (posedge clk or posedge reset)
   
endmodule // hdcp_cipher
