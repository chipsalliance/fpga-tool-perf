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

module hdcp_block (
		   input wire clk,
		   input wire reset,

		   input wire load,
		   input wire [83:0] B,
		   input wire [83:0] K,

		   output wire [83:0] Bo,
		   input wire rekey,
		   input wire lfsr_in,

		   output reg [23:0] ostream,
		   
		   input wire advance
		   );

   reg [27:0] 		      Bx;
   reg [27:0]		      By;
   reg [27:0] 		      Bz;
   wire [27:0] 		      o_Bx;
   wire [27:0]		      o_By;
   wire [27:0] 		      o_Bz;

   reg [27:0] 		      Kx;
   reg [27:0] 		      Ky;
   reg [27:0] 		      Kz;
   wire [27:0] 		      o_Kx;
   wire [27:0] 		      o_Ky;
   wire 		      o_Ky13; // bit 13 comes from lfsr_in when rekey is active
   wire [27:0] 		      o_Kz;

   wire [23:0] 		      ostream_r;
   
   // semi-auto generated with a perl script
   wire [3:0] 		      SK0_in;
   wire [3:0] 		      SK1_in;
   wire [3:0] 		      SK2_in;
   wire [3:0] 		      SK3_in;
   wire [3:0] 		      SK4_in;
   wire [3:0] 		      SK5_in;
   wire [3:0] 		      SK6_in;
   
   reg [3:0] 		      SK0;
   reg [3:0] 		      SK1;
   reg [3:0] 		      SK2;
   reg [3:0] 		      SK3;
   reg [3:0] 		      SK4;
   reg [3:0] 		      SK5;
   reg [3:0] 		      SK6;
   
   wire [3:0] 		      SB0_in;
   wire [3:0] 		      SB1_in;
   wire [3:0] 		      SB2_in;
   wire [3:0] 		      SB3_in;
   wire [3:0] 		      SB4_in;
   wire [3:0] 		      SB5_in;
   wire [3:0] 		      SB6_in;
   
   reg [3:0] 		      SB0;
   reg [3:0] 		      SB1;
   reg [3:0] 		      SB2;
   reg [3:0] 		      SB3;
   reg [3:0] 		      SB4;
   reg [3:0] 		      SB5;
   reg [3:0] 		      SB6;

   assign Bo = {Bz[27:0],By[27:0],Bx[27:0]};
   always @(posedge clk or posedge reset) begin
      if( reset ) begin
	 Bx <= 28'b0;
	 By <= 28'b0;
	 Bz <= 28'b0;
	 Kx <= 28'b0;
	 Ky <= 28'b0;
	 Kz <= 28'b0;
	 ostream <= 24'b0;
      end else begin
	 if( load ) begin
