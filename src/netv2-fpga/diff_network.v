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

module diff_network (
		     input wire [6:0]   i,
		     output wire [6:0]  o,
		     input wire [6:0]   k
		     );

   assign o[0] = k[0] ^      ^ i[1] ^ i[2] ^ i[3] ^ i[4] ^ i[5] ^ i[6];
   assign o[1] = k[1] ^ i[0] ^      ^ i[2] ^ i[3] ^ i[4] ^ i[5] ^ i[6];
   assign o[2] = k[2] ^ i[0] ^ i[1] ^      ^ i[3] ^ i[4] ^ i[5] ^ i[6];
   assign o[3] = k[3] ^ i[0] ^ i[1] ^ i[2] ^      ^ i[4] ^ i[5] ^ i[6];
   assign o[4] = k[4] ^ i[0] ^ i[1] ^ i[2] ^ i[3] ^      ^ i[5] ^ i[6];
   assign o[5] = k[5] ^ i[0] ^ i[1] ^ i[2] ^ i[3] ^ i[4] ^      ^ i[6];
   assign o[6] = k[6] ^ i[0] ^ i[1] ^ i[2] ^ i[3] ^ i[4] ^ i[5] ^ i[6];
   
endmodule // diff_network
