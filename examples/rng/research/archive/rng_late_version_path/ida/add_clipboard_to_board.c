// address: 0x1405e3b59-0x1405e7841
// name: add_clipboard_to_board__presenterZutilitiesZhelper95functions_u7274
_BOOL8 __fastcall add_clipboard_to_board__presenterZutilitiesZhelper95functions_u7274(
        __int64 a1,
        __int64 a2,
        __int64 a3)
{
  int v3; // r8d
  int v4; // r11d
  void *v5; // rdx
  __int64 v6; // rdx
  bool v7; // dl
  bool v8; // dl
  __int64 v9; // r11
  int v10; // ecx
  bool v11; // dl
  int v12; // r8d
  __int64 v13; // r11
  int v14; // ecx
  bool v15; // dl
  char v16; // bl
  __int64 v17; // r9
  unsigned __int8 v18; // r10
  void *v19; // rdx
  void *v20; // rdx
  __int64 v21; // rdx
  __int64 v22; // rdx
  __int64 v23; // r8
  __int64 v24; // rdx
  __int64 v25; // rdx
  __int64 v26; // rdx
  __int64 v27; // rdx
  int v28; // r8d
  void *v29; // rdx
  __int64 v30; // rdx
  __int64 v32[2]; // [rsp+A0h] [rbp+20h] BYREF
  __int64 v33[2]; // [rsp+B0h] [rbp+30h] BYREF
  __int64 v34; // [rsp+C0h] [rbp+40h] BYREF
  __int64 v35; // [rsp+C8h] [rbp+48h]
  __int64 v36; // [rsp+D0h] [rbp+50h]
  __int64 v37; // [rsp+E0h] [rbp+60h] BYREF
  __int64 v38; // [rsp+E8h] [rbp+68h]
  __int64 v39; // [rsp+F0h] [rbp+70h]
  __int64 v40[4]; // [rsp+100h] [rbp+80h] BYREF
  __int64 v41; // [rsp+120h] [rbp+A0h] BYREF
  __int64 v42; // [rsp+128h] [rbp+A8h]
  __int64 v43; // [rsp+130h] [rbp+B0h]
  __int64 v44; // [rsp+140h] [rbp+C0h] BYREF
  void *v45; // [rsp+148h] [rbp+C8h]
  __int64 v46; // [rsp+150h] [rbp+D0h] BYREF
  void *v47; // [rsp+158h] [rbp+D8h]
  char v48[560]; // [rsp+160h] [rbp+E0h] BYREF
  __int64 v49; // [rsp+390h] [rbp+310h] BYREF
  char v50; // [rsp+398h] [rbp+318h]
  __int64 v51; // [rsp+3A0h] [rbp+320h]
  __int64 v52[2]; // [rsp+3A8h] [rbp+328h] BYREF
  char v53; // [rsp+3B8h] [rbp+338h]
  __int64 v54; // [rsp+3C0h] [rbp+340h]
  __int64 v55; // [rsp+3C8h] [rbp+348h]
  _QWORD v56[2]; // [rsp+3F8h] [rbp+378h] BYREF
  __int64 v57; // [rsp+408h] [rbp+388h] BYREF
  char v58; // [rsp+410h] [rbp+390h]
  __int64 v59; // [rsp+418h] [rbp+398h]
  __int64 v60; // [rsp+420h] [rbp+3A0h] BYREF
  char v61; // [rsp+428h] [rbp+3A8h]
  char v62[80]; // [rsp+588h] [rbp+508h] BYREF
  __int64 v63; // [rsp+5D8h] [rbp+558h]
  char v64[560]; // [rsp+5E0h] [rbp+560h] BYREF
  __int64 v65; // [rsp+8F8h] [rbp+878h] BYREF
  __int64 v66; // [rsp+900h] [rbp+880h]
  __int64 v67; // [rsp+938h] [rbp+8B8h]
  unsigned int v68; // [rsp+944h] [rbp+8C4h]
  unsigned int v69; // [rsp+948h] [rbp+8C8h] BYREF
  unsigned int v70; // [rsp+94Ch] [rbp+8CCh] BYREF
  __int64 v71; // [rsp+950h] [rbp+8D0h]
  __int64 v72; // [rsp+958h] [rbp+8D8h]
  __int64 v73; // [rsp+960h] [rbp+8E0h]
  __int64 v74; // [rsp+970h] [rbp+8F0h]
  __int64 started; // [rsp+978h] [rbp+8F8h]
  __int64 v76; // [rsp+980h] [rbp+900h] BYREF
  __int64 v77; // [rsp+988h] [rbp+908h]
  __int64 v78; // [rsp+990h] [rbp+910h]
  __int64 v79; // [rsp+998h] [rbp+918h]
  __int64 v80; // [rsp+9A0h] [rbp+920h]
  __int64 v81; // [rsp+9A8h] [rbp+928h]
  __int64 v82; // [rsp+9B0h] [rbp+930h] BYREF
  __int64 v83; // [rsp+9B8h] [rbp+938h]
  __int64 v84; // [rsp+9C0h] [rbp+940h]
  __int64 v85; // [rsp+9C8h] [rbp+948h]
  __int64 v86; // [rsp+9D0h] [rbp+950h] BYREF
  __int64 v87; // [rsp+9D8h] [rbp+958h]
  __int64 v88; // [rsp+9E0h] [rbp+960h]
  __int64 v89; // [rsp+9E8h] [rbp+968h]
  __int64 v90[3]; // [rsp+9F0h] [rbp+970h] BYREF
  unsigned int v91; // [rsp+A08h] [rbp+988h]
  unsigned int v92; // [rsp+A0Ch] [rbp+98Ch]
  __int64 v93; // [rsp+A10h] [rbp+990h] BYREF
  void *v94; // [rsp+A18h] [rbp+998h]
  __int64 v95; // [rsp+A20h] [rbp+9A0h] BYREF
  __int64 v96; // [rsp+A28h] [rbp+9A8h]
  __int64 v97; // [rsp+A30h] [rbp+9B0h]
  __int64 v98; // [rsp+A40h] [rbp+9C0h] BYREF
  __int64 v99; // [rsp+A48h] [rbp+9C8h]
  __int64 v100; // [rsp+A50h] [rbp+9D0h]
  __int64 v101; // [rsp+A58h] [rbp+9D8h]
  __int64 v102; // [rsp+A60h] [rbp+9E0h]
  __int64 v103; // [rsp+A68h] [rbp+9E8h]
  char v104[8]; // [rsp+A70h] [rbp+9F0h] BYREF
  const char *v105; // [rsp+A78h] [rbp+9F8h]
  __int64 v106; // [rsp+A80h] [rbp+A00h]
  const char *v107; // [rsp+A88h] [rbp+A08h]
  __int16 v108; // [rsp+A90h] [rbp+A10h]
  __int64 v109; // [rsp+AA0h] [rbp+A20h] BYREF
  char *v110; // [rsp+AA8h] [rbp+A28h]
  __int64 v111; // [rsp+AB0h] [rbp+A30h] BYREF
  void *v112; // [rsp+AB8h] [rbp+A38h]
  char v113[48]; // [rsp+AC0h] [rbp+A40h] BYREF
  __int64 v114; // [rsp+AF0h] [rbp+A70h] BYREF
  void *v115; // [rsp+AF8h] [rbp+A78h]
  __int64 v116; // [rsp+B00h] [rbp+A80h]
  __int64 v117; // [rsp+B08h] [rbp+A88h]
  __int64 v118; // [rsp+B10h] [rbp+A90h]
  __int64 v119; // [rsp+B18h] [rbp+A98h]
  unsigned __int16 v120; // [rsp+B24h] [rbp+AA4h]
  __int16 v121; // [rsp+B26h] [rbp+AA6h]
  __int64 v122; // [rsp+B28h] [rbp+AA8h]
  __int64 v123; // [rsp+B30h] [rbp+AB0h]
  unsigned __int8 *v124; // [rsp+B38h] [rbp+AB8h]
  __int64 v125; // [rsp+B40h] [rbp+AC0h]
  __int64 v126; // [rsp+B48h] [rbp+AC8h]
  __int64 v127; // [rsp+B50h] [rbp+AD0h]
  char v128; // [rsp+B5Fh] [rbp+ADFh]
  __int64 v129; // [rsp+B60h] [rbp+AE0h]
  __int64 v130; // [rsp+B68h] [rbp+AE8h]
  __int64 v131; // [rsp+B70h] [rbp+AF0h]
  __int16 v132; // [rsp+B7Eh] [rbp+AFEh]
  __int64 v133; // [rsp+B80h] [rbp+B00h]
  __int64 v134; // [rsp+B88h] [rbp+B08h]
  __int64 v135; // [rsp+B90h] [rbp+B10h]
  _QWORD *v136; // [rsp+B98h] [rbp+B18h]
  __int64 v137; // [rsp+BA0h] [rbp+B20h]
  __int64 v138; // [rsp+BA8h] [rbp+B28h]
  __int64 v139; // [rsp+BB0h] [rbp+B30h]
  __int64 v140; // [rsp+BB8h] [rbp+B38h]
  __int64 v141; // [rsp+BC0h] [rbp+B40h]
  __int64 v142; // [rsp+BC8h] [rbp+B48h]
  unsigned __int8 v143; // [rsp+BD6h] [rbp+B56h]
  char v144; // [rsp+BD7h] [rbp+B57h]
  __int64 v145; // [rsp+BD8h] [rbp+B58h]
  _QWORD *v146; // [rsp+BE0h] [rbp+B60h]
  _QWORD *v147; // [rsp+BE8h] [rbp+B68h]
  char v148; // [rsp+BF7h] [rbp+B77h]
  __int64 v149; // [rsp+BF8h] [rbp+B78h]
  __int64 v150; // [rsp+C00h] [rbp+B80h]
  __int64 v151; // [rsp+C08h] [rbp+B88h]
  __int64 v152; // [rsp+C10h] [rbp+B90h]
  __int64 v153; // [rsp+C18h] [rbp+B98h]
  unsigned __int8 v154; // [rsp+C27h] [rbp+BA7h]
  _QWORD *v155; // [rsp+C28h] [rbp+BA8h]
  _QWORD *v156; // [rsp+C30h] [rbp+BB0h]
  char can_place_component__modelZboardZboard_u9929; // [rsp+C3Fh] [rbp+BBFh]
  _QWORD *v158; // [rsp+C40h] [rbp+BC0h]
  _QWORD *v159; // [rsp+C48h] [rbp+BC8h]
  char v160; // [rsp+C56h] [rbp+BD6h]
  unsigned __int8 v161; // [rsp+C57h] [rbp+BD7h]
  __int64 v162; // [rsp+C58h] [rbp+BD8h]
  __int64 v163; // [rsp+C60h] [rbp+BE0h]
  unsigned __int8 *v164; // [rsp+C68h] [rbp+BE8h]
  __int64 v165; // [rsp+C70h] [rbp+BF0h]
  __int64 v166; // [rsp+C78h] [rbp+BF8h]
  _QWORD *v167; // [rsp+C80h] [rbp+C00h]
  _QWORD *v168; // [rsp+C88h] [rbp+C08h]
  char v169; // [rsp+C97h] [rbp+C17h]
  __int64 v170; // [rsp+C98h] [rbp+C18h]
  __int64 v171; // [rsp+CA0h] [rbp+C20h]
  __int64 v172; // [rsp+CA8h] [rbp+C28h]
  __int64 v173; // [rsp+CB0h] [rbp+C30h]
  __int64 v174; // [rsp+CB8h] [rbp+C38h]
  unsigned __int8 v175; // [rsp+CC7h] [rbp+C47h]
  _QWORD *v176; // [rsp+CC8h] [rbp+C48h]
  _QWORD *v177; // [rsp+CD0h] [rbp+C50h]
  char v178; // [rsp+CDFh] [rbp+C5Fh]
  __int64 v179; // [rsp+CE0h] [rbp+C60h]
  __int64 v180; // [rsp+CE8h] [rbp+C68h]
  unsigned __int8 *v181; // [rsp+CF0h] [rbp+C70h]
  unsigned __int8 progress_bool__modelZsave_u1666; // [rsp+CFEh] [rbp+C7Eh]
  char v183; // [rsp+CFFh] [rbp+C7Fh]
  _BYTE *v184; // [rsp+D00h] [rbp+C80h]
  bool v185; // [rsp+D0Dh] [rbp+C8Dh]
  bool v186; // [rsp+D0Eh] [rbp+C8Eh]
  bool v187; // [rsp+D0Fh] [rbp+C8Fh]
  __int64 v188; // [rsp+D10h] [rbp+C90h]
  __int64 v189; // [rsp+D18h] [rbp+C98h]
  bool v190; // [rsp+D22h] [rbp+CA2h]
  bool v191; // [rsp+D23h] [rbp+CA3h]
  bool v192; // [rsp+D24h] [rbp+CA4h]
  bool v193; // [rsp+D25h] [rbp+CA5h]
  bool v194; // [rsp+D26h] [rbp+CA6h]
  bool v195; // [rsp+D27h] [rbp+CA7h]
  __int64 v196; // [rsp+D28h] [rbp+CA8h]
  __int64 v197; // [rsp+D30h] [rbp+CB0h]
  bool v198; // [rsp+D3Fh] [rbp+CBFh]
  __int64 v199; // [rsp+D40h] [rbp+CC0h]
  bool v200; // [rsp+D4Fh] [rbp+CCFh]
  __int64 v201; // [rsp+D50h] [rbp+CD0h]
  __int64 v202; // [rsp+D58h] [rbp+CD8h]
  __int64 v203; // [rsp+D60h] [rbp+CE0h]
  bool v204; // [rsp+D6Fh] [rbp+CEFh]

  v105 = "add_clipboard_to_board";
  v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
  v106 = 0i64;
  v108 = 0;
  nimFrame_149(v104);
  v184 = (_BYTE *)nimErrorFlag_144();
  v204 = 0;
  v114 = 0i64;
  v115 = 0i64;
  nimZeroMem_121(v113, 40i64);
  v111 = 0i64;
  v112 = 0i64;
  v109 = 0i64;
  v110 = 0i64;
  v106 = 1126i64;
  v183 = 0;
  v183 = immutable_loaded__modelZboardZboard_u17313();
  if ( *v184 )
    goto LABEL_242;
  if ( v183 != 1 )
  {
    v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
    v106 = 1132i64;
    get_completed_levels__modelZutilities_u6010(&v111);
    if ( *v184 )
      goto LABEL_242;
    v106 = 1136i64;
    progress_bool__modelZsave_u1666 = 0;
    progress_bool__modelZsave_u1666 = get_progress_bool__modelZsave_u1666(6i64);
    if ( *v184 )
      goto LABEL_242;
    v106 = 1130i64;
    v3 = *(unsigned __int8 *)refptr_is_campaign__modelZmodel95types_u726;
    v4 = *(unsigned __int8 *)refptr_dev_mode__modelZmodel95types_u727;
    v5 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
    v46 = *refptr_loaded_level__modelZmodel95types_u830;
    v47 = v5;
    v44 = v111;
    v45 = v112;
    v6 = *((_QWORD *)refptr_campaign__modelZmodel95types_u817 + 1);
    v41 = *(_QWORD *)refptr_campaign__modelZmodel95types_u817;
    v42 = v6;
    v43 = *((_QWORD *)refptr_campaign__modelZmodel95types_u817 + 2);
    get_budget__modelZboardZschematics_u2168(
      (unsigned int)&v46,
      (unsigned int)&v44,
      (unsigned int)&v41,
      v4,
      v3,
      progress_bool__modelZsave_u1666,
      (__int64)v113);
    if ( *v184 )
      goto LABEL_242;
    v181 = 0i64;
    v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    v203 = 0i64;
    v106 = 250i64;
    v180 = *(_QWORD *)(a1 + 152);
    v179 = v180;
    v106 = 251i64;
    while ( v203 < v179 )
    {
      v106 = 1139i64;
      v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
      if ( v203 < 0 || v203 >= *(_QWORD *)(a1 + 152) )
      {
        raiseIndexError2(v203, *(_QWORD *)(a1 + 152) - 1i64);
        goto LABEL_242;
      }
      v181 = (unsigned __int8 *)(*(_QWORD *)(a1 + 160) + 560 * v203 + 8);
      nimZeroMem_121(&v49, 1448i64);
      v106 = 1140i64;
      if ( *v181 == 78 )
      {
        v106 = 1148i64;
        get_custom_prototype__modelZboardZcustom95prototype95list_u451(*((_QWORD *)v181 + 49), &v49);
        if ( !*v184 )
        {
          v175 = 0;
          v174 = 0i64;
          v106 = 2655i64;
          v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
          v173 = len__modelZboardZschematics_u131(&v65);
          if ( !*v184 )
          {
            v172 = 0i64;
            v170 = v65 - 1;
            v171 = v65 - 1;
            v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
            v202 = 0i64;
            v106 = 97i64;
            while ( v202 <= v171 )
            {
              v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
              v172 = v202;
              v106 = 2657i64;
              if ( v202 < 0 || v172 >= v65 )
              {
LABEL_35:
                raiseIndexError2(v172, v65 - 1);
                break;
              }
              if ( *(_QWORD *)(v66 + 16 * v172 + 16) )
              {
                v106 = 1149i64;
                v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
                if ( v172 < 0 )
                  goto LABEL_35;
                if ( v172 >= v65 )
                  goto LABEL_35;
                v175 = *(_BYTE *)(v66 + 16 * v172 + 8);
                if ( v172 >= v65 )
                  goto LABEL_35;
                v174 = *(_QWORD *)(v66 + 16 * v172 + 16);
                v106 = 1150i64;
                v169 = 0;
                v169 = contains__modelZboardZschematics_u315(v113, v175);
                if ( *v184 )
                  break;
                if ( v169 )
                {
                  v106 = 1152i64;
                  v168 = 0i64;
                  v168 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v113, v175);
                  if ( *v184 )
                    break;
                  if ( *v168 == -1i64 )
                  {
                    v106 = 1153i64;
                  }
                  else
                  {
                    v106 = 1154i64;
                    v167 = 0i64;
                    v167 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v113, v175);
                    if ( *v184 )
                      break;
                    v8 = __OFSUB__(*v167, v174);
                    v101 = *v167 - v174;
                    if ( v8 )
                      goto LABEL_52;
                    *v167 = v101;
                  }
                }
                else
                {
                  v106 = 1151i64;
                }
                v106 = 2659i64;
                v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                v166 = 0i64;
                v166 = len__modelZboardZschematics_u131(&v65);
                if ( *v184 )
                  break;
                if ( v166 != v173 )
                {
                  v46 = TM__xlEKrMnRGXqvDRNJ4JVzrQ_251;
                  v47 = &TM__xlEKrMnRGXqvDRNJ4JVzrQ_250;
                  failedAssertImpl__stdZassertions_u234(&v46);
                  if ( *v184 )
                    break;
                }
              }
              v106 = 102i64;
              v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
              v102 = v202 + 1;
              if ( __OFADD__(1i64, v202) )
                goto LABEL_52;
              v202 = v102;
            }
          }
        }
      }
      else
      {
        v106 = 1141i64;
        v178 = 0;
        v178 = contains__modelZboardZschematics_u315(v113, *v181);
        if ( !*v184 )
        {
          if ( !v178 )
          {
            v106 = 170i64;
            v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            eqdestroy___modelZboardZprototype95list_u3239(&v49);
            v106 = 1142i64;
            v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
            goto LABEL_55;
          }
          v106 = 1143i64;
          v177 = 0i64;
          v177 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v113, *v181);
          if ( !*v184 )
          {
            if ( *v177 == -1i64 )
            {
              v106 = 170i64;
              v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              eqdestroy___modelZboardZprototype95list_u3239(&v49);
              v106 = 1144i64;
              v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
              goto LABEL_55;
            }
            v106 = 1145i64;
            v176 = 0i64;
            v176 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v113, *v181);
            if ( !*v184 )
            {
              v7 = __OFSUB__(*v176, 1i64);
              v103 = *v176 - 1i64;
              if ( !v7 )
              {
                *v176 = v103;
                v106 = 170i64;
                v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                eqdestroy___modelZboardZprototype95list_u3239(&v49);
                v106 = 1146i64;
                v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
                goto LABEL_55;
              }
LABEL_52:
              raiseOverflow();
            }
          }
        }
      }
      v106 = 170i64;
      v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      eqdestroy___modelZboardZprototype95list_u3239(&v49);
      if ( *v184 )
        goto LABEL_242;
