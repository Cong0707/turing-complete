// Benchmark "rng_joint_full" written by ABC on Sun Aug 02 00:14:45 2026

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
    new_n137, new_n138, new_n139, new_n140, new_n141, new_n143, new_n144,
    new_n145, new_n146, new_n147, new_n149, new_n150, new_n151, new_n152,
    new_n153, new_n155, new_n156, new_n157, new_n158, new_n159, new_n160,
    new_n162, new_n163, new_n164, new_n165, new_n166, new_n167, new_n169,
    new_n170, new_n171, new_n172, new_n173, new_n175, new_n176, new_n177,
    new_n178, new_n179, new_n181, new_n182, new_n183, new_n184, new_n185,
    new_n187, new_n188, new_n189, new_n190, new_n191, new_n193, new_n194,
    new_n195, new_n196, new_n197, new_n198, new_n199, new_n200, new_n202,
    new_n203, new_n204, new_n205, new_n206, new_n207, new_n208, new_n209,
    new_n211, new_n212, new_n213, new_n214, new_n215, new_n216, new_n217,
    new_n218, new_n220, new_n221, new_n222, new_n224, new_n227, new_n230,
    new_n232, new_n234, new_n235, new_n237, new_n239, new_n240, new_n253,
    new_n254, new_n255, new_n256, new_n257, new_n258, new_n259, new_n260,
    new_n261, new_n262, new_n264, new_n265, new_n266, new_n267, new_n268,
    new_n269, new_n270, new_n271, new_n272, new_n273, new_n275, new_n276,
    new_n277, new_n278, new_n279, new_n280, new_n281, new_n282, new_n283,
    new_n284, new_n286, new_n287, new_n288, new_n289, new_n290, new_n291,
    new_n292, new_n293, new_n294, new_n295, new_n297, new_n298, new_n299,
    new_n300, new_n301, new_n302, new_n303, new_n304, new_n305, new_n306,
    new_n308, new_n309, new_n310, new_n311, new_n312, new_n313, new_n314,
    new_n315, new_n316, new_n317, new_n319, new_n320, new_n321, new_n322,
    new_n323, new_n324, new_n325, new_n326, new_n327, new_n328, new_n330,
    new_n331, new_n332, new_n333, new_n334, new_n335, new_n336, new_n337,
    new_n338, new_n339, new_n341, new_n342, new_n343, new_n344, new_n345,
    new_n346, new_n347, new_n348, new_n349, new_n350, new_n352, new_n353,
    new_n354, new_n355, new_n356, new_n357, new_n358, new_n359, new_n360,
    new_n361, new_n363, new_n365, new_n366, new_n367, new_n369;
  OR      g000(.A(q30), .B(s13), .Y(new_n129));
  NOR     g001(.A(q1), .B(s30), .Y(new_n130));
  XNOR    g002(.A(new_n130), .B(new_n129), .Y(new_n131));
  NOR     g003(.A(q22), .B(s0), .Y(new_n132));
  XNOR    g004(.A(new_n132), .B(new_n131), .Y(new_n133));
  NOR     g005(.A(q17), .B(s17), .Y(new_n134));
  XNOR    g006(.A(new_n134), .B(new_n133), .Y(fb0));
  NOR     g007(.A(q23), .B(s1), .Y(new_n136));
  OR      g008(.A(q2), .B(s31), .Y(new_n137));
  NOR     g009(.A(q31), .B(s14), .Y(new_n138));
  XNOR    g010(.A(new_n138), .B(new_n137), .Y(new_n139));
  XNOR    g011(.A(new_n139), .B(new_n136), .Y(new_n140));
  NOR     g012(.A(q18), .B(s18), .Y(new_n141));
  XNOR    g013(.A(new_n141), .B(new_n140), .Y(fb1));
  NOR     g014(.A(q24), .B(s2), .Y(new_n143));
  XNOR    g015(.A(new_n143), .B(q3), .Y(new_n144));
  NOR     g016(.A(q15), .B(s15), .Y(new_n145));
  XNOR    g017(.A(new_n145), .B(new_n144), .Y(new_n146));
  NOR     g018(.A(q19), .B(s19), .Y(new_n147));
  XNOR    g019(.A(new_n147), .B(new_n146), .Y(fb2));
  NOR     g020(.A(q25), .B(s3), .Y(new_n149));
  XNOR    g021(.A(new_n149), .B(q4), .Y(new_n150));
  NOR     g022(.A(q16), .B(s16), .Y(new_n151));
  XNOR    g023(.A(new_n151), .B(new_n150), .Y(new_n152));
  NOR     g024(.A(q20), .B(s20), .Y(new_n153));
  XNOR    g025(.A(new_n153), .B(new_n152), .Y(fb3));
  NOR     g026(.A(q26), .B(s4), .Y(new_n155));
  NOT     g027(.A(q5), .Y(new_n156));
  NOR     g028(.A(q0), .B(s17), .Y(new_n157));
  XNOR    g029(.A(new_n157), .B(new_n156), .Y(new_n158));
  XOR     g030(.A(new_n158), .B(new_n155), .Y(new_n159));
  NOR     g031(.A(q21), .B(s21), .Y(new_n160));
  XNOR    g032(.A(new_n160), .B(new_n159), .Y(fb4));
  NOR     g033(.A(q27), .B(s5), .Y(new_n162));
  NOT     g034(.A(q6), .Y(new_n163));
  NOR     g035(.A(q1), .B(s18), .Y(new_n164));
  XNOR    g036(.A(new_n164), .B(new_n163), .Y(new_n165));
  XOR     g037(.A(new_n165), .B(new_n162), .Y(new_n166));
  NOR     g038(.A(q22), .B(s22), .Y(new_n167));
  XNOR    g039(.A(new_n167), .B(new_n166), .Y(fb5));
  NOR     g040(.A(q28), .B(s6), .Y(new_n169));
  XNOR    g041(.A(new_n169), .B(q7), .Y(new_n170));
  NOR     g042(.A(q2), .B(s19), .Y(new_n171));
  XNOR    g043(.A(new_n171), .B(new_n170), .Y(new_n172));
  NOR     g044(.A(q23), .B(s23), .Y(new_n173));
  XNOR    g045(.A(new_n173), .B(new_n172), .Y(fb6));
  NOR     g046(.A(q29), .B(s7), .Y(new_n175));
  XNOR    g047(.A(new_n175), .B(q8), .Y(new_n176));
  NOR     g048(.A(q3), .B(s20), .Y(new_n177));
  XNOR    g049(.A(new_n177), .B(new_n176), .Y(new_n178));
  NOR     g050(.A(q24), .B(s24), .Y(new_n179));
  XNOR    g051(.A(new_n179), .B(new_n178), .Y(fb7));
  NOR     g052(.A(q30), .B(s8), .Y(new_n181));
  XNOR    g053(.A(new_n181), .B(q9), .Y(new_n182));
  NOR     g054(.A(q4), .B(s21), .Y(new_n183));
  XNOR    g055(.A(new_n183), .B(new_n182), .Y(new_n184));
  NOR     g056(.A(q25), .B(s25), .Y(new_n185));
  XNOR    g057(.A(new_n185), .B(new_n184), .Y(fb8));
  NOR     g058(.A(q31), .B(s9), .Y(new_n187));
  XNOR    g059(.A(new_n187), .B(q5), .Y(new_n188));
  NOR     g060(.A(q10), .B(s22), .Y(new_n189));
  XNOR    g061(.A(new_n189), .B(new_n188), .Y(new_n190));
  NOR     g062(.A(q26), .B(s26), .Y(new_n191));
  XNOR    g063(.A(new_n191), .B(new_n190), .Y(fb9));
  NOT     g064(.A(q11), .Y(new_n193));
  NOR     g065(.A(q27), .B(s10), .Y(new_n194));
  XNOR    g066(.A(new_n194), .B(new_n193), .Y(new_n195));
  NOR     g067(.A(q15), .B(s27), .Y(new_n196));
  NOR     g068(.A(q6), .B(s23), .Y(new_n197));
  AND     g069(.A(new_n197), .B(new_n196), .Y(new_n198));
  NOR     g070(.A(new_n197), .B(new_n196), .Y(new_n199));
  NOR     g071(.A(new_n199), .B(new_n198), .Y(new_n200));
  XNOR    g072(.A(new_n200), .B(new_n195), .Y(fb10));
  NOT     g073(.A(q7), .Y(new_n202));
  NOR     g074(.A(q28), .B(s11), .Y(new_n203));
  XNOR    g075(.A(new_n203), .B(new_n202), .Y(new_n204));
  NOR     g076(.A(q16), .B(s28), .Y(new_n205));
  NOR     g077(.A(q12), .B(s24), .Y(new_n206));
  AND     g078(.A(new_n206), .B(new_n205), .Y(new_n207));
  NOR     g079(.A(new_n206), .B(new_n205), .Y(new_n208));
  NOR     g080(.A(new_n208), .B(new_n207), .Y(new_n209));
  XNOR    g081(.A(new_n209), .B(new_n204), .Y(fb11));
  NOT     g082(.A(q8), .Y(new_n211));
  NOR     g083(.A(q29), .B(s12), .Y(new_n212));
  XNOR    g084(.A(new_n212), .B(new_n211), .Y(new_n213));
  NOR     g085(.A(q0), .B(s29), .Y(new_n214));
  NOR     g086(.A(q13), .B(s25), .Y(new_n215));
  AND     g087(.A(new_n215), .B(new_n214), .Y(new_n216));
  NOR     g088(.A(new_n215), .B(new_n214), .Y(new_n217));
  NOR     g089(.A(new_n217), .B(new_n216), .Y(new_n218));
  XNOR    g090(.A(new_n218), .B(new_n213), .Y(fb12));
  NOT     g091(.A(q9), .Y(new_n220));
  NOR     g092(.A(q14), .B(s26), .Y(new_n221));
  XNOR    g093(.A(new_n221), .B(new_n220), .Y(new_n222));
  XNOR    g094(.A(new_n222), .B(new_n131), .Y(fb13));
  NOR     g095(.A(q10), .B(s27), .Y(new_n224));
  XNOR    g096(.A(new_n224), .B(new_n139), .Y(fb14));
  XNOR    g097(.A(new_n145), .B(q3), .Y(out15));
  NOR     g098(.A(q11), .B(s28), .Y(new_n227));
  XNOR    g099(.A(new_n227), .B(out15), .Y(fb15));
  XNOR    g100(.A(new_n151), .B(q4), .Y(out16));
  NOR     g101(.A(q12), .B(s29), .Y(new_n230));
  XNOR    g102(.A(new_n230), .B(out16), .Y(fb16));
  NOR     g103(.A(q13), .B(s30), .Y(new_n232));
  NOT     g104(.A(new_n232), .Y(fb30));
  OR      g105(.A(fb30), .B(new_n158), .Y(new_n234));
  NAND    g106(.A(fb30), .B(new_n158), .Y(new_n235));
  NAND    g107(.A(new_n235), .B(new_n234), .Y(fb17));
  NOR     g108(.A(q14), .B(s31), .Y(new_n237));
  NOT     g109(.A(new_n237), .Y(fb31));
  OR      g110(.A(fb31), .B(new_n165), .Y(new_n239));
  NAND    g111(.A(fb31), .B(new_n165), .Y(new_n240));
  NAND    g112(.A(new_n240), .B(new_n239), .Y(fb18));
  XNOR    g113(.A(new_n171), .B(q7), .Y(fb19));
  XNOR    g114(.A(new_n177), .B(q8), .Y(fb20));
  XNOR    g115(.A(new_n183), .B(q9), .Y(fb21));
  XNOR    g116(.A(new_n189), .B(q5), .Y(fb22));
  XNOR    g117(.A(new_n197), .B(q11), .Y(fb23));
  XNOR    g118(.A(new_n206), .B(q7), .Y(fb24));
  XNOR    g119(.A(new_n215), .B(q8), .Y(fb25));
  NOT     g120(.A(new_n222), .Y(fb26));
  NOT     g121(.A(new_n224), .Y(fb27));
  NOT     g122(.A(new_n227), .Y(fb28));
  NOT     g123(.A(new_n230), .Y(fb29));
  XNOR    g124(.A(new_n132), .B(new_n156), .Y(new_n253));
  NAND    g125(.A(q17), .B(q0), .Y(new_n254));
  NOR     g126(.A(q17), .B(q0), .Y(new_n255));
  NOR     g127(.A(new_n255), .B(s17), .Y(new_n256));
  AND     g128(.A(new_n256), .B(new_n254), .Y(new_n257));
  OR      g129(.A(new_n257), .B(new_n253), .Y(new_n258));
  NAND    g130(.A(new_n134), .B(q0), .Y(new_n259));
  NAND    g131(.A(new_n157), .B(q17), .Y(new_n260));
  NAND    g132(.A(new_n260), .B(new_n259), .Y(new_n261));
  NAND    g133(.A(new_n261), .B(new_n253), .Y(new_n262));
  NAND    g134(.A(new_n262), .B(new_n258), .Y(out0));
  XNOR    g135(.A(new_n136), .B(new_n163), .Y(new_n264));
  NAND    g136(.A(new_n141), .B(q1), .Y(new_n265));
  NAND    g137(.A(new_n164), .B(q18), .Y(new_n266));
  NAND    g138(.A(new_n266), .B(new_n265), .Y(new_n267));
  NAND    g139(.A(new_n267), .B(new_n264), .Y(new_n268));
  OR      g140(.A(q18), .B(q1), .Y(new_n269));
  AND     g141(.A(q18), .B(q1), .Y(new_n270));
  NOR     g142(.A(new_n270), .B(s18), .Y(new_n271));
  AND     g143(.A(new_n271), .B(new_n269), .Y(new_n272));
  OR      g144(.A(new_n272), .B(new_n264), .Y(new_n273));
  NAND    g145(.A(new_n273), .B(new_n268), .Y(out1));
  XNOR    g146(.A(new_n143), .B(new_n202), .Y(new_n275));
  OR      g147(.A(q19), .B(q2), .Y(new_n276));
  AND     g148(.A(q19), .B(q2), .Y(new_n277));
  NOR     g149(.A(new_n277), .B(s19), .Y(new_n278));
  AND     g150(.A(new_n278), .B(new_n276), .Y(new_n279));
  OR      g151(.A(new_n279), .B(new_n275), .Y(new_n280));
  NAND    g152(.A(new_n147), .B(q2), .Y(new_n281));
  NAND    g153(.A(new_n171), .B(q19), .Y(new_n282));
  NAND    g154(.A(new_n282), .B(new_n281), .Y(new_n283));
  NAND    g155(.A(new_n283), .B(new_n275), .Y(new_n284));
  NAND    g156(.A(new_n284), .B(new_n280), .Y(out2));
  XNOR    g157(.A(new_n149), .B(new_n211), .Y(new_n286));
  NAND    g158(.A(q20), .B(q3), .Y(new_n287));
  NOR     g159(.A(q20), .B(q3), .Y(new_n288));
  NOR     g160(.A(new_n288), .B(s20), .Y(new_n289));
  AND     g161(.A(new_n289), .B(new_n287), .Y(new_n290));
  OR      g162(.A(new_n290), .B(new_n286), .Y(new_n291));
  NAND    g163(.A(new_n153), .B(q3), .Y(new_n292));
  NAND    g164(.A(new_n177), .B(q20), .Y(new_n293));
  NAND    g165(.A(new_n293), .B(new_n292), .Y(new_n294));
  NAND    g166(.A(new_n294), .B(new_n286), .Y(new_n295));
  NAND    g167(.A(new_n295), .B(new_n291), .Y(out3));
  XNOR    g168(.A(new_n155), .B(new_n220), .Y(new_n297));
  NAND    g169(.A(new_n160), .B(q4), .Y(new_n298));
  NAND    g170(.A(new_n183), .B(q21), .Y(new_n299));
  NAND    g171(.A(new_n299), .B(new_n298), .Y(new_n300));
  NAND    g172(.A(new_n300), .B(new_n297), .Y(new_n301));
  OR      g173(.A(q21), .B(q4), .Y(new_n302));
  AND     g174(.A(q21), .B(q4), .Y(new_n303));
  NOR     g175(.A(new_n303), .B(s21), .Y(new_n304));
  AND     g176(.A(new_n304), .B(new_n302), .Y(new_n305));
  OR      g177(.A(new_n305), .B(new_n297), .Y(new_n306));
  NAND    g178(.A(new_n306), .B(new_n301), .Y(out4));
  XNOR    g179(.A(new_n162), .B(new_n156), .Y(new_n308));
  NAND    g180(.A(new_n167), .B(q10), .Y(new_n309));
  NAND    g181(.A(new_n189), .B(q22), .Y(new_n310));
  NAND    g182(.A(new_n310), .B(new_n309), .Y(new_n311));
  NAND    g183(.A(new_n311), .B(new_n308), .Y(new_n312));
  OR      g184(.A(q22), .B(q10), .Y(new_n313));
  AND     g185(.A(q22), .B(q10), .Y(new_n314));
  NOR     g186(.A(new_n314), .B(s22), .Y(new_n315));
  AND     g187(.A(new_n315), .B(new_n313), .Y(new_n316));
  OR      g188(.A(new_n316), .B(new_n308), .Y(new_n317));
  NAND    g189(.A(new_n317), .B(new_n312), .Y(out5));
  XNOR    g190(.A(new_n169), .B(new_n193), .Y(new_n319));
  NAND    g191(.A(new_n173), .B(q6), .Y(new_n320));
  NAND    g192(.A(new_n197), .B(q23), .Y(new_n321));
  NAND    g193(.A(new_n321), .B(new_n320), .Y(new_n322));
  NAND    g194(.A(new_n322), .B(new_n319), .Y(new_n323));
  OR      g195(.A(q23), .B(q6), .Y(new_n324));
  AND     g196(.A(q23), .B(q6), .Y(new_n325));
  NOR     g197(.A(new_n325), .B(s23), .Y(new_n326));
  AND     g198(.A(new_n326), .B(new_n324), .Y(new_n327));
  OR      g199(.A(new_n327), .B(new_n319), .Y(new_n328));
  NAND    g200(.A(new_n328), .B(new_n323), .Y(out6));
  XNOR    g201(.A(new_n175), .B(new_n202), .Y(new_n330));
  NAND    g202(.A(new_n179), .B(q12), .Y(new_n331));
  NAND    g203(.A(new_n206), .B(q24), .Y(new_n332));
  NAND    g204(.A(new_n332), .B(new_n331), .Y(new_n333));
  NAND    g205(.A(new_n333), .B(new_n330), .Y(new_n334));
  OR      g206(.A(q24), .B(q12), .Y(new_n335));
  AND     g207(.A(q24), .B(q12), .Y(new_n336));
  NOR     g208(.A(new_n336), .B(s24), .Y(new_n337));
  AND     g209(.A(new_n337), .B(new_n335), .Y(new_n338));
  OR      g210(.A(new_n338), .B(new_n330), .Y(new_n339));
  NAND    g211(.A(new_n339), .B(new_n334), .Y(out7));
  XNOR    g212(.A(new_n181), .B(new_n211), .Y(new_n341));
  NAND    g213(.A(new_n185), .B(q13), .Y(new_n342));
  NAND    g214(.A(new_n215), .B(q25), .Y(new_n343));
  NAND    g215(.A(new_n343), .B(new_n342), .Y(new_n344));
  NAND    g216(.A(new_n344), .B(new_n341), .Y(new_n345));
  OR      g217(.A(q25), .B(q13), .Y(new_n346));
  AND     g218(.A(q25), .B(q13), .Y(new_n347));
  NOR     g219(.A(new_n347), .B(s25), .Y(new_n348));
  AND     g220(.A(new_n348), .B(new_n346), .Y(new_n349));
  OR      g221(.A(new_n349), .B(new_n341), .Y(new_n350));
  NAND    g222(.A(new_n350), .B(new_n345), .Y(out8));
  XNOR    g223(.A(new_n187), .B(new_n220), .Y(new_n352));
  NAND    g224(.A(new_n191), .B(q14), .Y(new_n353));
  NAND    g225(.A(new_n221), .B(q26), .Y(new_n354));
  NAND    g226(.A(new_n354), .B(new_n353), .Y(new_n355));
  NAND    g227(.A(new_n355), .B(new_n352), .Y(new_n356));
  OR      g228(.A(q26), .B(q14), .Y(new_n357));
  AND     g229(.A(q26), .B(q14), .Y(new_n358));
  NOR     g230(.A(new_n358), .B(s26), .Y(new_n359));
  AND     g231(.A(new_n359), .B(new_n357), .Y(new_n360));
  OR      g232(.A(new_n360), .B(new_n352), .Y(new_n361));
  NAND    g233(.A(new_n361), .B(new_n356), .Y(out9));
  XNOR    g234(.A(new_n196), .B(new_n194), .Y(new_n363));
  XNOR    g235(.A(new_n363), .B(q10), .Y(out10));
  AND     g236(.A(new_n205), .B(new_n203), .Y(new_n365));
  NOR     g237(.A(new_n205), .B(new_n203), .Y(new_n366));
  NOR     g238(.A(new_n366), .B(new_n365), .Y(new_n367));
  XNOR    g239(.A(new_n367), .B(new_n193), .Y(out11));
  XNOR    g240(.A(new_n214), .B(new_n212), .Y(new_n369));
  XNOR    g241(.A(new_n369), .B(q12), .Y(out12));
  XOR     g242(.A(new_n131), .B(q13), .Y(out13));
  XOR     g243(.A(new_n139), .B(q14), .Y(out14));
  NOT     g244(.A(new_n158), .Y(out17));
  NOT     g245(.A(new_n165), .Y(out18));
  BUF     g246(.A(fb19), .Y(out19));
  BUF     g247(.A(fb20), .Y(out20));
  BUF     g248(.A(fb21), .Y(out21));
  BUF     g249(.A(fb22), .Y(out22));
  BUF     g250(.A(fb23), .Y(out23));
  BUF     g251(.A(fb24), .Y(out24));
  BUF     g252(.A(fb25), .Y(out25));
  BUF     g253(.A(fb26), .Y(out26));
  BUF     g254(.A(q10), .Y(out27));
  BUF     g255(.A(q11), .Y(out28));
  BUF     g256(.A(q12), .Y(out29));
  BUF     g257(.A(q13), .Y(out30));
  BUF     g258(.A(q14), .Y(out31));
endmodule


