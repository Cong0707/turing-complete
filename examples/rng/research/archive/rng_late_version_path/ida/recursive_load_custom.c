// address: 0x14067f85f-0x14068190e
// name: recursive_load__presenterZutilities_u37639
__int64 __fastcall recursive_load__presenterZutilities_u37639(__int64 *a1, __int64 a2, _QWORD *a3)
{
  __int64 v3; // rbx
  void *v4; // rdx
  __int64 v5; // rcx
  _QWORD *v6; // rdx
  __int64 v7; // rcx
  _QWORD *v8; // rdx
  void *v9; // rdx
  void *v10; // rdx
  __int64 v11; // r8
  void *v12; // rdx
  __int64 v13; // rax
  __int64 v14; // r10
  __int64 v15; // rcx
  __int64 v17; // [rsp+30h] [rbp-50h] BYREF
  _QWORD *v18; // [rsp+38h] [rbp-48h]
  __int64 (__fastcall *v19)(); // [rsp+40h] [rbp-40h] BYREF
  void *v20; // [rsp+48h] [rbp-38h]
  __int64 v21; // [rsp+50h] [rbp-30h] BYREF
  __int64 v22; // [rsp+58h] [rbp-28h]
  __int64 v23; // [rsp+60h] [rbp-20h]
  __int64 (__fastcall *v24)(); // [rsp+70h] [rbp-10h] BYREF
  _QWORD *v25; // [rsp+78h] [rbp-8h]
  __int64 (__fastcall *v26)(); // [rsp+80h] [rbp+0h]
  _QWORD *v27; // [rsp+88h] [rbp+8h]
  _WORD v28[22]; // [rsp+90h] [rbp+10h] BYREF
  int v29; // [rsp+BCh] [rbp+3Ch] BYREF
  __int64 (__fastcall *v30)(); // [rsp+2E0h] [rbp+260h] BYREF
  _QWORD *v31; // [rsp+2E8h] [rbp+268h]
  __int64 v32; // [rsp+2F8h] [rbp+278h] BYREF
  __int64 (__fastcall *v33)(); // [rsp+300h] [rbp+280h] BYREF
  _QWORD *v34; // [rsp+308h] [rbp+288h]
  __int64 (__fastcall *v35)(); // [rsp+310h] [rbp+290h] BYREF
  _QWORD *v36; // [rsp+318h] [rbp+298h]
  __int64 v37; // [rsp+320h] [rbp+2A0h] BYREF
  _QWORD *v38; // [rsp+328h] [rbp+2A8h]
  __int64 (__fastcall *v39)(); // [rsp+330h] [rbp+2B0h] BYREF
  _QWORD *v40; // [rsp+338h] [rbp+2B8h]
  unsigned __int64 v41; // [rsp+358h] [rbp+2D8h]
  __int64 v42; // [rsp+360h] [rbp+2E0h]
  __int64 v43; // [rsp+368h] [rbp+2E8h]
  __int64 (__fastcall *v44)(); // [rsp+370h] [rbp+2F0h] BYREF
  _QWORD *v45; // [rsp+378h] [rbp+2F8h]
  __int64 (__fastcall *v46)(); // [rsp+380h] [rbp+300h] BYREF
  _QWORD *v47; // [rsp+388h] [rbp+308h]
  __int64 (__fastcall *v48)(); // [rsp+390h] [rbp+310h] BYREF
  _QWORD *v49; // [rsp+398h] [rbp+318h]
  __int64 (__fastcall *v50)(); // [rsp+3A0h] [rbp+320h] BYREF
  _QWORD *v51; // [rsp+3A8h] [rbp+328h]
  __int64 (__fastcall *v52)(); // [rsp+3B0h] [rbp+330h] BYREF
  _QWORD *v53; // [rsp+3B8h] [rbp+338h]
  __int64 (__fastcall *v54)(); // [rsp+3C0h] [rbp+340h] BYREF
  _QWORD *v55; // [rsp+3C8h] [rbp+348h]
  __int64 (__fastcall *v56)(); // [rsp+3D0h] [rbp+350h] BYREF
  _QWORD *v57; // [rsp+3D8h] [rbp+358h]
  __int64 (__fastcall *v58)(); // [rsp+3E0h] [rbp+360h] BYREF
  _QWORD *v59; // [rsp+3E8h] [rbp+368h]
  __int64 (__fastcall *v60)(); // [rsp+3F0h] [rbp+370h] BYREF
  _QWORD *v61; // [rsp+3F8h] [rbp+378h]
  __int64 (__fastcall *v62)(); // [rsp+400h] [rbp+380h] BYREF
  _QWORD *v63; // [rsp+408h] [rbp+388h]
  char v64[8]; // [rsp+410h] [rbp+390h] BYREF
  const char *v65; // [rsp+418h] [rbp+398h]
  __int64 v66; // [rsp+420h] [rbp+3A0h]
  const char *v67; // [rsp+428h] [rbp+3A8h]
  __int16 v68; // [rsp+430h] [rbp+3B0h]
  __int64 (__fastcall *v69)(); // [rsp+440h] [rbp+3C0h] BYREF
  _QWORD *v70; // [rsp+448h] [rbp+3C8h]
  __int64 (__fastcall *v71)(); // [rsp+450h] [rbp+3D0h]
  _QWORD *v72; // [rsp+458h] [rbp+3D8h]
  __int64 (__fastcall *v73)(); // [rsp+460h] [rbp+3E0h]
  _QWORD *v74; // [rsp+468h] [rbp+3E8h]
  __int64 v75[4]; // [rsp+470h] [rbp+3F0h] BYREF
  __int64 (__fastcall *v76)(); // [rsp+490h] [rbp+410h]
  _QWORD *v77; // [rsp+498h] [rbp+418h]
  __int64 (__fastcall *v78)(); // [rsp+4A0h] [rbp+420h] BYREF
  _QWORD *v79; // [rsp+4A8h] [rbp+428h]
  __int64 (__fastcall *v80)(); // [rsp+4B0h] [rbp+430h] BYREF
  _QWORD *v81; // [rsp+4B8h] [rbp+438h]
  __int64 (__fastcall *v82)(); // [rsp+4C0h] [rbp+440h] BYREF
  _QWORD *v83; // [rsp+4C8h] [rbp+448h]
  __int64 v84; // [rsp+4D0h] [rbp+450h] BYREF
  _QWORD *v85; // [rsp+4D8h] [rbp+458h]
  __int64 (__fastcall *v86)(); // [rsp+4E0h] [rbp+460h] BYREF
  _QWORD *v87; // [rsp+4E8h] [rbp+468h]
  __int64 v88; // [rsp+4F0h] [rbp+470h] BYREF
  __int64 v89; // [rsp+4F8h] [rbp+478h]
  __int64 v90; // [rsp+500h] [rbp+480h]
  char v91; // [rsp+513h] [rbp+493h]
  unsigned int v92; // [rsp+514h] [rbp+494h]
  int v93; // [rsp+518h] [rbp+498h]
  char v94; // [rsp+51Fh] [rbp+49Fh]
  __int64 v95; // [rsp+520h] [rbp+4A0h]
  __int64 v96; // [rsp+528h] [rbp+4A8h]
  char Data__stdZprivateZoscommon_u33_10; // [rsp+537h] [rbp+4B7h]
  __int64 FirstFile__stdZprivateZoscommon_u24; // [rsp+538h] [rbp+4B8h]
  unsigned __int8 v99; // [rsp+547h] [rbp+4C7h]
  __int64 v100; // [rsp+548h] [rbp+4C8h]
  __int64 v101; // [rsp+550h] [rbp+4D0h]
  __int64 v102; // [rsp+558h] [rbp+4D8h]
  __int64 v103; // [rsp+560h] [rbp+4E0h]
  _QWORD *v104; // [rsp+568h] [rbp+4E8h]
  __int64 v105; // [rsp+570h] [rbp+4F0h]
  char v106; // [rsp+57Fh] [rbp+4FFh]
  __int64 v107; // [rsp+580h] [rbp+500h]
  __int64 v108; // [rsp+588h] [rbp+508h]
  __int64 *v109; // [rsp+590h] [rbp+510h]
  char v110; // [rsp+59Fh] [rbp+51Fh]
  __int64 v111; // [rsp+5A0h] [rbp+520h]
  __int64 *modelZcampaigns_u7913_1; // [rsp+5A8h] [rbp+528h]
  char v113; // [rsp+5B7h] [rbp+537h]
  _QWORD *v114; // [rsp+5B8h] [rbp+538h]
  char *v115; // [rsp+5C0h] [rbp+540h]
  __int64 v116; // [rsp+5C8h] [rbp+548h]
  __int64 v117; // [rsp+5D0h] [rbp+550h]
  char v118; // [rsp+5DFh] [rbp+55Fh]
  __int64 v119; // [rsp+5E0h] [rbp+560h]
  char v120; // [rsp+5EFh] [rbp+56Fh]
  __int64 v121; // [rsp+5F0h] [rbp+570h]
  unsigned __int8 v122; // [rsp+5FEh] [rbp+57Eh]
  char v123; // [rsp+5FFh] [rbp+57Fh]

  v3 = a1[1];
  v26 = (__int64 (__fastcall *)())*a1;
  v27 = (_QWORD *)v3;
  v65 = "recursive_load";
  v67 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
  v66 = 0i64;
  v68 = 0;
  nimFrame_162(v64);
  v115 = (char *)nimErrorFlag_157();
  v119 = 0i64;
  v114 = a3;
  nimZeroMem_132(&v88, 24i64);
  v86 = 0i64;
  v87 = 0i64;
  v84 = 0i64;
  v85 = 0i64;
  v82 = 0i64;
  v83 = 0i64;
  v80 = 0i64;
  v81 = 0i64;
  v78 = 0i64;
  v79 = 0i64;
  v76 = 0i64;
  v77 = 0i64;
  nimZeroMem_132(v75, 24i64);
  v66 = 3030i64;
  v24 = v26;
  v25 = v27;
  to_string__modelZsanitized95path_u445(&v86, &v24);
  if ( !*v115 )
  {
    v66 = 3032i64;
    get_progress_string__modelZsave_u1680(&v84, 8u);
    if ( !*v115 )
    {
      v66 = 3029i64;
      v24 = v86;
      v25 = v87;
      v19 = (__int64 (__fastcall *)())TM__8FyyixzftvDEeBWCL79bP9aA_747;
      v20 = &TM__8FyyixzftvDEeBWCL79bP9aA_746;
      v17 = v84;
      v18 = v85;
      read_localized_file__modelZtranslations_u2181(
        (unsigned int)&v21,
        (unsigned int)&v24,
        (unsigned int)&v19,
        (unsigned int)&v17,
        0);
      v88 = v21;
      v89 = v22;
      v90 = v23;
      if ( !*v115 )
      {
        v66 = 3035i64;
        v113 = 0;
        v21 = v88;
        v22 = v89;
        v23 = v90;
        v113 = isNone__modelZtranslations_u5944_2(&v21);
        if ( !*v115 )
        {
          if ( v113 == 1 )
          {
            v119 = 0i64;
            v66 = 3051i64;
            eqdestroy___presenterZutilities_u38089(v75);
            if ( !*v115 )
            {
              v66 = 394i64;
              v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              if ( v77 && (*v77 & 0x4000000000000000i64) == 0 )
                deallocShared(v77);
              if ( v79 && (*v79 & 0x4000000000000000i64) == 0 )
                deallocShared(v79);
              if ( v81 && (*v81 & 0x4000000000000000i64) == 0 )
                deallocShared(v81);
              if ( v83 && (*v83 & 0x4000000000000000i64) == 0 )
                deallocShared(v83);
              if ( v85 && (*v85 & 0x4000000000000000i64) == 0 )
                deallocShared(v85);
              if ( v87 && (*v87 & 0x4000000000000000i64) == 0 )
                deallocShared(v87);
              v66 = 142i64;
              v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\options.nim";
              eqdestroy___modelZtranslations_u2202(&v88);
            }
            goto LABEL_177;
          }
          v66 = 3037i64;
          v67 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
          modelZcampaigns_u7913_1 = 0i64;
          modelZcampaigns_u7913_1 = (__int64 *)unsafeGet__modelZcampaigns_u7913_1(&v88);
          if ( !*v115 )
          {
            v4 = (void *)modelZcampaigns_u7913_1[1];
            v19 = (__int64 (__fastcall *)())*modelZcampaigns_u7913_1;
            v20 = v4;
            nsuStrip((unsigned int)&v24, (unsigned int)&v19, 1, 1, (__int64)&TM__8FyyixzftvDEeBWCL79bP9aA_9);
            v82 = v24;
            v83 = v25;
            if ( !*v115 )
            {
              v66 = 3041i64;
              v19 = v26;
              v20 = v27;
              file_name__presenterZutilities_u35836(&v24, &v19);
              v80 = v24;
              v81 = v25;
              if ( !*v115 )
              {
                v66 = 3042i64;
                v111 = 0i64;
                v111 = nimNewObj(64i64, 8i64);
                v73 = v82;
                v74 = v83;
                v66 = 1699i64;
                v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                eqwasMoved___system_u2658(&v82);
                v5 = v111;
                v6 = v74;
                *(_QWORD *)v111 = v73;
                *(_QWORD *)(v5 + 8) = v6;
                v71 = v80;
                v72 = v81;
                v66 = 1699i64;
                v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                eqwasMoved___system_u2658(&v80);
                v7 = v111;
                v8 = v72;
                *(_QWORD *)(v111 + 16) = v71;
                *(_QWORD *)(v7 + 24) = v8;
                v66 = 3042i64;
                v67 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                v118 = a2 != 0;
                if ( a2 )
                  v118 = *(_BYTE *)(a2 + 56);
                *(_BYTE *)(v111 + 56) = v118;
                v119 = v111;
                v66 = 3044i64;
                v62 = 0i64;
                v63 = 0i64;
                v24 = v26;
                v25 = v27;
                to_string__modelZsanitized95path_u445(&v78, &v24);
                if ( !*v115 )
                {
                  rawNewString(&v24, (char *)v78 + 8);
                  v62 = v24;
                  v63 = v25;
                  v24 = v78;
                  v25 = v79;
                  appendString_79(&v62, &v24);
                  v24 = (__int64 (__fastcall *)())TM__8FyyixzftvDEeBWCL79bP9aA_748;
                  v25 = &TM__8FyyixzftvDEeBWCL79bP9aA_740;
                  appendString_79(&v62, &v24);
                  v76 = v62;
                  v77 = v63;
                  v110 = 0;
                  v24 = v62;
                  v25 = v63;
                  v110 = nosfileExists(&v24);
                  if ( !*v115 )
                  {
                    if ( v110 != 1 )
                      goto LABEL_59;
                    v60 = 0i64;
                    v61 = 0i64;
                    v58 = 0i64;
                    v59 = 0i64;
                    v56 = 0i64;
                    v57 = 0i64;
                    v66 = 3045i64;
                    v24 = v26;
                    v25 = v27;
                    v9 = (void *)v114[4];
                    v19 = (__int64 (__fastcall *)())v114[3];
                    v20 = v9;
                    minus___modelZutilities_u7455(&v58, &v24, &v19);
                    if ( !*v115 )
                    {
                      v24 = v58;
                      v25 = v59;
                      to_string__modelZsanitized95path_u445(&v56, &v24);
                      if ( !*v115 )
                      {
                        v24 = v56;
                        v25 = v57;
                        toLower__pureZunicode_u7800_3(&v60, &v24);
                        if ( !*v115 )
                        {
                          v109 = 0i64;
                          v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                          v117 = 0i64;
                          v66 = 250i64;
                          v108 = v114[1];
                          v107 = v108;
                          v66 = 251i64;
                          while ( v117 < v107 )
                          {
                            v66 = 3046i64;
                            v67 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                            if ( v117 < 0 || v117 >= v114[1] )
                            {
                              raiseIndexError2(v117, v114[1] - 1i64);
                              break;
                            }
                            v109 = (__int64 *)(v114[2] + 16 * v117 + 8);
                            v66 = 3047i64;
                            v106 = 0;
                            v24 = v60;
                            v25 = v61;
                            v10 = (void *)v109[1];
                            v19 = (__int64 (__fastcall *)())*v109;
                            v20 = v10;
                            v106 = nsuStartsWith(&v24, &v19);
                            if ( *v115 )
                              break;
                            if ( v106 == 1 )
                            {
                              *(_BYTE *)(v119 + 32) = 1;
                              v66 = 3049i64;
                              break;
                            }
                            v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                            ++v117;
                            v66 = 254i64;
                            v105 = v114[1];
                            if ( v105 != v107 )
                            {
                              v24 = (__int64 (__fastcall *)())TM__8FyyixzftvDEeBWCL79bP9aA_749;
                              v25 = &TM__8FyyixzftvDEeBWCL79bP9aA_140_0;
                              failedAssertImpl__stdZassertions_u234(&v24);
                              if ( *v115 )
                                break;
                            }
                          }
                        }
                      }
                    }
                    v66 = 394i64;
                    v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                    if ( v57 && (*v57 & 0x4000000000000000i64) == 0 )
                      deallocShared(v57);
                    if ( v59 && (*v59 & 0x4000000000000000i64) == 0 )
                      deallocShared(v59);
                    if ( v61 && (*v61 & 0x4000000000000000i64) == 0 )
                      deallocShared(v61);
                    if ( !*v115 )
                    {
LABEL_59:
                      v66 = 3052i64;
                      v67 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                      if ( a2 )
                      {
                        v104 = 0i64;
                        v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                        v116 = 0i64;
                        v66 = 250i64;
                        v103 = *(_QWORD *)(a2 + 40);
                        v102 = v103;
                        v66 = 251i64;
                        while ( 1 )
                        {
                          if ( v116 >= v102 )
                            goto LABEL_77;
                          v54 = 0i64;
                          v55 = 0i64;
                          v52 = 0i64;
                          v53 = 0i64;
                          v101 = 0i64;
                          v66 = 3053i64;
                          v67 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                          if ( v116 < 0 || v116 >= *(_QWORD *)(a2 + 40) )
                            break;
                          v104 = (_QWORD *)(*(_QWORD *)(a2 + 48) + 8 * v116 + 8);
                          v66 = 3054i64;
                          v11 = *v104;
                          v24 = v26;
                          v25 = v27;
                          v12 = *(void **)(v11 + 24);
                          v19 = *(__int64 (__fastcall **)())(v11 + 16);
                          v20 = v12;
                          slash___modelZsanitized95path_u1477(&v54, &v24, &v19);
                          if ( *v115 )
                            goto LABEL_157;
                          v24 = v54;
                          v25 = v55;
                          to_string__modelZsanitized95path_u445(&v52, &v24);
                          if ( *v115 )
                            goto LABEL_157;
                          v66 = 934i64;
                          v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                          v101 = eqdup___presenterZutilities_u22971(*v104, 1i64);
                          if ( *v115 )
                            goto LABEL_157;
                          v66 = 3054i64;
                          v67 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                          v24 = v52;
                          v25 = v53;
                          X5BX5Deq___presenterZutilities_u35966(v75, &v24, v101);
                          if ( *v115 )
                            goto LABEL_157;
                          v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                          ++v116;
                          v66 = 254i64;
                          v100 = *(_QWORD *)(a2 + 40);
                          if ( v100 != v102 )
                          {
                            v24 = (__int64 (__fastcall *)())TM__8FyyixzftvDEeBWCL79bP9aA_750;
                            v25 = &TM__8FyyixzftvDEeBWCL79bP9aA_140_0;
                            failedAssertImpl__stdZassertions_u234(&v24);
                            if ( *v115 )
                              goto LABEL_157;
                          }
                          v66 = 394i64;
                          v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                          if ( v53 && (*v53 & 0x4000000000000000i64) == 0 )
                            deallocShared(v53);
                          if ( v55 && (*v55 & 0x4000000000000000i64) == 0 )
                            deallocShared(v55);
                        }
                        raiseIndexError2(v116, *(_QWORD *)(a2 + 40) - 1i64);
                        goto LABEL_157;
                      }
LABEL_77:
                      v50 = 0i64;
                      v51 = 0i64;
                      v48 = 0i64;
                      v49 = 0i64;
                      v46 = 0i64;
                      v47 = 0i64;
                      v99 = 0;
                      v66 = 3056i64;
                      v67 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                      v24 = v26;
                      v25 = v27;
                      to_string__modelZsanitized95path_u445(&v48, &v24);
                      if ( *v115 )
                        goto LABEL_143;
                      nimZeroMem_132(v28, 592i64);
                      v66 = 201i64;
                      v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\std\\private\\osdirs.nim";
                      v24 = v48;
                      v25 = v49;
                      v19 = (__int64 (__fastcall *)())TM__8FyyixzftvDEeBWCL79bP9aA_751;
                      v20 = &TM__8FyyixzftvDEeBWCL79bP9aA_438;
                      slash___stdZprivateZospaths2_u87_18(&v46, &v24, &v19);
                      if ( *v115 )
                        goto LABEL_143;
                      v24 = v46;
                      v25 = v47;
                      FirstFile__stdZprivateZoscommon_u24 = findFirstFile__stdZprivateZoscommon_u24(&v24, v28);
                      if ( *v115 )
                        goto LABEL_143;
                      v66 = 202i64;
                      if ( FirstFile__stdZprivateZoscommon_u24 == -1 )
                      {
                        v66 = 203i64;
LABEL_143:
                        v66 = 394i64;
                        v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                        if ( v47 && (*v47 & 0x4000000000000000i64) == 0 )
                          deallocShared(v47);
                        if ( v49 && (*v49 & 0x4000000000000000i64) == 0 )
                          deallocShared(v49);
                        if ( v51 && (*v51 & 0x4000000000000000i64) == 0 )
                          deallocShared(v51);
                        if ( !*v115 )
                        {
                          v66 = 3066i64;
                          v67 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                          nimZeroMem_132(&v69, 16i64);
                          v69 = colonanonymous___presenterZutilities_u37872;
                          v70 = 0i64;
                          v14 = *(_QWORD *)(v119 + 40);
                          if ( *(_QWORD *)(v119 + 48) )
                            v15 = *(_QWORD *)(v119 + 48) + 8i64;
                          else
                            v15 = 0i64;
                          v24 = v69;
                          v25 = v70;
                          sort__presenterZutilities_u37910(v15, v14, &v24, 1i64);
                        }
                        goto LABEL_157;
                      }
                      v66 = 207i64;
                      while ( 1 )
                      {
                        v122 = 0;
                        v66 = 209i64;
                        Data__stdZprivateZoscommon_u33_10 = 0;
                        Data__stdZprivateZoscommon_u33_10 = skipFindData__stdZprivateZoscommon_u33_10(v28);
                        if ( *v115 )
                        {
LABEL_142:
                          v66 = 206i64;
                          ((void (__fastcall *)(__int64))*refptr_Dl_1744830719_)(FirstFile__stdZprivateZoscommon_u24);
                          goto LABEL_143;
                        }
                        if ( !Data__stdZprivateZoscommon_u33_10 )
                          break;
LABEL_137:
                        v66 = 217i64;
                        v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\std\\private\\osdirs.nim";
                        v93 = 0;
                        v93 = ((__int64 (__fastcall *)(__int64, _WORD *))*refptr_Dl_1744830716_)(
                                FirstFile__stdZprivateZoscommon_u24,
                                v28);
                        if ( !v93 )
                        {
                          v66 = 218i64;
                          v92 = ((__int64 (*)(void))*refptr_Dl_1744830633_)();
                          v66 = 219i64;
                          if ( v92 == 18 )
                            goto LABEL_142;
                          v66 = 220i64;
                          v24 = (__int64 (__fastcall *)())TM__8FyyixzftvDEeBWCL79bP9aA_754;
                          v25 = &TM__8FyyixzftvDEeBWCL79bP9aA_59_0;
                          raiseOSError__stdZoserrors_u122(v92, &v24);
                          if ( *v115 )
                            goto LABEL_142;
                        }
                      }
                      v44 = 0i64;
                      v45 = 0i64;
                      v66 = 210i64;
                      if ( (v28[0] & 0x10) != 0 )
                      {
                        v66 = 211i64;
                        v122 = 2;
                      }
                      v66 = 212i64;
                      if ( (v28[0] & 0x400) != 0 )
                      {
                        v66 = 213i64;
                        v41 = v122 + 1i64;
                        if ( v41 >= 4 )
                        {
                          raiseOverflow();
                          goto LABEL_133;
                        }
                        v122 = v41;
                      }
                      v42 = 0i64;
                      v43 = 0i64;
                      v39 = 0i64;
                      v40 = 0i64;
                      v37 = 0i64;
                      v38 = 0i64;
                      v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\std\\private\\osdirs.nim";
                      v66 = 215i64;
                      dollar___stdZwidestrs_u394(&v39, &v29);
                      if ( !*v115 )
                      {
                        v24 = v39;
                        v25 = v40;
                        nosextractFilename(&v37, &v24);
                        if ( !*v115 )
                        {
                          v19 = v48;
                          v20 = v49;
                          v17 = v37;
                          v18 = v38;
                          slash___stdZprivateZospaths2_u87_18(&v24, &v19, &v17);
                          v44 = v24;
                          v45 = v25;
                          if ( !*v115 )
                          {
                            v66 = 394i64;
                            v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                            if ( v38 && (*v38 & 0x4000000000000000i64) == 0 )
                              deallocShared(v38);
                            if ( v40 && (*v40 & 0x4000000000000000i64) == 0 )
                              deallocShared(v40);
                            v99 = v122;
                            v66 = 1699i64;
                            v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                            v24 = v44;
                            v25 = v45;
                            eqsink___system_u2667(&v50, &v24);
                            eqwasMoved___system_u2658(&v44);
                            v35 = 0i64;
                            v36 = 0i64;
                            v121 = 0i64;
                            v33 = 0i64;
                            v34 = 0i64;
                            v32 = 0i64;
                            v66 = 3057i64;
                            v67 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                            if ( v99 == 2 )
                            {
                              v66 = 3060i64;
                              v24 = v50;
                              v25 = v51;
                              as_sanitized_folder_name__modelZsanitized95path_u1302(&v35, &v24);
                              if ( !*v115 )
                              {
                                v66 = 3061i64;
                                v24 = v35;
                                v25 = v36;
                                to_string__modelZsanitized95path_u445(&v33, &v24);
                                if ( !*v115 )
                                {
                                  v21 = v75[0];
                                  v22 = v75[1];
                                  v23 = v75[2];
                                  v24 = v33;
                                  v25 = v34;
                                  v121 = getOrDefault__presenterZutilities_u37565(&v21, &v24);
                                  if ( !*v115 )
                                  {
                                    v66 = 3062i64;
                                    nimZeroMem_132(&v30, 16i64);
                                    v30 = recursive_load__presenterZutilities_u37639;
                                    v31 = v114;
                                    v24 = v35;
                                    v25 = v36;
                                    v13 = v114
                                        ? ((__int64 (__fastcall *)(__int64 (__fastcall **)(), __int64, _QWORD *))v30)(
                                            &v24,
                                            v121,
                                            v31)
                                        : ((__int64 (__fastcall *)(__int64 (__fastcall **)(), __int64))v30)(&v24, v121);
                                    v32 = v13;
                                    if ( !*v115 )
                                    {
                                      v66 = 3063i64;
                                      v120 = v32 != 0;
                                      if ( v32 )
                                      {
                                        v123 = 0;
                                        v96 = *(_QWORD *)(v32 + 40);
                                        v123 = v96 > 0;
                                        if ( v96 <= 0 )
                                          v123 = *(_BYTE *)(v32 + 32);
                                        v120 = v123;
                                      }
                                      if ( v120 == 1 )
                                      {
                                        v66 = 3064i64;
                                        v95 = v32;
                                        nimMarkCyclic_1(v32);
                                        v66 = 934i64;
                                        v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                                        eqwasMoved___presenterZutilities_u22961(&v32);
                                        if ( !*v115 )
                                        {
                                          v66 = 3064i64;
                                          v67 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                                          add__presenterZutilities_u37852(v119 + 40, v95);
                                        }
                                      }
                                    }
                                  }
                                }
                              }
                              v94 = *v115;
                              *v115 = 0;
                              v66 = 934i64;
                              v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                              eqdestroy___presenterZutilities_u22964(v32);
                              if ( !*v115 )
                              {
                                v66 = 394i64;
                                if ( v34 && (*v34 & 0x4000000000000000i64) == 0 )
                                  deallocShared(v34);
                                v66 = 934i64;
                                eqdestroy___presenterZutilities_u22964(v121);
                                if ( !*v115 )
                                {
                                  v66 = 394i64;
                                  if ( v36 && (*v36 & 0x4000000000000000i64) == 0 )
                                    deallocShared(v36);
                                  *v115 = v94;
                                }
                              }
                            }
                            else
                            {
                              v66 = 934i64;
                              v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                              eqdestroy___presenterZutilities_u22964(v32);
                              if ( !*v115 )
                              {
                                v66 = 394i64;
                                if ( v34 && (*v34 & 0x4000000000000000i64) == 0 )
                                  deallocShared(v34);
                                v66 = 934i64;
                                eqdestroy___presenterZutilities_u22964(v121);
                                if ( !*v115 )
                                {
                                  v66 = 394i64;
                                  if ( v36 && (*v36 & 0x4000000000000000i64) == 0 )
                                    deallocShared(v36);
                                  v66 = 3058i64;
                                  v67 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                                }
                              }
                            }
                          }
                        }
                      }
LABEL_133:
                      if ( v45 && (*v45 & 0x4000000000000000i64) == 0 )
                        deallocShared(v45);
                      if ( *v115 )
                        goto LABEL_142;
                      goto LABEL_137;
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
LABEL_157:
  v91 = *v115;
  *v115 = 0;
  v66 = 3051i64;
  eqdestroy___presenterZutilities_u38089(v75);
  if ( !*v115 )
  {
    v66 = 394i64;
    v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v77 && (*v77 & 0x4000000000000000i64) == 0 )
      deallocShared(v77);
    if ( v79 && (*v79 & 0x4000000000000000i64) == 0 )
      deallocShared(v79);
    if ( v81 && (*v81 & 0x4000000000000000i64) == 0 )
      deallocShared(v81);
    if ( v83 && (*v83 & 0x4000000000000000i64) == 0 )
      deallocShared(v83);
    if ( v85 && (*v85 & 0x4000000000000000i64) == 0 )
      deallocShared(v85);
    if ( v87 && (*v87 & 0x4000000000000000i64) == 0 )
      deallocShared(v87);
    v66 = 142i64;
    v67 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\options.nim";
    eqdestroy___modelZtranslations_u2202(&v88);
    *v115 = v91;
  }
LABEL_177:
  popFrame_162();
  return v119;
}