LABEL_55:
      v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      ++v203;
      v106 = 254i64;
      v165 = *(_QWORD *)(a1 + 152);
      if ( v165 != v179 )
      {
        v46 = TM__xlEKrMnRGXqvDRNJ4JVzrQ_253;
        v47 = &TM__xlEKrMnRGXqvDRNJ4JVzrQ_52;
        failedAssertImpl__stdZassertions_u234(&v46);
        if ( *v184 )
          goto LABEL_242;
      }
    }
    v164 = 0i64;
    v201 = 0i64;
    v106 = 250i64;
    v163 = *(_QWORD *)a3;
    v162 = v163;
    v106 = 251i64;
    while ( v201 < v162 )
    {
      v106 = 1156i64;
      v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
      if ( v201 < 0 || v201 >= *(_QWORD *)a3 )
      {
        raiseIndexError2(v201, *(_QWORD *)a3 - 1i64);
        goto LABEL_242;
      }
      v164 = (unsigned __int8 *)(*(_QWORD *)(a3 + 8) + 560 * v201 + 8);
      nimZeroMem_121(&v98, 24i64);
      nimZeroMem_121(&v95, 24i64);
      v93 = 0i64;
      v94 = 0i64;
      nimZeroMem_121(v48, 560i64);
      v106 = 1158i64;
      v91 = rotate__modelZsave95mongerZcommon_u4629(*(unsigned int *)(v164 + 2), *(unsigned __int8 *)(a3 + 36));
      if ( *v184 )
        goto LABEL_157;
      v92 = plus___modelZsave95mongerZcommon_u4308(*(unsigned int *)(a3 + 32), v91);
      if ( *v184 )
        goto LABEL_157;
      v106 = 1159i64;
      v161 = (*(_BYTE *)(a3 + 36) + v164[6]) & 3;
      v106 = 1160i64;
      if ( *v164 != 78 )
      {
        nimZeroMem_121(&v86, 24i64);
        v106 = 1161i64;
        v160 = 0;
        v160 = contains__modelZboardZschematics_u315(v113, *v164);
        if ( !*v184 )
        {
          if ( !v160 )
          {
            v106 = 250i64;
            v107 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
            eqdestroy___modelZboardZboard_u9871(&v86);
            v106 = 34i64;
            v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
            v46 = v93;
            v47 = v94;
            eqdestroy___modelZsave95mongerZversionsZv0_u296(&v46);
            v106 = 123i64;
            v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
            eqdestroy___modelZsave95mongerZsave95monger_u874(&v95);
            v106 = 131i64;
            eqdestroy___modelZsave95mongerZsave95monger_u895(&v98);
            v106 = 1162i64;
            v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
            goto LABEL_158;
          }
          v106 = 1163i64;
          v200 = 0;
          v159 = 0i64;
          v159 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v113, *v164);
          if ( !*v184 )
          {
            v200 = *v159 != -1i64;
            if ( !v200 )
            {
LABEL_74:
              if ( v200 )
              {
                v106 = 250i64;
                v107 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
                eqdestroy___modelZboardZboard_u9871(&v86);
                v106 = 34i64;
                v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                v46 = v93;
                v47 = v94;
                eqdestroy___modelZsave95mongerZversionsZv0_u296(&v46);
                v106 = 123i64;
                v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
                eqdestroy___modelZsave95mongerZsave95monger_u874(&v95);
                v106 = 131i64;
                eqdestroy___modelZsave95mongerZsave95monger_u895(&v98);
                v106 = 1165i64;
                v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
                goto LABEL_158;
              }
              v106 = 352i64;
              v107 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
              initHashSet__modelZboardZboard_u9946(&v41, 64i64);
              v86 = v41;
              v87 = v42;
              v88 = v43;
              if ( !*v184 )
              {
                v106 = 1166i64;
                v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
                can_place_component__modelZboardZboard_u9929 = 0;
                v9 = *((_QWORD *)v164 + 49);
                v10 = *v164;
                v41 = v86;
                v42 = v87;
                v43 = v88;
                can_place_component__modelZboardZboard_u9929 = board_can_place_component__modelZboardZboard_u9929(
                                                                 (int)a1 + 152,
                                                                 v10,
                                                                 v9,
                                                                 0,
                                                                 v92,
                                                                 v161,
                                                                 0,
                                                                 (__int64)&v41);
                if ( !*v184 )
                {
                  if ( !can_place_component__modelZboardZboard_u9929 )
                  {
                    v106 = 250i64;
                    v107 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
                    eqdestroy___modelZboardZboard_u9871(&v86);
                    v106 = 34i64;
                    v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                    v46 = v93;
                    v47 = v94;
                    eqdestroy___modelZsave95mongerZversionsZv0_u296(&v46);
                    v106 = 123i64;
                    v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
                    eqdestroy___modelZsave95mongerZsave95monger_u874(&v95);
                    v106 = 131i64;
                    eqdestroy___modelZsave95mongerZsave95monger_u895(&v98);
                    v106 = 1169i64;
                    v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
                    goto LABEL_158;
                  }
                  v106 = 1170i64;
                  v156 = 0i64;
                  v156 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v113, *v164);
                  if ( !*v184 && *v156 != -1i64 )
                  {
                    v106 = 1171i64;
                    v155 = 0i64;
                    v155 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v113, *v164);
                    if ( !*v184 )
                    {
                      v11 = __OFSUB__(*v155, 1i64);
                      v85 = *v155 - 1i64;
                      if ( v11 )
                        raiseOverflow();
                      else
                        *v155 = v85;
                    }
                  }
                }
              }
            }
            else
            {
              v106 = 1164i64;
              v158 = 0i64;
              v158 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v113, *v164);
              if ( !*v184 )
              {
                v200 = *v158 <= 0i64;
                goto LABEL_74;
              }
            }
          }
        }
        v106 = 250i64;
        v107 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
        eqdestroy___modelZboardZboard_u9871(&v86);
        if ( *v184 )
          goto LABEL_157;