//	    Bz <= B[83:56];
	    Bz <= {19'b0,1'b0,B[63:56]}; // repeater is fixed to zero
	    By <= B[55:28];
	    Bx <= B[27:0];

	    Kz <= K[83:56];
	    Ky <= K[55:28];
	    Kx <= K[27:0];
	    ostream <= 24'b0;
	 end else if( advance ) begin
	    Bx <= o_Bx;
	    By <= o_By;
	    Bz <= o_Bz;

	    Kx <= o_Kx;
	    Ky <= o_Ky;
	    Kz <= o_Kz;
	    ostream <= ostream_r;
	 end else begin
	    Bx <= Bx;
	    By <= By;
	    Bz <= Bz;

	    Kx <= Kx;
	    Ky <= Ky;
	    Kz <= Kz;
	    ostream <= ostream;
	 end
      end // else: !if( reset )
   end // always @ (posedge clk or posedge reset)
   

   ////////////
   // bround linear transformation
   // generated using perl script makebround.pl bround.csv > bround_code.txt
   ////////////
   diff_network bround1 ( .o({o_Bx[24],o_Bx[20],o_Bx[16],o_Bx[12],o_Bx[8],o_Bx[4],o_Bx[0]}),
			  .k({Ky[6],Ky[5],Ky[4],Ky[3],Ky[2],Ky[1],Ky[0]}),
			  .i({Bz[6],Bz[5],Bz[4],Bz[3],Bz[2],Bz[1],Bz[0]}) );
   
   diff_network bround2 ( .o({o_By[24],o_By[20],o_By[16],o_By[12],o_By[8],o_By[4],o_By[0]}),
			  .k({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
			  .i({By[12],By[2],By[1],By[0],Bz[9],Bz[8],Bz[7]}) );
   
   diff_network bround3 ( .o({o_By[25],o_By[21],o_By[17],o_By[13],o_By[9],o_By[5],o_By[1]}),
			  .k({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
			  .i({By[13],By[5],By[4],By[3],Bz[12],Bz[11],Bz[10]}) );
   
   diff_network bround4 ( .o({o_By[26],o_By[22],o_By[18],o_By[14],o_By[10],o_By[6],o_By[2]}),
			  .k({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
			  .i({By[14],By[8],By[7],By[6],Bz[15],Bz[14],Bz[13]}) );
   
   diff_network bround5 ( .o({o_By[27],o_By[23],o_By[19],o_By[15],o_By[11],o_By[7],o_By[3]}),
			  .k({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
			  .i({By[15],By[11],By[10],By[9],Bz[18],Bz[17],Bz[16]}) );
   
   diff_network bround6 ( .o({o_Bx[25],o_Bx[21],o_Bx[17],o_Bx[13],o_Bx[9],o_Bx[5],o_Bx[1]}),
			  .k({Ky[13],Ky[12],Ky[11],Ky[10],Ky[9],Ky[8],Ky[7]}),
			  .i({Bz[21],Bz[20],Bz[19],By[19],By[18],By[17],By[16]}) );
   
   diff_network bround7 ( .o({o_Bx[26],o_Bx[22],o_Bx[18],o_Bx[14],o_Bx[10],o_Bx[6],o_Bx[2]}),
			  .k({Ky[20],Ky[19],Ky[18],Ky[17],Ky[16],Ky[15],Ky[14]}),
			  .i({Bz[24],Bz[23],Bz[22],By[23],By[22],By[21],By[20]}) );
   
   diff_network bround8 ( .o({o_Bx[27],o_Bx[23],o_Bx[19],o_Bx[15],o_Bx[11],o_Bx[7],o_Bx[3]}),
			  .k({Ky[27],Ky[26],Ky[25],Ky[24],Ky[23],Ky[22],Ky[21]}),
			  .i({Bz[27],Bz[26],Bz[25],By[27],By[26],By[25],By[24]}) );
   
   
   ////////////
   // kround linear transform
   // generated using perl script makelinx.pl kround.csv > kround
   ////////////
   
   diff_network kround1 ( .o({o_Kx[24],o_Kx[20],o_Kx[16],o_Kx[12],o_Kx[8],o_Kx[4],o_Kx[0]}),
			  .i({Kz[6],Kz[5],Kz[4],Kz[3],Kz[2],Kz[1],Kz[0]}),
			  .k(7'b0) );
   
   diff_network kround2 ( .o({o_Ky[24],o_Ky[20],o_Ky[16],o_Ky[12],o_Ky[8],o_Ky[4],o_Ky[0]}),
			  .i({Ky[12],Ky[2],Ky[1],Ky[0],Kz[9],Kz[8],Kz[7]}),
			  .k(7'b0) );
   
   diff_network kround3 ( .o({o_Ky[25],o_Ky[21],o_Ky[17],o_Ky13,o_Ky[9],o_Ky[5],o_Ky[1]}),
			  .i({Ky[13],Ky[5],Ky[4],Ky[3],Kz[12],Kz[11],Kz[10]}),
			  .k(7'b0) );
   assign o_Ky[13] = rekey ? lfsr_in : o_Ky13;
   
   diff_network kround4 ( .o({o_Ky[26],o_Ky[22],o_Ky[18],o_Ky[14],o_Ky[10],o_Ky[6],o_Ky[2]}),
			  .i({Ky[14],Ky[8],Ky[7],Ky[6],Kz[15],Kz[14],Kz[13]}),
			  .k(7'b0) );
   
   diff_network kround5 ( .o({o_Ky[27],o_Ky[23],o_Ky[19],o_Ky[15],o_Ky[11],o_Ky[7],o_Ky[3]}),
			  .i({Ky[15],Ky[11],Ky[10],Ky[9],Kz[18],Kz[17],Kz[16]}),
			  .k(7'b0) );
   
   diff_network kround6 ( .o({o_Kx[25],o_Kx[21],o_Kx[17],o_Kx[13],o_Kx[9],o_Kx[5],o_Kx[1]}),
			  .i({Kz[21],Kz[20],Kz[19],Ky[19],Ky[18],Ky[17],Ky[16]}),
			  .k(7'b0) );
   
   diff_network kround7 ( .o({o_Kx[26],o_Kx[22],o_Kx[18],o_Kx[14],o_Kx[10],o_Kx[6],o_Kx[2]}),
			  .i({Kz[24],Kz[23],Kz[22],Ky[23],Ky[22],Ky[21],Ky[20]}),
			  .k(7'b0) );
   
   diff_network kround8 ( .o({o_Kx[27],o_Kx[23],o_Kx[19],o_Kx[15],o_Kx[11],o_Kx[7],o_Kx[3]}),
			  .i({Kz[27],Kz[26],Kz[25],Ky[27],Ky[26],Ky[25],Ky[24]}),
			  .k(7'b0) );
   
   /////////////
   // sboxes
   // generated using script makeblock.pl sbox_src.txt > sbox_code.txt
   /////////////
   always @(SK0_in[3:0]) begin
      case (SK0_in[3:0])
	4'h0: SK0 = 4'd8;
	4'h1: SK0 = 4'd14;
	4'h2: SK0 = 4'd5;
	4'h3: SK0 = 4'd9;
	4'h4: SK0 = 4'd3;
	4'h5: SK0 = 4'd0;
	4'h6: SK0 = 4'd12;
	4'h7: SK0 = 4'd6;
	4'h8: SK0 = 4'd1;
	4'h9: SK0 = 4'd11;
	4'hA: SK0 = 4'd15;
	4'hB: SK0 = 4'd2;
	4'hC: SK0 = 4'd4;
	4'hD: SK0 = 4'd7;
	4'hE: SK0 = 4'd10;
	4'hF: SK0 = 4'd13;
      endcase // case (SK0_in[3:0])
   end // always @ (SK0_in[3:0])
   
   always @(SK0_in[3:0]) begin
      case (SK0_in[3:0])
	4'h0: SK0 = 4'd8;
	4'h1: SK0 = 4'd14;
	4'h2: SK0 = 4'd5;
	4'h3: SK0 = 4'd9;
	4'h4: SK0 = 4'd3;
	4'h5: SK0 = 4'd0;
	4'h6: SK0 = 4'd12;
	4'h7: SK0 = 4'd6;
	4'h8: SK0 = 4'd1;
	4'h9: SK0 = 4'd11;
	4'hA: SK0 = 4'd15;
	4'hB: SK0 = 4'd2;
	4'hC: SK0 = 4'd4;
	4'hD: SK0 = 4'd7;
	4'hE: SK0 = 4'd10;
	4'hF: SK0 = 4'd13;
      endcase // case (SK0_in[3:0])
   end // always @ (SK0_in[3:0])
   
   always @(SK1_in[3:0]) begin
      case (SK1_in[3:0])
	4'h0: SK1 = 4'd1;
	4'h1: SK1 = 4'd6;
	4'h2: SK1 = 4'd4;
	4'h3: SK1 = 4'd15;
	4'h4: SK1 = 4'd8;
	4'h5: SK1 = 4'd3;
	4'h6: SK1 = 4'd11;
	4'h7: SK1 = 4'd5;
	4'h8: SK1 = 4'd10;
	4'h9: SK1 = 4'd0;
	4'hA: SK1 = 4'd9;
	4'hB: SK1 = 4'd12;
	4'hC: SK1 = 4'd7;
	4'hD: SK1 = 4'd13;
	4'hE: SK1 = 4'd14;
	4'hF: SK1 = 4'd2;
      endcase // case (SK1_in[3:0])
   end // always @ (SK1_in[3:0])
   
   always @(SK2_in[3:0]) begin
      case (SK2_in[3:0])
	4'h0: SK2 = 4'd13;
	4'h1: SK2 = 4'd11;
	4'h2: SK2 = 4'd8;
	4'h3: SK2 = 4'd6;
	4'h4: SK2 = 4'd7;
	4'h5: SK2 = 4'd4;
	4'h6: SK2 = 4'd2;
	4'h7: SK2 = 4'd15;
	4'h8: SK2 = 4'd1;
	4'h9: SK2 = 4'd12;
	4'hA: SK2 = 4'd14;
	4'hB: SK2 = 4'd0;
	4'hC: SK2 = 4'd10;
	4'hD: SK2 = 4'd3;
	4'hE: SK2 = 4'd9;
	4'hF: SK2 = 4'd5;
      endcase // case (SK2_in[3:0])
   end // always @ (SK2_in[3:0])
   
   always @(SK3_in[3:0]) begin
      case (SK3_in[3:0])
	4'h0: SK3 = 4'd0;
	4'h1: SK3 = 4'd14;
	4'h2: SK3 = 4'd11;
	4'h3: SK3 = 4'd7;
	4'h4: SK3 = 4'd12;
	4'h5: SK3 = 4'd3;
	4'h6: SK3 = 4'd2;
	4'h7: SK3 = 4'd13;
	4'h8: SK3 = 4'd15;
	4'h9: SK3 = 4'd4;
	4'hA: SK3 = 4'd8;
	4'hB: SK3 = 4'd1;
	4'hC: SK3 = 4'd9;
	4'hD: SK3 = 4'd10;
	4'hE: SK3 = 4'd5;
	4'hF: SK3 = 4'd6;
      endcase // case (SK3_in[3:0])
   end // always @ (SK3_in[3:0])
   
   always @(SK4_in[3:0]) begin
      case (SK4_in[3:0])
	4'h0: SK4 = 4'd12;
	4'h1: SK4 = 4'd7;
	4'h2: SK4 = 4'd15;
	4'h3: SK4 = 4'd8;
	4'h4: SK4 = 4'd11;
	4'h5: SK4 = 4'd14;
	4'h6: SK4 = 4'd1;
	4'h7: SK4 = 4'd4;
	4'h8: SK4 = 4'd6;
	4'h9: SK4 = 4'd10;
	4'hA: SK4 = 4'd3;
	4'hB: SK4 = 4'd5;
	4'hC: SK4 = 4'd0;
	4'hD: SK4 = 4'd9;
	4'hE: SK4 = 4'd13;
	4'hF: SK4 = 4'd2;
      endcase // case (SK4_in[3:0])
   end // always @ (SK4_in[3:0])
   
   always @(SK5_in[3:0]) begin
      case (SK5_in[3:0])
	4'h0: SK5 = 4'd1;
	4'h1: SK5 = 4'd12;
	4'h2: SK5 = 4'd7;
	4'h3: SK5 = 4'd2;
	4'h4: SK5 = 4'd8;
	4'h5: SK5 = 4'd3;
	4'h6: SK5 = 4'd4;
	4'h7: SK5 = 4'd14;
	4'h8: SK5 = 4'd11;
	4'h9: SK5 = 4'd5;
	4'hA: SK5 = 4'd0;
	4'hB: SK5 = 4'd15;
	4'hC: SK5 = 4'd13;
	4'hD: SK5 = 4'd6;
	4'hE: SK5 = 4'd10;
	4'hF: SK5 = 4'd9;
      endcase // case (SK5_in[3:0])
   end // always @ (SK5_in[3:0])
   
   always @(SK6_in[3:0]) begin
      case (SK6_in[3:0])
	4'h0: SK6 = 4'd10;
	4'h1: SK6 = 4'd7;
	4'h2: SK6 = 4'd6;
	4'h3: SK6 = 4'd1;
	4'h4: SK6 = 4'd0;
	4'h5: SK6 = 4'd14;
	4'h6: SK6 = 4'd3;
	4'h7: SK6 = 4'd13;
	4'h8: SK6 = 4'd12;
	4'h9: SK6 = 4'd9;
	4'hA: SK6 = 4'd11;
	4'hB: SK6 = 4'd2;
	4'hC: SK6 = 4'd15;
	4'hD: SK6 = 4'd5;
	4'hE: SK6 = 4'd4;
	4'hF: SK6 = 4'd8;
      endcase // case (SK6_in[3:0])
   end // always @ (SK6_in[3:0])
   
   always @(SB0_in[3:0]) begin
      case (SB0_in[3:0])
	4'h0: SB0 = 4'd12;
	4'h1: SB0 = 4'd9;
	4'h2: SB0 = 4'd3;
	4'h3: SB0 = 4'd0;
	4'h4: SB0 = 4'd11;
	4'h5: SB0 = 4'd5;
	4'h6: SB0 = 4'd13;
	4'h7: SB0 = 4'd6;
	4'h8: SB0 = 4'd2;
	4'h9: SB0 = 4'd4;
	4'hA: SB0 = 4'd14;
	4'hB: SB0 = 4'd7;
	4'hC: SB0 = 4'd8;
	4'hD: SB0 = 4'd15;
	4'hE: SB0 = 4'd1;
	4'hF: SB0 = 4'd10;
      endcase // case (SB0_in[3:0])
   end // always @ (SB0_in[3:0])
   
   always @(SB1_in[3:0]) begin
      case (SB1_in[3:0])
	4'h0: SB1 = 4'd3;
	4'h1: SB1 = 4'd8;
	4'h2: SB1 = 4'd14;
	4'h3: SB1 = 4'd1;
	4'h4: SB1 = 4'd5;
	4'h5: SB1 = 4'd2;
	4'h6: SB1 = 4'd11;
	4'h7: SB1 = 4'd13;
	4'h8: SB1 = 4'd10;
	4'h9: SB1 = 4'd4;
	4'hA: SB1 = 4'd9;
	4'hB: SB1 = 4'd7;
	4'hC: SB1 = 4'd6;
	4'hD: SB1 = 4'd15;
	4'hE: SB1 = 4'd12;
	4'hF: SB1 = 4'd0;
      endcase // case (SB1_in[3:0])
   end // always @ (SB1_in[3:0])
   
   always @(SB2_in[3:0]) begin
      case (SB2_in[3:0])
	4'h0: SB2 = 4'd7;
	4'h1: SB2 = 4'd4;
	4'h2: SB2 = 4'd1;
	4'h3: SB2 = 4'd10;
	4'h4: SB2 = 4'd11;
	4'h5: SB2 = 4'd13;
	4'h6: SB2 = 4'd14;
	4'h7: SB2 = 4'd3;
	4'h8: SB2 = 4'd12;
	4'h9: SB2 = 4'd15;
	4'hA: SB2 = 4'd6;
	4'hB: SB2 = 4'd0;
	4'hC: SB2 = 4'd2;
	4'hD: SB2 = 4'd8;
	4'hE: SB2 = 4'd9;
	4'hF: SB2 = 4'd5;
      endcase // case (SB2_in[3:0])
   end // always @ (SB2_in[3:0])
   
   always @(SB3_in[3:0]) begin
      case (SB3_in[3:0])
	4'h0: SB3 = 4'd6;
	4'h1: SB3 = 4'd3;
	4'h2: SB3 = 4'd1;
	4'h3: SB3 = 4'd4;
	4'h4: SB3 = 4'd10;
	4'h5: SB3 = 4'd12;
	4'h6: SB3 = 4'd15;
	4'h7: SB3 = 4'd2;
	4'h8: SB3 = 4'd5;
	4'h9: SB3 = 4'd14;
	4'hA: SB3 = 4'd11;
	4'hB: SB3 = 4'd8;
	4'hC: SB3 = 4'd9;
	4'hD: SB3 = 4'd7;
	4'hE: SB3 = 4'd0;
	4'hF: SB3 = 4'd13;
      endcase // case (SB3_in[3:0])
   end // always @ (SB3_in[3:0])
   
   always @(SB4_in[3:0]) begin
      case (SB4_in[3:0])
	4'h0: SB4 = 4'd3;
	4'h1: SB4 = 4'd6;
	4'h2: SB4 = 4'd15;
	4'h3: SB4 = 4'd12;
	4'h4: SB4 = 4'd4;
	4'h5: SB4 = 4'd1;
	4'h6: SB4 = 4'd9;
	4'h7: SB4 = 4'd2;
	4'h8: SB4 = 4'd5;
	4'h9: SB4 = 4'd8;
	4'hA: SB4 = 4'd10;
	4'hB: SB4 = 4'd7;
	4'hC: SB4 = 4'd11;
	4'hD: SB4 = 4'd13;
	4'hE: SB4 = 4'd0;
	4'hF: SB4 = 4'd14;
      endcase // case (SB4_in[3:0])
   end // always @ (SB4_in[3:0])
   
   always @(SB5_in[3:0]) begin
      case (SB5_in[3:0])
	4'h0: SB5 = 4'd11;
	4'h1: SB5 = 4'd14;
	4'h2: SB5 = 4'd6;
	4'h3: SB5 = 4'd8;
	4'h4: SB5 = 4'd5;
	4'h5: SB5 = 4'd2;
	4'h6: SB5 = 4'd12;
	4'h7: SB5 = 4'd7;
	4'h8: SB5 = 4'd1;
	4'h9: SB5 = 4'd4;
	4'hA: SB5 = 4'd15;
	4'hB: SB5 = 4'd3;
	4'hC: SB5 = 4'd10;
	4'hD: SB5 = 4'd13;
	4'hE: SB5 = 4'd9;
	4'hF: SB5 = 4'd0;
      endcase // case (SB5_in[3:0])
   end // always @ (SB5_in[3:0])
   
   always @(SB6_in[3:0]) begin
      case (SB6_in[3:0])
	4'h0: SB6 = 4'd1;
	4'h1: SB6 = 4'd11;
	4'h2: SB6 = 4'd7;
	4'h3: SB6 = 4'd4;
	4'h4: SB6 = 4'd2;
	4'h5: SB6 = 4'd5;
	4'h6: SB6 = 4'd12;
	4'h7: SB6 = 4'd9;
	4'h8: SB6 = 4'd13;
	4'h9: SB6 = 4'd6;
	4'hA: SB6 = 4'd8;
	4'hB: SB6 = 4'd15;
	4'hC: SB6 = 4'd14;
	4'hD: SB6 = 4'd0;
	4'hE: SB6 = 4'd3;
	4'hF: SB6 = 4'd10;
      endcase // case (SB6_in[3:0])
   end // always @ (SB6_in[3:0])

   //////
   /// Sbox wiring
   /// generated by perl script ./make_sboxwires.pl
   //////
   assign SB0_in[0] = Bx[0];
   assign SB0_in[1] = Bx[7];
   assign SB0_in[2] = Bx[14];
   assign SB0_in[3] = Bx[21];
   
   assign SK0_in[0] = Kx[0];
   assign SK0_in[1] = Kx[7];
   assign SK0_in[2] = Kx[14];
   assign SK0_in[3] = Kx[21];
   
   assign o_Bz[0] = SB0[0];
   assign o_Bz[7] = SB0[1];
   assign o_Bz[14] = SB0[2];
   assign o_Bz[21] = SB0[3];
   
   assign o_Kz[0] = SK0[0];
   assign o_Kz[7] = SK0[1];
   assign o_Kz[14] = SK0[2];
   assign o_Kz[21] = SK0[3];
   
   assign SB1_in[0] = Bx[1];
   assign SB1_in[1] = Bx[8];
   assign SB1_in[2] = Bx[15];
   assign SB1_in[3] = Bx[22];
   
   assign SK1_in[0] = Kx[1];
   assign SK1_in[1] = Kx[8];
   assign SK1_in[2] = Kx[15];
   assign SK1_in[3] = Kx[22];
   
   assign o_Bz[1] = SB1[0];
   assign o_Bz[8] = SB1[1];
   assign o_Bz[15] = SB1[2];
   assign o_Bz[22] = SB1[3];
   
   assign o_Kz[1] = SK1[0];
   assign o_Kz[8] = SK1[1];
   assign o_Kz[15] = SK1[2];
   assign o_Kz[22] = SK1[3];
   
   assign SB2_in[0] = Bx[2];
   assign SB2_in[1] = Bx[9];
   assign SB2_in[2] = Bx[16];
   assign SB2_in[3] = Bx[23];
   
   assign SK2_in[0] = Kx[2];
   assign SK2_in[1] = Kx[9];
   assign SK2_in[2] = Kx[16];
   assign SK2_in[3] = Kx[23];
   
   assign o_Bz[2] = SB2[0];
   assign o_Bz[9] = SB2[1];
   assign o_Bz[16] = SB2[2];
   assign o_Bz[23] = SB2[3];
   
   assign o_Kz[2] = SK2[0];
   assign o_Kz[9] = SK2[1];
   assign o_Kz[16] = SK2[2];
   assign o_Kz[23] = SK2[3];
   
   assign SB3_in[0] = Bx[3];
   assign SB3_in[1] = Bx[10];
   assign SB3_in[2] = Bx[17];
   assign SB3_in[3] = Bx[24];
   
   assign SK3_in[0] = Kx[3];
   assign SK3_in[1] = Kx[10];
   assign SK3_in[2] = Kx[17];
   assign SK3_in[3] = Kx[24];
   
   assign o_Bz[3] = SB3[0];
   assign o_Bz[10] = SB3[1];
   assign o_Bz[17] = SB3[2];
   assign o_Bz[24] = SB3[3];
   
   assign o_Kz[3] = SK3[0];
   assign o_Kz[10] = SK3[1];
   assign o_Kz[17] = SK3[2];
   assign o_Kz[24] = SK3[3];
   
   assign SB4_in[0] = Bx[4];
   assign SB4_in[1] = Bx[11];
   assign SB4_in[2] = Bx[18];
   assign SB4_in[3] = Bx[25];
   
   assign SK4_in[0] = Kx[4];
   assign SK4_in[1] = Kx[11];
   assign SK4_in[2] = Kx[18];
   assign SK4_in[3] = Kx[25];
   
   assign o_Bz[4] = SB4[0];
   assign o_Bz[11] = SB4[1];
   assign o_Bz[18] = SB4[2];
   assign o_Bz[25] = SB4[3];
   
   assign o_Kz[4] = SK4[0];
   assign o_Kz[11] = SK4[1];
   assign o_Kz[18] = SK4[2];
   assign o_Kz[25] = SK4[3];
   
   assign SB5_in[0] = Bx[5];
   assign SB5_in[1] = Bx[12];
   assign SB5_in[2] = Bx[19];
   assign SB5_in[3] = Bx[26];
   
   assign SK5_in[0] = Kx[5];
   assign SK5_in[1] = Kx[12];
   assign SK5_in[2] = Kx[19];
   assign SK5_in[3] = Kx[26];
   
   assign o_Bz[5] = SB5[0];
   assign o_Bz[12] = SB5[1];
   assign o_Bz[19] = SB5[2];
   assign o_Bz[26] = SB5[3];
   
   assign o_Kz[5] = SK5[0];
   assign o_Kz[12] = SK5[1];
   assign o_Kz[19] = SK5[2];
   assign o_Kz[26] = SK5[3];
   
   assign SB6_in[0] = Bx[6];
   assign SB6_in[1] = Bx[13];
   assign SB6_in[2] = Bx[20];
   assign SB6_in[3] = Bx[27];
   
   assign SK6_in[0] = Kx[6];
   assign SK6_in[1] = Kx[13];
   assign SK6_in[2] = Kx[20];
   assign SK6_in[3] = Kx[27];
   
   assign o_Bz[6] = SB6[0];
   assign o_Bz[13] = SB6[1];
   assign o_Bz[20] = SB6[2];
   assign o_Bz[27] = SB6[3];
   
   assign o_Kz[6] = SK6[0];
   assign o_Kz[13] = SK6[1];
   assign o_Kz[20] = SK6[2];
   assign o_Kz[27] = SK6[3];

   //////
   // output function
   // generated by perl script ./makeofunc.pl ofunc.txt > ostream_code.txt
   //////
assign ostream_r[0] = (Bz[17] & Kz[3]) ^ (Bz[26] & Kz[6]) ^ (Bz[22] & Kz[0]) ^ (Bz[27] & Kz[9]) ^ (Bz[21] & Kz[4]) ^ (Bz[18] & Kz[22]) ^ (Bz[2] & Kz[5]) ^ By[5] ^ Ky[10];

assign ostream_r[1] = (Bz[5] & Kz[20]) ^ (Bz[20] & Kz[18]) ^ (Bz[15] & Kz[7]) ^ (Bz[24] & Kz[23]) ^ (Bz[2] & Kz[15]) ^ (Bz[25] & Kz[5]) ^ (Bz[0] & Kz[3]) ^ By[16] ^ Ky[25];

assign ostream_r[2] = (Bz[22] & Kz[7]) ^ (Bz[5] & Kz[19]) ^ (Bz[14] & Kz[2]) ^ (Bz[16] & Kz[10]) ^ (Bz[25] & Kz[22]) ^ (Bz[17] & Kz[4]) ^ (Bz[20] & Kz[13]) ^ By[11] ^ Ky[21];

assign ostream_r[3] = (Bz[19] & Kz[6]) ^ (Bz[3] & Kz[14]) ^ (Bz[15] & Kz[9]) ^ (Bz[11] & Kz[8]) ^ (Bz[21] & Kz[17]) ^ (Bz[16] & Kz[18]) ^ (Bz[27] & Kz[12]) ^ By[1] ^ Ky[24];

assign ostream_r[4] = (Bz[19] & Kz[25]) ^ (Bz[6] & Kz[6]) ^ (Bz[17] & Kz[5]) ^ (Bz[18] & Kz[2]) ^ (Bz[22] & Kz[10]) ^ (Bz[7] & Kz[15]) ^ (Bz[9] & Kz[21]) ^ By[12] ^ Ky[8];

assign ostream_r[5] = (Bz[3] & Kz[27]) ^ (Bz[7] & Kz[14]) ^ (Bz[4] & Kz[2]) ^ (Bz[8] & Kz[4]) ^ (Bz[16] & Kz[24]) ^ (Bz[6] & Kz[19]) ^ (Bz[5] & Kz[1]) ^ By[17] ^ Ky[12];

assign ostream_r[6] = (Bz[8] & Kz[17]) ^ (Bz[21] & Kz[26]) ^ (Bz[27] & Kz[4]) ^ (Bz[2] & Kz[16]) ^ (Bz[11] & Kz[27]) ^ (Bz[24] & Kz[7]) ^ (Bz[12] & Kz[22]) ^ By[3] ^ Ky[11];

assign ostream_r[7] = (Bz[9] & Kz[9]) ^ (Bz[5] & Kz[10]) ^ (Bz[7] & Kz[19]) ^ (Bz[4] & Kz[11]) ^ (Bz[8] & Kz[7]) ^ (Bz[13] & Kz[6]) ^ (Bz[3] & Kz[8]) ^ By[15] ^ Ky[23];

assign ostream_r[8] = (Bz[26] & Kz[13]) ^ (Bz[13] & Kz[12]) ^ (Bz[23] & Kz[18]) ^ (Bz[10] & Kz[24]) ^ (Bz[11] & Kz[15]) ^ (Bz[7] & Kz[23]) ^ (Bz[15] & Kz[7]) ^ By[19] ^ Ky[16];

assign ostream_r[9] = (Bz[1] & Kz[0]) ^ (Bz[0] & Kz[5]) ^ (Bz[19] & Kz[20]) ^ (Bz[11] & Kz[25]) ^ (Bz[13] & Kz[1]) ^ (Bz[16] & Kz[24]) ^ (Bz[24] & Kz[9]) ^ By[18] ^ Ky[27];

assign ostream_r[10] = (Bz[26] & Kz[14]) ^ (Bz[13] & Kz[23]) ^ (Bz[9] & Kz[27]) ^ (Bz[14] & Kz[25]) ^ (Bz[10] & Kz[17]) ^ (Bz[4] & Kz[19]) ^ (Bz[1] & Kz[1]) ^ By[2] ^ Ky[22];

assign ostream_r[11] = (Bz[21] & Kz[6]) ^ (Bz[15] & Kz[21]) ^ (Bz[5] & Kz[17]) ^ (Bz[3] & Kz[15]) ^ (Bz[13] & Kz[26]) ^ (Bz[25] & Kz[11]) ^ (Bz[16] & Kz[16]) ^ By[27] ^ Ky[7];

assign ostream_r[12] = (Bz[20] & Kz[11]) ^ (Bz[7] & Kz[22]) ^ (Bz[18] & Kz[20]) ^ (Bz[12] & Kz[0]) ^ (Bz[17] & Kz[26]) ^ (Bz[1] & Kz[23]) ^ (Bz[16] & Kz[17]) ^ By[0] ^ Ky[2];

assign ostream_r[13] = (Bz[14] & Kz[8]) ^ (Bz[23] & Kz[4]) ^ (Bz[1] & Kz[3]) ^ (Bz[12] & Kz[14]) ^ (Bz[24] & Kz[20]) ^ (Bz[6] & Kz[26]) ^ (Bz[18] & Kz[23]) ^ By[9] ^ Ky[15];

assign ostream_r[14] = (Bz[19] & Kz[19]) ^ (Bz[6] & Kz[0]) ^ (Bz[21] & Kz[18]) ^ (Bz[25] & Kz[2]) ^ (Bz[23] & Kz[13]) ^ (Bz[1] & Kz[8]) ^ (Bz[10] & Kz[24]) ^ By[8] ^ Ky[14];

assign ostream_r[15] = (Bz[3] & Kz[16]) ^ (Bz[0] & Kz[21]) ^ (Bz[27] & Kz[24]) ^ (Bz[23] & Kz[25]) ^ (Bz[19] & Kz[12]) ^ (Bz[8] & Kz[27]) ^ (Bz[4] & Kz[15]) ^ By[7] ^ Ky[18];

assign ostream_r[16] = (Bz[6] & Kz[3]) ^ (Bz[5] & Kz[5]) ^ (Bz[14] & Kz[8]) ^ (Bz[22] & Kz[25]) ^ (Bz[24] & Kz[7]) ^ (Bz[18] & Kz[27]) ^ (Bz[2] & Kz[2]) ^ By[21] ^ Ky[26];

assign ostream_r[17] = (Bz[3] & Kz[11]) ^ (Bz[4] & Kz[14]) ^ (Bz[2] & Kz[23]) ^ (Bz[6] & Kz[17]) ^ (Bz[22] & Kz[22]) ^ (Bz[14] & Kz[13]) ^ (Bz[12] & Kz[19]) ^ By[26] ^ Ky[4];

assign ostream_r[18] = (Bz[25] & Kz[1]) ^ (Bz[21] & Kz[16]) ^ (Bz[19] & Kz[14]) ^ (Bz[9] & Kz[11]) ^ (Bz[10] & Kz[12]) ^ (Bz[15] & Kz[6]) ^ (Bz[13] & Kz[10]) ^ By[22] ^ Ky[19];

assign ostream_r[19] = (Bz[23] & Kz[21]) ^ (Bz[11] & Kz[1]) ^ (Bz[10] & Kz[10]) ^ (Bz[20] & Kz[20]) ^ (Bz[1] & Kz[18]) ^ (Bz[12] & Kz[26]) ^ (Bz[14] & Kz[9]) ^ By[4] ^ Ky[13];

assign ostream_r[20] = (Bz[11] & Kz[20]) ^ (Bz[26] & Kz[21]) ^ (Bz[20] & Kz[9]) ^ (Bz[17] & Kz[25]) ^ (Bz[8] & Kz[12]) ^ (Bz[23] & Kz[3]) ^ (Bz[0] & Kz[15]) ^ By[24] ^ Ky[0];

assign ostream_r[21] = (Bz[9] & Kz[18]) ^ (Bz[17] & Kz[12]) ^ (Bz[26] & Kz[21]) ^ (Bz[4] & Kz[27]) ^ (Bz[27] & Kz[1]) ^ (Bz[0] & Kz[16]) ^ (Bz[15] & Kz[24]) ^ By[6] ^ Ky[20];

assign ostream_r[22] = (Bz[22] & Kz[13]) ^ (Bz[12] & Kz[0]) ^ (Bz[2] & Kz[3]) ^ (Bz[10] & Kz[16]) ^ (Bz[7] & Kz[22]) ^ (Bz[20] & Kz[11]) ^ (Bz[25] & Kz[26]) ^ By[13] ^ Ky[9];

assign ostream_r[23] = (Bz[27] & Kz[2]) ^ (Bz[24] & Kz[0]) ^ (Bz[26] & Kz[13]) ^ (Bz[8] & Kz[5]) ^ (Bz[0] & Kz[4]) ^ (Bz[9] & Kz[8]) ^ (Bz[18] & Kz[10]) ^ By[23] ^ Ky[3];

endmodule // hdcp_block
