// address: 0x14027c2c6-0x14027e073
// name: load_schematic_raw__modelZboardZschematics_u34
__int64 __fastcall load_schematic_raw__modelZboardZschematics_u34(
        __int16 a1,
        __int64 *a2,
        char a3,
        __int64 a4,
        _QWORD *a5)
{
  _QWORD *v5; // rax
  __int64 v6; // rbx
  __int64 v7; // rbx
  __int64 v8; // rbx
  __int64 v9; // rbx
  __int64 v10; // rbx
  __int64 v11; // rbx
  bool v12; // dl
  bool v13; // dl
  __int64 v14; // rbx
  __int64 v15; // rbx
  __int64 v16; // rbx
  __int64 v17; // rbx
  __int64 v19[2]; // [rsp+A0h] [rbp+20h] BYREF
  __int64 v20[2]; // [rsp+B0h] [rbp+30h] BYREF
  __int64 v21[4]; // [rsp+C0h] [rbp+40h] BYREF
  __int64 v22[4]; // [rsp+E0h] [rbp+60h] BYREF
  __int64 v23[4]; // [rsp+100h] [rbp+80h] BYREF
  __int64 v24[2]; // [rsp+120h] [rbp+A0h] BYREF
  __int64 v25; // [rsp+130h] [rbp+B0h] BYREF
  void *v26; // [rsp+138h] [rbp+B8h]
  __int64 v27; // [rsp+140h] [rbp+C0h] BYREF
  __int64 v28; // [rsp+148h] [rbp+C8h]
  __int64 v29; // [rsp+150h] [rbp+D0h]
  __int64 v30[70]; // [rsp+160h] [rbp+E0h] BYREF
  __int64 v31[37]; // [rsp+390h] [rbp+310h] BYREF
  char v32; // [rsp+4B9h] [rbp+439h]
  char v33; // [rsp+4BAh] [rbp+43Ah]
  __int64 v34; // [rsp+8F8h] [rbp+878h] BYREF
  __int64 v35; // [rsp+900h] [rbp+880h]
  __int64 v36; // [rsp+938h] [rbp+8B8h]
  __int64 v37; // [rsp+940h] [rbp+8C0h]
  __int64 v38; // [rsp+948h] [rbp+8C8h]
  __int64 v39; // [rsp+950h] [rbp+8D0h]
  __int64 clamped_word_size__modelZboardZprototype95list_u4458; // [rsp+958h] [rbp+8D8h]
  __int64 v41; // [rsp+960h] [rbp+8E0h]
  __int64 v42; // [rsp+968h] [rbp+8E8h]
  __int64 v43; // [rsp+970h] [rbp+8F0h]
  int v44; // [rsp+984h] [rbp+904h]
  __int64 started; // [rsp+988h] [rbp+908h]
  __int64 v46; // [rsp+990h] [rbp+910h]
  __int64 v47; // [rsp+998h] [rbp+918h] BYREF
  char v48[8]; // [rsp+9A0h] [rbp+920h] BYREF
  const char *v49; // [rsp+9A8h] [rbp+928h]
  __int64 v50; // [rsp+9B0h] [rbp+930h]
  const char *v51; // [rsp+9B8h] [rbp+938h]
  __int16 v52; // [rsp+9C0h] [rbp+940h]
  __int64 v53[70]; // [rsp+9D0h] [rbp+950h] BYREF
  char v54[48]; // [rsp+C00h] [rbp+B80h] BYREF
  __int64 v55; // [rsp+C30h] [rbp+BB0h] BYREF
  __int64 v56; // [rsp+C38h] [rbp+BB8h]
  __int64 v57; // [rsp+C40h] [rbp+BC0h]
  __int64 v58; // [rsp+C48h] [rbp+BC8h]
  __int64 v59; // [rsp+C50h] [rbp+BD0h]
  __int64 v60; // [rsp+C58h] [rbp+BD8h]
  __int64 v61; // [rsp+C60h] [rbp+BE0h]
  __int64 v62; // [rsp+C68h] [rbp+BE8h]
  __int64 v63; // [rsp+C70h] [rbp+BF0h]
  __int64 v64; // [rsp+C78h] [rbp+BF8h]
  __int64 v65; // [rsp+C80h] [rbp+C00h]
  _QWORD *v66; // [rsp+C88h] [rbp+C08h]
  __int64 v67; // [rsp+C90h] [rbp+C10h]
  _QWORD *v68; // [rsp+C98h] [rbp+C18h]
  __int64 v69; // [rsp+CA0h] [rbp+C20h]
  _QWORD *v70; // [rsp+CA8h] [rbp+C28h]
  __int64 v71; // [rsp+CB0h] [rbp+C30h]
  char v72; // [rsp+CBFh] [rbp+C3Fh]
  __int64 v73; // [rsp+CC0h] [rbp+C40h]
  char v74; // [rsp+CCFh] [rbp+C4Fh]
  __int64 v75; // [rsp+CD0h] [rbp+C50h]
  _QWORD *v76; // [rsp+CD8h] [rbp+C58h]
  __int64 v77; // [rsp+CE0h] [rbp+C60h]
  __int64 v78; // [rsp+CE8h] [rbp+C68h]
  __int64 v79; // [rsp+CF0h] [rbp+C70h]
  __int64 v80; // [rsp+CF8h] [rbp+C78h]
  __int64 v81; // [rsp+D00h] [rbp+C80h]
  __int64 v82; // [rsp+D08h] [rbp+C88h]
  __int64 v83; // [rsp+D10h] [rbp+C90h]
  __int64 v84; // [rsp+D18h] [rbp+C98h]
  unsigned __int8 v85; // [rsp+D27h] [rbp+CA7h]
  __int64 v86; // [rsp+D28h] [rbp+CA8h]
  _QWORD *v87; // [rsp+D30h] [rbp+CB0h]
  __int64 v88; // [rsp+D38h] [rbp+CB8h]
  _QWORD *v89; // [rsp+D40h] [rbp+CC0h]
  __int64 v90; // [rsp+D48h] [rbp+CC8h]
  char v91; // [rsp+D57h] [rbp+CD7h]
  __int64 modelZboardZschematics_u244; // [rsp+D58h] [rbp+CD8h]
  char v93; // [rsp+D67h] [rbp+CE7h]
  __int64 v94; // [rsp+D68h] [rbp+CE8h]
  __int64 v95; // [rsp+D70h] [rbp+CF0h]
  __int64 v96; // [rsp+D78h] [rbp+CF8h]
  __int64 v97; // [rsp+D80h] [rbp+D00h]
  __int64 v98; // [rsp+D88h] [rbp+D08h]
  unsigned __int8 v99; // [rsp+D94h] [rbp+D14h]
  char v100; // [rsp+D95h] [rbp+D15h]
  char v101; // [rsp+D96h] [rbp+D16h]
  unsigned __int8 v102; // [rsp+D97h] [rbp+D17h]
  __int64 v103; // [rsp+D98h] [rbp+D18h]
  __int64 v104; // [rsp+DA0h] [rbp+D20h]
  __int64 v105; // [rsp+DA8h] [rbp+D28h]
  __int64 v106; // [rsp+DB0h] [rbp+D30h]
  char v107; // [rsp+DBFh] [rbp+D3Fh]
  __int64 v108; // [rsp+DC0h] [rbp+D40h]
  __int64 v109; // [rsp+DC8h] [rbp+D48h]
  __int64 v110; // [rsp+DD0h] [rbp+D50h]
  __int16 v111; // [rsp+DDEh] [rbp+D5Eh]
  _BYTE *v112; // [rsp+DE0h] [rbp+D60h]
  __int64 v113; // [rsp+DE8h] [rbp+D68h]
  __int64 v114; // [rsp+DF0h] [rbp+D70h]
  unsigned __int8 v115; // [rsp+DFFh] [rbp+D7Fh]
  __int64 v116; // [rsp+E00h] [rbp+D80h]
  __int64 v117; // [rsp+E08h] [rbp+D88h]

  v49 = "load_schematic_raw";
  v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
  v50 = 0i64;
  v52 = 0;
  nimFrame_75(v48);
  v112 = (_BYTE *)nimErrorFlag_73();
  nimZeroMem_55(a5, 72i64);
  nimZeroMem_55(&v55, 72i64);
  v111 = 0;
  nimZeroMem_55(v54, 48i64);
  v50 = 34i64;
  v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
  nimZeroMem_55(&v55, 72i64);
  v111 = a1;
  WORD1(v61) = a1;
  v55 = 1i64;
  v56 = newSeqPayload(1i64, 560i64, 8i64);
  nimZeroMem_55(v53, 560i64);
  nimZeroMem_55(&v53[10], 80i64);
  v53[11] = 1i64;
  nimZeroMem_55(&v53[12], 8i64);
  v53[12] = 256i64;
  LOBYTE(v53[13]) = 1;
  v53[14] = 1i64;
  nimZeroMem_55(&v53[15], 8i64);
  v53[15] = 256i64;
  LOBYTE(v53[16]) = 1;
  nimZeroMem_55(&v53[60], 24i64);
  LOBYTE(v53[60]) = 0;
  qmemcpy((void *)(v56 + 8), v53, 0x230ui64);
  v50 = 35i64;
  eqcopy___modelZboardZschematics_u1632(v54, a4);
  nimZeroMem_55(v30, 104i64);
  nimZeroMem_55(&v47, 8i64);
  nimZeroMem_55(v31, 104i64);
  v110 = 0i64;
  v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v117 = 0i64;
  v50 = 183i64;
  v109 = a2[4];
  v108 = v109;
  v50 = 184i64;
  while ( v117 < v108 )
  {
    v50 = 536i64;
    v51 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    v110 = v117;
    if ( v117 < 0 || v117 >= a2[4] )
    {
      raiseIndexError2(v117, a2[4] - 1);
      break;
    }
    v5 = (_QWORD *)(a2[5] + 104 * v117);
    v6 = v5[2];
    v31[0] = v5[1];
    v31[1] = v6;
    v7 = v5[4];
    v31[2] = v5[3];
    v31[3] = v7;
    v8 = v5[6];
    v31[4] = v5[5];
    v31[5] = v8;
    v9 = v5[8];
    v31[6] = v5[7];
    v31[7] = v9;
    v10 = v5[10];
    v31[8] = v5[9];
    v31[9] = v10;
    v11 = v5[12];
    v31[10] = v5[11];
    v31[11] = v11;
    v31[12] = v5[13];
    v47 = v110;
    v50 = 185i64;
    v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    eqcopy___modelZsave95mongerZcommon_u3692(v30, v31);
    v50 = 38i64;
    v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
    v107 = 0;
    v107 = is_tombstone__modelZsave95mongerZcommon_u4884(v30);
    if ( *v112 )
      break;
    if ( v107 != 1 )
    {
      v50 = 194i64;
      v51 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
      v46 = bits__modelZsave95mongerZcommon_u192(1i64);
      if ( *v112 )
        break;
      v50 = 40i64;
      v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
      v27 = v30[3];
      v28 = v30[4];
      v29 = v30[5];
      v25 = v30[1];
      v26 = (void *)v30[2];
      started = board_start_wire__modelZboardZboard_u6704(
                  (unsigned int)&v55,
                  (unsigned int)&v27,
                  BYTE2(v30[0]),
                  (unsigned int)&v25,
                  *(_QWORD *)refptr_INVALID_WIRE_ID__modelZsave95mongerZcommon_u3579,
                  v46);
      if ( *v112 )
        break;
    }
    else
    {
      v50 = 39i64;
    }
    v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v117;
    v50 = 187i64;
    v106 = a2[4];
    if ( v106 != v108 )
    {
      v25 = TM__DRGBjVoeyzCuYwSWCgAUCw_3;
      v26 = &TM__DRGBjVoeyzCuYwSWCgAUCw_2;
      failedAssertImpl__stdZassertions_u234(&v25);
      if ( *v112 )
        break;
    }
  }
  v50 = 185i64;
  eqdestroy___modelZsave95mongerZcommon_u3689(v30);
  if ( *v112 )
  {
LABEL_130:
    v50 = 35i64;
    v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
    eqdestroy___modelZboardZschematics_u1629(v54);
    v50 = 173i64;
    v51 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
    eqdestroy___modelZsave95mongerZsave95monger_u2637(&v55);
    return popFrame_75();
  }
  v50 = 42i64;
  v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
  if ( a3 == 3 || a3 == 5 || a3 == 6 )
  {
    v50 = 43i64;
    WORD1(v61) = 255;
  }
  nimZeroMem_55(v30, 560i64);
  v105 = 0i64;
  v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v116 = 0i64;
  v50 = 183i64;
  v104 = *a2;
  v103 = v104;
  v50 = 184i64;
  while ( v116 < v103 )
  {
    v50 = 45i64;
    v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
    v105 = v116;
    if ( v116 < 0 || v116 >= *a2 )
    {
      raiseIndexError2(v116, *a2 - 1);
      goto LABEL_130;
    }
    qmemcpy(v30, (const void *)(560 * v116 + a2[1] + 8), sizeof(v30));
    v50 = 46i64;
    if ( LOBYTE(v30[0]) )
    {
      v102 = v30[0];
      v44 = *(_DWORD *)((char *)v30 + 2);
      v41 = v30[46];
      v42 = v30[47];
      v43 = v30[48];
      v115 = 0;
      v50 = 52i64;
      v101 = 0;
      v101 = isSome__modelZboardZschematics_u78(v54);
      if ( *v112 )
        goto LABEL_130;
      if ( v101 == 1 )
      {
        v50 = 53i64;
        if ( v102 == 78 )
        {
          nimZeroMem_55(v31, 1448i64);
          v50 = 54i64;
          v100 = 0;
          v100 = notin_custom_prototypes__modelZboardZcustom95prototype95list_u189(v30[49]);
          if ( !*v112 )
          {
            if ( v100 == 1 )
            {
              v50 = 170i64;
              v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              eqdestroy___modelZboardZprototype95list_u3239(v31);
              v50 = 55i64;
              v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
              goto LABEL_125;
            }
            v50 = 56i64;
            get_custom_prototype__modelZboardZcustom95prototype95list_u451(v30[49], v31);
            if ( !*v112 )
            {
              v50 = 57i64;
              if ( v32 == 1 )
              {
                v50 = 170i64;
                v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                eqdestroy___modelZboardZprototype95list_u3239(v31);
                v50 = 58i64;
                v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
                goto LABEL_125;
              }
              v50 = 59i64;
              if ( v33 == 1 )
              {
                v50 = 170i64;
                v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                eqdestroy___modelZboardZprototype95list_u3239(v31);
                v50 = 60i64;
                v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
                goto LABEL_125;
              }
              v99 = 0;
              v98 = 0i64;
              v50 = 2655i64;
              v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
              v97 = len__modelZboardZschematics_u131(&v34);
              if ( !*v112 )
              {
                v96 = 0i64;
                v94 = v34 - 1;
                v95 = v34 - 1;
                v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                v114 = 0i64;
                v50 = 97i64;
                while ( v114 <= v95 )
                {
                  v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                  v96 = v114;
                  v50 = 2657i64;
                  if ( v114 < 0 || v96 >= v34 )
                  {
LABEL_48:
                    raiseIndexError2(v96, v34 - 1);
                    goto LABEL_98;
                  }
                  if ( *(_QWORD *)(v35 + 16 * v96 + 16) )
                  {
                    v50 = 62i64;
                    v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
                    if ( v96 < 0 )
                      goto LABEL_48;
                    if ( v96 >= v34 )
                      goto LABEL_48;
                    v99 = *(_BYTE *)(v35 + 16 * v96 + 8);
                    if ( v96 >= v34 )
                      goto LABEL_48;
                    v98 = *(_QWORD *)(v35 + 16 * v96 + 16);
                    v50 = 63i64;
                    v93 = 0;
                    v93 = is_free_component_type__modelZscores_u1938(v99);
                    if ( *v112 )
                      goto LABEL_98;
                    if ( v93 != 1 )
                    {
                      v50 = 65i64;
                      modelZboardZschematics_u244 = 0i64;
                      modelZboardZschematics_u244 = get__modelZboardZschematics_u244(v54);
                      if ( *v112 )
                        goto LABEL_98;
                      v91 = 0;
                      v91 = contains__modelZboardZschematics_u315(modelZboardZschematics_u244, v99);
                      if ( *v112 )
                        goto LABEL_98;
                      if ( !v91 )
                      {
                        v115 = v99;
                        v50 = 67i64;
                        break;
                      }
                      v50 = 69i64;
                      v90 = 0i64;
                      v90 = get__modelZboardZschematics_u244(v54);
                      if ( *v112 )
                        goto LABEL_98;
                      v89 = 0i64;
                      v89 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v90, v99);
                      if ( *v112 )
                        goto LABEL_98;
                      if ( *v89 == -1i64 )
                      {
                        v50 = 70i64;
                      }
                      else
                      {
                        v50 = 72i64;
                        v88 = 0i64;
                        v88 = get__modelZboardZschematics_u244(v54);
                        if ( *v112 )
                          goto LABEL_98;
                        v87 = 0i64;
                        v87 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v88, v99);
                        if ( *v112 )
                          goto LABEL_98;
                        if ( v98 > *v87 )
                        {
                          v115 = v99;
                          v50 = 74i64;
                          break;
                        }
                      }
                    }
                    v50 = 2659i64;
                    v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                    v86 = 0i64;
                    v86 = len__modelZboardZschematics_u131(&v34);
                    if ( *v112 )
                      goto LABEL_98;
                    if ( v86 != v97 )
                    {
                      v25 = TM__DRGBjVoeyzCuYwSWCgAUCw_7;
                      v26 = &TM__DRGBjVoeyzCuYwSWCgAUCw_6;
                      failedAssertImpl__stdZassertions_u234(&v25);
                      if ( *v112 )
                        goto LABEL_98;
                    }
                  }
                  v50 = 102i64;
                  v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                  v39 = v114 + 1;
                  if ( __OFADD__(1i64, v114) )
                  {
LABEL_88:
                    raiseOverflow();
                    goto LABEL_98;
                  }
                  v114 = v39;
                }
                v50 = 76i64;
                v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
                if ( !v115 )
                {
                  v85 = 0;
                  v84 = 0i64;
                  v50 = 2655i64;
                  v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                  v83 = len__modelZboardZschematics_u131(&v34);
                  if ( !*v112 )
                  {
                    v82 = 0i64;
                    v80 = v34 - 1;
                    v81 = v34 - 1;
                    v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                    v113 = 0i64;
                    v50 = 97i64;
                    while ( v113 <= v81 )
                    {
                      v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                      v82 = v113;
                      v50 = 2657i64;
                      if ( v113 < 0 || v82 >= v34 )
                      {
LABEL_81:
                        raiseIndexError2(v82, v34 - 1);
                        break;
                      }
                      if ( *(_QWORD *)(v35 + 16 * v82 + 16) )
                      {
                        v50 = 77i64;
                        v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
                        if ( v82 < 0 )
                          goto LABEL_81;
                        if ( v82 >= v34 )
                          goto LABEL_81;
                        v85 = *(_BYTE *)(v35 + 16 * v82 + 8);
                        if ( v82 >= v34 )
                          goto LABEL_81;
                        v84 = *(_QWORD *)(v35 + 16 * v82 + 16);
                        v50 = 78i64;
                        v79 = 0i64;
                        v79 = get__modelZboardZschematics_u244(v54);
                        if ( *v112 )
                          break;
                        v78 = 0i64;
                        v78 = getOrDefault__modelZboardZschematics_u1095(v79, v85, -1i64);
                        if ( *v112 )
                          break;
                        if ( v78 != -1 )
                        {
                          v50 = 79i64;
                          v77 = 0i64;
                          v77 = get__modelZboardZschematics_u244(v54);
                          if ( *v112 )
                            break;
                          v76 = 0i64;
                          v76 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v77, v85);
                          if ( *v112 )
                            break;
                          v12 = __OFSUB__(*v76, v84);
                          v37 = *v76 - v84;
                          if ( v12 )
                            goto LABEL_88;
                          *v76 = v37;
                        }
                        v50 = 2659i64;
                        v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                        v75 = 0i64;
                        v75 = len__modelZboardZschematics_u131(&v34);
                        if ( *v112 )
                          break;
                        if ( v75 != v83 )
                        {
                          v25 = TM__DRGBjVoeyzCuYwSWCgAUCw_10;
                          v26 = &TM__DRGBjVoeyzCuYwSWCgAUCw_6;
                          failedAssertImpl__stdZassertions_u234(&v25);
                          if ( *v112 )
                            break;
                        }
                      }
                      v50 = 102i64;
                      v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                      v38 = v113 + 1;
                      if ( __OFADD__(1i64, v113) )
                        goto LABEL_88;
                      v113 = v38;
                    }
                  }
                }
              }
            }
          }
LABEL_98:
          v50 = 170i64;
          v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          eqdestroy___modelZboardZprototype95list_u3239(v31);
          if ( *v112 )
            goto LABEL_130;
        }
        else
        {
          v50 = 80i64;
          v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
          v74 = 0;
          v74 = is_free_component_type__modelZscores_u1938(v102);
          if ( *v112 )
            goto LABEL_130;
          if ( v74 != 1 )
          {
            v50 = 82i64;
            v73 = 0i64;
            v73 = get__modelZboardZschematics_u244(v54);
            if ( *v112 )
              goto LABEL_130;
            v72 = 0;
            v72 = contains__modelZboardZschematics_u315(v73, LOBYTE(v30[0]));
            if ( *v112 )
              goto LABEL_130;
            if ( v72 )
            {
              v50 = 85i64;
              v71 = 0i64;
              v71 = get__modelZboardZschematics_u244(v54);
              if ( *v112 )
                goto LABEL_130;
              v70 = 0i64;
              v70 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v71, LOBYTE(v30[0]));
              if ( *v112 )
                goto LABEL_130;
              if ( *v70 != -1i64 )
              {
                v50 = 86i64;
                v69 = 0i64;
                v69 = get__modelZboardZschematics_u244(v54);
                if ( *v112 )
                  goto LABEL_130;
                v68 = 0i64;
                v68 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v69, LOBYTE(v30[0]));
                if ( *v112 )
                  goto LABEL_130;
                if ( !*v68 )
                {
                  v50 = 87i64;
                  v115 = v30[0];
                }
                v50 = 88i64;
                v67 = 0i64;
                v67 = get__modelZboardZschematics_u244(v54);
                if ( *v112 )
                  goto LABEL_130;
                v66 = 0i64;
                v66 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v67, LOBYTE(v30[0]));
                if ( *v112 )
                  goto LABEL_130;
                v13 = __OFSUB__(*v66, -1i64);
                v36 = *v66 + 1i64;
                if ( v13 )
                {
                  raiseOverflow();
                  goto LABEL_130;
                }
                *v66 = v36;
              }
            }
            else
            {
              v50 = 83i64;
              v115 = v30[0];
            }
          }
        }
      }
      v50 = 100i64;
      clamped_word_size__modelZboardZprototype95list_u4458 = get_clamped_word_size__modelZboardZprototype95list_u4458(
                                                               v102,
                                                               v30[28],
                                                               0);
      if ( *v112 )
        goto LABEL_130;
      v50 = 90i64;
      v65 = 0i64;
      v27 = v41;
      v28 = v42;
      v29 = v43;
      v25 = v30[24];
      v26 = (void *)v30[25];
      v24[0] = v30[26];
      v24[1] = v30[27];
      v23[0] = v30[60];
      v23[1] = v30[61];
      v23[2] = v30[62];
      v22[0] = v30[50];
      v22[1] = v30[51];
      v22[2] = v30[52];
      v21[0] = v30[53];
      v21[1] = v30[54];
      v21[2] = v30[55];
      v20[0] = v30[21];
      v20[1] = v30[22];
      v19[0] = v30[30];
      v19[1] = v30[31];
      v65 = board_add_component__modelZboardZboard_u21118(
              (unsigned int)&v55,
              v102,
              (unsigned int)&v27,
              v44,
              BYTE6(v30[0]),
              v30[1],
              (__int64)&v25,
              (__int64)v24,
              v30[49],
              clamped_word_size__modelZboardZprototype95list_u4458,
              LOBYTE(v30[59]),
              (__int64)v23,
              (__int64)v22,
              0i64,
              (__int64)v21,
              (__int64)v20,
              SLOWORD(v30[23]),
              (__int64)v19,
              v115);
      if ( *v112 )
        goto LABEL_130;
    }
LABEL_125:
    v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v116;
    v50 = 187i64;
    v64 = *a2;
    if ( v64 != v103 )
    {
      v25 = TM__DRGBjVoeyzCuYwSWCgAUCw_13;
      v26 = &TM__DRGBjVoeyzCuYwSWCgAUCw_2;
      failedAssertImpl__stdZassertions_u234(&v25);
      if ( *v112 )
        goto LABEL_130;
    }
  }
  v14 = v56;
  *a5 = v55;
  a5[1] = v14;
  v15 = v58;
  a5[2] = v57;
  a5[3] = v15;
  v16 = v60;
  a5[4] = v59;
  a5[5] = v16;
  v17 = v62;
  a5[6] = v61;
  a5[7] = v17;
  a5[8] = v63;
  v50 = 173i64;
  v51 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
  eqwasMoved___modelZsave95mongerZsave95monger_u2634(&v55);
  v50 = 35i64;
  v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
  eqdestroy___modelZboardZschematics_u1629(v54);
  v50 = 173i64;
  v51 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
  eqdestroy___modelZsave95mongerZsave95monger_u2637(&v55);
  return popFrame_75();
}