LABEL_149:
        v106 = 1193i64;
        v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
        nimZeroMem_121(v90, 24i64);
        v106 = 1199i64;
        v89 = new_permanent_id__modelZsave95mongerZcommon_u3402();
        if ( !*v184 )
        {
          v106 = 1062i64;
          v107 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
          initTable__modelZboardZboard_u21145(&v41, 32i64);
          v98 = v41;
          v99 = v42;
          v100 = v43;
          if ( !*v184 )
          {
            v106 = 1065i64;
            initTable__modelZboardZboard_u21177(&v41, 32i64);
            v95 = v41;
            v96 = v42;
            v97 = v43;
            if ( !*v184 )
            {
              v106 = 1068i64;
              newSeq__modelZboardZboard_u21234(&v93, 0i64);
              v106 = 1193i64;
              v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
              v16 = v164[472];
              v17 = *((_QWORD *)v164 + 49);
              v18 = *v164;
              v41 = v90[0];
              v42 = v90[1];
              v43 = v90[2];
              v19 = (void *)*((_QWORD *)v164 + 25);
              v46 = *((_QWORD *)v164 + 24);
              v47 = v19;
              v20 = (void *)*((_QWORD *)v164 + 27);
              v44 = *((_QWORD *)v164 + 26);
              v45 = v20;
              v21 = *((_QWORD *)v164 + 61);
              v40[0] = *((_QWORD *)v164 + 60);
              v40[1] = v21;
              v40[2] = *((_QWORD *)v164 + 62);
              v37 = v98;
              v38 = v99;
              v39 = v100;
              v34 = v95;
              v35 = v96;
              v36 = v97;
              v22 = *((_QWORD *)v164 + 22);
              v33[0] = *((_QWORD *)v164 + 21);
              v33[1] = v22;
              v32[0] = v93;
              v32[1] = (__int64)v94;
              v134 = board_add_component__modelZboardZboard_u21118(
                       a1 + 152,
                       v18,
                       &v41,
                       v92,
                       v161,
                       v89,
                       &v46,
                       &v44,
                       v17,
                       *((_QWORD *)v164 + 28),
                       v16,
                       v40,
                       &v37,
                       0i64,
                       &v34,
                       v33,
                       0,
                       v32,
                       0);
              if ( !*v184 )
              {
                v106 = 1209i64;
                nimZeroMem_121(&v49, 1152i64);
                v50 = 0;
                v63 = v134;
                v106 = 34i64;
                v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                if ( v134 >= 0 && v134 < *(_QWORD *)(a1 + 152) )
                {
                  eqdup___modelZsave95mongerZversionsZv0_u151(*(_QWORD *)(a1 + 160) + 560 * v134 + 8, v48);
                  qmemcpy(v64, v48, sizeof(v64));
                  nimZeroMem_121(v52, 560i64);
                  nimZeroMem_121(v56, 80i64);
                  v56[1] = 1i64;
                  nimZeroMem_121(&v57, 8i64);
                  v57 = 256i64;
                  v58 = 1;
                  v59 = 1i64;
                  nimZeroMem_121(&v60, 8i64);
                  v60 = 256i64;
                  v61 = 1;
                  nimZeroMem_121(v62, 24i64);
                  v62[0] = 0;
                  v51 = 0i64;
                  v106 = 1209i64;
                  v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
                  add__modelZboardZboard_u16866(&v114, &v49);
                }
                else
                {
                  raiseIndexError2(v134, *(_QWORD *)(a1 + 152) - 1i64);
                }
              }
            }
          }
        }
        goto LABEL_157;
      }
      nimZeroMem_121(&v49, 1448i64);
      nimZeroMem_121(&v82, 24i64);
      v106 = 1173i64;
      v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
      get_custom_prototype__modelZboardZcustom95prototype95list_u451(*((_QWORD *)v164 + 49), &v49);
      if ( !*v184 )
      {
        v154 = 0;
        v153 = 0i64;
        v106 = 2655i64;
        v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
        v152 = len__modelZboardZschematics_u131(&v65);
        if ( !*v184 )
        {
          v151 = 0i64;
          v149 = v65 - 1;
          v150 = v65 - 1;
          v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v199 = 0i64;
          v106 = 97i64;
          while ( v199 <= v150 )
          {
            v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
            v151 = v199;
            v106 = 2657i64;
            if ( v199 < 0 || v151 >= v65 )
            {
LABEL_100:
              raiseIndexError2(v151, v65 - 1);
              goto LABEL_148;
            }
            if ( *(_QWORD *)(v66 + 16 * v151 + 16) )
            {
              v106 = 1174i64;
              v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
              if ( v151 < 0 )
                goto LABEL_100;
              if ( v151 >= v65 )
                goto LABEL_100;
              v154 = *(_BYTE *)(v66 + 16 * v151 + 8);
              if ( v151 >= v65 )
                goto LABEL_100;
              v153 = *(_QWORD *)(v66 + 16 * v151 + 16);
              v106 = 1175i64;
              if ( v154 == 79 || v154 == 81 || v154 == 90 )
              {
                v106 = 1176i64;
              }
              else
              {
                v106 = 1178i64;
                v148 = 0;
                v148 = contains__modelZboardZschematics_u315(v113, v154);
                if ( *v184 )
                  goto LABEL_148;
                if ( !v148 )
                {
                  v106 = 250i64;
                  v107 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
                  eqdestroy___modelZboardZboard_u9871(&v82);
                  v106 = 170i64;
                  v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                  eqdestroy___modelZboardZprototype95list_u3239(&v49);
                  v106 = 34i64;
                  v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                  v46 = v93;
                  v47 = v94;
                  eqdestroy___modelZsave95mongerZversionsZv0_u296(&v46);
                  v106 = 123i64;
                  v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
                  eqdestroy___modelZsave95mongerZsave95monger_u874(&v95);
                  v106 = 131i64;
                  eqdestroy___modelZsave95mongerZsave95monger_u895(&v98);
                  v106 = 1179i64;
                  v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
                  goto LABEL_158;
                }
                v106 = 1180i64;
                v198 = 0;
                v147 = 0i64;
                v147 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v113, v154);
                if ( *v184 )
                  goto LABEL_148;
                v198 = *v147 != -1i64;
                if ( v198 )
                {
                  v146 = 0i64;
                  v146 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v113, v154);
                  if ( *v184 )
                    goto LABEL_148;
                  v198 = v153 > *v146;
                }
                if ( v198 )
                {
                  v106 = 250i64;
                  v107 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
                  eqdestroy___modelZboardZboard_u9871(&v82);
                  v106 = 170i64;
                  v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                  eqdestroy___modelZboardZprototype95list_u3239(&v49);
                  v106 = 34i64;
                  v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                  v46 = v93;
                  v47 = v94;
                  eqdestroy___modelZsave95mongerZversionsZv0_u296(&v46);
                  v106 = 123i64;
                  v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
                  eqdestroy___modelZsave95mongerZsave95monger_u874(&v95);
                  v106 = 131i64;
                  eqdestroy___modelZsave95mongerZsave95monger_u895(&v98);
                  v106 = 1181i64;
                  v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
                  goto LABEL_158;
                }
              }
              v106 = 2659i64;
              v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
              v145 = 0i64;
              v145 = len__modelZboardZschematics_u131(&v65);
              if ( *v184 )
                goto LABEL_148;
              if ( v145 != v152 )
              {
                v46 = TM__xlEKrMnRGXqvDRNJ4JVzrQ_255;
                v47 = &TM__xlEKrMnRGXqvDRNJ4JVzrQ_250;
                failedAssertImpl__stdZassertions_u234(&v46);
                if ( *v184 )
                  goto LABEL_148;
              }
            }
            v106 = 102i64;
            v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
            v81 = v199 + 1;
            if ( __OFADD__(1i64, v199) )
            {
LABEL_146:
              raiseOverflow();
              goto LABEL_148;
            }
            v199 = v81;
          }
          v106 = 352i64;
          v107 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
          initHashSet__modelZboardZboard_u9946(&v41, 64i64);
          v82 = v41;
          v83 = v42;
          v84 = v43;
          if ( !*v184 )
          {
            v106 = 1183i64;
            v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
            v144 = 0;
            v12 = v164[6];
            v13 = *((_QWORD *)v164 + 49);
            v14 = *v164;
            v41 = v82;
            v42 = v83;
            v43 = v84;
            v144 = board_can_place_component__modelZboardZboard_u9929(
                     (int)a1 + 152,
                     v14,
                     v13,
                     0,
                     v92,
                     v12,
                     0,
                     (__int64)&v41);
            if ( !*v184 )
            {
              if ( !v144 )
              {
                v106 = 250i64;
                v107 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
                eqdestroy___modelZboardZboard_u9871(&v82);
                v106 = 170i64;
                v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                eqdestroy___modelZboardZprototype95list_u3239(&v49);
                v106 = 34i64;
                v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                v46 = v93;
                v47 = v94;
                eqdestroy___modelZsave95mongerZversionsZv0_u296(&v46);
                v106 = 123i64;
                v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
                eqdestroy___modelZsave95mongerZsave95monger_u874(&v95);
                v106 = 131i64;
                eqdestroy___modelZsave95mongerZsave95monger_u895(&v98);
                v106 = 1187i64;
                v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
                goto LABEL_158;
              }
              v143 = 0;
              v142 = 0i64;
              v106 = 2655i64;
              v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
              v141 = len__modelZboardZschematics_u131(&v65);
              if ( !*v184 )
              {
                v140 = 0i64;
                v138 = v65 - 1;
                v139 = v65 - 1;
                v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                v197 = 0i64;
                v106 = 97i64;
                while ( v197 <= v139 )
                {
                  v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                  v140 = v197;
                  v106 = 2657i64;
                  if ( v197 < 0 || v140 >= v65 )
                  {
LABEL_135:
                    raiseIndexError2(v140, v65 - 1);
                    break;
                  }
                  if ( *(_QWORD *)(v66 + 16 * v140 + 16) )
                  {
                    v106 = 1189i64;
                    v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
                    if ( v140 < 0 )
                      goto LABEL_135;
                    if ( v140 >= v65 )
                      goto LABEL_135;
                    v143 = *(_BYTE *)(v66 + 16 * v140 + 8);
                    if ( v140 >= v65 )
                      goto LABEL_135;
                    v142 = *(_QWORD *)(v66 + 16 * v140 + 16);
                    v106 = 1190i64;
                    v137 = 0i64;
                    v137 = getOrDefault__modelZboardZschematics_u1095(v113, v143, -1i64);
                    if ( *v184 )
                      break;
                    if ( v137 != -1 )
                    {
                      v106 = 1191i64;
                      v136 = 0i64;
                      v136 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v113, v143);
                      if ( *v184 )
                        break;
                      v15 = __OFSUB__(*v136, v142);
                      v79 = *v136 - v142;
                      if ( v15 )
                        goto LABEL_146;
                      *v136 = v79;
                    }
                    v106 = 2659i64;
                    v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                    v135 = 0i64;
                    v135 = len__modelZboardZschematics_u131(&v65);
                    if ( *v184 )
                      break;
                    if ( v135 != v141 )
                    {
                      v46 = TM__xlEKrMnRGXqvDRNJ4JVzrQ_258;
                      v47 = &TM__xlEKrMnRGXqvDRNJ4JVzrQ_250;
                      failedAssertImpl__stdZassertions_u234(&v46);
                      if ( *v184 )
                        break;
                    }
                  }
                  v106 = 102i64;
                  v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                  v80 = v197 + 1;
                  if ( __OFADD__(1i64, v197) )
                    goto LABEL_146;
                  v197 = v80;
                }
              }
            }
          }
        }
      }
