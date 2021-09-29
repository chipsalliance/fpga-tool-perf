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

// lfsr module for hdcp cipher
module hdcp_lfsr(
		   input wire    clk,
		   input wire    reset,           // this is just a low-level reset
		   
		   input wire [55:0]  iv,              // initial values

		   input  wire   init_iv,         // load initial values
		   input  wire   advance,         // advance state one cycle
		   output wire   onebit           // my one-bit output
		   );

   reg [12:0] 			 lfsr0;
   reg [13:0] 			 lfsr1;
   reg [15:0] 			 lfsr2;
   reg [16:0] 			 lfsr3;

   wire [3:0] 			 comb_tap0;
   wire [3:0] 			 comb_tap1;
   wire [3:0] 			 comb_tap2;
   
   always @(posedge clk or posedge reset) begin
      if( reset == 1 ) begin
	 lfsr0 <= 13'b0;
	 lfsr1 <= 14'b0;
	 lfsr2 <= 16'b0;
	 lfsr3 <= 17'b0;
      end else begin
	 if( init_iv ) begin
	    // assume bit-offsets start from 0
	    lfsr0[12:0] <= {~iv[6],iv[11:0]};
	    lfsr1[13:0] <= {~iv[18],iv[24:12]};
	    lfsr2[15:0] <= {~iv[32],iv[39:25]};
	    lfsr3[16:0] <= {~iv[47],iv[55:40]};
	 end else if( advance ) begin
	    // 13 11 9 5
	    // 12 10 8 4
	    lfsr0[0 ] <= lfsr0[4] ^ lfsr0[8] ^ lfsr0[10] ^ lfsr0[12];
	    lfsr0[1 ] <= lfsr0[0 ];
	    lfsr0[2 ] <= lfsr0[1 ];
	    lfsr0[3 ] <= lfsr0[2 ];
	    lfsr0[4 ] <= lfsr0[3 ];
	    lfsr0[5 ] <= lfsr0[4 ];
	    lfsr0[6 ] <= lfsr0[5 ];
	    lfsr0[7 ] <= lfsr0[6 ];
	    lfsr0[8 ] <= lfsr0[7 ];
	    lfsr0[9 ] <= lfsr0[8 ];
	    lfsr0[10] <= lfsr0[9 ];
	    lfsr0[11] <= lfsr0[10];
	    lfsr0[12] <= lfsr0[11];

	    //4 6 7 10 11 14
	    //3 5 6 9  10 13
	    lfsr1[0 ] <= lfsr1[3] ^ lfsr1[5] ^ lfsr1[6] ^ lfsr1[9] ^ lfsr1[10] ^ lfsr1[13];
	    lfsr1[1 ] <= lfsr1[0 ];
	    lfsr1[2 ] <= lfsr1[1 ];
	    lfsr1[3 ] <= lfsr1[2 ];
	    lfsr1[4 ] <= lfsr1[3 ];
	    lfsr1[5 ] <= lfsr1[4 ];
	    lfsr1[6 ] <= lfsr1[5 ];
	    lfsr1[7 ] <= lfsr1[6 ];
	    lfsr1[8 ] <= lfsr1[7 ];
	    lfsr1[9 ] <= lfsr1[8 ];
	    lfsr1[10] <= lfsr1[9 ];
	    lfsr1[11] <= lfsr1[10];
	    lfsr1[12] <= lfsr1[11];
	    lfsr1[13] <= lfsr1[12];

	    //5 7 8 12 15 16
	    //4 6 7 11 14 15
	    lfsr2[0 ] <= lfsr2[4] ^ lfsr2[6] ^ lfsr2[7] ^ lfsr2[11] ^ lfsr2[14] ^ lfsr2[15];
	    lfsr2[1 ] <= lfsr2[0 ];
	    lfsr2[2 ] <= lfsr2[1 ];
	    lfsr2[3 ] <= lfsr2[2 ];
	    lfsr2[4 ] <= lfsr2[3 ];
	    lfsr2[5 ] <= lfsr2[4 ];
	    lfsr2[6 ] <= lfsr2[5 ];
	    lfsr2[7 ] <= lfsr2[6 ];
	    lfsr2[8 ] <= lfsr2[7 ];
	    lfsr2[9 ] <= lfsr2[8 ];
	    lfsr2[10] <= lfsr2[9 ];
	    lfsr2[11] <= lfsr2[10];
	    lfsr2[12] <= lfsr2[11];
	    lfsr2[13] <= lfsr2[12];
	    lfsr2[14] <= lfsr2[13];
	    lfsr2[15] <= lfsr2[14];

	    //5 11 15 17
	    //4 10 14 16
	    lfsr3[0 ] <= lfsr3[4] ^ lfsr3[10] ^ lfsr3[14] ^ lfsr3[16];
	    lfsr3[1 ] <= lfsr3[0 ];
	    lfsr3[2 ] <= lfsr3[1 ];
	    lfsr3[3 ] <= lfsr3[2 ];
	    lfsr3[4 ] <= lfsr3[3 ];
	    lfsr3[5 ] <= lfsr3[4 ];
	    lfsr3[6 ] <= lfsr3[5 ];
	    lfsr3[7 ] <= lfsr3[6 ];
	    lfsr3[8 ] <= lfsr3[7 ];
	    lfsr3[9 ] <= lfsr3[8 ];
	    lfsr3[10] <= lfsr3[9 ];
	    lfsr3[11] <= lfsr3[10];
	    lfsr3[12] <= lfsr3[11];
	    lfsr3[13] <= lfsr3[12];
	    lfsr3[14] <= lfsr3[13];
	    lfsr3[15] <= lfsr3[14];
	    lfsr3[16] <= lfsr3[15];
	 end else begin
	    // hold state
	    lfsr0 <= lfsr0;
	    lfsr1 <= lfsr1;
	    lfsr2 <= lfsr2;
	    lfsr3 <= lfsr3;
	 end
      end // else: !if( reset == 1 )
   end // always @ (posedge clk or posedge reset)

   assign comb_tap0[0] = lfsr0[3];
   assign comb_tap0[1] = lfsr1[4];
   assign comb_tap0[2] = lfsr2[5];
   assign comb_tap0[3] = lfsr3[5];
   
   assign comb_tap1[0] = lfsr0[7];
   assign comb_tap1[1] = lfsr1[8];
   assign comb_tap1[2] = lfsr2[9];
   assign comb_tap1[3] = lfsr3[11];
   
   assign comb_tap2[0] = lfsr0[12];
   assign comb_tap2[1] = lfsr1[13];
   assign comb_tap2[2] = lfsr2[15];
   assign comb_tap2[3] = lfsr3[16];

   wire [3:0] sh_dout;
   shuffle_network sh0 ( .clk(clk), .reset(reset),
			 .din(comb_tap0[0] ^ comb_tap0[1] ^ comb_tap0[2] ^ comb_tap0[3]),
			 .sel(comb_tap1[0]),
			 .advance(advance),
			 .init_iv(init_iv),
			 .dout(sh_dout[0])
			 );
   
   shuffle_network sh1 ( .clk(clk), .reset(reset),
			 .din(sh_dout[0]),
			 .sel(comb_tap1[1]),
			 .advance(advance),
			 .init_iv(init_iv),
			 .dout(sh_dout[1])
			 );
   
   shuffle_network sh2 ( .clk(clk), .reset(reset),
			 .din(sh_dout[1]),
			 .sel(comb_tap1[2]),
			 .advance(advance),
			 .init_iv(init_iv),
			 .dout(sh_dout[2])
			 );

   shuffle_network sh3 ( .clk(clk), .reset(reset),
			 .din(sh_dout[2]),
			 .sel(comb_tap1[3]),
			 .advance(advance),
			 .init_iv(init_iv),
			 .dout(sh_dout[3])
			 );
   
   assign onebit = sh_dout[3] ^ comb_tap2[0] ^ comb_tap2[1] ^ comb_tap2[2] ^ comb_tap2[3];
   
endmodule // hdcp_lfsr

