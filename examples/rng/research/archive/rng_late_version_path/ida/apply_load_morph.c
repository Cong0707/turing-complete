// address: 0x14059f111-0x1405a19fb
// name: apply_load_morph__modelZutilities_u2304
__int64 __fastcall apply_load_morph__modelZutilities_u2304(__int64 *a1, __int64 *a2, __int64 a3)
{
  __int64 v3; // rax
  __int64 v4; // rdx
  _QWORD *v5; // rdx
  _QWORD *v6; // rdx
  _QWORD *v7; // rdx
  __int64 v8; // rdx
  _QWORD *v9; // rdx
  _QWORD *v10; // rdx
  __int64 v11; // rdx
  __int64 v12; // r9
  __int64 v13; // rcx
  __int64 v15[2]; // [rsp+A0h] [rbp+20h] BYREF
  __int64 v16[2]; // [rsp+B0h] [rbp+30h] BYREF
  __int64 v17[4]; // [rsp+C0h] [rbp+40h] BYREF
  __int64 v18[4]; // [rsp+E0h] [rbp+60h] BYREF
  __int64 v19; // [rsp+100h] [rbp+80h] BYREF
  __int64 v20; // [rsp+108h] [rbp+88h]
  __int64 v21; // [rsp+110h] [rbp+90h]
  __int64 v22; // [rsp+120h] [rbp+A0h] BYREF
  __int64 v23; // [rsp+128h] [rbp+A8h]
  __int64 v24; // [rsp+130h] [rbp+B0h]
  __int64 v25; // [rsp+140h] [rbp+C0h] BYREF
  void *v26; // [rsp+148h] [rbp+C8h]
  __int64 v27; // [rsp+150h] [rbp+D0h] BYREF
  _QWORD *v28; // [rsp+158h] [rbp+D8h]
  __int64 v29; // [rsp+160h] [rbp+E0h]
  _QWORD *v30; // [rsp+168h] [rbp+E8h]
  unsigned __int8 v31[2]; // [rsp+170h] [rbp+F0h] BYREF
  unsigned int v32; // [rsp+172h] [rbp+F2h]
  char v33; // [rsp+176h] [rbp+F6h]
  __int64 v34; // [rsp+178h] [rbp+F8h]
  __int64 v35; // [rsp+180h] [rbp+100h]
  __int64 v36; // [rsp+188h] [rbp+108h]
  __int64 v37; // [rsp+190h] [rbp+110h]
  __int64 v38; // [rsp+198h] [rbp+118h]
  __int64 v39; // [rsp+1A0h] [rbp+120h]
  __int64 v40; // [rsp+1A8h] [rbp+128h]
  __int64 v41; // [rsp+1B0h] [rbp+130h]
  __int64 v42; // [rsp+1B8h] [rbp+138h]
  __int64 v43; // [rsp+1C0h] [rbp+140h]
  __int64 v44; // [rsp+1C8h] [rbp+148h]
  __int64 v45; // [rsp+1D0h] [rbp+150h]
  __int64 v46; // [rsp+1D8h] [rbp+158h]
  __int64 v47; // [rsp+218h] [rbp+198h]
  __int64 v48; // [rsp+220h] [rbp+1A0h]
  __int64 v49; // [rsp+230h] [rbp+1B0h]
  _QWORD *v50; // [rsp+238h] [rbp+1B8h]
  __int64 v51; // [rsp+240h] [rbp+1C0h]
  void *v52; // [rsp+248h] [rbp+1C8h]
  __int64 v53; // [rsp+250h] [rbp+1D0h]
  __int64 v54; // [rsp+260h] [rbp+1E0h]
  __int64 v55; // [rsp+268h] [rbp+1E8h]
  __int64 v56; // [rsp+2E0h] [rbp+260h]
  __int64 v57; // [rsp+2E8h] [rbp+268h]
  __int64 v58; // [rsp+2F0h] [rbp+270h]
  __int64 v59; // [rsp+2F8h] [rbp+278h]
  __int64 v60; // [rsp+300h] [rbp+280h]
  __int64 v61; // [rsp+308h] [rbp+288h]
  __int64 v62; // [rsp+310h] [rbp+290h]
  char v63; // [rsp+348h] [rbp+2C8h]
  __int64 v64; // [rsp+350h] [rbp+2D0h]
  __int64 v65; // [rsp+358h] [rbp+2D8h]
  __int64 v66; // [rsp+360h] [rbp+2E0h]
  __int64 v67; // [rsp+3A0h] [rbp+320h]
  __int64 v68; // [rsp+3A8h] [rbp+328h]
  __int64 v69; // [rsp+3B0h] [rbp+330h]
  __int64 v70; // [rsp+3C0h] [rbp+340h] BYREF
  __int64 v71; // [rsp+3C8h] [rbp+348h]
  __int64 v72; // [rsp+3D0h] [rbp+350h]
  __int64 v73; // [rsp+3D8h] [rbp+358h]
  __int64 v74; // [rsp+3E0h] [rbp+360h] BYREF
  __int64 v75; // [rsp+3E8h] [rbp+368h]
  __int64 v76; // [rsp+3F0h] [rbp+370h]
  __int64 v77; // [rsp+3F8h] [rbp+378h] BYREF
  __int64 v78; // [rsp+400h] [rbp+380h] BYREF
  _QWORD *v79; // [rsp+408h] [rbp+388h]
  __int64 v80[2]; // [rsp+410h] [rbp+390h] BYREF
  __int64 v81; // [rsp+420h] [rbp+3A0h]
  _QWORD *v82; // [rsp+428h] [rbp+3A8h]
  __int64 v83; // [rsp+430h] [rbp+3B0h] BYREF
  _QWORD *v84; // [rsp+438h] [rbp+3B8h]
  __int64 v85[4]; // [rsp+440h] [rbp+3C0h] BYREF
  __int64 v86; // [rsp+460h] [rbp+3E0h] BYREF
  __int64 v87; // [rsp+468h] [rbp+3E8h]
  __int64 v88; // [rsp+470h] [rbp+3F0h] BYREF
  __int64 v89; // [rsp+478h] [rbp+3F8h]
  __int64 v90[4]; // [rsp+480h] [rbp+400h] BYREF
  __int64 v91; // [rsp+4A0h] [rbp+420h] BYREF
  __int64 v92; // [rsp+4A8h] [rbp+428h]
  __int64 v93; // [rsp+4B8h] [rbp+438h] BYREF
  __int64 v94; // [rsp+4C0h] [rbp+440h] BYREF
  _QWORD *v95; // [rsp+4C8h] [rbp+448h]
  __int64 v96; // [rsp+4D0h] [rbp+450h] BYREF
  _QWORD *v97; // [rsp+4D8h] [rbp+458h]
  __int64 v98; // [rsp+4E0h] [rbp+460h]
  _QWORD *v99; // [rsp+4E8h] [rbp+468h]
  __int64 v100; // [rsp+4F0h] [rbp+470h]
  _QWORD *v101; // [rsp+4F8h] [rbp+478h]
  __int64 v102; // [rsp+500h] [rbp+480h] BYREF
  _QWORD *v103; // [rsp+508h] [rbp+488h]
  char v104[8]; // [rsp+510h] [rbp+490h] BYREF
  const char *v105; // [rsp+518h] [rbp+498h]
  __int64 v106; // [rsp+520h] [rbp+4A0h]
  const char *v107; // [rsp+528h] [rbp+4A8h]
  __int16 v108; // [rsp+530h] [rbp+4B0h]
  __int64 v109[4]; // [rsp+540h] [rbp+4C0h] BYREF
  __int64 v110; // [rsp+560h] [rbp+4E0h] BYREF
  __int64 v111; // [rsp+568h] [rbp+4E8h]
  __int64 v112; // [rsp+570h] [rbp+4F0h]
  __int64 v113; // [rsp+580h] [rbp+500h] BYREF
  __int64 v114; // [rsp+588h] [rbp+508h]
  __int64 v115; // [rsp+590h] [rbp+510h]
  char v116[8]; // [rsp+5A0h] [rbp+520h] BYREF
  __int64 v117; // [rsp+5A8h] [rbp+528h]
  __int64 v118; // [rsp+5B0h] [rbp+530h]
  __int64 v119; // [rsp+A68h] [rbp+9E8h]
  __int64 v120; // [rsp+A70h] [rbp+9F0h]
  char v121; // [rsp+A7Fh] [rbp+9FFh]
  __int64 v122; // [rsp+A80h] [rbp+A00h]
  __int64 v123; // [rsp+A88h] [rbp+A08h]
  __int64 v124; // [rsp+A90h] [rbp+A10h]
  __int64 v125; // [rsp+A98h] [rbp+A18h]
  __int64 v126; // [rsp+AA0h] [rbp+A20h]
  char v127; // [rsp+AAFh] [rbp+A2Fh]
  __int64 v128; // [rsp+AB0h] [rbp+A30h]
  char v129; // [rsp+ABFh] [rbp+A3Fh]
  __int64 v130; // [rsp+AC0h] [rbp+A40h]
  __int64 v131; // [rsp+AC8h] [rbp+A48h]
  __int64 v132; // [rsp+AD0h] [rbp+A50h]
  __int64 v133; // [rsp+AD8h] [rbp+A58h]
  unsigned __int8 v134; // [rsp+AE6h] [rbp+A66h]
  char v135; // [rsp+AE7h] [rbp+A67h]
  __int64 v136; // [rsp+AE8h] [rbp+A68h]
  __int64 v137; // [rsp+AF0h] [rbp+A70h]
  __int64 v138; // [rsp+AF8h] [rbp+A78h]
  __int64 v139; // [rsp+B00h] [rbp+A80h]
  __int64 v140; // [rsp+B08h] [rbp+A88h]
  __int64 v141; // [rsp+B10h] [rbp+A90h]
  __int64 v142; // [rsp+B18h] [rbp+A98h]
  char v143; // [rsp+B25h] [rbp+AA5h]
  char v144; // [rsp+B26h] [rbp+AA6h]
  char v145; // [rsp+B27h] [rbp+AA7h]
  __int64 v146; // [rsp+B28h] [rbp+AA8h]
  __int64 v147; // [rsp+B30h] [rbp+AB0h]
  __int64 v148; // [rsp+B38h] [rbp+AB8h]
  __int64 v149; // [rsp+B40h] [rbp+AC0h]
  unsigned __int8 v150; // [rsp+B4Fh] [rbp+ACFh]
  __int64 v151; // [rsp+B50h] [rbp+AD0h]
  __int64 v152; // [rsp+B58h] [rbp+AD8h]
  __int64 v153; // [rsp+B60h] [rbp+AE0h]
  _BYTE *v154; // [rsp+B68h] [rbp+AE8h]
  __int64 v155; // [rsp+B70h] [rbp+AF0h]
  __int64 v156; // [rsp+B78h] [rbp+AF8h]
  __int64 v157; // [rsp+B80h] [rbp+B00h]
  __int64 v158; // [rsp+B88h] [rbp+B08h]
  __int64 v159; // [rsp+B90h] [rbp+B10h]
  bool v160; // [rsp+B9Fh] [rbp+B1Fh]

  v3 = *a2;
  v4 = a2[1];
  v29 = v3;
  v30 = (_QWORD *)v4;
  v105 = "apply_load_morph";
  v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  v106 = 0i64;
  v108 = 0;
  nimFrame_145(v104);
  v154 = (_BYTE *)nimErrorFlag_141();
  nimZeroMem_118(v116, 1224i64);
  nimZeroMem_118(&v113, 24i64);
  nimZeroMem_118(&v110, 24i64);
  nimZeroMem_118(v109, 24i64);
  v106 = 205i64;
  if ( *(_BYTE *)refptr_dev_mode__modelZmodel95types_u727 != 1 )
  {
    v106 = 210i64;
    v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
    v160 = 0;
    v160 = *(_BYTE *)(a3 + 64) != 4;
    if ( v160 )
    {
      v27 = v29;
      v28 = v30;
      v25 = TM__8FyyixzftvDEeBWCL79bP9aA_126;
      v26 = &TM__8FyyixzftvDEeBWCL79bP9aA_100;
      v160 = (unsigned __int8)eqStrings_19(&v27, &v25) == 0;
    }
    if ( v160 )
    {
      v102 = 0i64;
      v103 = 0i64;
      v100 = 0i64;
      v101 = 0i64;
      v98 = 0i64;
      v99 = 0i64;
      v106 = 213i64;
      v96 = 0i64;
      v97 = 0i64;
      rawNewString(&v27, *refptr_campaign_name__modelZmodel95types_u826 + v29 + 14);
      v96 = v27;
      v97 = v28;
      v5 = (_QWORD *)refptr_campaign_name__modelZmodel95types_u826[1];
      v27 = *refptr_campaign_name__modelZmodel95types_u826;
      v28 = v5;
      appendString_73(&v96, &v27);
      v27 = TM__8FyyixzftvDEeBWCL79bP9aA_127;
      v28 = &TM__8FyyixzftvDEeBWCL79bP9aA_63;
      appendString_73(&v96, &v27);
      v27 = v29;
      v28 = v30;
      appendString_73(&v96, &v27);
      v27 = TM__8FyyixzftvDEeBWCL79bP9aA_128;
      v28 = &TM__8FyyixzftvDEeBWCL79bP9aA_94;
      appendString_73(&v96, &v27);
      v100 = v96;
      v101 = v97;
      v106 = 214i64;
      v94 = 0i64;
      v95 = 0i64;
      rawNewString(&v27, *(_QWORD *)(a3 + 48) + 13i64);
      v94 = v27;
      v95 = v28;
      v6 = *(_QWORD **)(a3 + 56);
      v27 = *(_QWORD *)(a3 + 48);
      v28 = v6;
      appendString_73(&v94, &v27);
      v27 = TM__8FyyixzftvDEeBWCL79bP9aA_129;
      v28 = &TM__8FyyixzftvDEeBWCL79bP9aA_94;
      appendString_73(&v94, &v27);
      v98 = v94;
      v99 = v95;
      v106 = 212i64;
      v27 = v100;
      v28 = v101;
      v25 = v94;
      v26 = v95;
      file_get_bytes__modelZsave95mongerZsave95monger_u38(&v102, &v27, &v25);
      if ( !*v154 )
      {
        v106 = 216i64;
        v27 = v102;
        v28 = v103;
        parse_state__modelZsave95mongerZsave95monger_u73(&v27, 0, 0, (__int64)v116);
      }
      v106 = 394i64;
      v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v99 && (*v99 & 0x4000000000000000i64) == 0 )
        deallocShared(v99);
      if ( v101 && (*v101 & 0x4000000000000000i64) == 0 )
        deallocShared(v101);
      v106 = 1772i64;
      v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\times.nim";
      v27 = v102;
      v28 = v103;
      eqdestroy___pureZtimes_u2668(&v27);
      if ( *v154 )
        goto LABEL_161;
    }
    v153 = 0i64;
    v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    v159 = 0i64;
    v152 = v117;
    v151 = v117;
    v106 = 251i64;
    while ( v159 < v151 )
    {
      v106 = 243i64;
      v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
      if ( v159 < 0 || v159 >= v117 )
      {
        raiseIndexError2(v159, v117 - 1);
        goto LABEL_161;
      }
      v153 = v118 + 560 * v159 + 8;
      v150 = 0;
      nimZeroMem_118(&v93, 8i64);
      v91 = 0i64;
      v92 = 0i64;
      nimZeroMem_118(v90, 24i64);
      v88 = 0i64;
      v89 = 0i64;
      v86 = 0i64;
      v87 = 0i64;
      nimZeroMem_118(v85, 24i64);
      v106 = 245i64;
      if ( *(_BYTE *)(v153 + 472) )
      {
        v106 = 248i64;
        v150 = *(_BYTE *)v153;
        v31[0] = v150;
        v106 = 184i64;
        v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
        v93 = eqdup___modelZsave95mongerZcommon_u182(*(_QWORD *)(v153 + 224));
        v34 = v93;
        v106 = 34i64;
        v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        v7 = *(_QWORD **)(v153 + 248);
        v27 = *(_QWORD *)(v153 + 240);
        v28 = v7;
        eqdup___modelZsave95mongerZversionsZv0_u302(&v91, &v27);
        v35 = v91;
        v36 = v92;
        v106 = 23i64;
        v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v12.nim";
        v8 = *(_QWORD *)(v153 + 376);
        v19 = *(_QWORD *)(v153 + 368);
        v20 = v8;
        v21 = *(_QWORD *)(v153 + 384);
        eqdup___modelZsave95mongerZversionsZv12_u295(&v22, &v19);
        v90[0] = v22;
        v90[1] = v23;
        v90[2] = v24;
        v37 = v22;
        v38 = v23;
        v39 = v24;
        v106 = 1699i64;
        v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v9 = *(_QWORD **)(v153 + 200);
        v27 = *(_QWORD *)(v153 + 192);
        v28 = v9;
        eqdup___system_u2664(&v88, &v27);
        v40 = v88;
        v41 = v89;
        v106 = 119i64;
        v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
        v10 = *(_QWORD **)(v153 + 176);
        v27 = *(_QWORD *)(v153 + 168);
        v28 = v10;
        eqdup___modelZsave95mongerZserialize_u461(&v86, &v27);
        v42 = v86;
        v43 = v87;
        v106 = 123i64;
        v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
        v11 = *(_QWORD *)(v153 + 432);
        v22 = *(_QWORD *)(v153 + 424);
        v23 = v11;
        v24 = *(_QWORD *)(v153 + 440);
        eqdup___modelZsave95mongerZsave95monger_u880(&v19, &v22);
        v85[0] = v19;
        v85[1] = v20;
        v85[2] = v21;
        v44 = v19;
        v45 = v20;
        v46 = v21;
        v106 = 247i64;
        v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
        X5BX5Deq___modelZutilities_u2446(&v113, *(_QWORD *)(v153 + 8), v31);
        if ( *v154 )
          goto LABEL_161;
      }
      else
      {
        v106 = 246i64;
      }
      v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      ++v159;
      v106 = 254i64;
      v149 = v117;
      if ( v117 != v151 )
      {
        v27 = TM__8FyyixzftvDEeBWCL79bP9aA_130;
        v28 = &TM__8FyyixzftvDEeBWCL79bP9aA_31;
        failedAssertImpl__stdZassertions_u234(&v27);
        if ( *v154 )
          goto LABEL_161;
      }
    }
    nimZeroMem_118(v31, 560i64);
    v148 = 0i64;
    v158 = 0i64;
    v106 = 183i64;
    v147 = *a1;
    v146 = v147;
    v106 = 184i64;
    while ( v158 < v146 )
    {
      v148 = v158;
      v106 = 34i64;
      v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      if ( v158 < 0 || v158 >= *a1 )
      {
        raiseIndexError2(v158, *a1 - 1);
        break;
      }
      eqcopy___modelZsave95mongerZversionsZv0_u148(v31, a1[1] + 560 * v158 + 8);
      v106 = 258i64;
      v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
      v145 = 0;
      v19 = v109[0];
      v20 = v109[1];
      v21 = v109[2];
      v145 = contains__modelZsave95mongerZsave95monger_u1046(&v19, v34);
      if ( *v154 )
        break;
      if ( v145 == 1 )
      {
        v83 = 0i64;
        v84 = 0i64;
        v81 = 0i64;
        v82 = 0i64;
        v106 = 259i64;
        v78 = 0i64;
        v79 = 0i64;
        dollar___modelZsave95mongerZcommon_u132(&v83, v31[0]);
        rawNewString(&v27, v83 + 48);
        v78 = v27;
        v79 = v28;
        v27 = TM__8FyyixzftvDEeBWCL79bP9aA_132;
        v28 = &TM__8FyyixzftvDEeBWCL79bP9aA_131;
        appendString_73(&v78, &v27);
        v27 = v83;
        v28 = v84;
        appendString_73(&v78, &v27);
        v81 = v78;
        v82 = v79;
        v80[0] = v78;
        v80[1] = (__int64)v79;
        log__globals_u23(v80, 1i64);
        if ( !*v154 )
        {
          v106 = 260i64;
          board_delete_component__modelZboardZboard_u5664(a1, v148);
          if ( !*v154 )
          {
            v106 = 394i64;
            v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v82 && (*v82 & 0x4000000000000000i64) == 0 )
              deallocShared(v82);
            if ( v84 && (*v84 & 0x4000000000000000i64) == 0 )
              deallocShared(v84);
            v106 = 261i64;
            v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
            goto LABEL_69;
          }
        }
        v106 = 394i64;
        v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v82 && (*v82 & 0x4000000000000000i64) == 0 )
          deallocShared(v82);
        if ( v84 && (*v84 & 0x4000000000000000i64) == 0 )
          deallocShared(v84);
        if ( *v154 )
          break;
      }
      v106 = 262i64;
      v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
      incl__modelZsave95mongerZsave95monger_u1438(v109, v34);
      if ( *v154 )
        break;
      v106 = 264i64;
      if ( v63 )
      {
        v106 = 267i64;
        v144 = 0;
        v12 = *(_QWORD *)(a3 + 480);
        if ( *(_QWORD *)(a3 + 488) )
          v13 = *(_QWORD *)(a3 + 488) + 8i64;
        else
          v13 = 0i64;
        v27 = v49;
        v28 = v50;
        v144 = contains__stdZenumutils_u50_6(v13, v12, &v27);
        if ( v144 != 1 )
        {
          v106 = 271i64;
          v143 = 0;
          v19 = v113;
          v20 = v114;
          v21 = v115;
          v143 = contains__modelZutilities_u4136(&v19, v34);
          if ( *v154 )
            break;
          if ( v143 )
          {
            v106 = 278i64;
            v142 = 0i64;
            v142 = X5BX5D___modelZutilities_u4265(&v113, v34);
            if ( *v154 )
              break;
            v106 = 277i64;
            copy_overwrite_data__modelZutilities_u2398(a1, v148, v142);
            if ( *v154 )
              break;
            v106 = 280i64;
            del__modelZutilities_u4390(&v113, v34);
            if ( *v154 )
              break;
          }
          else
          {
            v106 = 273i64;
            if ( v148 < 0 || v148 >= *a1 )
            {
              raiseIndexError2(v148, *a1 - 1);
              break;
            }
            X5BX5Deq___modelZsimulationZpreorder_u11513(&v110, *(_QWORD *)(a1[1] + 560 * v148 + 16), v148);
            if ( *v154 )
              break;
          }
        }
        else
        {
          v106 = 268i64;
          board_delete_component__modelZboardZboard_u5664(a1, v148);
          if ( *v154 )
            break;
          v106 = 269i64;
        }
      }
      else
      {
        v106 = 265i64;
      }
