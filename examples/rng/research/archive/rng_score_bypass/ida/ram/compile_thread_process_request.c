__int64 __fastcall process_request__modelZsimulationZcompile95thread_u141(__int64 *a1)
{
  __int64 v1; // rax
  char v2; // dl
  bool v3; // of
  __int64 v4; // rax
  __int64 v5; // rax
  char v6; // dl
  __int64 v7; // rax
  _QWORD *v8; // rax
  _QWORD *v9; // rdx
  __int64 v10; // rbx
  __int64 v11; // rbx
  __int64 v12; // rbx
  __int64 v13; // rdx
  __int64 v14; // rdx
  _QWORD *v15; // rdx
  __int64 v16; // rdx
  __int64 v17; // rdx
  __int64 v18; // rdx
  __int64 v19; // rdx
  __int64 v20; // rdx
  __int64 v21; // rdx
  __int64 v22; // rdx
  __int64 v23; // rdx
  __int64 v25; // [rsp+50h] [rbp-30h] BYREF
  __int64 v26; // [rsp+58h] [rbp-28h]
  __int64 v27; // [rsp+60h] [rbp-20h]
  __int64 v28; // [rsp+70h] [rbp-10h] BYREF
  __int64 v29; // [rsp+78h] [rbp-8h]
  __int64 v30; // [rsp+80h] [rbp+0h] BYREF
  __int64 v31; // [rsp+88h] [rbp+8h]
  _QWORD *v32; // [rsp+90h] [rbp+10h] BYREF
  __int64 v33; // [rsp+98h] [rbp+18h]
  _QWORD *v34; // [rsp+A0h] [rbp+20h] BYREF
  __int64 v35; // [rsp+A8h] [rbp+28h]
  _QWORD *v36; // [rsp+B0h] [rbp+30h] BYREF
  _QWORD *v37; // [rsp+B8h] [rbp+38h]
  _QWORD *v38; // [rsp+C0h] [rbp+40h] BYREF
  __int64 v39; // [rsp+C8h] [rbp+48h]
  _QWORD *v40; // [rsp+D0h] [rbp+50h]
  _QWORD *v41; // [rsp+D8h] [rbp+58h]
  _QWORD *v42; // [rsp+E0h] [rbp+60h]
  __int64 v43; // [rsp+E8h] [rbp+68h]
  _QWORD *v44; // [rsp+170h] [rbp+F0h] BYREF
  _QWORD *v45; // [rsp+178h] [rbp+F8h]
  __int64 v46; // [rsp+180h] [rbp+100h]
  __int64 v47; // [rsp+188h] [rbp+108h] BYREF
  __int64 v48; // [rsp+190h] [rbp+110h]
  __int64 v49; // [rsp+198h] [rbp+118h]
  __int64 v50; // [rsp+1A0h] [rbp+120h]
  __int64 v51; // [rsp+1A8h] [rbp+128h]
  __int64 v52; // [rsp+1B0h] [rbp+130h]
  __int64 v53; // [rsp+1B8h] [rbp+138h]
  __int64 v54; // [rsp+1C0h] [rbp+140h]
  __int64 v55; // [rsp+1C8h] [rbp+148h]
  __int64 v56; // [rsp+1D0h] [rbp+150h]
  __int64 v57; // [rsp+1D8h] [rbp+158h]
  __int64 v58; // [rsp+1E0h] [rbp+160h]
  __int64 v59; // [rsp+1E8h] [rbp+168h]
  _QWORD *v60; // [rsp+1F0h] [rbp+170h] BYREF
  _QWORD *v61; // [rsp+1F8h] [rbp+178h]
  __int64 v62[8]; // [rsp+200h] [rbp+180h] BYREF
  _QWORD *v63; // [rsp+240h] [rbp+1C0h] BYREF
  __int64 v64; // [rsp+248h] [rbp+1C8h]
  __int64 v65; // [rsp+250h] [rbp+1D0h]
  __int64 v66; // [rsp+258h] [rbp+1D8h]
  __int64 v67; // [rsp+260h] [rbp+1E0h]
  __int64 v68; // [rsp+268h] [rbp+1E8h]
  __int64 v69; // [rsp+270h] [rbp+1F0h]
  __int64 v70; // [rsp+278h] [rbp+1F8h]
  __int64 v71; // [rsp+280h] [rbp+200h]
  __int64 v72; // [rsp+288h] [rbp+208h]
  __int64 v73; // [rsp+290h] [rbp+210h]
  __int64 v74; // [rsp+298h] [rbp+218h]
  __int64 v75; // [rsp+2A0h] [rbp+220h]
  __int64 v76; // [rsp+2A8h] [rbp+228h]
  __int64 v77; // [rsp+2B0h] [rbp+230h]
  __int64 v78; // [rsp+2B8h] [rbp+238h]
  _QWORD *v79; // [rsp+2C0h] [rbp+240h]
  __int64 v80; // [rsp+2C8h] [rbp+248h]
  __int64 v81; // [rsp+2D0h] [rbp+250h]
  __int64 v82; // [rsp+2D8h] [rbp+258h]
  __int64 v83; // [rsp+2E0h] [rbp+260h]
  __int64 v84; // [rsp+2E8h] [rbp+268h]
  __int64 v85; // [rsp+2F0h] [rbp+270h]
  __int64 v86; // [rsp+2F8h] [rbp+278h]
  __int64 v87; // [rsp+300h] [rbp+280h]
  __int64 v88; // [rsp+308h] [rbp+288h]
  _QWORD *v89; // [rsp+310h] [rbp+290h]
  _QWORD *v90; // [rsp+318h] [rbp+298h]
  __int64 v91; // [rsp+320h] [rbp+2A0h]
  __int64 v92[90]; // [rsp+330h] [rbp+2B0h] BYREF
  __int64 v93[91]; // [rsp+600h] [rbp+580h] BYREF
  __int64 v94; // [rsp+8D8h] [rbp+858h]
  __int64 v95; // [rsp+8E0h] [rbp+860h]
  __int64 v96; // [rsp+8E8h] [rbp+868h] BYREF
  __int64 v97; // [rsp+8F0h] [rbp+870h]
  __int64 v98; // [rsp+8F8h] [rbp+878h] BYREF
  __int64 v99; // [rsp+900h] [rbp+880h] BYREF
  __int64 v100; // [rsp+908h] [rbp+888h]
  __int64 v101; // [rsp+910h] [rbp+890h]
  __int64 v102; // [rsp+920h] [rbp+8A0h]
  __int64 v103; // [rsp+928h] [rbp+8A8h] BYREF
  __int64 v104; // [rsp+930h] [rbp+8B0h] BYREF
  _QWORD *v105; // [rsp+938h] [rbp+8B8h]
  _QWORD *v106; // [rsp+940h] [rbp+8C0h] BYREF
  _QWORD *v107; // [rsp+948h] [rbp+8C8h]
  _QWORD *v108; // [rsp+950h] [rbp+8D0h]
  _QWORD *v109; // [rsp+958h] [rbp+8D8h]
  _QWORD *v110; // [rsp+960h] [rbp+8E0h] BYREF
  _QWORD *v111; // [rsp+968h] [rbp+8E8h]
  _QWORD *v112; // [rsp+970h] [rbp+8F0h] BYREF
  _QWORD *v113; // [rsp+978h] [rbp+8F8h]
  __int64 v114[3]; // [rsp+980h] [rbp+900h] BYREF
  __int64 v115; // [rsp+998h] [rbp+918h]
  __int64 v116; // [rsp+9A0h] [rbp+920h] BYREF
  __int64 v117; // [rsp+9A8h] [rbp+928h]
  _QWORD *v118; // [rsp+9B0h] [rbp+930h]
  _QWORD *v119; // [rsp+9B8h] [rbp+938h]
  __int64 v120; // [rsp+9C0h] [rbp+940h] BYREF
  _QWORD *v121; // [rsp+9C8h] [rbp+948h]
  _QWORD *v122; // [rsp+9D0h] [rbp+950h] BYREF
  _QWORD *v123; // [rsp+9D8h] [rbp+958h]
  _QWORD *v124; // [rsp+9E0h] [rbp+960h] BYREF
  _QWORD *v125; // [rsp+9E8h] [rbp+968h]
  __int64 v126; // [rsp+9F0h] [rbp+970h]
  __int64 v127; // [rsp+9F8h] [rbp+978h]
  char v128[8]; // [rsp+A00h] [rbp+980h] BYREF
  const char *v129; // [rsp+A08h] [rbp+988h]
  __int64 v130; // [rsp+A10h] [rbp+990h]
  const char *v131; // [rsp+A18h] [rbp+998h]
  __int16 v132; // [rsp+A20h] [rbp+9A0h]
  __int64 v133; // [rsp+A30h] [rbp+9B0h] BYREF
  unsigned __int8 v134; // [rsp+A38h] [rbp+9B8h]
  int v135; // [rsp+A40h] [rbp+9C0h]
  _QWORD *v136; // [rsp+A48h] [rbp+9C8h] BYREF
  _QWORD *v137; // [rsp+A50h] [rbp+9D0h]
  _QWORD *v138; // [rsp+A58h] [rbp+9D8h]
  _QWORD *v139; // [rsp+A60h] [rbp+9E0h]
  char v140; // [rsp+A68h] [rbp+9E8h]
  __int64 v141[82]; // [rsp+A70h] [rbp+9F0h] BYREF
  __int64 v142; // [rsp+D00h] [rbp+C80h] BYREF
  unsigned __int8 v143; // [rsp+D08h] [rbp+C88h]
  int v144; // [rsp+D10h] [rbp+C90h]
  __int64 v145; // [rsp+D18h] [rbp+C98h]
  _QWORD v146[86]; // [rsp+D20h] [rbp+CA0h] BYREF
  char v147[32]; // [rsp+FD0h] [rbp+F50h] BYREF
  __int64 v148[2]; // [rsp+FF0h] [rbp+F70h] BYREF
  __int64 v149[2]; // [rsp+1040h] [rbp+FC0h] BYREF
  __int64 v150[2]; // [rsp+1080h] [rbp+1000h] BYREF
  __int64 v151[2]; // [rsp+1090h] [rbp+1010h] BYREF
  __int64 v152[2]; // [rsp+10A0h] [rbp+1020h] BYREF
  __int64 v153[2]; // [rsp+10C0h] [rbp+1040h] BYREF
  __int64 v154[2]; // [rsp+10D0h] [rbp+1050h] BYREF
  __int64 v155[2]; // [rsp+10E0h] [rbp+1060h] BYREF
  __int64 v156[2]; // [rsp+10F0h] [rbp+1070h] BYREF
  __int64 v157[2]; // [rsp+1100h] [rbp+1080h] BYREF
  __int64 v158[2]; // [rsp+1110h] [rbp+1090h] BYREF
  __int64 v159[2]; // [rsp+1120h] [rbp+10A0h] BYREF
  __int64 v160[2]; // [rsp+1130h] [rbp+10B0h] BYREF
  __int64 v161[2]; // [rsp+1140h] [rbp+10C0h] BYREF
  __int64 v162[2]; // [rsp+1150h] [rbp+10D0h] BYREF
  __int64 v163[2]; // [rsp+1160h] [rbp+10E0h] BYREF
  __int64 v164[2]; // [rsp+1170h] [rbp+10F0h] BYREF
  __int64 v165[2]; // [rsp+1180h] [rbp+1100h] BYREF
  __int64 v166[2]; // [rsp+1190h] [rbp+1110h] BYREF
  __int64 v167[2]; // [rsp+11A0h] [rbp+1120h] BYREF
  __int64 v168[3]; // [rsp+11B0h] [rbp+1130h] BYREF
  __int64 v169; // [rsp+11C8h] [rbp+1148h]
  char v170; // [rsp+11D6h] [rbp+1156h]
  char v171; // [rsp+11D7h] [rbp+1157h]
  __int64 v172; // [rsp+11D8h] [rbp+1158h]
  __int64 v173; // [rsp+11E0h] [rbp+1160h]
  __int64 v174; // [rsp+11E8h] [rbp+1168h]
  __int64 v175; // [rsp+11F0h] [rbp+1170h]
  __int64 v176; // [rsp+11F8h] [rbp+1178h]
  __int64 v177; // [rsp+1200h] [rbp+1180h]
  char v178; // [rsp+120Eh] [rbp+118Eh]
  char v179; // [rsp+120Fh] [rbp+118Fh]
  __int64 v180; // [rsp+1210h] [rbp+1190h]
  __int64 v181; // [rsp+1218h] [rbp+1198h]
  __int64 v182; // [rsp+1220h] [rbp+11A0h]
  __int64 v183; // [rsp+1228h] [rbp+11A8h]
  __int64 v184; // [rsp+1230h] [rbp+11B0h]
  __int64 v185; // [rsp+1238h] [rbp+11B8h]
  char v186; // [rsp+1246h] [rbp+11C6h]
  char v187; // [rsp+1247h] [rbp+11C7h]
  __int64 v188; // [rsp+1248h] [rbp+11C8h]
  __int64 v189; // [rsp+1250h] [rbp+11D0h]
  __int64 v190; // [rsp+1258h] [rbp+11D8h]
  __int64 v191; // [rsp+1260h] [rbp+11E0h]
  char v192; // [rsp+126Fh] [rbp+11EFh]
  __int64 v193; // [rsp+1270h] [rbp+11F0h]
  char v194; // [rsp+127Dh] [rbp+11FDh]
  char init_data__modelZboardZmemory95manager_u326; // [rsp+127Eh] [rbp+11FEh]
  char v196; // [rsp+127Fh] [rbp+11FFh]
  __int64 v197; // [rsp+1280h] [rbp+1200h]
  __int64 v198; // [rsp+1288h] [rbp+1208h]
  __int64 v199; // [rsp+1290h] [rbp+1210h]
  __int64 v200; // [rsp+1298h] [rbp+1218h]
  __int64 v201; // [rsp+12A0h] [rbp+1220h]
  char v202; // [rsp+12AFh] [rbp+122Fh]
  __int64 v203; // [rsp+12B0h] [rbp+1230h]
  char v204; // [rsp+12BDh] [rbp+123Dh]
  char v205; // [rsp+12BEh] [rbp+123Eh]
  char v206; // [rsp+12BFh] [rbp+123Fh]
  __int64 v207; // [rsp+12C0h] [rbp+1240h]
  char v208; // [rsp+12CFh] [rbp+124Fh]
  __int64 v209; // [rsp+12D0h] [rbp+1250h]
  __int64 v210; // [rsp+12D8h] [rbp+1258h]
  __int64 v211; // [rsp+12E0h] [rbp+1260h]
  __int64 v212; // [rsp+12E8h] [rbp+1268h]
  __int64 v213; // [rsp+12F0h] [rbp+1270h]
  __int64 v214; // [rsp+12F8h] [rbp+1278h]
  __int64 v215; // [rsp+1300h] [rbp+1280h]
  __int64 v216; // [rsp+1308h] [rbp+1288h]
  __int64 v217; // [rsp+1310h] [rbp+1290h]
  char *v218; // [rsp+1318h] [rbp+1298h]
  __int64 v219; // [rsp+1320h] [rbp+12A0h]
  __int64 v220; // [rsp+1328h] [rbp+12A8h]
  __int64 v221; // [rsp+1330h] [rbp+12B0h]
  __int64 v222; // [rsp+1338h] [rbp+12B8h]
  bool v223; // [rsp+1346h] [rbp+12C6h]
  char v224; // [rsp+1347h] [rbp+12C7h]
  __int64 v225; // [rsp+1348h] [rbp+12C8h]
  __int64 v226; // [rsp+1350h] [rbp+12D0h]
  char v227; // [rsp+135Eh] [rbp+12DEh]
  char v228; // [rsp+135Fh] [rbp+12DFh]

  v129 = "process_request";
  v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
  v130 = 0i64;
  v132 = 0;
  nimFrame_89(v128);
  v218 = (char *)nimErrorFlag_87();
  nimZeroMem_67(v147, 32i64);
  nimZeroMem_67(&v142, 720i64);
  nimZeroMem_67(&v133, 720i64);
  v130 = 92i64;
  while ( 1 )
  {
    v217 = 0i64;
    v217 = peek__modelZsimulationZcompile95thread_u148(&request_channel__modelZsimulationZcompile95thread_u90);
    if ( !v217 )
      break;
    nimZeroMem_67(v92, 720i64);
    v130 = 93i64;
    recv__modelZsimulationZcompile95thread_u153(&request_channel__modelZsimulationZcompile95thread_u90, v92);
    if ( !*v218 )
    {
      v130 = 94i64;
      if ( LOBYTE(v92[1]) > 1u )
        goto LABEL_15;
      v130 = 95i64;
      v1 = a1[31];
      v2 = 0;
      v3 = __OFADD__(1i64, v1);
      v4 = v1 + 1;
      if ( v3 )
        v2 = 1;
      v126 = v4;
      if ( (v2 & 1) == 0 )
      {
        if ( v92[0] != v126 )
        {
          v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_6;
          v37 = &TM__nTvHpEr8JHyxC5V4m579axA_5;
          failedAssertImpl__stdZassertions_u234(&v36);
          if ( *v218 )
            goto LABEL_18;
        }
        v130 = 96i64;
        v5 = a1[31];
        v6 = 0;
        v3 = __OFADD__(1i64, v5);
        v7 = v5 + 1;
        if ( v3 )
          v6 = 1;
        v127 = v7;
        if ( (v6 & 1) == 0 )
        {
          a1[31] = v127;
LABEL_15:
          v130 = 97i64;
          if ( LOBYTE(v92[1]) || (v130 = 98i64, clear__modelZsimulationZcompile95thread_u244(v147), !*v218) )
          {
            v130 = 99i64;
            nimZeroMem_67(v93, 720i64);
            qmemcpy(v93, v92, 0x2D0ui64);
            v130 = 326i64;
            v131 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            eqwasMoved___modelZsimulationZpreorder_u8397(v92, v92);
            v130 = 99i64;
            v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
            addLast__modelZsimulationZcompile95thread_u420(v147, v93);
          }
          goto LABEL_18;
        }
      }
      raiseOverflow();
    }
LABEL_18:
    v130 = 326i64;
    v131 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
    eqdestroy___modelZsimulationZpreorder_u8400(v92);
    if ( *v218 )
      goto LABEL_284;
  }
  v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
  v228 = 0;
  v130 = 105i64;
  while ( 1 )
  {
    v216 = 0i64;
    v216 = len__modelZsimulationZcompile95thread_u293_0(v147);
    if ( *v218 )
      goto LABEL_284;
    if ( v216 <= 0 )
      break;
    nimZeroMem_67(v93, 720i64);
    nimZeroMem_67(&v63, 232i64);
    v130 = 106i64;
    popFirst__modelZsimulationZcompile95thread_u795(v147, v93);
    if ( *v218 )
      goto LABEL_108;
    v130 = 108i64;
    if ( LOBYTE(v93[1]) == 2 )
    {
      v130 = 326i64;
      v131 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      eqcopy___modelZsimulationZpreorder_u8403(&v142, v93);
      v130 = 368i64;
      v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\channels_builtin.nim";
      eqdestroy___modelZsimulationZcompile95thread_u2387(&v63);
      if ( *v218 )
        goto LABEL_284;
      v130 = 326i64;
      v131 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      eqdestroy___modelZsimulationZpreorder_u8400(v93);
      v130 = 110i64;
      v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
    }
    else
    {
      v130 = 112i64;
      if ( LOBYTE(v93[1]) == 3 )
      {
        v130 = 326i64;
        v131 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        eqcopy___modelZsimulationZpreorder_u8403(&v133, v93);
        v130 = 368i64;
        v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\channels_builtin.nim";
        eqdestroy___modelZsimulationZcompile95thread_u2387(&v63);
        if ( *v218 )
          goto LABEL_284;
        v130 = 326i64;
        v131 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        eqdestroy___modelZsimulationZpreorder_u8400(v93);
        v130 = 114i64;
        v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
      }
      else
      {
        v130 = 116i64;
        if ( LOBYTE(v93[1]) == 4 )
        {
          v228 = 1;
          v130 = 368i64;
          v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\channels_builtin.nim";
          eqdestroy___modelZsimulationZcompile95thread_u2387(&v63);
          if ( *v218 )
            goto LABEL_284;
          v130 = 326i64;
          v131 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          eqdestroy___modelZsimulationZpreorder_u8400(v93);
          v130 = 118i64;
          v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
        }
        else
        {
          v130 = 120i64;
          log_request__modelZsimulationZcompile95thread_u101(v93);
          if ( *v218 )
            goto LABEL_108;
          v130 = 122i64;
          nimZeroMem_67(&v63, 232i64);
          v130 = 124i64;
          if ( !LOBYTE(v93[1]) )
          {
            nimZeroMem_67(&v44, 192i64);
            v124 = 0i64;
            v125 = 0i64;
            v122 = 0i64;
            v123 = 0i64;
            v120 = 0i64;
            v121 = 0i64;
            nimZeroMem_67(v92, 192i64);
            v130 = 125i64;
            if ( (v93[1] & 7) != 0 )
            {
              dollar___modelZmodel95types_u521(v148, LOBYTE(v93[1]));
              v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_16;
              v37 = &TM__nTvHpEr8JHyxC5V4m579axA_15;
              v34 = (_QWORD *)v148[0];
              v35 = v148[1];
              raiseFieldErrorStr(&v36, &v34);
            }
            else
            {
              v36 = (_QWORD *)v93[2];
              v37 = (_QWORD *)v93[3];
              v34 = (_QWORD *)v93[74];
              v35 = v93[75];
              v32 = (_QWORD *)v93[76];
              v33 = v93[77];
              v30 = v93[86];
              v31 = v93[87];
              v28 = v93[4];
              v29 = v93[5];
              preorder__modelZsimulationZpreorder_u8738(
                (__int64 *)&v36,
                (__int64 *)&v34,
                (__int64 *)&v32,
                a1,
                &v30,
                &v28,
                v93[0],
                (__int64)&v44);
              if ( !*v218 )
              {
                v130 = 72i64;
                v131 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                v36 = v60;
                v37 = v61;
                eqcopy___modelZsave95mongerZversionsZv0_u1079(&v124, &v36);
                v215 = 0i64;
                v213 = v50 - 1;
                v214 = v50 - 1;
                v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                v226 = 0i64;
                v130 = 97i64;
                while ( v226 <= v214 )
                {
                  v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                  v215 = v226;
                  v130 = 133i64;
                  if ( v226 < 0 || v215 >= v50 )
                  {
                    raiseIndexError2(v215, v50 - 1);
                    goto LABEL_80;
                  }
                  if ( v215 < 0 || v215 >= (__int64)v124 )
                  {
                    raiseIndexError2(v215, (char *)v124 - 1);
                    goto LABEL_80;
                  }
                  v8 = (_QWORD *)(v51 + 232 * v215 + 160);
                  v9 = &v125[70 * v215 + 38];
                  v10 = v125[70 * v215 + 41];
                  v8[1] = v125[70 * v215 + 40];
                  v8[2] = v10;
                  v11 = v9[5];
                  v8[3] = v9[4];
                  v8[4] = v11;
                  v12 = v9[7];
                  v8[5] = v9[6];
                  v8[6] = v12;
                  v8[7] = v9[8];
                  v130 = 102i64;
                  v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                  v117 = v226 + 1;
                  if ( __OFADD__(1i64, v226) )
                  {
LABEL_47:
                    raiseOverflow();
                    goto LABEL_80;
                  }
                  v226 = v117;
                }
                nimZeroMem_67(&v38, 168i64);
                nimZeroMem_67(&v116, 8i64);
                v130 = 135i64;
                v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                nimZeroMem_67(&v38, 168i64);
                v130 = 767i64;
                v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                v13 = a1[1];
                v25 = *a1;
                v26 = v13;
                v27 = a1[2];
                v212 = len__modelZboardZmemory95manager_u2711(&v25);
                if ( !*v218 )
                {
                  v211 = 0i64;
                  v210 = 0i64;
                  v130 = 768i64;
                  v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                  v209 = *a1 - 1;
                  v210 = v209;
                  v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                  v225 = 0i64;
                  v130 = 97i64;
                  while ( v225 <= v210 )
                  {
                    v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                    v211 = v225;
                    v130 = 769i64;
                    if ( v225 < 0 || v211 >= *a1 )
                    {
LABEL_61:
                      raiseIndexError2(v211, *a1 - 1);
                      goto LABEL_80;
                    }
                    v208 = 0;
                    v208 = isFilled__pureZcollectionsZtables_u31_10(*(_QWORD *)(a1[1] + 184 * v211 + 8));
                    if ( *v218 )
                      goto LABEL_80;
                    if ( v208 == 1 )
                    {
                      v130 = 135i64;
                      v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                      if ( v211 < 0 )
                        goto LABEL_61;
                      if ( v211 >= *a1 )
                        goto LABEL_61;
                      v116 = *(_QWORD *)(a1[1] + 184 * v211 + 16);
                      v130 = 112i64;
                      v131 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
                      if ( v211 >= *a1 )
                        goto LABEL_61;
                      eqcopy___modelZboardZmemory95manager_u229(&v38, a1[1] + 184 * v211 + 16 + 8);
                      v130 = 136i64;
                      v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                      get_reset_data_range__modelZboardZmemory95manager_u118(v114, &v38);
                      if ( *v218 )
                        goto LABEL_80;
                      v36 = (_QWORD *)v114[0];
                      v37 = (_QWORD *)v114[1];
                      X5BX5Deq___modelZsimulationZcompile95thread_u936(v62, v116, &v36);
                      if ( *v218 )
                        goto LABEL_80;
                      v130 = 771i64;
                      v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                      v207 = 0i64;
                      v14 = a1[1];
                      v25 = *a1;
                      v26 = v14;
                      v27 = a1[2];
                      v207 = len__modelZboardZmemory95manager_u2711(&v25);
                      if ( *v218 )
                        goto LABEL_80;
                      if ( v207 != v212 )
                      {
                        v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_27;
                        v37 = &TM__nTvHpEr8JHyxC5V4m579axA_26;
                        failedAssertImpl__stdZassertions_u234(&v36);
                        if ( *v218 )
                          goto LABEL_80;
                      }
                    }
                    v130 = 102i64;
                    v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                    v115 = v225 + 1;
                    if ( __OFADD__(1i64, v225) )
                      goto LABEL_47;
                    v225 = v115;
                  }
                  v130 = 112i64;
                  v131 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
                  eqdestroy___modelZboardZmemory95manager_u226(&v38);
                  v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                  v122 = 0i64;
                  v123 = 0i64;
                  v130 = 140i64;
                  if ( (v93[1] & 7) != 0 )
                  {
                    dollar___modelZmodel95types_u521(v149, LOBYTE(v93[1]));
                    v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_29;
                    v37 = &TM__nTvHpEr8JHyxC5V4m579axA_15;
                    v34 = (_QWORD *)v149[0];
                    v35 = v149[1];
                    raiseFieldErrorStr(&v36, &v34);
                  }
                  else
                  {
                    v36 = (_QWORD *)v93[2];
                    v37 = (_QWORD *)v93[3];
                    v34 = v124;
                    v35 = (__int64)v125;
                    v32 = v44;
                    v33 = (__int64)v45;
                    v30 = v93[83];
                    v31 = v93[84];
                    v28 = v93[88];
                    v29 = v93[89];
                    generate_source(
                      (unsigned int)&v120,
                      (unsigned int)&v36,
                      (unsigned int)&v93[4],
                      (unsigned int)&v34,
                      (__int64)&v32,
                      v46,
                      (__int64)&v30,
                      v47,
                      v48,
                      (__int64)&v28);
                    if ( !*v218 )
                    {
                      v130 = 178i64;
                      LOBYTE(v38) = 0;
                      LODWORD(v41) = v46;
                      v39 = v120;
                      v40 = v121;
                      handle_request_compile_and_run__modelZsimulationZsimulator95functions_u19(&v36, a1 + 25, &v38);
                      v122 = v36;
                      v123 = v37;
                      if ( !*v218 )
                      {
                        v130 = 187i64;
                        dealloc_dead_buffers__modelZboardZmemory95manager_u2648(a1, &v60, v93[0]);
                        if ( !*v218 )
                        {
                          v63 = (_QWORD *)v93[0];
                          LOBYTE(v64) = 1;
                          v130 = 1513i64;
                          v131 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                          eqdup___modelZsimulationZpreorder_u31176(&v44, v92);
                          v65 = v92[0];
                          v66 = v92[1];
                          v67 = v92[2];
                          v68 = v92[3];
                          v69 = v92[4];
                          v70 = v92[5];
                          v71 = v92[6];
                          v72 = v92[7];
                          v73 = v92[8];
                          v74 = v92[9];
                          v75 = v92[10];
                          v76 = v92[11];
                          v77 = v92[12];
                          v78 = v92[13];
                          v79 = (_QWORD *)v92[14];
                          v80 = v92[15];
                          v81 = v92[16];
                          v82 = v92[17];
                          v83 = v92[18];
                          v84 = v92[19];
                          v85 = v92[20];
                          v86 = v92[21];
                          v87 = v92[22];
                          v88 = v92[23];
                          v118 = v122;
                          v119 = v123;
                          v130 = 1699i64;
                          v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                          eqwasMoved___system_u2658(&v122);
                          v89 = v118;
                          v90 = v119;
                          v130 = 196i64;
                          v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                          a1[32] = v46;
                        }
                      }
                    }
                  }
                }
              }
            }
LABEL_80:
            v130 = 394i64;
            v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v121 && (*v121 & 0x4000000000000000i64) == 0 )
              deallocShared(v121);
            if ( v123 && (*v123 & 0x4000000000000000i64) == 0 )
              deallocShared(v123);
            v130 = 72i64;
            v131 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
            v36 = v124;
            v37 = v125;
            eqdestroy___modelZsave95mongerZversionsZv0_u1076(&v36);
            v130 = 1513i64;
            v131 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            eqdestroy___modelZsimulationZpreorder_u31170(&v44);
            if ( *v218 )
              goto LABEL_108;
LABEL_95:
            v130 = 212i64;
            if ( v63 )
              goto LABEL_106;
            v112 = 0i64;
            v113 = 0i64;
            v110 = 0i64;
            v111 = 0i64;
            v108 = 0i64;
            v109 = 0i64;
            v106 = 0i64;
            v107 = 0i64;
            dollar___modelZmodel95types_u563(&v112, (unsigned __int8)v64);
            dollar___modelZmodel95types_u521(&v110, LOBYTE(v93[1]));
            rawNewString(&v36, (char *)v110 + (_QWORD)v112 + 94);
            v106 = v36;
            v107 = v37;
            v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_40;
            v37 = &TM__nTvHpEr8JHyxC5V4m579axA_39;
            appendString_30(&v106, &v36);
            v36 = v112;
            v37 = v113;
            appendString_30(&v106, &v36);
            v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_43;
            v37 = &TM__nTvHpEr8JHyxC5V4m579axA_42;
            appendString_30(&v106, &v36);
            v36 = v110;
            v37 = v111;
            appendString_30(&v106, &v36);
            v108 = v106;
            v109 = v107;
            v36 = v106;
            v37 = v107;
            failedAssertImpl__stdZassertions_u234(&v36);
            if ( !*v218 )
            {
              v130 = 394i64;
              v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              if ( v109 && (*v109 & 0x4000000000000000i64) == 0 )
                deallocShared(v109);
              if ( v111 && (*v111 & 0x4000000000000000i64) == 0 )
                deallocShared(v111);
              if ( v113 && (*v113 & 0x4000000000000000i64) == 0 )
                deallocShared(v113);
LABEL_106:
              v130 = 214i64;
              v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
              log_response__modelZsimulationZcompile95thread_u124(&v63);
              if ( !*v218 )
              {
                v130 = 215i64;
                nimZeroMem_67(v92, 232i64);
                v92[0] = (__int64)v63;
                v92[1] = v64;
                v92[2] = v65;
                v92[3] = v66;
                v92[4] = v67;
                v92[5] = v68;
                v92[6] = v69;
                v92[7] = v70;
                v92[8] = v71;
                v92[9] = v72;
                v92[10] = v73;
                v92[11] = v74;
                v92[12] = v75;
                v92[13] = v76;
                v92[14] = v77;
                v92[15] = v78;
                v92[16] = (__int64)v79;
                v92[17] = v80;
                v92[18] = v81;
                v92[19] = v82;
                v92[20] = v83;
                v92[21] = v84;
                v92[22] = v85;
                v92[23] = v86;
                v92[24] = v87;
                v92[25] = v88;
                v92[26] = (__int64)v89;
                v92[27] = (__int64)v90;
                v92[28] = v91;
                v130 = 368i64;
                v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\channels_builtin.nim";
                eqwasMoved___modelZsimulationZcompile95thread_u2384(&v63);
                v130 = 215i64;
                v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                send__modelZsimulationZcompile95thread_u2355(
                  &response_channel__modelZsimulationZcompile95thread_u92,
                  v92);
              }
              goto LABEL_108;
            }
            goto LABEL_108;
          }
          v130 = 197i64;
          v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
          if ( LOBYTE(v93[1]) != 1 )
            goto LABEL_95;
          nimZeroMem_67(v92, 32i64);
          v130 = 198i64;
          LOBYTE(v92[0]) = 1;
          if ( (v93[1] & 7) != 1i64 )
          {
            dollar___modelZmodel95types_u521(v150, LOBYTE(v93[1]));
            v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_36;
            v37 = &TM__nTvHpEr8JHyxC5V4m579axA_35;
            v34 = (_QWORD *)v150[0];
            v35 = v150[1];
            raiseFieldErrorStr(&v36, &v34);
            goto LABEL_108;
          }
          LOBYTE(v92[1]) = v93[2];
          if ( (v93[1] & 7) != 1i64 )
          {
            dollar___modelZmodel95types_u521(v151, LOBYTE(v93[1]));
            v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_38;
            v37 = &TM__nTvHpEr8JHyxC5V4m579axA_37;
            v34 = (_QWORD *)v151[0];
            v35 = v151[1];
            raiseFieldErrorStr(&v36, &v34);
            goto LABEL_108;
          }
          v92[2] = v93[3];
          v130 = 205i64;
          handle_request_do__modelZsimulationZsimulator95functions_u288(v92);
          if ( !*v218 )
          {
            v130 = 207i64;
            nimZeroMem_67(&v63, 232i64);
            v63 = (_QWORD *)v93[0];
            LOBYTE(v64) = 0;
            v130 = 180i64;
            eqdestroy___modelZsimulationZcompile95thread_u3529(v92);
            goto LABEL_95;
          }
LABEL_108:
          v206 = *v218;
          *v218 = 0;
          v130 = 368i64;
          v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\channels_builtin.nim";
          eqdestroy___modelZsimulationZcompile95thread_u2387(&v63);
          if ( *v218 )
            goto LABEL_284;
          v130 = 326i64;
          v131 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          eqdestroy___modelZsimulationZpreorder_u8400(v93);
          *v218 = v206;
          if ( *v218 )
            goto LABEL_284;
        }
      }
    }
  }
  v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
  v227 = 0;
  v130 = 218i64;
  if ( !v133 )
    goto LABEL_287;
  nimZeroMem_67(&v44, 200i64);
  nimZeroMem_67(v92, 232i64);
  v130 = 219i64;
  log_request__modelZsimulationZcompile95thread_u101(&v133);
  if ( !*v218 )
  {
    v130 = 221i64;
    if ( (v134 & 7) != 3i64 )
    {
      dollar___modelZmodel95types_u521(v152, v134);
      v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_47;
      v37 = &TM__nTvHpEr8JHyxC5V4m579axA_46;
      v34 = (_QWORD *)v152[0];
      v35 = v152[1];
      raiseFieldErrorStr(&v36, &v34);
      goto LABEL_143;
    }
    v130 = 222i64;
    if ( (v134 & 7) != 3i64 )
    {
      dollar___modelZmodel95types_u521(v153, v134);
      v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_49;
      v37 = &TM__nTvHpEr8JHyxC5V4m579axA_46;
      v34 = (_QWORD *)v153[0];
      v35 = v153[1];
      raiseFieldErrorStr(&v36, &v34);
      goto LABEL_143;
    }
    v130 = 221i64;
    v36 = v138;
    v37 = v139;
    v34 = v136;
    v35 = (__int64)v137;
    compile_isa__modelZsimulationZcompile95thread_u130(&v36, &v34, v135 != -1, &v44);
    if ( *v218 )
      goto LABEL_143;
    v130 = 224i64;
    if ( v45 )
    {
      v104 = 0i64;
      v105 = 0i64;
      v93[0] = 26i64;
      v93[1] = (__int64)&TM__nTvHpEr8JHyxC5V4m579axA_50;
      v130 = 227i64;
      dollar___systemZdollars_u14(&v104, v44);
      if ( !*v218 )
      {
        v93[2] = v104;
        v93[3] = (__int64)v105;
        v93[4] = 3i64;
        v93[5] = (__int64)&TM__nTvHpEr8JHyxC5V4m579axA_52;
        v93[6] = (__int64)v45;
        v93[7] = v46;
        v130 = 225i64;
        log__modelZsimulationZcompile95thread_u2512(v93, 4i64);
        if ( !*v218 )
        {
          v130 = 394i64;
          v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v105 && (*v105 & 0x4000000000000000i64) == 0 )
            deallocShared(v105);
          goto LABEL_124;
        }
      }
    }
    else
    {
LABEL_124:
      v130 = 232i64;
      v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
      v224 = 0;
      if ( (v134 & 7) == 3i64 )
      {
        v224 = v140;
        if ( !v140 )
        {
          v130 = 233i64;
          v223 = v45 == 0i64;
          if ( !v45 )
          {
            if ( (v134 & 7) != 3i64 )
            {
              dollar___modelZmodel95types_u521(v155, v134);
              v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_55;
              v37 = &TM__nTvHpEr8JHyxC5V4m579axA_46;
              v34 = (_QWORD *)v155[0];
              v35 = v155[1];
              raiseFieldErrorStr(&v36, &v34);
              goto LABEL_143;
            }
            v15 = (_QWORD *)a1[24];
            v36 = (_QWORD *)a1[23];
            v37 = v15;
            v34 = v136;
            v35 = (__int64)v137;
            v223 = (unsigned __int8)eqStrings_16(&v36, &v34) == 0;
          }
          v224 = v223;
        }
        if ( v224 == 1 )
        {
          v130 = 1492i64;
          v131 = "D:\\TuringComplete_Phu\\model\\isa_spec\\assemble.nim";
          eqcopy___modelZisa95specZassemble_u15431(a1 + 3, &v47);
          if ( *v218 )
            goto LABEL_143;
          v130 = 1699i64;
          v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( (v134 & 7) != 3i64 )
          {
            dollar___modelZmodel95types_u521(v156, v134);
            v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_56;
            v37 = &TM__nTvHpEr8JHyxC5V4m579axA_46;
            v34 = (_QWORD *)v156[0];
            v35 = v156[1];
            raiseFieldErrorStr(&v36, &v34);
            goto LABEL_143;
          }
          v36 = v136;
          v37 = v137;
          eqsink___system_u2667(a1 + 23, &v36);
          if ( (v134 & 7) != 3i64 )
          {
            dollar___modelZmodel95types_u521(v157, v134);
            v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_57;
            v37 = &TM__nTvHpEr8JHyxC5V4m579axA_46;
            v34 = (_QWORD *)v157[0];
            v35 = v157[1];
            raiseFieldErrorStr(&v36, &v34);
            goto LABEL_143;
          }
          eqwasMoved___system_u2658(&v136);
          v130 = 236i64;
          v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
          v227 = 1;
        }
        v130 = 238i64;
        v92[0] = v133;
        LOBYTE(v92[1]) = 3;
        if ( (v134 & 7) == 3i64 )
        {
          LODWORD(v92[2]) = v135;
          nimZeroMem_67(&v63, 200i64);
          v63 = v44;
          v64 = (__int64)v45;
          v65 = v46;
          v66 = v47;
          v67 = v48;
          v68 = v49;
          v69 = v50;
          v70 = v51;
          v71 = v52;
          v72 = v53;
          v73 = v54;
          v74 = v55;
          v75 = v56;
          v76 = v57;
          v77 = v58;
          v78 = v59;
          v79 = v60;
          v80 = (__int64)v61;
          v81 = v62[0];
          v82 = v62[1];
          v83 = v62[2];
          v84 = v62[3];
          v85 = v62[4];
          v86 = v62[5];
          v87 = v62[6];
          v130 = 1837i64;
          v131 = "D:\\TuringComplete_Phu\\model\\isa_spec\\isa_spec.nim";
          eqwasMoved___modelZisa95specZisa95spec_u19139(&v44);
          v92[3] = (__int64)v63;
          v92[4] = v64;
          v92[5] = v65;
          v92[6] = v66;
          v92[7] = v67;
          v92[8] = v68;
          v92[9] = v69;
          v92[10] = v70;
          v92[11] = v71;
          v92[12] = v72;
          v92[13] = v73;
          v92[14] = v74;
          v92[15] = v75;
          v92[16] = v76;
          v92[17] = v77;
          v92[18] = v78;
          v92[19] = (__int64)v79;
          v92[20] = v80;
          v92[21] = v81;
          v92[22] = v82;
          v92[23] = v83;
          v92[24] = v84;
          v92[25] = v85;
          v92[26] = v86;
          v92[27] = v87;
          LOBYTE(v92[28]) = v227;
          v130 = 246i64;
          v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
          log_response__modelZsimulationZcompile95thread_u124(v92);
          if ( !*v218 )
          {
            v130 = 247i64;
            nimZeroMem_67(v93, 232i64);
            v93[0] = v92[0];
            v93[1] = v92[1];
            v93[2] = v92[2];
            v93[3] = v92[3];
            v93[4] = v92[4];
            v93[5] = v92[5];
            v93[6] = v92[6];
            v93[7] = v92[7];
            v93[8] = v92[8];
            v93[9] = v92[9];
            v93[10] = v92[10];
            v93[11] = v92[11];
            v93[12] = v92[12];
            v93[13] = v92[13];
            v93[14] = v92[14];
            v93[15] = v92[15];
            v93[16] = v92[16];
            v93[17] = v92[17];
            v93[18] = v92[18];
            v93[19] = v92[19];
            v93[20] = v92[20];
            v93[21] = v92[21];
            v93[22] = v92[22];
            v93[23] = v92[23];
            v93[24] = v92[24];
            v93[25] = v92[25];
            v93[26] = v92[26];
            v93[27] = v92[27];
            v93[28] = v92[28];
            v130 = 368i64;
            v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\channels_builtin.nim";
            eqwasMoved___modelZsimulationZcompile95thread_u2384(v92);
            v130 = 247i64;
            v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
            send__modelZsimulationZcompile95thread_u2355(&response_channel__modelZsimulationZcompile95thread_u92, v93);
          }
        }
        else
        {
          dollar___modelZmodel95types_u521(v158, v134);
          v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_58;
          v37 = &TM__nTvHpEr8JHyxC5V4m579axA_46;
          v34 = (_QWORD *)v158[0];
          v35 = v158[1];
          raiseFieldErrorStr(&v36, &v34);
        }
      }
      else
      {
        dollar___modelZmodel95types_u521(v154, v134);
        v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_54;
        v37 = &TM__nTvHpEr8JHyxC5V4m579axA_46;
        v34 = (_QWORD *)v154[0];
        v35 = v154[1];
        raiseFieldErrorStr(&v36, &v34);
      }
    }
  }
