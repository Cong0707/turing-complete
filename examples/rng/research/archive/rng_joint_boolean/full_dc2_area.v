// Benchmark "rng_joint_full" written by ABC on Sun Aug 02 00:13:58 2026

module rng_joint_full ( 
    s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15,
    s16, s17, s18, s19, s20, s21, s22, s23, s24, s25, s26, s27, s28, s29,
    s30, s31, q0, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13,
    q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26, q27,
    q28, q29, q30, q31,
    fb0, fb1, fb2, fb3, fb4, fb5, fb6, fb7, fb8, fb9, fb10, fb11, fb12,
    fb13, fb14, fb15, fb16, fb17, fb18, fb19, fb20, fb21, fb22, fb23, fb24,
    fb25, fb26, fb27, fb28, fb29, fb30, fb31, out0, out1, out2, out3, out4,
    out5, out6, out7, out8, out9, out10, out11, out12, out13, out14, out15,
    out16, out17, out18, out19, out20, out21, out22, out23, out24, out25,
    out26, out27, out28, out29, out30, out31  );
  input  s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14,
    s15, s16, s17, s18, s19, s20, s21, s22, s23, s24, s25, s26, s27, s28,
    s29, s30, s31, q0, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12,
    q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26,
    q27, q28, q29, q30, q31;
  output fb0, fb1, fb2, fb3, fb4, fb5, fb6, fb7, fb8, fb9, fb10, fb11, fb12,
    fb13, fb14, fb15, fb16, fb17, fb18, fb19, fb20, fb21, fb22, fb23, fb24,
    fb25, fb26, fb27, fb28, fb29, fb30, fb31, out0, out1, out2, out3, out4,
    out5, out6, out7, out8, out9, out10, out11, out12, out13, out14, out15,
    out16, out17, out18, out19, out20, out21, out22, out23, out24, out25,
    out26, out27, out28, out29, out30, out31;
  wire new_n129, new_n130, new_n131, new_n132, new_n133, new_n134, new_n136,
    new_n137, new_n138, new_n139, new_n140, new_n141, new_n143, new_n145,
    new_n146, new_n147, new_n149, new_n151, new_n152, new_n153, new_n155,
    new_n156, new_n157, new_n158, new_n159, new_n160, new_n162, new_n163,
    new_n164, new_n165, new_n166, new_n167, new_n168, new_n170, new_n171,
    new_n172, new_n173, new_n174, new_n175, new_n176, new_n177, new_n179,
    new_n180, new_n181, new_n182, new_n183, new_n184, new_n185, new_n186,
    new_n188, new_n189, new_n190, new_n191, new_n192, new_n193, new_n194,
    new_n195, new_n197, new_n198, new_n199, new_n200, new_n201, new_n202,
    new_n203, new_n205, new_n206, new_n207, new_n208, new_n209, new_n210,
    new_n211, new_n212, new_n213, new_n215, new_n216, new_n217, new_n218,
    new_n219, new_n220, new_n221, new_n223, new_n224, new_n225, new_n226,
    new_n227, new_n228, new_n229, new_n231, new_n232, new_n234, new_n235,
    new_n236, new_n238, new_n240, new_n242, new_n244, new_n245, new_n247,
    new_n249, new_n250;
  NOR     g000(.A(q1), .B(s30), .Y(new_n129));
  NOR     g001(.A(q30), .B(s13), .Y(new_n130));
  XNOR    g002(.A(new_n130), .B(new_n129), .Y(new_n131));
  NOR     g003(.A(q17), .B(s17), .Y(new_n132));
  NOR     g004(.A(q22), .B(s0), .Y(new_n133));
  XNOR    g005(.A(new_n133), .B(new_n132), .Y(new_n134));
  XOR     g006(.A(new_n134), .B(new_n131), .Y(fb0));
  NOR     g007(.A(q2), .B(s31), .Y(new_n136));
  NOR     g008(.A(q31), .B(s14), .Y(new_n137));
  XNOR    g009(.A(new_n137), .B(new_n136), .Y(new_n138));
  NOR     g010(.A(q18), .B(s18), .Y(new_n139));
  NOR     g011(.A(q23), .B(s1), .Y(new_n140));
  XNOR    g012(.A(new_n140), .B(new_n139), .Y(new_n141));
  XOR     g013(.A(new_n141), .B(new_n138), .Y(fb1));
  NOR     g014(.A(q15), .B(s15), .Y(new_n143));
  XNOR    g015(.A(new_n143), .B(q3), .Y(out15));
  NOR     g016(.A(q19), .B(s19), .Y(new_n145));
  NOR     g017(.A(q24), .B(s2), .Y(new_n146));
  XNOR    g018(.A(new_n146), .B(new_n145), .Y(new_n147));
  XNOR    g019(.A(new_n147), .B(out15), .Y(fb2));
  NOR     g020(.A(q16), .B(s16), .Y(new_n149));
  XNOR    g021(.A(new_n149), .B(q4), .Y(out16));
  NOR     g022(.A(q20), .B(s20), .Y(new_n151));
  NOR     g023(.A(q25), .B(s3), .Y(new_n152));
  XNOR    g024(.A(new_n152), .B(new_n151), .Y(new_n153));
  XNOR    g025(.A(new_n153), .B(out16), .Y(fb3));
  NOT     g026(.A(q5), .Y(new_n155));
  NOR     g027(.A(q0), .B(s17), .Y(new_n156));
  XNOR    g028(.A(new_n156), .B(new_n155), .Y(new_n157));
  NOR     g029(.A(q21), .B(s21), .Y(new_n158));
  NOR     g030(.A(q26), .B(s4), .Y(new_n159));
  XNOR    g031(.A(new_n159), .B(new_n158), .Y(new_n160));
  XOR     g032(.A(new_n160), .B(new_n157), .Y(fb4));
  NOR     g033(.A(q1), .B(s18), .Y(new_n162));
  NOR     g034(.A(new_n162), .B(q6), .Y(new_n163));
  AND     g035(.A(new_n162), .B(q6), .Y(new_n164));
  NOR     g036(.A(new_n164), .B(new_n163), .Y(new_n165));
  NOR     g037(.A(q22), .B(s22), .Y(new_n166));
  NOR     g038(.A(q27), .B(s5), .Y(new_n167));
  XNOR    g039(.A(new_n167), .B(new_n166), .Y(new_n168));
  XOR     g040(.A(new_n168), .B(new_n165), .Y(fb5));
  NOT     g041(.A(q7), .Y(new_n170));
  NOR     g042(.A(q2), .B(s19), .Y(new_n171));
  XNOR    g043(.A(new_n171), .B(new_n170), .Y(new_n172));
  NOR     g044(.A(q23), .B(s23), .Y(new_n173));
  NOR     g045(.A(q28), .B(s6), .Y(new_n174));
  XNOR    g046(.A(new_n174), .B(new_n173), .Y(new_n175));
  AND     g047(.A(new_n175), .B(new_n172), .Y(new_n176));
  NOR     g048(.A(new_n175), .B(new_n172), .Y(new_n177));
  NOR     g049(.A(new_n177), .B(new_n176), .Y(fb6));
  NOT     g050(.A(q8), .Y(new_n179));
  NOR     g051(.A(q3), .B(s20), .Y(new_n180));
  XNOR    g052(.A(new_n180), .B(new_n179), .Y(new_n181));
  NOR     g053(.A(q24), .B(s24), .Y(new_n182));
  NOR     g054(.A(q29), .B(s7), .Y(new_n183));
  XNOR    g055(.A(new_n183), .B(new_n182), .Y(new_n184));
  AND     g056(.A(new_n184), .B(new_n181), .Y(new_n185));
  NOR     g057(.A(new_n184), .B(new_n181), .Y(new_n186));
  NOR     g058(.A(new_n186), .B(new_n185), .Y(fb7));
  NOT     g059(.A(q9), .Y(new_n188));
  NOR     g060(.A(q4), .B(s21), .Y(new_n189));
  XNOR    g061(.A(new_n189), .B(new_n188), .Y(new_n190));
  NOR     g062(.A(q25), .B(s25), .Y(new_n191));
  NOR     g063(.A(q30), .B(s8), .Y(new_n192));
  XNOR    g064(.A(new_n192), .B(new_n191), .Y(new_n193));
  AND     g065(.A(new_n193), .B(new_n190), .Y(new_n194));
  NOR     g066(.A(new_n193), .B(new_n190), .Y(new_n195));
  NOR     g067(.A(new_n195), .B(new_n194), .Y(fb8));
  NOR     g068(.A(q10), .B(s22), .Y(new_n197));
  XNOR    g069(.A(new_n197), .B(new_n155), .Y(new_n198));
  NOR     g070(.A(q26), .B(s26), .Y(new_n199));
  NOR     g071(.A(q31), .B(s9), .Y(new_n200));
  XNOR    g072(.A(new_n200), .B(new_n199), .Y(new_n201));
  AND     g073(.A(new_n201), .B(new_n198), .Y(new_n202));
  NOR     g074(.A(new_n201), .B(new_n198), .Y(new_n203));
  NOR     g075(.A(new_n203), .B(new_n202), .Y(fb9));
  NOR     g076(.A(q6), .B(s23), .Y(new_n205));
  NOR     g077(.A(new_n205), .B(q11), .Y(new_n206));
  AND     g078(.A(new_n205), .B(q11), .Y(new_n207));
  NOR     g079(.A(new_n207), .B(new_n206), .Y(new_n208));
  NOR     g080(.A(q15), .B(s27), .Y(new_n209));
  NOR     g081(.A(q27), .B(s10), .Y(new_n210));
  XNOR    g082(.A(new_n210), .B(new_n209), .Y(new_n211));
  AND     g083(.A(new_n211), .B(new_n208), .Y(new_n212));
  NOR     g084(.A(new_n211), .B(new_n208), .Y(new_n213));
  NOR     g085(.A(new_n213), .B(new_n212), .Y(fb10));
  NOR     g086(.A(q12), .B(s24), .Y(new_n215));
  XNOR    g087(.A(new_n215), .B(new_n170), .Y(new_n216));
  NOR     g088(.A(q16), .B(s28), .Y(new_n217));
  NOR     g089(.A(q28), .B(s11), .Y(new_n218));
  XNOR    g090(.A(new_n218), .B(new_n217), .Y(new_n219));
  AND     g091(.A(new_n219), .B(new_n216), .Y(new_n220));
  NOR     g092(.A(new_n219), .B(new_n216), .Y(new_n221));
  NOR     g093(.A(new_n221), .B(new_n220), .Y(fb11));
  NOR     g094(.A(q13), .B(s25), .Y(new_n223));
  XNOR    g095(.A(new_n223), .B(new_n179), .Y(new_n224));
  NOR     g096(.A(q0), .B(s29), .Y(new_n225));
  NOR     g097(.A(q29), .B(s12), .Y(new_n226));
  XNOR    g098(.A(new_n226), .B(new_n225), .Y(new_n227));
  AND     g099(.A(new_n227), .B(new_n224), .Y(new_n228));
  NOR     g100(.A(new_n227), .B(new_n224), .Y(new_n229));
  NOR     g101(.A(new_n229), .B(new_n228), .Y(fb12));
  NOR     g102(.A(q14), .B(s26), .Y(new_n231));
  XNOR    g103(.A(new_n231), .B(new_n188), .Y(new_n232));
  XOR     g104(.A(new_n232), .B(new_n131), .Y(fb13));
  NOR     g105(.A(q10), .B(s27), .Y(new_n234));
  AND     g106(.A(new_n234), .B(new_n138), .Y(new_n235));
  NOR     g107(.A(new_n234), .B(new_n138), .Y(new_n236));
  NOR     g108(.A(new_n236), .B(new_n235), .Y(fb14));
  NOR     g109(.A(q11), .B(s28), .Y(new_n238));
  XNOR    g110(.A(new_n238), .B(out15), .Y(fb15));
  NOR     g111(.A(q12), .B(s29), .Y(new_n240));
  XNOR    g112(.A(new_n240), .B(out16), .Y(fb16));
  NOR     g113(.A(q13), .B(s30), .Y(new_n242));
  NOT     g114(.A(new_n242), .Y(fb30));
  OR      g115(.A(fb30), .B(new_n157), .Y(new_n244));
  NAND    g116(.A(fb30), .B(new_n157), .Y(new_n245));
  NAND    g117(.A(new_n245), .B(new_n244), .Y(fb17));
  NOR     g118(.A(q14), .B(s31), .Y(new_n247));
  NOT     g119(.A(new_n247), .Y(fb31));
  OR      g120(.A(fb31), .B(new_n165), .Y(new_n249));
  NAND    g121(.A(fb31), .B(new_n165), .Y(new_n250));
  NAND    g122(.A(new_n250), .B(new_n249), .Y(fb18));
  NOT     g123(.A(new_n172), .Y(fb19));
  NOT     g124(.A(new_n181), .Y(fb20));
  NOT     g125(.A(new_n190), .Y(fb21));
  NOT     g126(.A(new_n198), .Y(fb22));
  NOT     g127(.A(new_n208), .Y(fb23));
  NOT     g128(.A(new_n216), .Y(fb24));
  NOT     g129(.A(new_n224), .Y(fb25));
  NOT     g130(.A(new_n232), .Y(fb26));
  NOT     g131(.A(new_n234), .Y(fb27));
  NOT     g132(.A(new_n238), .Y(fb28));
  NOT     g133(.A(new_n240), .Y(fb29));
  XOR     g134(.A(new_n157), .B(new_n134), .Y(out0));
  XOR     g135(.A(new_n165), .B(new_n141), .Y(out1));
  XOR     g136(.A(new_n172), .B(new_n147), .Y(out2));
  XOR     g137(.A(new_n181), .B(new_n153), .Y(out3));
  XOR     g138(.A(new_n190), .B(new_n160), .Y(out4));
  XOR     g139(.A(new_n198), .B(new_n168), .Y(out5));
  XOR     g140(.A(new_n208), .B(new_n175), .Y(out6));
  XOR     g141(.A(new_n216), .B(new_n184), .Y(out7));
  XOR     g142(.A(new_n224), .B(new_n193), .Y(out8));
  XOR     g143(.A(new_n232), .B(new_n201), .Y(out9));
  XNOR    g144(.A(new_n211), .B(q10), .Y(out10));
  XNOR    g145(.A(new_n219), .B(q11), .Y(out11));
  XNOR    g146(.A(new_n227), .B(q12), .Y(out12));
  XNOR    g147(.A(new_n131), .B(q13), .Y(out13));
  XNOR    g148(.A(new_n138), .B(q14), .Y(out14));
  NOT     g149(.A(new_n157), .Y(out17));
  NOT     g150(.A(new_n165), .Y(out18));
  BUF     g151(.A(fb19), .Y(out19));
  BUF     g152(.A(fb20), .Y(out20));
  BUF     g153(.A(fb21), .Y(out21));
  BUF     g154(.A(fb22), .Y(out22));
  BUF     g155(.A(fb23), .Y(out23));
  BUF     g156(.A(fb24), .Y(out24));
  BUF     g157(.A(fb25), .Y(out25));
  BUF     g158(.A(fb26), .Y(out26));
  BUF     g159(.A(q10), .Y(out27));
  BUF     g160(.A(q11), .Y(out28));
  BUF     g161(.A(q12), .Y(out29));
  BUF     g162(.A(q13), .Y(out30));
  BUF     g163(.A(q14), .Y(out31));
endmodule


