/*
* Copyright (C) 2020  The SymbiFlow Authors.
*
*  Use of this source code is governed by a ISC-style
*  license that can be found in the LICENSE file or at
*  https://opensource.org/licenses/ISC
*
*  SPDX-License-Identifier: ISC
*/
module rom #(
    parameter ROM_SIZE_BITS = 9  // Size in 32-bit words
) (
    // Closk & reset
    input wire CLK,
    input wire RST,

    // ROM interface
    input wire                     I_STB,
    input wire [ROM_SIZE_BITS-1:0] I_ADR,

    output wire        O_STB,
    output wire [31:0] O_DAT
);

  // ============================================================================
  localparam ROM_SIZE = (1 << ROM_SIZE_BITS);

  reg [31:0] rom     [0:ROM_SIZE-1];

  reg        rom_stb;
  reg [31:0] rom_dat;

  always @(posedge CLK) rom_dat <= rom[I_ADR];

  always @(posedge CLK or posedge RST)
    if (RST) rom_stb <= 1'd0;
    else rom_stb <= I_STB;

  assign O_STB = rom_stb;
  assign O_DAT = rom_dat;

  // ============================================================================

  initial begin
    rom['h0000] <= 32'hCE3DCB47;
    rom['h0001] <= 32'h07882CB6;
    rom['h0002] <= 32'h0092A9F4;
    rom['h0003] <= 32'h13B944BD;
    rom['h0004] <= 32'h1DCC3AA1;
    rom['h0005] <= 32'h7CC72FA4;
    rom['h0006] <= 32'h0636E9DF;
    rom['h0007] <= 32'h6099A592;
    rom['h0008] <= 32'h5EB5DA9F;
    rom['h0009] <= 32'hC44C70B0;
    rom['h000A] <= 32'h71FFD8D1;
    rom['h000B] <= 32'h810086EB;
    rom['h000C] <= 32'hCD0C0B22;
    rom['h000D] <= 32'hC94E18C2;
    rom['h000E] <= 32'h80D116A5;
    rom['h000F] <= 32'hD2C5CBAD;
    rom['h0010] <= 32'h93E5714E;
    rom['h0011] <= 32'hC52553A6;
    rom['h0012] <= 32'h5E8B3EE2;
    rom['h0013] <= 32'h1C3ADDB1;
    rom['h0014] <= 32'h45DC4439;
    rom['h0015] <= 32'h1CD7F52E;
    rom['h0016] <= 32'h7133663C;
    rom['h0017] <= 32'hE9EA04E8;
    rom['h0018] <= 32'h7B8F1A56;
    rom['h0019] <= 32'h6C132A71;
    rom['h001A] <= 32'h3F49CC79;
    rom['h001B] <= 32'hF9F38271;
    rom['h001C] <= 32'h1E76856B;
    rom['h001D] <= 32'h3FC69E73;
    rom['h001E] <= 32'h824FE66C;
    rom['h001F] <= 32'h1D30645C;
    rom['h0020] <= 32'hC6040B31;
    rom['h0021] <= 32'h5A7C18BB;
    rom['h0022] <= 32'hBA50B07C;
    rom['h0023] <= 32'hE446BEB1;
    rom['h0024] <= 32'hBAB009EF;
    rom['h0025] <= 32'h2F343A25;
    rom['h0026] <= 32'hB2D25DC9;
    rom['h0027] <= 32'h128D80B8;
    rom['h0028] <= 32'h56AAAFC5;
    rom['h0029] <= 32'h4088AFD4;
    rom['h002A] <= 32'hA2C59FC0;
    rom['h002B] <= 32'h605210E2;
    rom['h002C] <= 32'hBA37B776;
    rom['h002D] <= 32'hF2EE8426;
    rom['h002E] <= 32'hA0C26CBD;
    rom['h002F] <= 32'hEB736308;
    rom['h0030] <= 32'h22A96994;
    rom['h0031] <= 32'hD77C1E20;
    rom['h0032] <= 32'h45D63F30;
    rom['h0033] <= 32'h52B894B2;
    rom['h0034] <= 32'h727120E4;
    rom['h0035] <= 32'h6FF3CC13;
    rom['h0036] <= 32'hDD7ABC25;
    rom['h0037] <= 32'hDC9FEEB2;
    rom['h0038] <= 32'hCE498077;
    rom['h0039] <= 32'h0DD145F9;
    rom['h003A] <= 32'hD7CED8C3;
    rom['h003B] <= 32'hB9E011E4;
    rom['h003C] <= 32'h0C5B69E7;
    rom['h003D] <= 32'h21E6D6A2;
    rom['h003E] <= 32'hFFF0A99B;
    rom['h003F] <= 32'h14069D90;
    rom['h0040] <= 32'h856492B9;
    rom['h0041] <= 32'hC74D2B1E;
    rom['h0042] <= 32'h6CB09264;
    rom['h0043] <= 32'hD7BA7E46;
    rom['h0044] <= 32'h29B2B97F;
    rom['h0045] <= 32'hE311BDA9;
    rom['h0046] <= 32'h134C3C9A;
    rom['h0047] <= 32'hB344D4CC;
    rom['h0048] <= 32'h5E8BF53F;
    rom['h0049] <= 32'hD825CF79;
    rom['h004A] <= 32'h6EAE8AFE;
    rom['h004B] <= 32'hA4ADA03F;
    rom['h004C] <= 32'hB0197C99;
    rom['h004D] <= 32'hC8D5C86E;
    rom['h004E] <= 32'hEF713B63;
    rom['h004F] <= 32'h58BD4976;
    rom['h0050] <= 32'h58E4E2FA;
    rom['h0051] <= 32'hEF87CDA1;
    rom['h0052] <= 32'hC031E109;
    rom['h0053] <= 32'hDF3D9DEB;
    rom['h0054] <= 32'hB6BD710B;
    rom['h0055] <= 32'h08FDC499;
    rom['h0056] <= 32'hC190802C;
    rom['h0057] <= 32'h93013AA8;
    rom['h0058] <= 32'h2387EF90;
    rom['h0059] <= 32'h79E85EED;
    rom['h005A] <= 32'h2DCD394F;
    rom['h005B] <= 32'h38EBC05B;
    rom['h005C] <= 32'h22405C89;
    rom['h005D] <= 32'h71C52D02;
    rom['h005E] <= 32'h7AAAD284;
    rom['h005F] <= 32'h2E94F394;
    rom['h0060] <= 32'h2177192B;
    rom['h0061] <= 32'h5ABF33EE;
    rom['h0062] <= 32'h040596E0;
    rom['h0063] <= 32'h3F3EB2DD;
    rom['h0064] <= 32'hD9E53448;
    rom['h0065] <= 32'h5A4F17D4;
    rom['h0066] <= 32'h99E080EE;
    rom['h0067] <= 32'h03383C42;
    rom['h0068] <= 32'hCAA8C8C2;
    rom['h0069] <= 32'hCA5F7011;
    rom['h006A] <= 32'hA4FBB5AD;
    rom['h006B] <= 32'h50CF592D;
    rom['h006C] <= 32'h551EAEFF;
    rom['h006D] <= 32'h253D6252;
    rom['h006E] <= 32'hEEE469AB;
    rom['h006F] <= 32'h97302B2D;
    rom['h0070] <= 32'h206D4366;
    rom['h0071] <= 32'h4EC577D0;
    rom['h0072] <= 32'h07543E1E;
    rom['h0073] <= 32'h5AE150D1;
    rom['h0074] <= 32'h7573920C;
    rom['h0075] <= 32'h5B0A024A;
    rom['h0076] <= 32'h4AAF463F;
    rom['h0077] <= 32'hEBE34613;
    rom['h0078] <= 32'h62F4366D;
    rom['h0079] <= 32'h4FDC1063;
    rom['h007A] <= 32'hEA997324;
    rom['h007B] <= 32'h2F1EAE8A;
    rom['h007C] <= 32'hEC9BA9DE;
    rom['h007D] <= 32'h23591D5D;
    rom['h007E] <= 32'hD03B2C9B;
    rom['h007F] <= 32'h45C58E1C;
    rom['h0080] <= 32'hC7BE6DC3;
    rom['h0081] <= 32'h95E40CE3;
    rom['h0082] <= 32'hC5D5DB86;
    rom['h0083] <= 32'hA0CEB58D;
    rom['h0084] <= 32'h9E4AFBD1;
    rom['h0085] <= 32'hCFF63CF3;
    rom['h0086] <= 32'hF7A864C0;
    rom['h0087] <= 32'h4A9AE1E3;
    rom['h0088] <= 32'h182A6B1C;
    rom['h0089] <= 32'h4E9CE824;
    rom['h008A] <= 32'hEE86BF61;
    rom['h008B] <= 32'h0B37373A;
    rom['h008C] <= 32'h6418596B;
    rom['h008D] <= 32'hE29A44DA;
    rom['h008E] <= 32'hF6B42967;
    rom['h008F] <= 32'hB9D9C0AD;
    rom['h0090] <= 32'h6B5CE3A8;
    rom['h0091] <= 32'h6CBCB764;
    rom['h0092] <= 32'hA57EB261;
    rom['h0093] <= 32'h5470230A;
    rom['h0094] <= 32'hF8216CE6;
    rom['h0095] <= 32'hA150950D;
    rom['h0096] <= 32'h6FC5CA08;
    rom['h0097] <= 32'h26193C52;
    rom['h0098] <= 32'h84E1D60D;
    rom['h0099] <= 32'hF33E868D;
    rom['h009A] <= 32'h44E668DD;
    rom['h009B] <= 32'h8430441F;
    rom['h009C] <= 32'hC221DEE0;
    rom['h009D] <= 32'h4552E4B6;
    rom['h009E] <= 32'hBE9A17FE;
    rom['h009F] <= 32'hCE04CB35;
    rom['h00A0] <= 32'h873B9726;
    rom['h00A1] <= 32'hCBD67AF7;
    rom['h00A2] <= 32'hD2A10712;
    rom['h00A3] <= 32'hA2F35436;
    rom['h00A4] <= 32'h08D9BC9D;
    rom['h00A5] <= 32'hBBC3558E;
    rom['h00A6] <= 32'h1CE34C1B;
    rom['h00A7] <= 32'h29D81B92;
    rom['h00A8] <= 32'h59D1F498;
    rom['h00A9] <= 32'hCEC87CD3;
    rom['h00AA] <= 32'hA278DE7F;
    rom['h00AB] <= 32'hC2DA00E3;
    rom['h00AC] <= 32'hF8D4809B;
    rom['h00AD] <= 32'h2586F469;
    rom['h00AE] <= 32'hE5D9A78F;
    rom['h00AF] <= 32'h96818BC3;
    rom['h00B0] <= 32'hD3B98A4D;
    rom['h00B1] <= 32'h1F5D6347;
    rom['h00B2] <= 32'h1D041420;
    rom['h00B3] <= 32'hD7FE7946;
    rom['h00B4] <= 32'hD8723B6D;
    rom['h00B5] <= 32'h70E870EB;
    rom['h00B6] <= 32'h6E49EBBF;
    rom['h00B7] <= 32'hD98EB8A3;
    rom['h00B8] <= 32'h5D52BF45;
    rom['h00B9] <= 32'h386C9C06;
    rom['h00BA] <= 32'hA85CCB3C;
    rom['h00BB] <= 32'hF6369A32;
    rom['h00BC] <= 32'h7F51C734;
    rom['h00BD] <= 32'h5B309426;
    rom['h00BE] <= 32'hD43F05CA;
    rom['h00BF] <= 32'h04CF148C;
    rom['h00C0] <= 32'h07770DC4;
    rom['h00C1] <= 32'h6487AC39;
    rom['h00C2] <= 32'h4AEE4BF9;
    rom['h00C3] <= 32'h672580D4;
    rom['h00C4] <= 32'hF360804B;
    rom['h00C5] <= 32'hC5C7915B;
    rom['h00C6] <= 32'h45925C06;
    rom['h00C7] <= 32'h1D52F1F4;
    rom['h00C8] <= 32'h3AA9B53A;
    rom['h00C9] <= 32'hBC478FD6;
    rom['h00CA] <= 32'hA294E876;
    rom['h00CB] <= 32'h8A878DA7;
    rom['h00CC] <= 32'hC28EB186;
    rom['h00CD] <= 32'h19A88DA1;
    rom['h00CE] <= 32'h61C5122A;
    rom['h00CF] <= 32'h74E48D70;
    rom['h00D0] <= 32'hA7057D26;
    rom['h00D1] <= 32'hBA1A9FB7;
    rom['h00D2] <= 32'h661571B0;
    rom['h00D3] <= 32'hE92234B4;
    rom['h00D4] <= 32'h71FDF1D6;
    rom['h00D5] <= 32'hFDCE1E6F;
    rom['h00D6] <= 32'h63D340B2;
    rom['h00D7] <= 32'h6C2C52DC;
    rom['h00D8] <= 32'hFEE754A9;
    rom['h00D9] <= 32'h363229E4;
    rom['h00DA] <= 32'h37A7DF2B;
    rom['h00DB] <= 32'h9E54829D;
    rom['h00DC] <= 32'h8CED1324;
    rom['h00DD] <= 32'h845FEC8D;
    rom['h00DE] <= 32'hD1A8EDBF;
    rom['h00DF] <= 32'hDBF3CCB3;
    rom['h00E0] <= 32'hB387ACD2;
    rom['h00E1] <= 32'h4329D4C6;
    rom['h00E2] <= 32'h56CFB38A;
    rom['h00E3] <= 32'hBEEE4323;
    rom['h00E4] <= 32'hC6BF02FD;
    rom['h00E5] <= 32'hFB518C7F;
    rom['h00E6] <= 32'hE8D4CA92;
    rom['h00E7] <= 32'h4FA664CA;
    rom['h00E8] <= 32'h8617993C;
    rom['h00E9] <= 32'hBE35A2BD;
    rom['h00EA] <= 32'hBAF88C40;
    rom['h00EB] <= 32'h97281344;
    rom['h00EC] <= 32'hF4FC0857;
    rom['h00ED] <= 32'h18502BB5;
    rom['h00EE] <= 32'h802CF03E;
    rom['h00EF] <= 32'hCE0F60C7;
    rom['h00F0] <= 32'h23075872;
    rom['h00F1] <= 32'hFBD5EC33;
    rom['h00F2] <= 32'hC8642089;
    rom['h00F3] <= 32'hD6E69334;
    rom['h00F4] <= 32'h3089A6D1;
    rom['h00F5] <= 32'h743B3678;
    rom['h00F6] <= 32'h58DF6E7D;
    rom['h00F7] <= 32'h67932CEC;
    rom['h00F8] <= 32'h39D6A5E7;
    rom['h00F9] <= 32'h68BCC94C;
    rom['h00FA] <= 32'h6CE374CF;
    rom['h00FB] <= 32'h9E4C3229;
    rom['h00FC] <= 32'h8DF4F042;
    rom['h00FD] <= 32'h2AD69C1D;
    rom['h00FE] <= 32'h8E060C4D;
    rom['h00FF] <= 32'h531BA19B;
    rom['h0100] <= 32'h2C232DA6;
    rom['h0101] <= 32'hFD393EF6;
    rom['h0102] <= 32'h5A593FA8;
    rom['h0103] <= 32'hE4F7F59F;
    rom['h0104] <= 32'hC1FDD9D2;
    rom['h0105] <= 32'h854AB286;
    rom['h0106] <= 32'hA6C6D37F;
    rom['h0107] <= 32'h2B681256;
    rom['h0108] <= 32'h1AC19A1B;
    rom['h0109] <= 32'h2090DCB3;
    rom['h010A] <= 32'hF8D91B09;
    rom['h010B] <= 32'hD880646F;
    rom['h010C] <= 32'hFA0E8F96;
    rom['h010D] <= 32'h887BC762;
    rom['h010E] <= 32'hBA3E8829;
    rom['h010F] <= 32'h80E2E59F;
    rom['h0110] <= 32'h6479E7E1;
    rom['h0111] <= 32'hD378D2CC;
    rom['h0112] <= 32'h41EDCA0F;
    rom['h0113] <= 32'hE0EF7454;
    rom['h0114] <= 32'h46EF2A92;
    rom['h0115] <= 32'h2967F591;
    rom['h0116] <= 32'hAB7CC627;
    rom['h0117] <= 32'h44C393EE;
    rom['h0118] <= 32'h6BC3962B;
    rom['h0119] <= 32'h24D6979D;
    rom['h011A] <= 32'h1E5573D7;
    rom['h011B] <= 32'h58B432FB;
    rom['h011C] <= 32'hFFCA748C;
    rom['h011D] <= 32'h3E54DAE1;
    rom['h011E] <= 32'h59F26B16;
    rom['h011F] <= 32'h9D322226;
    rom['h0120] <= 32'h5A8A1580;
    rom['h0121] <= 32'h493E4392;
    rom['h0122] <= 32'h3E8C743C;
    rom['h0123] <= 32'hFF90AFBD;
    rom['h0124] <= 32'h02FA0B20;
    rom['h0125] <= 32'h2F704D81;
    rom['h0126] <= 32'h05345A6E;
    rom['h0127] <= 32'hC004DAAC;
    rom['h0128] <= 32'h6F616D41;
    rom['h0129] <= 32'h6A6AE1DE;
    rom['h012A] <= 32'h21D4D696;
    rom['h012B] <= 32'h335B758D;
    rom['h012C] <= 32'h6C403126;
    rom['h012D] <= 32'hD76C936A;
    rom['h012E] <= 32'hEC23F0AD;
    rom['h012F] <= 32'h4DEFAFE1;
    rom['h0130] <= 32'h12021810;
    rom['h0131] <= 32'h9783D7A1;
    rom['h0132] <= 32'h1C9DE2F3;
    rom['h0133] <= 32'h5163CE8F;
    rom['h0134] <= 32'h3EDCF679;
    rom['h0135] <= 32'hBA61AA67;
    rom['h0136] <= 32'hE0E56699;
    rom['h0137] <= 32'h32CA0251;
    rom['h0138] <= 32'hE885EE13;
    rom['h0139] <= 32'hA02B7920;
    rom['h013A] <= 32'h5D171E66;
    rom['h013B] <= 32'h62249DE5;
    rom['h013C] <= 32'h10B37D3E;
    rom['h013D] <= 32'hC16F999D;
    rom['h013E] <= 32'h5DCE4224;
    rom['h013F] <= 32'h116E50EE;
    rom['h0140] <= 32'h750E1469;
    rom['h0141] <= 32'h841D7210;
    rom['h0142] <= 32'h69E94EF6;
    rom['h0143] <= 32'h430097F3;
    rom['h0144] <= 32'h0C251ECB;
    rom['h0145] <= 32'h54FA0AAB;
    rom['h0146] <= 32'hAF6A4A2B;
    rom['h0147] <= 32'h4732EE08;
    rom['h0148] <= 32'hDFB70C84;
    rom['h0149] <= 32'hF678B7F4;
    rom['h014A] <= 32'h22398E8B;
    rom['h014B] <= 32'h8293F3AC;
    rom['h014C] <= 32'hE5126CF0;
    rom['h014D] <= 32'h5461908A;
    rom['h014E] <= 32'hE8CE9A5B;
    rom['h014F] <= 32'h3AA4A61C;
    rom['h0150] <= 32'h8569FAC1;
    rom['h0151] <= 32'h805EC1DD;
    rom['h0152] <= 32'hC0296B45;
    rom['h0153] <= 32'hD5C0118F;
    rom['h0154] <= 32'h2E9A01C2;
    rom['h0155] <= 32'h28BBDB89;
    rom['h0156] <= 32'h5F106BB8;
    rom['h0157] <= 32'hA9AE4FB3;
    rom['h0158] <= 32'h524DA1BB;
    rom['h0159] <= 32'hC85290E5;
    rom['h015A] <= 32'h54DFEB8A;
    rom['h015B] <= 32'hE28A9534;
    rom['h015C] <= 32'hB0939277;
    rom['h015D] <= 32'h7CAC0A9D;
    rom['h015E] <= 32'h5917EF1A;
    rom['h015F] <= 32'h7CB7AF1A;
    rom['h0160] <= 32'hB309B216;
    rom['h0161] <= 32'h21F5E298;
    rom['h0162] <= 32'h20813D01;
    rom['h0163] <= 32'h0BD6DC34;
    rom['h0164] <= 32'h99240415;
    rom['h0165] <= 32'h25DDD774;
    rom['h0166] <= 32'h46E1ACFC;
    rom['h0167] <= 32'h8FBCA374;
    rom['h0168] <= 32'h696A3614;
    rom['h0169] <= 32'h04369408;
    rom['h016A] <= 32'hD590938A;
    rom['h016B] <= 32'hE8870309;
    rom['h016C] <= 32'h56FE3302;
    rom['h016D] <= 32'h7447D185;
    rom['h016E] <= 32'h4A4A8D14;
    rom['h016F] <= 32'h9B2B9E0A;
    rom['h0170] <= 32'h319043B1;
    rom['h0171] <= 32'h1FE49809;
    rom['h0172] <= 32'hB0986251;
    rom['h0173] <= 32'h614295A4;
    rom['h0174] <= 32'hFEF4E58E;
    rom['h0175] <= 32'h7A652AB4;
    rom['h0176] <= 32'h16B4146D;
    rom['h0177] <= 32'hBBD18584;
    rom['h0178] <= 32'h198110DE;
    rom['h0179] <= 32'hC1205688;
    rom['h017A] <= 32'h9C754251;
    rom['h017B] <= 32'hC0BCD250;
    rom['h017C] <= 32'h1B539EFE;
    rom['h017D] <= 32'hA1308AC1;
    rom['h017E] <= 32'hB7B34739;
    rom['h017F] <= 32'h5B57B460;
    rom['h0180] <= 32'h138C5660;
    rom['h0181] <= 32'h8EE1AEB5;
    rom['h0182] <= 32'h1729F2E3;
    rom['h0183] <= 32'h498A2CA5;
    rom['h0184] <= 32'h6B52F2E6;
    rom['h0185] <= 32'h89EA9495;
    rom['h0186] <= 32'hD11F5317;
    rom['h0187] <= 32'hD5939D1A;
    rom['h0188] <= 32'h29498922;
    rom['h0189] <= 32'h191292DD;
    rom['h018A] <= 32'h5B88F597;
    rom['h018B] <= 32'hF9A021F8;
    rom['h018C] <= 32'h512F04EB;
    rom['h018D] <= 32'h46DD4314;
    rom['h018E] <= 32'h6DB4C1EB;
    rom['h018F] <= 32'hDCDE0A69;
    rom['h0190] <= 32'h8A869518;
    rom['h0191] <= 32'hA5C17D5C;
    rom['h0192] <= 32'hF8E1D019;
    rom['h0193] <= 32'h7AAA674A;
    rom['h0194] <= 32'h001EC536;
    rom['h0195] <= 32'hD25BD990;
    rom['h0196] <= 32'h253A5C41;
    rom['h0197] <= 32'h1605B875;
    rom['h0198] <= 32'h71DFE26B;
    rom['h0199] <= 32'h53623575;
    rom['h019A] <= 32'h16FCA7AD;
    rom['h019B] <= 32'h21205616;
    rom['h019C] <= 32'hD74A549F;
    rom['h019D] <= 32'hFCF6B455;
    rom['h019E] <= 32'h783707C9;
    rom['h019F] <= 32'h0DEAD982;
    rom['h01A0] <= 32'h33225255;
    rom['h01A1] <= 32'hA20730D0;
    rom['h01A2] <= 32'h9A2F8C56;
    rom['h01A3] <= 32'h8FF84A51;
    rom['h01A4] <= 32'hE5280633;
    rom['h01A5] <= 32'h5D3E6639;
    rom['h01A6] <= 32'hE266415B;
    rom['h01A7] <= 32'h150AD73C;
    rom['h01A8] <= 32'hADE62A56;
    rom['h01A9] <= 32'hDEFC1F4A;
    rom['h01AA] <= 32'hB435C4A5;
    rom['h01AB] <= 32'hE940284E;
    rom['h01AC] <= 32'h81FAB8B7;
    rom['h01AD] <= 32'hD61DBFAA;
    rom['h01AE] <= 32'h83C6D67F;
    rom['h01AF] <= 32'h0A1D9F5A;
    rom['h01B0] <= 32'h041A166B;
    rom['h01B1] <= 32'hFB91F7B6;
    rom['h01B2] <= 32'h9F2A2582;
    rom['h01B3] <= 32'h08526B70;
    rom['h01B4] <= 32'hD1D2688F;
    rom['h01B5] <= 32'h08AEFBA2;
    rom['h01B6] <= 32'hC5E85B03;
    rom['h01B7] <= 32'hB031A4B6;
    rom['h01B8] <= 32'h7FB82350;
    rom['h01B9] <= 32'h098A0389;
    rom['h01BA] <= 32'hFE83316D;
    rom['h01BB] <= 32'hBB599E02;
    rom['h01BC] <= 32'hC60EC016;
    rom['h01BD] <= 32'h3BAE5990;
    rom['h01BE] <= 32'h6F27D89B;
    rom['h01BF] <= 32'h40177883;
    rom['h01C0] <= 32'hDB20243C;
    rom['h01C1] <= 32'hDFDD35D3;
    rom['h01C2] <= 32'h7A7D5C29;
    rom['h01C3] <= 32'h387A982E;
    rom['h01C4] <= 32'h5CE1CEC0;
    rom['h01C5] <= 32'h1CFB05B0;
    rom['h01C6] <= 32'h24B17A27;
    rom['h01C7] <= 32'hE25F60FB;
    rom['h01C8] <= 32'hFBC45447;
    rom['h01C9] <= 32'hBEE39FEA;
    rom['h01CA] <= 32'h43E8E52A;
    rom['h01CB] <= 32'h11DBA99D;
    rom['h01CC] <= 32'h8060557D;
    rom['h01CD] <= 32'hC55BFCF1;
    rom['h01CE] <= 32'h67F5E020;
    rom['h01CF] <= 32'hF6151B9F;
    rom['h01D0] <= 32'h46431432;
    rom['h01D1] <= 32'h9FB9250B;
    rom['h01D2] <= 32'h37EFFC6D;
    rom['h01D3] <= 32'h50D50D53;
    rom['h01D4] <= 32'h5AA2EFDB;
    rom['h01D5] <= 32'hA8C7D02C;
    rom['h01D6] <= 32'h4BE4A212;
    rom['h01D7] <= 32'h61148629;
    rom['h01D8] <= 32'hDA924F9F;
    rom['h01D9] <= 32'h1FFD9B2C;
    rom['h01DA] <= 32'h67BCCE90;
    rom['h01DB] <= 32'h3AFE1FC8;
    rom['h01DC] <= 32'h880240A5;
    rom['h01DD] <= 32'hF526105C;
    rom['h01DE] <= 32'hD814F010;
    rom['h01DF] <= 32'h7029F6D7;
    rom['h01E0] <= 32'h3E876907;
    rom['h01E1] <= 32'h90EE5C39;
    rom['h01E2] <= 32'hA471D493;
    rom['h01E3] <= 32'h59AA5D96;
    rom['h01E4] <= 32'hE4730A4C;
    rom['h01E5] <= 32'h8F4C1ECC;
    rom['h01E6] <= 32'hCBC1F037;
    rom['h01E7] <= 32'h4C31F794;
    rom['h01E8] <= 32'h4006C022;
    rom['h01E9] <= 32'hCB8FACC8;
    rom['h01EA] <= 32'h5F2DDF5C;
    rom['h01EB] <= 32'h2B01C202;
    rom['h01EC] <= 32'h5FB7F7AC;
    rom['h01ED] <= 32'h5AB08D0A;
    rom['h01EE] <= 32'hEDA78EE3;
    rom['h01EF] <= 32'hFF16F393;
    rom['h01F0] <= 32'h3E93657C;
    rom['h01F1] <= 32'hE91F147D;
    rom['h01F2] <= 32'h4FF16B58;
    rom['h01F3] <= 32'h9B3ABDA8;
    rom['h01F4] <= 32'h8ED4333C;
    rom['h01F5] <= 32'h003D520D;
    rom['h01F6] <= 32'h362B91D8;
    rom['h01F7] <= 32'h6658FB47;
    rom['h01F8] <= 32'h0D494FD5;
    rom['h01F9] <= 32'hDFEB255F;
    rom['h01FA] <= 32'hD43B4DC0;
    rom['h01FB] <= 32'hF7DF64EA;
    rom['h01FC] <= 32'h6D6E427B;
    rom['h01FD] <= 32'h05DFDE94;
    rom['h01FE] <= 32'h940BE15C;
    rom['h01FF] <= 32'h5A98F7F1;

  end

  // ============================================================================

endmodule