LABEL_143:
  v205 = *v218;
  *v218 = 0;
  v130 = 368i64;
  v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\channels_builtin.nim";
  eqdestroy___modelZsimulationZcompile95thread_u2387(v92);
  if ( !*v218 )
  {
    v130 = 1837i64;
    v131 = "D:\\TuringComplete_Phu\\model\\isa_spec\\isa_spec.nim";
    eqdestroy___modelZisa95specZisa95spec_u19142(&v44);
    if ( !*v218 )
    {
      *v218 = v205;
      if ( !*v218 )
      {
LABEL_287:
        v130 = 249i64;
        v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
        if ( !v142 )
          goto LABEL_202;
        nimZeroMem_67(&v38, 48i64);
        nimZeroMem_67(&v44, 144i64);
        nimZeroMem_67(v92, 232i64);
        v130 = 250i64;
        log_request__modelZsimulationZcompile95thread_u101(&v142);
        if ( !*v218 )
        {
          v130 = 770i64;
          v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
          if ( (v143 & 7) == 2i64 )
          {
            eqcopy___modelZsimulationZcompile95thread_u3072(&v38, v146);
            v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
            v130 = 254i64;
            v36 = v40;
            v37 = v41;
            v34 = v42;
            v35 = v43;
            v32 = v38;
            v33 = v39;
            compile_asm__modelZsimulationZcompile95thread_u135(
              (unsigned int)&v36,
              (unsigned int)&v34,
              (unsigned int)&v32,
              (_DWORD)a1 + 24,
              (__int64)&v44);
            if ( !*v218 )
            {
              v130 = 256i64;
              if ( (v143 & 7) == 2i64 )
              {
                v204 = 0;
                v16 = a1[1];
                v25 = *a1;
                v26 = v16;
                v27 = a1[2];
                v204 = contains__modelZboardZmemory95manager_u622(&v25, v145);
                if ( !*v218 )
                {
                  if ( v204 == 1 )
                  {
                    v130 = 257i64;
                    if ( (v143 & 7) != 2i64 )
                    {
                      dollar___modelZmodel95types_u521(v161, v143);
                      v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_62;
                      v37 = &TM__nTvHpEr8JHyxC5V4m579axA_59;
                      v34 = (_QWORD *)v161[0];
                      v35 = v161[1];
                      raiseFieldErrorStr(&v36, &v34);
                      goto LABEL_200;
                    }
                    v203 = 0i64;
                    v203 = X5BX5D___modelZboardZmemory95manager_u1131(a1, v145);
                    if ( *v218 )
                      goto LABEL_200;
                    if ( (v143 & 7) != 2i64 )
                    {
                      dollar___modelZmodel95types_u521(v162, v143);
                      v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_63;
                      v37 = &TM__nTvHpEr8JHyxC5V4m579axA_59;
                      v34 = (_QWORD *)v162[0];
                      v35 = v162[1];
                      raiseFieldErrorStr(&v36, &v34);
                      goto LABEL_200;
                    }
                    v202 = 0;
                    v202 = eqeq___modelZsimulationZcompile95thread_u2639(v203 + 80, v146);
                    if ( !v202 )
                    {
                      v227 = 1;
                      v130 = 260i64;
                      v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                      if ( (v143 & 7) != 2i64 )
                      {
                        dollar___modelZmodel95types_u521(v163, v143);
                        v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_64;
                        v37 = &TM__nTvHpEr8JHyxC5V4m579axA_59;
                        v34 = (_QWORD *)v163[0];
                        v35 = v163[1];
                        raiseFieldErrorStr(&v36, &v34);
                        goto LABEL_200;
                      }
                      v201 = 0i64;
                      v201 = X5BX5D___modelZboardZmemory95manager_u1131(a1, v145);
                      if ( *v218 )
                        goto LABEL_200;
                      if ( (v143 & 7) != 2i64 )
                      {
                        dollar___modelZmodel95types_u521(v164, v143);
                        v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_65;
                        v37 = &TM__nTvHpEr8JHyxC5V4m579axA_59;
                        v34 = (_QWORD *)v164[0];
                        v35 = v164[1];
                        raiseFieldErrorStr(&v36, &v34);
                        goto LABEL_200;
                      }
                      v130 = 770i64;
                      v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                      eqcopy___modelZsimulationZcompile95thread_u3072(v201 + 80, v146);
                    }
                  }
                  v130 = 263i64;
                  v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                  if ( v133 )
                    goto LABEL_196;
                  nimZeroMem_67(v93, 168i64);
                  nimZeroMem_67(&v103, 8i64);
                  v130 = 767i64;
                  v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                  v17 = a1[1];
                  v25 = *a1;
                  v26 = v17;
                  v27 = a1[2];
                  v200 = len__modelZboardZmemory95manager_u2711(&v25);
                  if ( !*v218 )
                  {
                    v199 = 0i64;
                    v198 = 0i64;
                    v130 = 768i64;
                    v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                    v197 = *a1 - 1;
                    v198 = v197;
                    v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                    v222 = 0i64;
                    v130 = 97i64;
                    while ( v222 <= v198 )
                    {
                      v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                      v199 = v222;
                      v130 = 769i64;
                      if ( v222 < 0 || v199 >= *a1 )
                      {
LABEL_180:
                        raiseIndexError2(v199, *a1 - 1);
                        break;
                      }
                      v196 = 0;
                      v196 = isFilled__pureZcollectionsZtables_u31_10(*(_QWORD *)(a1[1] + 184 * v199 + 8));
                      if ( *v218 )
                        break;
                      if ( v196 == 1 )
                      {
                        v130 = 264i64;
                        v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                        if ( v199 < 0 )
                          goto LABEL_180;
                        if ( v199 >= *a1 )
                          goto LABEL_180;
                        v103 = *(_QWORD *)(a1[1] + 184 * v199 + 16);
                        v130 = 112i64;
                        v131 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
                        if ( v199 >= *a1 )
                          goto LABEL_180;
                        eqcopy___modelZboardZmemory95manager_u229(v93, a1[1] + 184 * v199 + 16 + 8);
                        v130 = 265i64;
                        v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                        init_data__modelZboardZmemory95manager_u326 = get_init_data__modelZboardZmemory95manager_u326(v93);
                        if ( *v218 )
                          break;
                        v130 = 266i64;
                        if ( init_data__modelZboardZmemory95manager_u326 == 1 )
                        {
                          v130 = 269i64;
                          if ( (v143 & 7) != 2i64 )
                          {
                            dollar___modelZmodel95types_u521(v165, v143);
                            v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_66;
                            v37 = &TM__nTvHpEr8JHyxC5V4m579axA_59;
                            v34 = (_QWORD *)v165[0];
                            v35 = v165[1];
                            raiseFieldErrorStr(&v36, &v34);
                            break;
                          }
                          v194 = 0;
                          v36 = (_QWORD *)v93[14];
                          v37 = (_QWORD *)v93[15];
                          v34 = (_QWORD *)v146[4];
                          v35 = v146[5];
                          v194 = eqeq___modelZsimulationZcompile95thread_u2649(&v36, &v34);
                          if ( v194 )
                          {
                            v130 = 271i64;
                            v36 = v44;
                            v37 = v45;
                            reload_reset_data__modelZboardZmemory95manager_u296(v103, v93, &v36);
                            if ( *v218 )
                              break;
                          }
                          else
                          {
                            v130 = 270i64;
                          }
                        }
                        else
                        {
                          v130 = 267i64;
                        }
                        v130 = 771i64;
                        v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                        v193 = 0i64;
                        v18 = a1[1];
                        v25 = *a1;
                        v26 = v18;
                        v27 = a1[2];
                        v193 = len__modelZboardZmemory95manager_u2711(&v25);
                        if ( *v218 )
                          break;
                        if ( v193 != v200 )
                        {
                          v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_67;
                          v37 = &TM__nTvHpEr8JHyxC5V4m579axA_26;
                          failedAssertImpl__stdZassertions_u234(&v36);
                          if ( *v218 )
                            break;
                        }
                      }
                      v130 = 102i64;
                      v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                      v102 = v222 + 1;
                      if ( __OFADD__(1i64, v222) )
                      {
                        raiseOverflow();
                        break;
                      }
                      v222 = v102;
                    }
                  }
                  v130 = 112i64;
                  v131 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
                  eqdestroy___modelZboardZmemory95manager_u226(v93);
                  if ( !*v218 )
                  {
LABEL_196:
                    v130 = 273i64;
                    v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                    setLen__pureZtimes_u2688(&v44, 0i64);
                    v130 = 274i64;
                    v92[0] = v142;
                    LOBYTE(v92[1]) = 2;
                    if ( (v143 & 7) == 2i64 )
                    {
                      LODWORD(v92[2]) = v144;
                      nimZeroMem_67(&v63, 144i64);
                      v63 = v44;
                      v64 = (__int64)v45;
                      v65 = v46;
                      v66 = v47;
                      v67 = v48;
                      v68 = v49;
                      v69 = v50;
                      v70 = v51;
                      v71 = v52;
                      v72 = v53;
                      v73 = v54;
                      v74 = v55;
                      v75 = v56;
                      v76 = v57;
                      v77 = v58;
                      v78 = v59;
                      v79 = v60;
                      v80 = (__int64)v61;
                      v130 = 1863i64;
                      v131 = "D:\\TuringComplete_Phu\\model\\isa_spec\\assemble.nim";
                      eqwasMoved___modelZisa95specZassemble_u18441(&v44);
                      v92[3] = (__int64)v63;
                      v92[4] = v64;
                      v92[5] = v65;
                      v92[6] = v66;
                      v92[7] = v67;
                      v92[8] = v68;
                      v92[9] = v69;
                      v92[10] = v70;
                      v92[11] = v71;
                      v92[12] = v72;
                      v92[13] = v73;
                      v92[14] = v74;
                      v92[15] = v75;
                      v92[16] = v76;
                      v92[17] = v77;
                      v92[18] = v78;
                      v92[19] = (__int64)v79;
                      v92[20] = v80;
                      LOBYTE(v92[21]) = v227;
                      v130 = 281i64;
                      v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                      log_response__modelZsimulationZcompile95thread_u124(v92);
                      if ( !*v218 )
                      {
                        v130 = 282i64;
                        nimZeroMem_67(v93, 232i64);
                        v93[0] = v92[0];
                        v93[1] = v92[1];
                        v93[2] = v92[2];
                        v93[3] = v92[3];
                        v93[4] = v92[4];
                        v93[5] = v92[5];
                        v93[6] = v92[6];
                        v93[7] = v92[7];
                        v93[8] = v92[8];
                        v93[9] = v92[9];
                        v93[10] = v92[10];
                        v93[11] = v92[11];
                        v93[12] = v92[12];
                        v93[13] = v92[13];
                        v93[14] = v92[14];
                        v93[15] = v92[15];
                        v93[16] = v92[16];
                        v93[17] = v92[17];
                        v93[18] = v92[18];
                        v93[19] = v92[19];
                        v93[20] = v92[20];
                        v93[21] = v92[21];
                        v93[22] = v92[22];
                        v93[23] = v92[23];
                        v93[24] = v92[24];
                        v93[25] = v92[25];
                        v93[26] = v92[26];
                        v93[27] = v92[27];
                        v93[28] = v92[28];
                        v130 = 368i64;
                        v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\channels_builtin.nim";
                        eqwasMoved___modelZsimulationZcompile95thread_u2384(v92);
                        v130 = 282i64;
                        v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                        send__modelZsimulationZcompile95thread_u2355(
                          &response_channel__modelZsimulationZcompile95thread_u92,
                          v93);
                      }
                    }
                    else
                    {
                      dollar___modelZmodel95types_u521(v166, v143);
                      v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_69;
                      v37 = &TM__nTvHpEr8JHyxC5V4m579axA_59;
                      v34 = (_QWORD *)v166[0];
                      v35 = v166[1];
                      raiseFieldErrorStr(&v36, &v34);
                    }
                  }
                }
              }
              else
              {
                dollar___modelZmodel95types_u521(v160, v143);
                v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_61;
                v37 = &TM__nTvHpEr8JHyxC5V4m579axA_59;
                v34 = (_QWORD *)v160[0];
                v35 = v160[1];
                raiseFieldErrorStr(&v36, &v34);
              }
            }
          }
          else
          {
            dollar___modelZmodel95types_u521(v159, v143);
            v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_60;
            v37 = &TM__nTvHpEr8JHyxC5V4m579axA_59;
            v34 = (_QWORD *)v159[0];
            v35 = v159[1];
            raiseFieldErrorStr(&v36, &v34);
          }
        }
LABEL_200:
        v192 = *v218;
        *v218 = 0;
        v130 = 368i64;
        v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\channels_builtin.nim";
        eqdestroy___modelZsimulationZcompile95thread_u2387(v92);
        if ( !*v218 )
        {
          v130 = 1863i64;
          v131 = "D:\\TuringComplete_Phu\\model\\isa_spec\\assemble.nim";
          eqdestroy___modelZisa95specZassemble_u18444(&v44);
          v130 = 770i64;
          v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
          eqdestroy___modelZsimulationZcompile95thread_u3069(&v38);
          *v218 = v192;
          if ( !*v218 )
          {
LABEL_202:
            v130 = 284i64;
            v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
            if ( !v133 )
              goto LABEL_259;
            nimZeroMem_67(v93, 48i64);
            nimZeroMem_67(&v99, 24i64);
            nimZeroMem_67(&v98, 8i64);
            v130 = 285i64;
            v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
            if ( (v134 & 7) == 3i64 )
            {
              v99 = v141[0];
              v100 = v141[1];
              v101 = v141[2];
              if ( (v134 & 7) == 3i64 )
              {
                eqwasMoved___modelZsimulationZcompile95thread_u3663(v141);
                v130 = 767i64;
                v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                v25 = v99;
                v26 = v100;
                v27 = v101;
                v191 = len__modelZsimulationZcompile95thread_u2796(&v25);
                if ( !*v218 )
                {
                  v190 = 0i64;
                  v188 = v99 - 1;
                  v189 = v99 - 1;
                  v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                  v221 = 0i64;
                  v130 = 97i64;
                  while ( v221 <= v189 )
                  {
                    v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                    v190 = v221;
                    v130 = 769i64;
                    if ( v221 < 0 || v190 >= v99 )
                    {
LABEL_219:
                      raiseIndexError2(v190, v99 - 1);
                      break;
                    }
                    v187 = 0;
                    v187 = isFilled__pureZcollectionsZtables_u31_10(*(_QWORD *)(v100 + (v190 << 6) + 8));
                    if ( *v218 )
                      break;
                    if ( v187 == 1 )
                    {
                      v130 = 285i64;
                      v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                      if ( v190 < 0 )
                        goto LABEL_219;
                      if ( v190 >= v99 )
                        goto LABEL_219;
                      v98 = *(_QWORD *)(v100 + (v190 << 6) + 16);
                      v130 = 770i64;
                      v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                      if ( v190 >= v99 )
                        goto LABEL_219;
                      eqcopy___modelZsimulationZcompile95thread_u3072(v93, v100 + (v190 << 6) + 16 + 8);
                      v130 = 286i64;
                      v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                      v186 = 0;
                      v19 = a1[1];
                      v25 = *a1;
                      v26 = v19;
                      v27 = a1[2];
                      v186 = contains__modelZboardZmemory95manager_u622(&v25, v98);
                      if ( *v218 )
                        break;
                      if ( v186 == 1 )
                      {
                        v130 = 287i64;
                        v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                        v185 = 0i64;
                        v185 = X5BX5D___modelZboardZmemory95manager_u1131(a1, v98);
                        if ( *v218 )
                          break;
                        v130 = 770i64;
                        v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                        eqsink___modelZsimulationZcompile95thread_u3078(v185 + 80, v93);
                        eqwasMoved___modelZsimulationZcompile95thread_u3066(v93);
                      }
                      v130 = 771i64;
                      v184 = 0i64;
                      v25 = v99;
                      v26 = v100;
                      v27 = v101;
                      v184 = len__modelZsimulationZcompile95thread_u2796(&v25);
                      if ( *v218 )
                        break;
                      if ( v184 != v191 )
                      {
                        v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_72;
                        v37 = &TM__nTvHpEr8JHyxC5V4m579axA_26;
                        failedAssertImpl__stdZassertions_u234(&v36);
                        if ( *v218 )
                          break;
                      }
                    }
                    v130 = 102i64;
                    v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                    v97 = v221 + 1;
                    if ( __OFADD__(1i64, v221) )
                    {
                      raiseOverflow();
                      break;
                    }
                    v221 = v97;
                  }
                }
              }
              else
              {
                dollar___modelZmodel95types_u521(v168, v134);
                v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_71;
                v37 = &TM__nTvHpEr8JHyxC5V4m579axA_46;
                v34 = (_QWORD *)v168[0];
                v35 = v168[1];
                raiseFieldErrorStr(&v36, &v34);
              }
            }
            else
            {
              dollar___modelZmodel95types_u521(v167, v134);
              v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_70;
              v37 = &TM__nTvHpEr8JHyxC5V4m579axA_46;
              v34 = (_QWORD *)v167[0];
              v35 = v167[1];
              raiseFieldErrorStr(&v36, &v34);
            }
            v130 = 285i64;
            v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
            eqdestroy___modelZsimulationZcompile95thread_u3666(&v99);
            v130 = 770i64;
            v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
            eqdestroy___modelZsimulationZcompile95thread_u3069(v93);
            if ( !*v218 )
            {
              nimZeroMem_67(v93, 168i64);
              nimZeroMem_67(&v96, 8i64);
              v130 = 767i64;
              v20 = a1[1];
              v25 = *a1;
              v26 = v20;
              v27 = a1[2];
              v183 = len__modelZboardZmemory95manager_u2711(&v25);
              if ( !*v218 )
              {
                v182 = 0i64;
                v181 = 0i64;
                v130 = 768i64;
                v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                v180 = *a1 - 1;
                v181 = v180;
                v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                v220 = 0i64;
                v130 = 97i64;
                while ( 1 )
                {
                  if ( v220 > v181 )
                    goto LABEL_258;
                  v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                  v182 = v220;
                  v130 = 769i64;
                  if ( v220 < 0 || v182 >= *a1 )
                  {
LABEL_243:
                    raiseIndexError2(v182, *a1 - 1);
                    goto LABEL_258;
                  }
                  v179 = 0;
                  v179 = isFilled__pureZcollectionsZtables_u31_10(*(_QWORD *)(a1[1] + 184 * v182 + 8));
                  if ( *v218 )
                    goto LABEL_258;
                  if ( v179 == 1 )
                    break;
LABEL_255:
                  v130 = 102i64;
                  v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                  v95 = v220 + 1;
                  if ( __OFADD__(1i64, v220) )
                  {
                    raiseOverflow();
                    goto LABEL_258;
                  }
                  v220 = v95;
                }
                v130 = 289i64;
                v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                if ( v182 < 0 )
                  goto LABEL_243;
                if ( v182 >= *a1 )
                  goto LABEL_243;
                v96 = *(_QWORD *)(a1[1] + 184 * v182 + 16);
                v130 = 112i64;
                v131 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
                if ( v182 >= *a1 )
                  goto LABEL_243;
                eqcopy___modelZboardZmemory95manager_u229(v93, a1[1] + 184 * v182 + 16 + 8);
                nimZeroMem_67(v92, 144i64);
                v130 = 290i64;
                v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                v178 = get_init_data__modelZboardZmemory95manager_u326(v93);
                if ( !*v218 )
                {
                  v130 = 291i64;
                  if ( !v178 )
                  {
                    v130 = 1863i64;
                    v131 = "D:\\TuringComplete_Phu\\model\\isa_spec\\assemble.nim";
                    eqdestroy___modelZisa95specZassemble_u18444(v92);
                    v130 = 292i64;
                    v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                    goto LABEL_252;
                  }
                  v130 = 294i64;
                  if ( v178 != 1 )
                  {
                    v130 = 1863i64;
                    v131 = "D:\\TuringComplete_Phu\\model\\isa_spec\\assemble.nim";
                    eqdestroy___modelZisa95specZassemble_u18444(v92);
                    v130 = 295i64;
                    v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                    goto LABEL_252;
                  }
                  v130 = 297i64;
                  v36 = (_QWORD *)v93[12];
                  v37 = (_QWORD *)v93[13];
                  v34 = (_QWORD *)v93[14];
                  v35 = v93[15];
                  v32 = (_QWORD *)v93[10];
                  v33 = v93[11];
                  compile_asm__modelZsimulationZcompile95thread_u135(
                    (unsigned int)&v36,
                    (unsigned int)&v34,
                    (unsigned int)&v32,
                    (_DWORD)a1 + 24,
                    (__int64)v92);
                  if ( !*v218 )
                  {
                    v130 = 302i64;
                    v36 = (_QWORD *)v92[0];
                    v37 = (_QWORD *)v92[1];
                    reload_reset_data__modelZboardZmemory95manager_u296(v96, v93, &v36);
                  }
                }
                v130 = 1863i64;
                v131 = "D:\\TuringComplete_Phu\\model\\isa_spec\\assemble.nim";
                eqdestroy___modelZisa95specZassemble_u18444(v92);
                if ( *v218 )
                  goto LABEL_258;
LABEL_252:
                v130 = 771i64;
                v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                v177 = 0i64;
                v21 = a1[1];
                v25 = *a1;
                v26 = v21;
                v27 = a1[2];
                v177 = len__modelZboardZmemory95manager_u2711(&v25);
                if ( *v218 )
                  goto LABEL_258;
                if ( v177 != v183 )
                {
                  v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_74;
                  v37 = &TM__nTvHpEr8JHyxC5V4m579axA_26;
                  failedAssertImpl__stdZassertions_u234(&v36);
                  if ( *v218 )
                    goto LABEL_258;
                }
                goto LABEL_255;
              }
LABEL_258:
              v130 = 112i64;
              v131 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
              eqdestroy___modelZboardZmemory95manager_u226(v93);
              if ( !*v218 )
              {
LABEL_259:
                v130 = 304i64;
                v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                if ( v228 == 1 )
                {
                  v176 = 0i64;
                  v130 = 831i64;
                  v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                  v22 = a1[1];
                  v25 = *a1;
                  v26 = v22;
                  v27 = a1[2];
                  v175 = len__modelZboardZmemory95manager_u2711(&v25);
                  if ( !*v218 )
                  {
                    v174 = 0i64;
                    v173 = 0i64;
                    v130 = 832i64;
                    v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                    v172 = *a1 - 1;
                    v173 = v172;
                    v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                    v219 = 0i64;
                    v130 = 97i64;
                    while ( v219 <= v173 )
                    {
                      v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                      v174 = v219;
                      v130 = 833i64;
                      if ( v219 < 0 || v174 >= *a1 )
                      {
LABEL_265:
                        raiseIndexError2(v174, *a1 - 1);
                        break;
                      }
                      v171 = 0;
                      v171 = isFilled__pureZcollectionsZtables_u31_10(*(_QWORD *)(a1[1] + 184 * v174 + 8));
                      if ( *v218 )
                        break;
                      if ( v171 == 1 )
                      {
                        v130 = 305i64;
                        v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                        if ( v174 < 0 || v174 >= *a1 )
                          goto LABEL_265;
                        v176 = a1[1] + 184 * v174 + 16 + 8;
                        v130 = 306i64;
                        v170 = get_init_data__modelZboardZmemory95manager_u326(v176);
                        if ( *v218 )
                          break;
                        v130 = 307i64;
                        if ( v170 == 2 || v170 == 4 || v170 == 5 )
                        {
                          v130 = 310i64;
                          if ( *(_BYTE *)(v176 + 160) )
                          {
                            v130 = 311i64;
                            store_buffer__modelZboardZmemory95manager_u2619(v176);
                            if ( *v218 )
                              break;
                          }
                        }
                        else
                        {
                          v130 = 308i64;
                        }
                        v130 = 835i64;
                        v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                        v169 = 0i64;
                        v23 = a1[1];
                        v25 = *a1;
                        v26 = v23;
                        v27 = a1[2];
                        v169 = len__modelZboardZmemory95manager_u2711(&v25);
                        if ( *v218 )
                          break;
                        if ( v169 != v175 )
                        {
                          v36 = (_QWORD *)TM__nTvHpEr8JHyxC5V4m579axA_77;
                          v37 = &TM__nTvHpEr8JHyxC5V4m579axA_76;
                          failedAssertImpl__stdZassertions_u234(&v36);
                          if ( *v218 )
                            break;
                        }
                      }
                      v130 = 102i64;
                      v131 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                      v94 = v219 + 1;
                      if ( __OFADD__(1i64, v219) )
                      {
                        raiseOverflow();
                        break;
                      }
                      v219 = v94;
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
LABEL_284:
  v130 = 326i64;
  v131 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  eqdestroy___modelZsimulationZpreorder_u8400(&v133);
  eqdestroy___modelZsimulationZpreorder_u8400(&v142);
  v130 = 90i64;
  v131 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
  eqdestroy___modelZsimulationZcompile95thread_u3488(v147);
  return popFrame_89();
}