LABEL_69:
      v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      ++v158;
      v106 = 187i64;
      v141 = *a1;
      if ( v141 != v146 )
      {
        v27 = TM__8FyyixzftvDEeBWCL79bP9aA_135;
        v28 = &TM__8FyyixzftvDEeBWCL79bP9aA_134;
        failedAssertImpl__stdZassertions_u234(&v27);
        if ( *v154 )
          break;
      }
    }
    v106 = 34i64;
    v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    eqdestroy___modelZsave95mongerZversionsZv0_u145(v31);
    if ( *v154 )
      goto LABEL_161;
    nimZeroMem_118(&v77, 8i64);
    v140 = 0i64;
    v106 = 767i64;
    v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
    v19 = v110;
    v20 = v111;
    v21 = v112;
    v139 = len__modelZutilities_u4848(&v19);
    if ( *v154 )
      goto LABEL_161;
    v138 = 0i64;
    v136 = v110 - 1;
    v137 = v110 - 1;
    v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v157 = 0i64;
    v106 = 97i64;
    while ( v157 <= v137 )
    {
      v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
      v138 = v157;
      v106 = 769i64;
      if ( v157 < 0 || v138 >= v110 )
      {
LABEL_86:
        raiseIndexError2(v138, v110 - 1);
        goto LABEL_161;
      }
      v135 = 0;
      v135 = isFilled__pureZcollectionsZtables_u31_18(*(_QWORD *)(v111 + 24 * v138 + 8));
      if ( *v154 )
        goto LABEL_161;
      if ( v135 == 1 )
      {
        v106 = 282i64;
        v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
        if ( v138 < 0 )
          goto LABEL_86;
        if ( v138 >= v110 )
          goto LABEL_86;
        v77 = *(_QWORD *)(v111 + 24 * v138 + 16);
        if ( v138 >= v110 )
          goto LABEL_86;
        v140 = *(_QWORD *)(v111 + 24 * v138 + 24);
        v106 = 283i64;
        if ( v140 < 0 || v140 >= *a1 )
        {
LABEL_132:
          raiseIndexError2(v140, *a1 - 1);
          goto LABEL_161;
        }
        v134 = *(_BYTE *)(a1[1] + 560 * v140 + 8);
        v106 = 284i64;
        v75 = *(_QWORD *)refptr_NO_ID__modelZsave95mongerZcommon_u3361;
        nimZeroMem_118(v31, 112i64);
        nimZeroMem_118(&v74, 8i64);
        v106 = 285i64;
        nimZeroMem_118(v31, 112i64);
        v106 = 767i64;
        v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
        v19 = v113;
        v20 = v114;
        v21 = v115;
        v133 = len__modelZutilities_u5160(&v19);
        if ( !*v154 )
        {
          v132 = 0i64;
          v130 = v113 - 1;
          v131 = v113 - 1;
          v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v156 = 0i64;
          v106 = 97i64;
          while ( v156 <= v131 )
          {
            v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
            v132 = v156;
            v106 = 769i64;
            if ( v156 < 0 || v132 >= v113 )
            {
LABEL_102:
              raiseIndexError2(v132, v113 - 1);
              break;
            }
            v129 = 0;
            v129 = isFilled__pureZcollectionsZtables_u31_18(*(_QWORD *)(v114 + (v132 << 7) + 8));
            if ( *v154 )
              break;
            if ( v129 == 1 )
            {
              v106 = 285i64;
              v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
              if ( v132 < 0 )
                goto LABEL_102;
              if ( v132 >= v113 )
                goto LABEL_102;
              v74 = *(_QWORD *)(v114 + (v132 << 7) + 16);
              v106 = 170i64;
              v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              if ( v132 >= v113 )
                goto LABEL_102;
              eqcopy___modelZutilities_u3552(v31, v114 + (v132 << 7) + 16 + 8);
              v106 = 286i64;
              v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
              if ( v134 == v31[0] )
              {
                v106 = 287i64;
                if ( v140 < 0 || v140 >= *a1 )
                {
                  raiseIndexError2(v140, *a1 - 1);
                  break;
                }
                *(_QWORD *)(a1[1] + 560 * v140 + 16) = v74;
                v106 = 288i64;
                copy_overwrite_data__modelZutilities_u2398(a1, v140, v31);
                if ( !*v154 )
                {
                  v75 = v74;
                  v106 = 170i64;
                  v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                  eqdestroy___modelZutilities_u3549(v31);
                  v106 = 290i64;
                  v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
                  goto LABEL_116;
                }
                break;
              }
              v106 = 771i64;
              v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
              v128 = 0i64;
              v19 = v113;
              v20 = v114;
              v21 = v115;
              v128 = len__modelZutilities_u5160(&v19);
              if ( *v154 )
                break;
              if ( v128 != v133 )
              {
                v27 = TM__8FyyixzftvDEeBWCL79bP9aA_136;
                v28 = &TM__8FyyixzftvDEeBWCL79bP9aA_56;
                failedAssertImpl__stdZassertions_u234(&v27);
                if ( *v154 )
                  break;
              }
            }
            v106 = 102i64;
            v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
            v73 = v156 + 1;
            if ( __OFADD__(1i64, v156) )
            {
              raiseOverflow();
              break;
            }
            v156 = v73;
          }
        }
        v106 = 170i64;
        v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        eqdestroy___modelZutilities_u3549(v31);
        if ( *v154 )
          goto LABEL_161;
LABEL_116:
        v106 = 292i64;
        v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
        v127 = 0;
        v127 = eqeq___modelZsave95mongerZversionsZv7_u353(v75, *(_QWORD *)refptr_NO_ID__modelZsave95mongerZcommon_u3361);
        if ( v127 )
        {
          v106 = 295i64;
          if ( v140 < 0 || v140 >= *a1 )
            goto LABEL_132;
          *(_BYTE *)(a1[1] + 560 * v140 + 480) = 0;
          v106 = 296i64;
          if ( v134 == 40
            || v134 > 0x3Bu && v134 <= 0x41u
            || v134 > 0x43u && v134 <= 0x46u
            || v134 > 0x48u && v134 <= 0x4Bu
            || v134 == 77 )
          {
            v106 = 297i64;
            if ( v140 < 0 || v140 >= *a1 )
              goto LABEL_132;
            *(_BYTE *)(a1[1] + 560 * v140 + 8) = 0;
          }
        }
        else
        {
          v106 = 293i64;
          del__modelZutilities_u4390(&v113, v75);
          if ( *v154 )
            goto LABEL_161;
        }
        v106 = 771i64;
        v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
        v126 = 0i64;
        v19 = v110;
        v20 = v111;
        v21 = v112;
        v126 = len__modelZutilities_u4848(&v19);
        if ( *v154 )
          goto LABEL_161;
        if ( v126 != v139 )
        {
          v27 = TM__8FyyixzftvDEeBWCL79bP9aA_138;
          v28 = &TM__8FyyixzftvDEeBWCL79bP9aA_56;
          failedAssertImpl__stdZassertions_u234(&v27);
          if ( *v154 )
            goto LABEL_161;
        }
      }
      v106 = 102i64;
      v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v76 = v157 + 1;
      if ( __OFADD__(1i64, v157) )
      {
        raiseOverflow();
        goto LABEL_161;
      }
      v157 = v76;
    }
    v106 = 299i64;
    v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
    v125 = 0i64;
    v19 = v113;
    v20 = v114;
    v21 = v115;
    v125 = len__modelZutilities_u5160(&v19);
    if ( *v154 || v125 <= 0 )
    {
LABEL_161:
      v106 = 160i64;
      v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
      eqdestroy___modelZsave95mongerZsave95monger_u2597(v109);
      v106 = 358i64;
      v107 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      eqdestroy___modelZsimulationZpreorder_u30636(&v110);
      v106 = 227i64;
      v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
      eqdestroy___modelZutilities_u5661(&v113);
      v106 = 121i64;
      v107 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
      eqdestroy___modelZboardZschematics_u1681(v116);
      return popFrame_145();
    }
    nimZeroMem_118(v31, 560i64);
    v124 = 0i64;
    v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    v155 = 0i64;
    v123 = v117;
    v122 = v117;
    v106 = 184i64;
    while ( 1 )
    {
      if ( v155 >= v122 )
      {
LABEL_160:
        v106 = 34i64;
        v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        eqdestroy___modelZsave95mongerZversionsZv0_u145(v31);
        goto LABEL_161;
      }
      v124 = v155;
      v106 = 34i64;
      v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      if ( v155 < 0 || v155 >= v117 )
      {
        raiseIndexError2(v155, v117 - 1);
        goto LABEL_160;
      }
      eqcopy___modelZsave95mongerZversionsZv0_u148(v31, v118 + 560 * v155 + 8);
      nimZeroMem_118(&v70, 24i64);
      v106 = 301i64;
      v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
      v121 = 0;
      v19 = v113;
      v20 = v114;
      v21 = v115;
      v121 = contains__modelZutilities_u4136(&v19, v34);
      if ( *v154 )
        goto LABEL_155;
      if ( v121 )
        break;
      v106 = 123i64;
      v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
      eqdestroy___modelZsave95mongerZsave95monger_u874(&v70);
      v106 = 302i64;
      v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
LABEL_156:
      v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      ++v155;
      v106 = 187i64;
      v119 = v117;
      if ( v117 != v122 )
      {
        v27 = TM__8FyyixzftvDEeBWCL79bP9aA_140;
        v28 = &TM__8FyyixzftvDEeBWCL79bP9aA_134;
        failedAssertImpl__stdZassertions_u234(&v27);
        if ( *v154 )
          goto LABEL_160;
      }
    }
    v67 = v56;
    v68 = v57;
    v69 = v58;
    v106 = 1065i64;
    v107 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    initTable__modelZboardZboard_u21177(&v19, 32i64);
    v70 = v19;
    v71 = v20;
    v72 = v21;
    if ( !*v154 )
    {
      v106 = 308i64;
      v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
      v120 = 0i64;
      v19 = v67;
      v20 = v68;
      v21 = v69;
      v27 = v49;
      v28 = v50;
      v25 = v51;
      v26 = v52;
      v22 = v64;
      v23 = v65;
      v24 = v66;
      v18[0] = v60;
      v18[1] = v61;
      v18[2] = v62;
      v17[0] = v70;
      v17[1] = v71;
      v17[2] = v72;
      v16[0] = v47;
      v16[1] = v48;
      v15[0] = v54;
      v15[1] = v55;
      v120 = board_add_component__modelZboardZboard_u21118(
               (__int64)a1,
               v31[0],
               &v19,
               v32,
               v33,
               v34,
               &v27,
               &v25,
               v59,
               v53,
               v63,
               &v22,
               v18,
               0i64,
               v17,
               v16,
               0,
               v15,
               0);
    }
LABEL_155:
    v106 = 123i64;
    v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
    eqdestroy___modelZsave95mongerZsave95monger_u874(&v70);
    if ( *v154 )
      goto LABEL_160;
    goto LABEL_156;
  }
  v106 = 160i64;
  v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
  eqdestroy___modelZsave95mongerZsave95monger_u2597(v109);
  v106 = 358i64;
  v107 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  eqdestroy___modelZsimulationZpreorder_u30636(&v110);
  v106 = 227i64;
  v107 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  eqdestroy___modelZutilities_u5661(&v113);
  v106 = 121i64;
  v107 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
  eqdestroy___modelZboardZschematics_u1681(v116);
  return popFrame_145();
}
