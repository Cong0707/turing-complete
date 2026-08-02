// address: 0x1405a19fb-0x1405a4680
// name: load_level__modelZutilities_u7564
__int64 __fastcall load_level__modelZutilities_u7564(__int64 a1, __int64 *a2)
{
  __int64 v2; // rax
  __int64 v3; // rdx
  char *v4; // rdx
  char *v5; // rdx
  __int64 v6; // rdx
  char *v7; // rdx
  char *v8; // rdx
  char *v9; // rdx
  char *v10; // rdx
  char *v11; // rdx
  char *v12; // rdx
  char *v13; // rdx
  char *v14; // rdx
  char *v15; // rdx
  char *v16; // rdx
  __int64 *address; // rbx
  char *v18; // rdx
  __int64 *v19; // rbx
  char *v20; // rdx
  char *v21; // rdx
  __int64 v22; // rax
  char *v23; // rdx
  char *v24; // rdx
  __int64 v25; // rax
  __int64 *v26; // rbx
  char *v27; // rdx
  __int64 v28; // rax
  char *v29; // rdx
  __int64 *v30; // rbx
  char *v31; // rdx
  char *v32; // rdx
  __int64 *v33; // rbx
  char *v34; // rdx
  __int64 v35; // rax
  __int64 *v36; // rbx
  char *v37; // rdx
  __int64 v38; // rax
  char *v39; // rdx
  __int64 *v40; // rbx
  char *v41; // rdx
  char *v42; // rdx
  __int64 *v43; // rbx
  __int64 v44; // rax
  char *v45; // rdx
  __int64 *v46; // rax
  char *v47; // rdx
  __int64 *v48; // rax
  char *v49; // rdx
  int v50; // ebx
  char *v51; // rdx
  unsigned __int8 v52; // al
  char v53; // al
  __int64 *v54; // rbx
  char *v55; // rdx
  char *v56; // rdx
  __int64 *v57; // rax
  char *v58; // rdx
  char *v59; // rdx
  char *v60; // rdx
  char *v61; // rcx
  __int64 *v62; // rax
  char *v63; // rdx
  int v64; // r8d
  int v65; // r11d
  char *v66; // rdx
  __int64 v67; // rdx
  char *v68; // rdx
  char *v69; // rdx
  char *v70; // rdx
  char *v71; // rdx
  __int64 v73; // [rsp+40h] [rbp-40h] BYREF
  __int64 v74; // [rsp+48h] [rbp-38h]
  __int64 v75; // [rsp+50h] [rbp-30h]
  __int64 v76; // [rsp+60h] [rbp-20h] BYREF
  char *v77; // [rsp+68h] [rbp-18h]
  __int64 v78; // [rsp+70h] [rbp-10h] BYREF
  char *v79; // [rsp+78h] [rbp-8h]
  __int64 v80; // [rsp+80h] [rbp+0h]
  char *v81; // [rsp+88h] [rbp+8h]
  char v82[48]; // [rsp+90h] [rbp+10h] BYREF
  char v83[8]; // [rsp+C0h] [rbp+40h] BYREF
  __int64 v84; // [rsp+C8h] [rbp+48h]
  void *v85; // [rsp+D0h] [rbp+50h]
  __int64 v86; // [rsp+110h] [rbp+90h] BYREF
  char *v87; // [rsp+118h] [rbp+98h]
  __int64 v88; // [rsp+120h] [rbp+A0h] BYREF
  char *v89; // [rsp+128h] [rbp+A8h]
  __int64 v90; // [rsp+130h] [rbp+B0h] BYREF
  char *v91; // [rsp+138h] [rbp+B8h]
  __int64 v92; // [rsp+140h] [rbp+C0h] BYREF
  char *v93; // [rsp+148h] [rbp+C8h]
  __int64 v94; // [rsp+150h] [rbp+D0h] BYREF
  char *v95; // [rsp+158h] [rbp+D8h]
  __int64 v96; // [rsp+160h] [rbp+E0h] BYREF
  char *v97; // [rsp+168h] [rbp+E8h]
  __int64 v98; // [rsp+170h] [rbp+F0h] BYREF
  char *v99; // [rsp+178h] [rbp+F8h]
  __int64 v100; // [rsp+180h] [rbp+100h] BYREF
  char *v101; // [rsp+188h] [rbp+108h]
  __int64 v102; // [rsp+190h] [rbp+110h] BYREF
  char *v103; // [rsp+198h] [rbp+118h]
  __int64 v104; // [rsp+1A0h] [rbp+120h]
  char *v105; // [rsp+1A8h] [rbp+128h]
  __int64 v106; // [rsp+1B0h] [rbp+130h] BYREF
  char *v107; // [rsp+1B8h] [rbp+138h]
  __int64 v108; // [rsp+1C0h] [rbp+140h] BYREF
  char *v109; // [rsp+1C8h] [rbp+148h]
  __int64 v110; // [rsp+1D0h] [rbp+150h] BYREF
  char *v111; // [rsp+1D8h] [rbp+158h]
  __int64 v112; // [rsp+1E0h] [rbp+160h]
  char *v113; // [rsp+1E8h] [rbp+168h]
  __int64 v114; // [rsp+1F0h] [rbp+170h]
  char *v115; // [rsp+1F8h] [rbp+178h]
  __int64 v116; // [rsp+200h] [rbp+180h] BYREF
  char *v117; // [rsp+208h] [rbp+188h]
  __int64 v118; // [rsp+210h] [rbp+190h] BYREF
  char *v119; // [rsp+218h] [rbp+198h]
  __int64 v120; // [rsp+220h] [rbp+1A0h] BYREF
  char *v121; // [rsp+228h] [rbp+1A8h]
  __int64 v122; // [rsp+230h] [rbp+1B0h] BYREF
  char *v123; // [rsp+238h] [rbp+1B8h]
  __int64 v124; // [rsp+240h] [rbp+1C0h] BYREF
  char *v125; // [rsp+248h] [rbp+1C8h]
  __int64 v126; // [rsp+250h] [rbp+1D0h] BYREF
  char *v127; // [rsp+258h] [rbp+1D8h]
  __int64 v128; // [rsp+260h] [rbp+1E0h] BYREF
  char *v129; // [rsp+268h] [rbp+1E8h]
  __int64 v130; // [rsp+270h] [rbp+1F0h] BYREF
  char *v131; // [rsp+278h] [rbp+1F8h]
  __int64 v132; // [rsp+280h] [rbp+200h] BYREF
  char *v133; // [rsp+288h] [rbp+208h]
  __int64 v134; // [rsp+290h] [rbp+210h] BYREF
  void *v135; // [rsp+298h] [rbp+218h]
  __int64 v136; // [rsp+2A0h] [rbp+220h] BYREF
  void *v137; // [rsp+2A8h] [rbp+228h]
  char v138[8]; // [rsp+2B0h] [rbp+230h] BYREF
  const char *v139; // [rsp+2B8h] [rbp+238h]
  __int64 v140; // [rsp+2C0h] [rbp+240h]
  const char *v141; // [rsp+2C8h] [rbp+248h]
  __int16 v142; // [rsp+2D0h] [rbp+250h]
  __int64 v143; // [rsp+2E0h] [rbp+260h] BYREF
  char *v144; // [rsp+2E8h] [rbp+268h]
  __int64 v145; // [rsp+2F0h] [rbp+270h] BYREF
  char *v146; // [rsp+2F8h] [rbp+278h]
  __int64 v147; // [rsp+300h] [rbp+280h] BYREF
  char *v148; // [rsp+308h] [rbp+288h]
  __int64 v149; // [rsp+310h] [rbp+290h] BYREF
  char *v150; // [rsp+318h] [rbp+298h]
  __int64 v151; // [rsp+320h] [rbp+2A0h] BYREF
  char *v152; // [rsp+328h] [rbp+2A8h]
  __int16 v153; // [rsp+348h] [rbp+2C8h]
  char v154; // [rsp+360h] [rbp+2E0h]
  char v155; // [rsp+378h] [rbp+2F8h]
  __int64 v156; // [rsp+528h] [rbp+4A8h]
  char *v157; // [rsp+530h] [rbp+4B0h]
  __int64 v158; // [rsp+538h] [rbp+4B8h]
  char *v159; // [rsp+540h] [rbp+4C0h]
  __int64 v160; // [rsp+550h] [rbp+4D0h]
  __int64 v161; // [rsp+558h] [rbp+4D8h]
  __int64 v162; // [rsp+560h] [rbp+4E0h]
  unsigned __int8 progress_bool__modelZsave_u1666; // [rsp+56Eh] [rbp+4EEh]
  char v164; // [rsp+56Fh] [rbp+4EFh]
  __int64 v165; // [rsp+570h] [rbp+4F0h]
  char v166; // [rsp+57Dh] [rbp+4FDh]
  char v167; // [rsp+57Eh] [rbp+4FEh]
  unsigned __int8 v168; // [rsp+57Fh] [rbp+4FFh]
  __int64 v169; // [rsp+580h] [rbp+500h]
  __int64 v170; // [rsp+588h] [rbp+508h]
  __int64 v171; // [rsp+590h] [rbp+510h]
  __int64 v172; // [rsp+598h] [rbp+518h]
  __int64 v173; // [rsp+5A0h] [rbp+520h]
  __int64 v174; // [rsp+5A8h] [rbp+528h]
  char v175; // [rsp+5B7h] [rbp+537h]
  __int64 v176; // [rsp+5B8h] [rbp+538h]
  _BYTE *v177; // [rsp+5C0h] [rbp+540h]
  bool v178; // [rsp+5CCh] [rbp+54Ch]
  bool v179; // [rsp+5CDh] [rbp+54Dh]
  bool v180; // [rsp+5CEh] [rbp+54Eh]
  bool v181; // [rsp+5CFh] [rbp+54Fh]

  v2 = *a2;
  v3 = a2[1];
  v80 = v2;
  v81 = (char *)v3;
  v139 = "load_level";
  v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  v140 = 0i64;
  v142 = 0;
  nimFrame_145(v138);
  v177 = (_BYTE *)nimErrorFlag_141();
  nimZeroMem_118(&v151, 560i64);
  v140 = 664i64;
  v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  clear_on_new_scheamtic_load__modelZutilities_u92(a1);
  if ( *v177 )
    goto LABEL_124;
  v140 = 666i64;
  v4 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
  v78 = *refptr_loaded_level__modelZmodel95types_u830;
  v79 = v4;
  v76 = TM__8FyyixzftvDEeBWCL79bP9aA_5;
  v77 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_4;
  if ( (unsigned __int8)eqStrings_19(&v78, &v76) == 1 )
  {
    v140 = 667i64;
    update_custom_used_components__modelZboardZcustom95prototype_u2713();
    if ( *v177 )
      goto LABEL_124;
  }
  v140 = 1699i64;
  v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  v78 = v80;
  v79 = v81;
  eqcopy___system_u2661(refptr_loaded_level__modelZmodel95types_u830, &v78);
  v140 = 670i64;
  v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  reset_ui__modelZutilities_u6022(a1);
  if ( *v177 )
    goto LABEL_124;
  v140 = 671i64;
  v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  v176 = 0i64;
  v5 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
  v78 = *refptr_loaded_level__modelZmodel95types_u830;
  v79 = v5;
  v176 = X5BX5D___modelZboardZboard_u17368(refptr_campaign__modelZmodel95types_u817, &v78);
  if ( *v177 )
    goto LABEL_124;
  v140 = 770i64;
  v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
  eqcopy___modelZboardZschematics_u4046(&v151, v176);
  v149 = 0i64;
  v150 = 0i64;
  v147 = 0i64;
  v148 = 0i64;
  v145 = 0i64;
  v146 = 0i64;
  v143 = 0i64;
  v144 = 0i64;
  v140 = 677i64;
  v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  v175 = 0;
  v6 = *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 1);
  v73 = *(_QWORD *)refptr_level_progress__modelZmodel95types_u825;
  v74 = v6;
  v75 = *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 2);
  v7 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
  v78 = *refptr_loaded_level__modelZmodel95types_u830;
  v79 = v7;
  v175 = contains__modelZcampaigns_u16380(&v73, &v78);
  if ( !*v177 )
  {
    if ( v175 )
      goto LABEL_22;
    v140 = 678i64;
    if ( v154 == 3 )
    {
      v140 = 679i64;
      if ( v156 )
      {
        v136 = 0i64;
        v137 = 0i64;
        v140 = 680i64;
        nimZeroMem_118(v83, 72i64);
        v140 = 1699i64;
        v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v78 = v156;
        v79 = v157;
        eqdup___system_u2664(&v136, &v78);
        v84 = v136;
        v85 = v137;
        v140 = 680i64;
        v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
        v8 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
        v78 = *refptr_loaded_level__modelZmodel95types_u830;
        v79 = v8;
        X5BX5Deq___modelZinitialize_u80(refptr_level_progress__modelZmodel95types_u825, &v78, v83);
        if ( *v177 )
          goto LABEL_117;
      }
      else
      {
        v134 = 0i64;
        v135 = 0i64;
        v140 = 683i64;
        nimZeroMem_118(v83, 72i64);
        v140 = 1699i64;
        v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v9 = (char *)*((_QWORD *)refptr_loaded_architecture__modelZmodel95types_u831 + 1);
        v78 = *(_QWORD *)refptr_loaded_architecture__modelZmodel95types_u831;
        v79 = v9;
        eqdup___system_u2664(&v134, &v78);
        v84 = v134;
        v85 = v135;
        v140 = 683i64;
        v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
        v10 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
        v78 = *refptr_loaded_level__modelZmodel95types_u830;
        v79 = v10;
        X5BX5Deq___modelZinitialize_u80(refptr_level_progress__modelZmodel95types_u825, &v78, v83);
        if ( *v177 )
          goto LABEL_117;
      }
    }
    else
    {
      v140 = 686i64;
      nimZeroMem_118(v83, 72i64);
      v84 = 7i64;
      v85 = &TM__8FyyixzftvDEeBWCL79bP9aA_41;
      v11 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
      v78 = *refptr_loaded_level__modelZmodel95types_u830;
      v79 = v11;
      X5BX5Deq___modelZinitialize_u80(refptr_level_progress__modelZmodel95types_u825, &v78, v83);
      if ( *v177 )
        goto LABEL_117;
    }
    v140 = 688i64;
    if ( !v155 )
    {
      v140 = 689i64;
      v174 = 0i64;
      v12 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
      v78 = *refptr_loaded_level__modelZmodel95types_u830;
      v79 = v12;
      v174 = X5BX5D___modelZcampaigns_u16467(refptr_level_progress__modelZmodel95types_u825, &v78);
      if ( *v177 )
        goto LABEL_117;
      *(_QWORD *)(v174 + 24) = -1i64;
      v140 = 690i64;
      v173 = 0i64;
      v13 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
      v78 = *refptr_loaded_level__modelZmodel95types_u830;
      v79 = v13;
      v173 = X5BX5D___modelZcampaigns_u16467(refptr_level_progress__modelZmodel95types_u825, &v78);
      if ( *v177 )
        goto LABEL_117;
      *(_QWORD *)(v173 + 32) = -1i64;
      v140 = 691i64;
      v172 = 0i64;
      v14 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
      v78 = *refptr_loaded_level__modelZmodel95types_u830;
      v79 = v14;
      v172 = X5BX5D___modelZcampaigns_u16467(refptr_level_progress__modelZmodel95types_u825, &v78);
      if ( *v177 )
        goto LABEL_117;
      *(_QWORD *)(v172 + 40) = -1i64;
    }
    v140 = 693i64;
    save_level_data__modelZutilities_u5679();
    if ( !*v177 )
    {
LABEL_22:
      v140 = 696i64;
      v171 = 0i64;
      v15 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
      v78 = *refptr_loaded_level__modelZmodel95types_u830;
      v79 = v15;
      v171 = X5BX5D___modelZcampaigns_u16467(refptr_level_progress__modelZmodel95types_u825, &v78);
      if ( *v177 )
        goto LABEL_117;
      v16 = *(char **)(v171 + 16);
      v78 = *(_QWORD *)(v171 + 8);
      v79 = v16;
      as_sanitized_folder_name__modelZsanitized95path_u472(&v149, &v78);
      if ( *v177 )
        goto LABEL_117;
      v140 = 698i64;
      if ( v154 == 3 )
      {
        v140 = 699i64;
        v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
        v132 = 0i64;
        v133 = 0i64;
        v78 = v149;
        v79 = v150;
        to_string__modelZsanitized95path_u445(&v132, &v78);
        if ( *v177 )
        {
          v78 = v132;
          v79 = v133;
          eqdestroy___system_u281_38(&v78);
          goto LABEL_117;
        }
        v140 = 1699i64;
        v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v78 = v132;
        v79 = v133;
        eqsink___system_u2667(refptr_loaded_architecture__modelZmodel95types_u831, &v78);
        v140 = 700i64;
        v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
        v130 = 0i64;
        v131 = 0i64;
        address = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_base_path__modelZmodel95types_u77);
        rawNewString(&v78, *address + 25);
        v130 = v78;
        v131 = v79;
        v18 = (char *)address[1];
        v78 = *address;
        v79 = v18;
        appendString_73(&v130, &v78);
        v78 = TM__8FyyixzftvDEeBWCL79bP9aA_62;
        v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_61;
        appendString_73(&v130, &v78);
        v140 = 1699i64;
        v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v19 = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_level_path__modelZmodel95types_u78);
        v78 = v130;
        v79 = v131;
        eqsink___system_u2667(v19, &v78);
        v140 = 701i64;
        v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
        v128 = 0i64;
        v129 = 0i64;
        rawNewString(&v78, *v19 + *(_QWORD *)refptr_loaded_architecture__modelZmodel95types_u831 + 1);
        v128 = v78;
        v129 = v79;
        v20 = (char *)v19[1];
        v78 = *v19;
        v79 = v20;
        appendString_73(&v128, &v78);
        v21 = (char *)*((_QWORD *)refptr_loaded_architecture__modelZmodel95types_u831 + 1);
        v78 = *(_QWORD *)refptr_loaded_architecture__modelZmodel95types_u831;
        v79 = v21;
        appendString_73(&v128, &v78);
        v78 = TM__8FyyixzftvDEeBWCL79bP9aA_64;
        v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_63;
        appendString_73(&v128, &v78);
        v140 = 1699i64;
        v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v22 = _emutls_get_address(refptr___emutls_v_global_save_arch_path__modelZmodel95types_u79);
        v78 = v128;
        v79 = v129;
        eqsink___system_u2667(v22, &v78);
        v140 = 703i64;
        v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
        v126 = 0i64;
        v127 = 0i64;
        rawNewString(&v78, *(_QWORD *)refptr_loaded_architecture__modelZmodel95types_u831 + *v19 + v151 + 2);
        v126 = v78;
        v127 = v79;
        v23 = (char *)v19[1];
        v78 = *v19;
        v79 = v23;
        appendString_73(&v126, &v78);
        v24 = (char *)*((_QWORD *)refptr_loaded_architecture__modelZmodel95types_u831 + 1);
        v78 = *(_QWORD *)refptr_loaded_architecture__modelZmodel95types_u831;
        v79 = v24;
        appendString_73(&v126, &v78);
        v78 = TM__8FyyixzftvDEeBWCL79bP9aA_65;
        v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_63;
        appendString_73(&v126, &v78);
        v78 = v151;
        v79 = v152;
        appendString_73(&v126, &v78);
        v78 = TM__8FyyixzftvDEeBWCL79bP9aA_66;
        v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_63;
        appendString_73(&v126, &v78);
        v140 = 1699i64;
        v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v25 = _emutls_get_address(refptr___emutls_v_global_save_schematic_path__modelZmodel95types_u80);
        v78 = v126;
        v79 = v127;
        eqsink___system_u2667(v25, &v78);
      }
      else
      {
        v140 = 704i64;
        v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
        if ( v154 == 5 )
        {
          v140 = 706i64;
          v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
          v124 = 0i64;
          v125 = 0i64;
          v26 = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_base_path__modelZmodel95types_u77);
          rawNewString(&v78, *v26 + v151 + 13);
          v124 = v78;
          v125 = v79;
          v27 = (char *)v26[1];
          v78 = *v26;
          v79 = v27;
          appendString_73(&v124, &v78);
          v78 = TM__8FyyixzftvDEeBWCL79bP9aA_68;
          v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_67;
          appendString_73(&v124, &v78);
          v78 = v151;
          v79 = v152;
          appendString_73(&v124, &v78);
          v78 = TM__8FyyixzftvDEeBWCL79bP9aA_69;
          v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_63;
          appendString_73(&v124, &v78);
          v140 = 1699i64;
          v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          v28 = _emutls_get_address(refptr___emutls_v_global_save_level_path__modelZmodel95types_u78);
          v78 = v124;
          v79 = v125;
          eqsink___system_u2667(v28, &v78);
          v140 = 708i64;
          v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
          v122 = 0i64;
          v123 = 0i64;
          v170 = 0i64;
          v29 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
          v78 = *refptr_loaded_level__modelZmodel95types_u830;
          v79 = v29;
          v170 = X5BX5D___modelZcampaigns_u16467(refptr_level_progress__modelZmodel95types_u825, &v78);
          if ( *v177 )
            goto LABEL_117;
          v30 = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_level_path__modelZmodel95types_u78);
          rawNewString(&v78, *v30 + *(_QWORD *)(v170 + 8) + 1);
          v122 = v78;
          v123 = v79;
          v31 = (char *)v30[1];
          v78 = *v30;
          v79 = v31;
          appendString_73(&v122, &v78);
          v32 = *(char **)(v170 + 16);
          v78 = *(_QWORD *)(v170 + 8);
          v79 = v32;
          appendString_73(&v122, &v78);
          v78 = TM__8FyyixzftvDEeBWCL79bP9aA_70;
          v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_63;
          appendString_73(&v122, &v78);
          v140 = 1699i64;
          v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          v33 = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_arch_path__modelZmodel95types_u79);
          v78 = v122;
          v79 = v123;
          eqsink___system_u2667(v33, &v78);
          v140 = 709i64;
          v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
          v120 = 0i64;
          v121 = 0i64;
          rawNewString(&v78, *v33 + 8);
          v120 = v78;
          v121 = v79;
          v34 = (char *)v33[1];
          v78 = *v33;
          v79 = v34;
          appendString_73(&v120, &v78);
          v78 = TM__8FyyixzftvDEeBWCL79bP9aA_72;
          v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_71;
          appendString_73(&v120, &v78);
          v140 = 1699i64;
          v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          v35 = _emutls_get_address(refptr___emutls_v_global_save_schematic_path__modelZmodel95types_u80);
          v78 = v120;
          v79 = v121;
          eqsink___system_u2667(v35, &v78);
        }
        else
        {
          v140 = 712i64;
          v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
          v118 = 0i64;
          v119 = 0i64;
          v36 = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_base_path__modelZmodel95types_u77);
          rawNewString(&v78, *v36 + v151 + 13);
          v118 = v78;
          v119 = v79;
          v37 = (char *)v36[1];
          v78 = *v36;
          v79 = v37;
          appendString_73(&v118, &v78);
          v78 = TM__8FyyixzftvDEeBWCL79bP9aA_73;
          v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_67;
          appendString_73(&v118, &v78);
          v78 = v151;
          v79 = v152;
          appendString_73(&v118, &v78);
          v78 = TM__8FyyixzftvDEeBWCL79bP9aA_74;
          v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_63;
          appendString_73(&v118, &v78);
          v140 = 1699i64;
          v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          v38 = _emutls_get_address(refptr___emutls_v_global_save_level_path__modelZmodel95types_u78);
          v78 = v118;
          v79 = v119;
          eqsink___system_u2667(v38, &v78);
          v140 = 714i64;
          v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
          v116 = 0i64;
          v117 = 0i64;
          v169 = 0i64;
          v39 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
          v78 = *refptr_loaded_level__modelZmodel95types_u830;
          v79 = v39;
          v169 = X5BX5D___modelZcampaigns_u16467(refptr_level_progress__modelZmodel95types_u825, &v78);
          if ( *v177 )
            goto LABEL_117;
          v40 = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_level_path__modelZmodel95types_u78);
          rawNewString(&v78, *v40 + *(_QWORD *)(v169 + 8) + 1);
          v116 = v78;
          v117 = v79;
          v41 = (char *)v40[1];
          v78 = *v40;
          v79 = v41;
          appendString_73(&v116, &v78);
          v42 = *(char **)(v169 + 16);
          v78 = *(_QWORD *)(v169 + 8);
          v79 = v42;
          appendString_73(&v116, &v78);
          v78 = TM__8FyyixzftvDEeBWCL79bP9aA_75;
          v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_63;
          appendString_73(&v116, &v78);
          v140 = 1699i64;
          v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          v43 = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_arch_path__modelZmodel95types_u79);
          v78 = v116;
          v79 = v117;
          eqsink___system_u2667(v43, &v78);
          v44 = _emutls_get_address(refptr___emutls_v_global_save_schematic_path__modelZmodel95types_u80);
          v45 = (char *)v43[1];
          v78 = *v43;
          v79 = v45;
          eqcopy___system_u2661(v44, &v78);
        }
      }
      v140 = 717i64;
      v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
      v46 = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_schematic_path__modelZmodel95types_u80);
      v47 = (char *)v46[1];
      v78 = *v46;
      v79 = v47;
      noscreateDir(&v78);
      if ( !*v177 )
      {
        v140 = 720i64;
        v48 = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_base_path__modelZmodel95types_u77);
        v49 = (char *)v48[1];
        v78 = *v48;
        v79 = v49;
        as_sanitized_folder_name__modelZsanitized95path_u1302(&v145, &v78);
        if ( !*v177 )
        {
          v140 = 722i64;
          get_completed_levels__modelZutilities_u6010(&v143);
          if ( !*v177 )
          {
            v140 = 724i64;
            v168 = 0;
            v78 = TM__8FyyixzftvDEeBWCL79bP9aA_103;
            v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_102;
            v168 = is_complete__modelZcampaigns_u16328(&v78);
            if ( !*v177 )
            {
              v140 = 719i64;
              v50 = v168;
              v51 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
              v78 = *refptr_loaded_level__modelZmodel95types_u830;
              v79 = v51;
              v76 = TM__8FyyixzftvDEeBWCL79bP9aA_101;
              v77 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_100;
              v52 = eqStrings_19(&v78, &v76);
              v78 = v145;
              v79 = v146;
              v76 = v143;
              v77 = v144;
              architecture_get_all__modelZutilities_u7406(
                (unsigned int)&v147,
                (unsigned int)&v78,
                (unsigned int)&v151,
                (unsigned int)&v76,
                v52,
                v50);
              if ( !*v177 )
              {
                v181 = 0;
                v140 = 726i64;
                v180 = 0;
                v179 = 0;
                v178 = 0;
                v78 = v80;
                v79 = v81;
                v76 = TM__8FyyixzftvDEeBWCL79bP9aA_104;
                v77 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_44;
                v53 = eqStrings_19(&v78, &v76);
                v178 = v53 == 0;
                if ( !v53 )
                {
                  v78 = v80;
                  v79 = v81;
                  v76 = TM__8FyyixzftvDEeBWCL79bP9aA_105;
                  v77 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_100;
                  v178 = (unsigned __int8)eqStrings_19(&v78, &v76) == 0;
                }
                v179 = v178;
                if ( v178 )
                {
                  v78 = v80;
                  v79 = v81;
                  v76 = TM__8FyyixzftvDEeBWCL79bP9aA_106;
                  v77 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_4;
                  v179 = (unsigned __int8)eqStrings_19(&v78, &v76) == 0;
                }
                v180 = v179;
                if ( v179 )
                {
                  v140 = 727i64;
                  v78 = v80;
                  v79 = v81;
                  v76 = TM__8FyyixzftvDEeBWCL79bP9aA_108;
                  v77 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_107;
                  v180 = (unsigned __int8)eqStrings_19(&v78, &v76) == 0;
                }
                v181 = v180;
                if ( v180 )
                {
                  v78 = v80;
                  v79 = v81;
                  v76 = TM__8FyyixzftvDEeBWCL79bP9aA_110;
                  v77 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_109;
                  v181 = (unsigned __int8)eqStrings_19(&v78, &v76) == 0;
                }
                if ( !v181
                  || (v140 = 728i64, v78 = v80, v79 = v81, set_progress_string__modelZsave_u1683(1i64, &v78), !*v177) )
                {
                  v140 = 730i64;
                  if ( !v158 )
                    goto LABEL_60;
                  v114 = 0i64;
                  v115 = 0i64;
                  v112 = 0i64;
                  v113 = 0i64;
                  v140 = 731i64;
                  v110 = 0i64;
                  v111 = 0i64;
                  v54 = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_arch_path__modelZmodel95types_u79);
                  rawNewString(&v78, *v54 + 8);
                  v110 = v78;
                  v111 = v79;
                  v55 = (char *)v54[1];
                  v78 = *v54;
                  v79 = v55;
                  appendString_73(&v110, &v78);
                  v78 = TM__8FyyixzftvDEeBWCL79bP9aA_112;
                  v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_111;
                  appendString_73(&v110, &v78);
                  v114 = v110;
                  v115 = v111;
                  v140 = 732i64;
                  v108 = 0i64;
                  v109 = 0i64;
                  rawNewString(&v78, *v54 + 8);
                  v108 = v78;
                  v109 = v79;
                  v56 = (char *)v54[1];
                  v78 = *v54;
                  v79 = v56;
                  appendString_73(&v108, &v78);
                  v78 = TM__8FyyixzftvDEeBWCL79bP9aA_113;
                  v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_111;
                  appendString_73(&v108, &v78);
                  v112 = v108;
                  v113 = v109;
                  v167 = 0;
                  v78 = v108;
                  v79 = v109;
                  v167 = nosfileExists(&v78);
                  if ( !*v177 && !v167 )
                  {
                    v140 = 733i64;
                    v57 = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_arch_path__modelZmodel95types_u79);
                    v58 = (char *)v57[1];
                    v78 = *v57;
                    v79 = v58;
                    noscreateDir(&v78);
                    if ( !*v177 )
                    {
                      v140 = 734i64;
                      v78 = v114;
                      v79 = v115;
                      v76 = v158;
                      v77 = v159;
                      writeFile__stdZsyncio_u629(&v78, &v76);
                    }
                  }
                  v140 = 394i64;
                  v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                  if ( v113 && (*(_QWORD *)v113 & 0x4000000000000000i64) == 0 )
                    deallocShared(v113);
                  if ( v115 && (*(_QWORD *)v115 & 0x4000000000000000i64) == 0 )
                    deallocShared(v115);
                  if ( !*v177 )
                  {
LABEL_60:
                    v140 = 736i64;
                    v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
                    v166 = 0;
                    v166 = immutable_loaded__modelZboardZboard_u17313();
                    if ( !*v177 )
                    {
                      if ( v166 != 1 )
                      {
                        v140 = 740i64;
                        v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
                        v164 = 0;
                        if ( v148 )
                          v61 = v148 + 8;
                        else
                          v61 = 0i64;
                        v78 = v149;
                        v79 = v150;
                        v164 = contains__modelZutilities_u8206(v61, v147, &v78);
                        if ( v164 != 1 )
                        {
                          v86 = 0i64;
                          v87 = 0i64;
                          v140 = 763i64;
                          v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
                          if ( v147 > 0 )
                          {
                            v70 = (char *)*((_QWORD *)v148 + 2);
                            v76 = *((_QWORD *)v148 + 1);
                            v77 = v70;
                            to_string__modelZsanitized95path_u445(&v78, &v76);
                            v86 = v78;
                            v87 = v79;
                            if ( !*v177 )
                            {
                              v140 = 764i64;
                              if ( v154 == 3 )
                              {
                                v140 = 1699i64;
                                v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                                v78 = v86;
                                v79 = v87;
                                eqcopy___system_u2661(refptr_loaded_architecture__modelZmodel95types_u831, &v78);
                              }
                              v140 = 767i64;
                              v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
                              v160 = 0i64;
                              v71 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
                              v78 = *refptr_loaded_level__modelZmodel95types_u830;
                              v79 = v71;
                              v160 = X5BX5D___modelZcampaigns_u16467(
                                       refptr_level_progress__modelZmodel95types_u825,
                                       &v78);
                              if ( !*v177 )
                              {
                                v140 = 1699i64;
                                v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                                v78 = v86;
                                v79 = v87;
                                eqsink___system_u2667(v160 + 8, &v78);
                                eqwasMoved___system_u2658(&v86);
                                v140 = 769i64;
                                v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
                                v78 = v80;
                                v79 = v81;
                                load_level__modelZutilities_u7564(a1, &v78);
                              }
                            }
                          }
                          else
                          {
                            raiseIndexError2(0i64, v147 - 1);
                          }
                          v140 = 394i64;
                          v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                          if ( v87 && (*(_QWORD *)v87 & 0x4000000000000000i64) == 0 )
                            deallocShared(v87);
                        }
                        else
                        {
                          v100 = 0i64;
                          v101 = 0i64;
                          v98 = 0i64;
                          v99 = 0i64;
                          v96 = 0i64;
                          v97 = 0i64;
                          v94 = 0i64;
                          v95 = 0i64;
                          v92 = 0i64;
                          v93 = 0i64;
                          v90 = 0i64;
                          v91 = 0i64;
                          nimZeroMem_118(v83, 48i64);
                          v88 = 0i64;
                          v89 = 0i64;
                          v140 = 742i64;
                          v62 = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_level_path__modelZmodel95types_u78);
                          v63 = (char *)v62[1];
                          v78 = *v62;
                          v79 = v63;
                          as_sanitized_folder_name__modelZsanitized95path_u1302(&v98, &v78);
                          if ( !*v177 )
                          {
                            v78 = v98;
                            v79 = v99;
                            v76 = v149;
                            v77 = v150;
                            slash___modelZsanitized95path_u1477(&v96, &v78, &v76);
                            if ( !*v177 )
                            {
                              v140 = 743i64;
                              default_path__modelZutilities_u7363(&v94);
                              if ( !*v177 )
                              {
                                v78 = v96;
                                v79 = v97;
                                v76 = v94;
                                v77 = v95;
                                slash___modelZsave_u2259(&v100, &v78, &v76);
                                if ( !*v177 )
                                {
                                  v140 = 745i64;
                                  v78 = v100;
                                  v79 = v101;
                                  to_absolute_path__modelZsave_u2267(&v90, &v78);
                                  if ( !*v177 )
                                  {
                                    v78 = v90;
                                    v79 = v91;
                                    v76 = TM__8FyyixzftvDEeBWCL79bP9aA_118;
                                    v77 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_2;
                                    file_get_bytes__modelZsave95mongerZsave95monger_u38(&v92, &v78, &v76);
                                    if ( !*v177 )
                                    {
                                      v140 = 748i64;
                                      get_completed_levels__modelZutilities_u6010(&v88);
                                      if ( !*v177 )
                                      {
                                        v140 = 752i64;
                                        progress_bool__modelZsave_u1666 = 0;
                                        progress_bool__modelZsave_u1666 = get_progress_bool__modelZsave_u1666(6i64);
                                        if ( !*v177 )
                                        {
                                          v140 = 746i64;
                                          nimZeroMem_118(v82, 40i64);
                                          v64 = *(unsigned __int8 *)refptr_is_campaign__modelZmodel95types_u726;
                                          v65 = *(unsigned __int8 *)refptr_dev_mode__modelZmodel95types_u727;
                                          v66 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
                                          v78 = *refptr_loaded_level__modelZmodel95types_u830;
                                          v79 = v66;
                                          v76 = v88;
                                          v77 = v89;
                                          v67 = *((_QWORD *)refptr_campaign__modelZmodel95types_u817 + 1);
                                          v73 = *(_QWORD *)refptr_campaign__modelZmodel95types_u817;
                                          v74 = v67;
                                          v75 = *((_QWORD *)refptr_campaign__modelZmodel95types_u817 + 2);
                                          get_budget__modelZboardZschematics_u2168(
                                            (unsigned int)&v78,
                                            (unsigned int)&v76,
                                            (unsigned int)&v73,
                                            v65,
                                            v64,
                                            progress_bool__modelZsave_u1666,
                                            (__int64)v82);
                                          if ( !*v177 )
                                          {
                                            v140 = 754i64;
                                            some__modelZutilities_u8335(v82, v83);
                                            if ( !*v177 )
                                            {
                                              v140 = 756i64;
                                              v78 = v92;
                                              v79 = v93;
                                              v162 = load_schematic__modelZboardZschematics_u1650(
                                                       a1,
                                                       v153,
                                                       &v78,
                                                       v154,
                                                       (__int64)v83);
                                              if ( !*v177 )
                                              {
                                                v140 = 758i64;
                                                clone_buffer_reset_data_files__modelZutilities_u6846(a1);
                                                if ( !*v177 )
                                                {
                                                  v140 = 203i64;
                                                  v161 = 0i64;
                                                  v68 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
                                                  v78 = *refptr_loaded_level__modelZmodel95types_u830;
                                                  v79 = v68;
                                                  v161 = X5BX5D___modelZboardZboard_u17368(
                                                           refptr_campaign__modelZmodel95types_u817,
                                                           &v78);
                                                  if ( !*v177 )
                                                  {
                                                    v140 = 759i64;
                                                    v69 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
                                                    v78 = *refptr_loaded_level__modelZmodel95types_u830;
                                                    v79 = v69;
                                                    apply_load_morph__modelZutilities_u2304(a1 + 152, &v78, v161);
                                                    if ( !*v177 )
                                                    {
                                                      v140 = 761i64;
                                                      set_command_setting__modelZsimulator95types_u130(2i64, v162);
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
                                }
                              }
                            }
                          }
                          v140 = 2128i64;
                          v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                          v78 = v88;
                          v79 = v89;
                          eqdestroy___system_u3734(&v78);
                          v140 = 35i64;
                          v141 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
                          eqdestroy___modelZboardZschematics_u1629(v83);
                          v140 = 394i64;
                          v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                          if ( v91 && (*(_QWORD *)v91 & 0x4000000000000000i64) == 0 )
                            deallocShared(v91);
                          v140 = 1772i64;
                          v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\times.nim";
                          v78 = v92;
                          v79 = v93;
                          eqdestroy___pureZtimes_u2668(&v78);
                          v140 = 394i64;
                          v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                          if ( v95 && (*(_QWORD *)v95 & 0x4000000000000000i64) == 0 )
                            deallocShared(v95);
                          if ( v97 && (*(_QWORD *)v97 & 0x4000000000000000i64) == 0 )
                            deallocShared(v97);
                          if ( v99 && (*(_QWORD *)v99 & 0x4000000000000000i64) == 0 )
                            deallocShared(v99);
                          if ( v101 && (*(_QWORD *)v101 & 0x4000000000000000i64) == 0 )
                            deallocShared(v101);
                        }
                      }
                      else
                      {
                        v106 = 0i64;
                        v107 = 0i64;
                        v104 = 0i64;
                        v105 = 0i64;
                        nimZeroMem_118(v83, 48i64);
                        v140 = 737i64;
                        v102 = 0i64;
                        v103 = 0i64;
                        rawNewString(
                          &v78,
                          *refptr_campaign_name__modelZmodel95types_u826
                        + *refptr_loaded_level__modelZmodel95types_u830
                        + 14);
                        v102 = v78;
                        v103 = v79;
                        v59 = (char *)refptr_campaign_name__modelZmodel95types_u826[1];
                        v78 = *refptr_campaign_name__modelZmodel95types_u826;
                        v79 = v59;
                        appendString_73(&v102, &v78);
                        v78 = TM__8FyyixzftvDEeBWCL79bP9aA_114;
                        v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_63;
                        appendString_73(&v102, &v78);
                        v60 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
                        v78 = *refptr_loaded_level__modelZmodel95types_u830;
                        v79 = v60;
                        appendString_73(&v102, &v78);
                        v78 = TM__8FyyixzftvDEeBWCL79bP9aA_115;
                        v79 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_94;
                        appendString_73(&v102, &v78);
                        v104 = v102;
                        v105 = v103;
                        v78 = v102;
                        v79 = v103;
                        v76 = TM__8FyyixzftvDEeBWCL79bP9aA_116;
                        v77 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_2;
                        file_get_bytes__modelZsave95mongerZsave95monger_u38(&v106, &v78, &v76);
                        if ( !*v177 )
                        {
                          v140 = 119i64;
                          v141 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
                          none__modelZboardZschematics_u1660_0(v83);
                          if ( !*v177 )
                          {
                            v140 = 738i64;
                            v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
                            v78 = v106;
                            v79 = v107;
                            v165 = load_schematic__modelZboardZschematics_u1650(a1, v153, &v78, v154, (__int64)v83);
                            if ( !*v177 )
                            {
                              v140 = 739i64;
                              if ( v165 >= 0 )
                                set_command_setting__modelZsimulator95types_u130(2i64, v165);
                              else
                                raiseRangeErrorNoArgs();
                            }
                          }
                        }
                        v140 = 35i64;
                        v141 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
                        eqdestroy___modelZboardZschematics_u1629(v83);
                        v140 = 394i64;
                        v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                        if ( v105 && (*(_QWORD *)v105 & 0x4000000000000000i64) == 0 )
                          deallocShared(v105);
                        v140 = 1772i64;
                        v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\times.nim";
                        v78 = v106;
                        v79 = v107;
                        eqdestroy___pureZtimes_u2668(&v78);
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
  }
LABEL_117:
  v140 = 2128i64;
  v78 = v143;
  v79 = v144;
  eqdestroy___system_u3734(&v78);
  v140 = 394i64;
  if ( v146 && (*(_QWORD *)v146 & 0x4000000000000000i64) == 0 )
    deallocShared(v146);
  v140 = 651i64;
  v78 = v147;
  v79 = v148;
  eqdestroy___modelZsanitized95path_u794(&v78);
  v140 = 394i64;
  if ( v150 && (*(_QWORD *)v150 & 0x4000000000000000i64) == 0 )
    deallocShared(v150);
  v140 = 674i64;
  v141 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  *(_WORD *)(a1 + 202) = v153;
LABEL_124:
  v140 = 770i64;
  v141 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
  eqdestroy___modelZboardZschematics_u4043(&v151);
  return popFrame_145();
}