LABEL_148:
      v106 = 250i64;
      v107 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
      eqdestroy___modelZboardZboard_u9871(&v82);
      v106 = 170i64;
      v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      eqdestroy___modelZboardZprototype95list_u3239(&v49);
      if ( !*v184 )
        goto LABEL_149;
LABEL_157:
      v106 = 34i64;
      v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      v46 = v93;
      v47 = v94;
      eqdestroy___modelZsave95mongerZversionsZv0_u296(&v46);
      v106 = 123i64;
      v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
      eqdestroy___modelZsave95mongerZsave95monger_u874(&v95);
      v106 = 131i64;
      eqdestroy___modelZsave95mongerZsave95monger_u895(&v98);
      if ( *v184 )
        goto LABEL_242;
LABEL_158:
      v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      ++v201;
      v106 = 254i64;
      v133 = *(_QWORD *)a3;
      if ( v133 != v162 )
      {
        v46 = TM__xlEKrMnRGXqvDRNJ4JVzrQ_260;
        v47 = &TM__xlEKrMnRGXqvDRNJ4JVzrQ_52;
        failedAssertImpl__stdZassertions_u234(&v46);
        if ( *v184 )
          goto LABEL_242;
      }
    }
    v106 = 1217i64;
    v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
    v132 = *(_WORD *)(a1 + 202);
    v131 = 0i64;
    v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    v196 = 0i64;
    v106 = 250i64;
    v130 = *(_QWORD *)(a3 + 16);
    v129 = v130;
    v106 = 251i64;
    while ( 1 )
    {
      if ( v196 >= v129 )
      {
        v106 = 1241i64;
        v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
        board_update_wires__modelZboardZboard_u16726(&v109, a1 + 152);
        if ( !*v184 )
        {
          v106 = 1242i64;
          v30 = v110 ? (__int64)(v110 + 8) : 0i64;
          add__presenterZutilitiesZhelper95functions_u8347(&v114, v30, v109);
          v106 = 1243i64;
          add_undo_changes__modelZboardZboard_u17728(&v114);
          if ( !*v184 )
          {
            v116 = v114;
            v204 = v114 != 0;
            v106 = 934i64;
            v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            v46 = v109;
            v47 = v110;
            eqdestroy___modelZboardZboard_u17903(&v46);
            v106 = 2128i64;
            v46 = v111;
            v47 = v112;
            eqdestroy___system_u3734(&v46);
            v106 = 1411i64;
            v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
            eqdestroy___modelZboardZschematics_u2219(v113);
            v106 = 934i64;
            v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            v46 = v114;
            v47 = v115;
            eqdestroy___modelZboardZboard_u17903(&v46);
            goto LABEL_243;
          }
        }
LABEL_242:
        v46 = v109;
        v47 = v110;
        eqdestroy___modelZboardZboard_u17903(&v46);
        v106 = 2128i64;
        v46 = v111;
        v47 = v112;
        eqdestroy___system_u3734(&v46);
        v106 = 1411i64;
        v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
        eqdestroy___modelZboardZschematics_u2219(v113);
        v106 = 934i64;
        v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v46 = v114;
        v47 = v115;
        eqdestroy___modelZboardZboard_u17903(&v46);
        goto LABEL_243;
      }
      v106 = 1218i64;
      v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
      if ( v196 < 0 || v196 >= *(_QWORD *)(a3 + 16) )
      {
        raiseIndexError2(v196, *(_QWORD *)(a3 + 16) - 1i64);
        goto LABEL_242;
      }
      v131 = *(_QWORD *)(a3 + 24) + 104 * v196 + 8;
      nimZeroMem_121(&v76, 24i64);
      v128 = 0;
      v106 = 1221i64;
      v23 = *(unsigned __int8 *)(a3 + 36);
      v24 = *(_QWORD *)(v131 + 32);
      v37 = *(_QWORD *)(v131 + 24);
      v38 = v24;
      v39 = *(_QWORD *)(v131 + 40);
      rotate_then_translate__modelZsave95mongerZcommon_u4638(&v34, &v37, v23, *(unsigned int *)(a3 + 32));
      v76 = v34;
      v77 = v35;
      v78 = v36;
      if ( *v184 )
        goto LABEL_231;
      nimZeroMem_121(&v70, 4i64);
      v70 = v76;
      v106 = 1223i64;
      v195 = 0;
      v194 = 0;
      v193 = 0;
      if ( v132 == (__int16)0x8000 )
        goto LABEL_221;
      v193 = (__int16)v70 <= (__int16)-v132;
      if ( (__int16)v70 > (__int16)-v132 )
        v193 = v132 <= (__int16)v70;
      v194 = v193;
      if ( !v193 )
      {
        if ( v132 == (__int16)0x8000 )
          goto LABEL_221;
        v194 = SHIWORD(v70) <= (unsigned __int16)-v132;
      }
      v195 = v194;
      if ( !v194 )
      {
        v106 = 1224i64;
        v195 = v132 <= SHIWORD(v70);
      }
      if ( v195 )
        break;
      v106 = 1226i64;
      v25 = *(_QWORD *)(a1 + 744);
      v34 = *(_QWORD *)(a1 + 736);
      v35 = v25;
      v36 = *(_QWORD *)(a1 + 752);
      v127 = getOrDefault__presenterZutilitiesZhelper95functions_u2124(&v34, v70, -1i64);
      if ( *v184 )
        goto LABEL_231;
      v106 = 1227i64;
      if ( v127 < 0 )
      {
        v106 = 704i64;
        v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
        v126 = v77;
        if ( v77 )
        {
          v69 = v76;
          v124 = 0i64;
          v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          v189 = 0i64;
          v123 = v77;
          v122 = v77;
          v106 = 251i64;
          while ( v189 < v122 )
          {
            v106 = 708i64;
            v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
            if ( v189 < 0 || v189 >= v77 )
            {
              raiseIndexError2(v189, v77 - 1);
              goto LABEL_231;
            }
            v124 = (unsigned __int8 *)(v78 + 4 * v189 + 8);
            v106 = 709i64;
            if ( *v124 > 7u )
            {
              raiseIndexError2(*v124, 7i64);
              goto LABEL_231;
            }
            v68 = *((_DWORD *)refptr_DIRECTIONS__modelZsave95mongerZcommon_u3356 + *v124);
            v121 = 0;
            v120 = 0;
            v106 = 710i64;
            v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
            v120 = *((_WORD *)v124 + 1) - 1;
            v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
            v188 = 0i64;
            v106 = 97i64;
            while ( v188 <= v120 )
            {
              v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
              v121 = v188;
              v106 = 711i64;
              pluseq___modelZsave95mongerZcommon_u4332(&v69, v68);
              if ( *v184 )
                goto LABEL_231;
              v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
              v70 = v69;
              v106 = 1223i64;
              v187 = 0;
              v186 = 0;
              v185 = 0;
              if ( v132 == (__int16)0x8000 )
                goto LABEL_221;
              v185 = (__int16)v70 <= (__int16)-v132;
              if ( (__int16)v70 > (__int16)-v132 )
                v185 = v132 <= (__int16)v70;
              v186 = v185;
              if ( !v185 )
              {
                if ( v132 == (__int16)0x8000 )
                  goto LABEL_221;
                v186 = SHIWORD(v70) <= (unsigned __int16)-v132;
              }
              v187 = v186;
              if ( !v186 )
              {
                v106 = 1224i64;
                v187 = v132 <= SHIWORD(v70);
              }
              if ( v187 )
                goto LABEL_216;
              v106 = 1226i64;
              v27 = *(_QWORD *)(a1 + 744);
              v34 = *(_QWORD *)(a1 + 736);
              v35 = v27;
              v36 = *(_QWORD *)(a1 + 752);
              v119 = getOrDefault__presenterZutilitiesZhelper95functions_u2124(&v34, v70, -1i64);
              if ( *v184 )
                goto LABEL_231;
              v106 = 1227i64;
              if ( v119 >= 0 )
                goto LABEL_219;
              v106 = 102i64;
              v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
              v67 = v188 + 1;
              if ( __OFADD__(1i64, v188) )
                goto LABEL_221;
              v188 = v67;
            }
            v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v189;
            v106 = 254i64;
            v118 = v77;
            if ( v77 != v122 )
            {
              v46 = TM__xlEKrMnRGXqvDRNJ4JVzrQ_262;
              v47 = &TM__xlEKrMnRGXqvDRNJ4JVzrQ_52;
              failedAssertImpl__stdZassertions_u234(&v46);
              if ( *v184 )
                goto LABEL_231;
            }
          }
LABEL_228:
          v106 = 194i64;
          v107 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
          v74 = bits__modelZsave95mongerZcommon_u192(1i64);
          if ( !*v184 )
          {
            v106 = 1230i64;
            v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
            v28 = *(unsigned __int8 *)(v131 + 2);
            v34 = v76;
            v35 = v77;
            v36 = v78;
            v29 = *(void **)(v131 + 16);
            v46 = *(_QWORD *)(v131 + 8);
            v47 = v29;
            started = board_start_wire__modelZboardZboard_u6704(
                        (int)a1 + 152,
                        (unsigned int)&v34,
                        v28,
                        (unsigned int)&v46,
                        *(_QWORD *)refptr_INVALID_WIRE_ID__modelZsave95mongerZcommon_u3579,
                        v74);
            if ( !*v184 )
            {
              v106 = 1232i64;
              nimZeroMem_121(&v49, 1152i64);
              v50 = 1;
              v49 = started;
              v71 = v76;
              v72 = v77;
              v73 = v78;
              v106 = 546i64;
              v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
              eqwasMoved___modelZsave95mongerZcommon_u4084(&v76);
              v51 = v71;
              v52[0] = v72;
              v52[1] = v73;
              v106 = 1237i64;
              v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
              v128 = *(_BYTE *)(v131 + 2);
              v53 = v128;
              v54 = 0i64;
              v55 = 0i64;
              v106 = 1232i64;
              v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
              add__modelZboardZboard_u16866(&v114, &v49);
            }
          }
LABEL_231:
          v106 = 546i64;
          v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
          eqdestroy___modelZsave95mongerZcommon_u4087(&v76);
          if ( *v184 )
            goto LABEL_242;
          goto LABEL_232;
        }
        v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
        v70 = HIDWORD(v76);
        v106 = 1223i64;
        v192 = 0;
        v191 = 0;
        v190 = 0;
        if ( v132 == (__int16)0x8000 )
          goto LABEL_221;
        v190 = (__int16)v70 <= (__int16)-v132;
        if ( (__int16)v70 > (__int16)-v132 )
          v190 = v132 <= (__int16)v70;
        v191 = v190;
        if ( !v190 )
        {
          if ( v132 == (__int16)0x8000 )
          {
LABEL_221:
            raiseOverflow();
            goto LABEL_231;
          }
          v191 = SHIWORD(v70) <= (unsigned __int16)-v132;
        }
        v192 = v191;
        if ( !v191 )
        {
          v106 = 1224i64;
          v192 = v132 <= SHIWORD(v70);
        }
        if ( v192 )
          break;
        v106 = 1226i64;
        v26 = *(_QWORD *)(a1 + 744);
        v34 = *(_QWORD *)(a1 + 736);
        v35 = v26;
        v36 = *(_QWORD *)(a1 + 752);
        v125 = getOrDefault__presenterZutilitiesZhelper95functions_u2124(&v34, v70, -1i64);
        if ( *v184 )
          goto LABEL_231;
        v106 = 1227i64;
        if ( v125 < 0 )
          goto LABEL_228;
      }
LABEL_219:
      v106 = 546i64;
      v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
      eqdestroy___modelZsave95mongerZcommon_u4087(&v76);
      v106 = 1228i64;
      v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
LABEL_232:
      v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      ++v196;
      v106 = 254i64;
      v117 = *(_QWORD *)(a3 + 16);
      if ( v117 != v129 )
      {
        v46 = TM__xlEKrMnRGXqvDRNJ4JVzrQ_263;
        v47 = &TM__xlEKrMnRGXqvDRNJ4JVzrQ_52;
        failedAssertImpl__stdZassertions_u234(&v46);
        if ( *v184 )
          goto LABEL_242;
      }
    }
LABEL_216:
    v106 = 546i64;
    v107 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    eqdestroy___modelZsave95mongerZcommon_u4087(&v76);
    v106 = 1225i64;
    v107 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
    goto LABEL_232;
  }
  v106 = 934i64;
  v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  v46 = v109;
  v47 = v110;
  eqdestroy___modelZboardZboard_u17903(&v46);
  v106 = 2128i64;
  v46 = v111;
  v47 = v112;
  eqdestroy___system_u3734(&v46);
  v106 = 1411i64;
  v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
  eqdestroy___modelZboardZschematics_u2219(v113);
  v106 = 934i64;
  v107 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  v46 = v114;
  v47 = v115;
  eqdestroy___modelZboardZboard_u17903(&v46);
LABEL_243:
  popFrame_149();
  return v204;
}
