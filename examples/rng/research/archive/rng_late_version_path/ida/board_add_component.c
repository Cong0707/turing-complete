// address: 0x140243dca-0x1402469c8
// name: board_add_component__modelZboardZboard_u21118
__int64 __fastcall board_add_component__modelZboardZboard_u21118(
        __int64 a1,
        unsigned __int8 a2,
        __int64 *a3,
        unsigned int a4,
        char a5,
        __int64 a6,
        __int64 *a7,
        __int64 *a8,
        __int64 a9,
        __int64 a10,
        char a11,
        __int64 *a12,
        __int64 *a13,
        __int64 a14,
        __int64 *a15,
        __int64 *a16,
        __int16 a17,
        __int64 *a18,
        char a19)
{
  __int64 v21; // rdx
  __int64 v22; // rdx
  __int64 v23; // rdx
  __int64 v24; // rdx
  __int64 v25; // rdx
  __int64 v26; // rdx
  __int64 v27; // rdx
  __int64 v28; // rdx
  __int64 v29; // rdx
  char *v30; // rax
  __int64 v31; // rbx
  __int64 v32; // rbx
  __int64 v33; // rbx
  __int64 v34; // rbx
  __int64 v35; // rbx
  char *v36; // rax
  __int64 v37; // rbx
  __int64 v38; // rbx
  __int64 v39; // rbx
  __int64 v40; // rbx
  __int64 v41; // rbx
  __int64 v42; // rdx
  __int64 v43; // rdx
  __int64 v44; // rdx
  __int64 v45; // rbx
  __int64 v46; // rbx
  __int64 v47; // rbx
  __int64 v48; // rdx
  __int64 v50; // [rsp+20h] [rbp-60h] BYREF
  __int64 v51; // [rsp+28h] [rbp-58h]
  __int64 v52; // [rsp+30h] [rbp-50h]
  __int64 v53; // [rsp+40h] [rbp-40h] BYREF
  __int64 v54; // [rsp+48h] [rbp-38h]
  __int64 v55; // [rsp+50h] [rbp-30h]
  __int64 v56; // [rsp+60h] [rbp-20h] BYREF
  char *v57; // [rsp+68h] [rbp-18h]
  __int64 v58; // [rsp+70h] [rbp-10h]
  char *v59; // [rsp+78h] [rbp-8h]
  __int64 v60; // [rsp+80h] [rbp+0h]
  char *v61; // [rsp+88h] [rbp+8h]
  __int64 v62; // [rsp+90h] [rbp+10h]
  char *v63; // [rsp+98h] [rbp+18h]
  __int64 v64; // [rsp+A0h] [rbp+20h]
  char *v65; // [rsp+A8h] [rbp+28h]
  char v66; // [rsp+B0h] [rbp+30h]
  __int16 v67; // [rsp+B4h] [rbp+34h]
  char v68; // [rsp+B8h] [rbp+38h]
  char v69; // [rsp+BCh] [rbp+3Ch]
  __int64 v70[182]; // [rsp+C0h] [rbp+40h] BYREF
  __int64 v71; // [rsp+670h] [rbp+5F0h]
  __int64 v72; // [rsp+678h] [rbp+5F8h]
  __int64 v73; // [rsp+680h] [rbp+600h]
  __int64 v74; // [rsp+688h] [rbp+608h]
  __int64 v75; // [rsp+690h] [rbp+610h] BYREF
  char *v76; // [rsp+698h] [rbp+618h]
  char v77[8]; // [rsp+6A0h] [rbp+620h] BYREF
  const char *v78; // [rsp+6A8h] [rbp+628h]
  __int64 v79; // [rsp+6B0h] [rbp+630h]
  const char *v80; // [rsp+6B8h] [rbp+638h]
  __int16 v81; // [rsp+6C0h] [rbp+640h]
  __int64 v82; // [rsp+6D8h] [rbp+658h]
  __int64 v83; // [rsp+6E0h] [rbp+660h]
  _QWORD *v84; // [rsp+6E8h] [rbp+668h]
  __int64 v85; // [rsp+6F0h] [rbp+670h]
  __int64 v86; // [rsp+6F8h] [rbp+678h]
  __int64 v87; // [rsp+700h] [rbp+680h]
  __int64 v88; // [rsp+708h] [rbp+688h]
  __int64 v89[4]; // [rsp+710h] [rbp+690h] BYREF
  __int64 v90[4]; // [rsp+730h] [rbp+6B0h] BYREF
  __int64 v91; // [rsp+750h] [rbp+6D0h] BYREF
  char *v92; // [rsp+758h] [rbp+6D8h]
  __int64 v93; // [rsp+760h] [rbp+6E0h] BYREF
  char *v94; // [rsp+768h] [rbp+6E8h]
  __int64 v95; // [rsp+770h] [rbp+6F0h] BYREF
  char *v96; // [rsp+778h] [rbp+6F8h]
  __int64 v97; // [rsp+780h] [rbp+700h] BYREF
  __int64 v98; // [rsp+788h] [rbp+708h]
  __int64 v99[3]; // [rsp+790h] [rbp+710h] BYREF
  __int64 v100; // [rsp+7A8h] [rbp+728h] BYREF
  __int64 v101[4]; // [rsp+7B0h] [rbp+730h] BYREF
  __int64 v102; // [rsp+7D0h] [rbp+750h] BYREF
  __int64 v103; // [rsp+7D8h] [rbp+758h]
  int v104; // [rsp+7ECh] [rbp+76Ch] BYREF
  __int64 v105[70]; // [rsp+7F0h] [rbp+770h] BYREF
  __int64 v106; // [rsp+A20h] [rbp+9A0h] BYREF
  _QWORD *v107; // [rsp+A28h] [rbp+9A8h]
  __int64 v108; // [rsp+A30h] [rbp+9B0h] BYREF
  char *v109; // [rsp+A38h] [rbp+9B8h]
  char v110[96]; // [rsp+A40h] [rbp+9C0h] BYREF
  __int64 v111; // [rsp+AA0h] [rbp+A20h]
  __int64 v112; // [rsp+AB0h] [rbp+A30h]
  __int64 v113; // [rsp+AC0h] [rbp+A40h]
  __int64 v114; // [rsp+FF0h] [rbp+F70h] BYREF
  char *v115; // [rsp+FF8h] [rbp+F78h]
  __int64 v116; // [rsp+1000h] [rbp+F80h]
  __int64 v117; // [rsp+1008h] [rbp+F88h]
  __int64 v118; // [rsp+1010h] [rbp+F90h]
  __int64 v119; // [rsp+1018h] [rbp+F98h]
  char v121; // [rsp+102Fh] [rbp+FAFh]
  __int64 v122; // [rsp+1030h] [rbp+FB0h]
  __int64 v123; // [rsp+1038h] [rbp+FB8h]
  __int64 v124; // [rsp+1040h] [rbp+FC0h]
  __int64 v125; // [rsp+1048h] [rbp+FC8h]
  __int64 v126; // [rsp+1050h] [rbp+FD0h]
  __int64 v127; // [rsp+1058h] [rbp+FD8h]
  __int64 v128; // [rsp+1060h] [rbp+FE0h]
  __int64 v129; // [rsp+1068h] [rbp+FE8h]
  __int64 v130; // [rsp+1070h] [rbp+FF0h]
  __int64 v131; // [rsp+1078h] [rbp+FF8h]
  __int64 v132; // [rsp+1080h] [rbp+1000h]
  __int64 v133; // [rsp+1088h] [rbp+1008h]
  __int64 v134; // [rsp+1090h] [rbp+1010h]
  char v135; // [rsp+109Fh] [rbp+101Fh]
  __int64 v136; // [rsp+10A0h] [rbp+1020h]
  __int64 v137; // [rsp+10A8h] [rbp+1028h]
  __int64 v138; // [rsp+10B0h] [rbp+1030h]
  __int64 v139; // [rsp+10B8h] [rbp+1038h]
  char v140; // [rsp+10C7h] [rbp+1047h]
  __int64 v141; // [rsp+10C8h] [rbp+1048h]
  __int64 v142; // [rsp+10D0h] [rbp+1050h]
  __int64 *v143; // [rsp+10D8h] [rbp+1058h]
  __int64 v144; // [rsp+10E0h] [rbp+1060h]
  _QWORD *v145; // [rsp+10E8h] [rbp+1068h]
  __int64 v146; // [rsp+10F0h] [rbp+1070h]
  __int64 v147; // [rsp+10F8h] [rbp+1078h]
  __int64 *v148; // [rsp+1100h] [rbp+1080h]
  __int64 v149; // [rsp+1108h] [rbp+1088h]
  char v150; // [rsp+1110h] [rbp+1090h]
  char valid; // [rsp+1111h] [rbp+1091h]
  char v152; // [rsp+1112h] [rbp+1092h]
  char v153; // [rsp+1113h] [rbp+1093h]
  __int16 v154; // [rsp+1114h] [rbp+1094h]
  char v155; // [rsp+1117h] [rbp+1097h]
  __int64 v156; // [rsp+1118h] [rbp+1098h]
  unsigned __int8 v157; // [rsp+1127h] [rbp+10A7h]
  _BYTE *v158; // [rsp+1128h] [rbp+10A8h]
  bool v159; // [rsp+1137h] [rbp+10B7h]
  __int64 v160; // [rsp+1138h] [rbp+10B8h]
  __int64 v161; // [rsp+1140h] [rbp+10C0h]
  __int64 v162; // [rsp+1148h] [rbp+10C8h]
  bool v163; // [rsp+1157h] [rbp+10D7h]
  __int64 v164; // [rsp+1158h] [rbp+10D8h]
  char v165; // [rsp+1165h] [rbp+10E5h]
  char v166; // [rsp+1166h] [rbp+10E6h]
  char v167; // [rsp+1167h] [rbp+10E7h]
  __int64 v168; // [rsp+1168h] [rbp+10E8h]
  unsigned __int16 v169; // [rsp+1176h] [rbp+10F6h]
  __int64 v170; // [rsp+1178h] [rbp+10F8h]
  unsigned __int8 v172; // [rsp+11C8h] [rbp+1148h]

  v21 = a7[1];
  v64 = *a7;
  v65 = (char *)v21;
  v22 = a8[1];
  v62 = *a8;
  v63 = (char *)v22;
  v23 = a16[1];
  v60 = *a16;
  v61 = (char *)v23;
  v24 = a18[1];
  v58 = *a18;
  v59 = (char *)v24;
  v172 = a2;
  v69 = a5;
  v68 = a11;
  v67 = a17;
  v66 = a19;
  v78 = "board_add_component";
  v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  v79 = 0i64;
  v81 = 0;
  nimFrame_73(v77);
  v158 = (_BYTE *)nimErrorFlag_71();
  v170 = 0i64;
  v114 = 0i64;
  v115 = 0i64;
  nimZeroMem_53(v110, 1448i64);
  v108 = 0i64;
  v109 = 0i64;
  v106 = 0i64;
  v107 = 0i64;
  nimZeroMem_53(v105, 560i64);
  v157 = 0;
  v156 = 0i64;
  nimZeroMem_53(&v104, 4i64);
  v155 = 0;
  v102 = 0i64;
  v103 = 0i64;
  nimZeroMem_53(v101, 24i64);
  nimZeroMem_53(&v100, 8i64);
  nimZeroMem_53(v99, 24i64);
  v154 = 0;
  v97 = 0i64;
  v98 = 0i64;
  v95 = 0i64;
  v96 = 0i64;
  v93 = 0i64;
  v94 = 0i64;
  v91 = 0i64;
  v92 = 0i64;
  nimZeroMem_53(v90, 24i64);
  v153 = 0;
  nimZeroMem_53(v89, 24i64);
  v152 = 0;
  v79 = 1072i64;
  v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  v167 = 0;
  v166 = v172 == 78;
  if ( v172 == 78 )
  {
    v166 = notin_custom_prototypes__modelZboardZcustom95prototype95list_u189(a9);
    if ( *v158 )
      goto LABEL_135;
  }
  v167 = v166;
  if ( !v166 )
  {
    v79 = 1073i64;
    v167 = ((TM__CKxtw4nX41tlcDT9cZT8kGA_2[v172 >> 3] >> (v172 & 7)) & 1) != 0;
  }
  if ( v167 == 1 )
  {
    v170 = -1i64;
    v79 = 34i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    v56 = v91;
    v57 = v92;
    eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
    v56 = v93;
    v57 = v94;
    eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
    v56 = v95;
    v57 = v96;
    eqdestroy___modelZsave95mongerZversionsZv0_u448(&v56);
    eqdestroy___modelZsave95mongerZversionsZv0_u145(v105);
    v79 = 394i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v107 && (*v107 & 0x4000000000000000i64) == 0 )
      deallocShared(v107);
    v79 = 34i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    v56 = v108;
    v57 = v109;
    eqdestroy___modelZsave95mongerZversionsZv0_u296(&v56);
    v79 = 170i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    eqdestroy___modelZboardZprototype95list_u3239(v110);
    v79 = 119i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
    v56 = v114;
    v57 = v115;
    eqdestroy___modelZsave95mongerZserialize_u455(&v56);
    goto LABEL_139;
  }
  v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  v88 = a6;
  v79 = 1078i64;
  valid = 0;
  valid = is_valid__modelZsave95mongerZcommon_u3408(a6);
  if ( *v158 )
    goto LABEL_135;
  if ( !valid )
  {
    v79 = 1079i64;
    v88 = new_permanent_id__modelZsave95mongerZcommon_u3402();
    if ( *v158 )
      goto LABEL_135;
  }
  v79 = 119i64;
  v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
  v56 = v60;
  v57 = v61;
  eqcopy___modelZsave95mongerZserialize_u458(&v114, &v56);
  v79 = 1082i64;
  v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  v150 = 0;
  v25 = *((_QWORD *)refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347 + 1);
  v53 = *(_QWORD *)refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347;
  v54 = v25;
  v55 = *((_QWORD *)refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347 + 2);
  v150 = contains__modelZboardZboard_u21313(&v53, v172);
  if ( *v158 )
    goto LABEL_135;
  if ( v150 == 1 )
  {
    v79 = 119i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
    v56 = v60;
    v57 = v61;
    eqcopy___modelZsave95mongerZserialize_u458(&v114, &v56);
    v79 = 1084i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    while ( 1 )
    {
      v149 = v114;
      v148 = 0i64;
      v148 = (__int64 *)X5BX5D___modelZsave95mongerZversionsZv7_u2794(
                          refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347,
                          v172);
      if ( *v158 )
        goto LABEL_135;
      v147 = *v148;
      if ( v149 >= v147 )
      {
        v79 = 1086i64;
        v143 = 0i64;
        v143 = (__int64 *)X5BX5D___modelZsave95mongerZversionsZv7_u2794(
                            refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347,
                            v172);
        if ( *v158 )
          goto LABEL_135;
        v142 = *v143;
        if ( v142 < 0 )
        {
          raiseRangeErrorI(v142, 0i64, 0x7FFFFFFFFFFFFFFFi64);
          goto LABEL_135;
        }
        setLen__modelZsave95mongerZserialize_u475(&v114, v142);
        break;
      }
      v146 = 0i64;
      v79 = 1085i64;
      v145 = 0i64;
      v145 = (_QWORD *)X5BX5D___modelZsave95mongerZversionsZv7_u2794(
                         refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347,
                         v172);
      if ( *v158 )
        goto LABEL_135;
      v144 = v114;
      if ( v114 < 0 || v144 >= *v145 )
      {
        raiseIndexError2(v144, *v145 - 1i64);
        goto LABEL_135;
      }
      v146 = *(_QWORD *)(v145[1] + 8 * v144 + 8);
      add__modelZsave95mongerZserialize_u151(&v114, v146);
    }
  }
  v87 = a10;
  v79 = 1090i64;
  v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  v141 = 0i64;
  v141 = X5BX5D___modelZboardZprototype95list_u4239(refptr_PROTOTYPES__modelZboardZprototype95list_u3752, v172);
  if ( *v158 )
  {
LABEL_135:
    v79 = 34i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    v56 = v91;
    v57 = v92;
    eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
    v56 = v93;
    v57 = v94;
    eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
    v56 = v95;
    v57 = v96;
    eqdestroy___modelZsave95mongerZversionsZv0_u448(&v56);
    eqdestroy___modelZsave95mongerZversionsZv0_u145(v105);
    v79 = 394i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v107 && (*v107 & 0x4000000000000000i64) == 0 )
      deallocShared(v107);
LABEL_138:
    v79 = 34i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    v56 = v108;
    v57 = v109;
    eqdestroy___modelZsave95mongerZversionsZv0_u296(&v56);
    v79 = 170i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    eqdestroy___modelZboardZprototype95list_u3239(v110);
    v79 = 119i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
    v56 = v114;
    v57 = v115;
    eqdestroy___modelZsave95mongerZserialize_u455(&v56);
    goto LABEL_139;
  }
  v79 = 170i64;
  v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  eqcopy___modelZboardZprototype95list_u3242(v110, v141);
  v79 = 1092i64;
  v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  if ( v172 != 78 )
  {
LABEL_37:
    v79 = 1097i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    if ( v110[0] == 4 )
    {
      v79 = 1098i64;
      v87 = bits__modelZsave95mongerZcommon_u192(1i64);
      if ( *v158 )
        goto LABEL_135;
    }
    v169 = 0;
    v79 = 1101i64;
    v165 = 0;
    v26 = refptr_PROTOTYPES__modelZboardZprototype95list_u3752[1];
    v53 = *refptr_PROTOTYPES__modelZboardZprototype95list_u3752;
    v54 = v26;
    v55 = refptr_PROTOTYPES__modelZboardZprototype95list_u3752[2];
    v165 = contains__modelZboardZboard_u10031(&v53, v172);
    if ( *v158 )
      goto LABEL_135;
    if ( v165 == 1 )
    {
      v139 = 0i64;
      v139 = X5BX5D___modelZboardZprototype95list_u4239(refptr_PROTOTYPES__modelZboardZprototype95list_u3752, v172);
      if ( *v158 )
        goto LABEL_135;
      v165 = *(_WORD *)(v139 + 66) != 0;
    }
    if ( v165 == 1 )
    {
      nimZeroMem_53(v70, 560i64);
      v138 = 0i64;
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      v164 = 0i64;
      v79 = 183i64;
      v137 = *(_QWORD *)a1;
      v136 = v137;
      v79 = 184i64;
      while ( v164 < v136 )
      {
        v138 = v164;
        v79 = 34i64;
        v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        if ( v164 < 0 || v164 >= *(_QWORD *)a1 )
        {
          raiseIndexError2(v164, *(_QWORD *)a1 - 1i64);
          break;
        }
        eqcopy___modelZsave95mongerZversionsZv0_u148(v70, *(_QWORD *)(a1 + 8) + 560 * v164 + 8);
        v79 = 1103i64;
        v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
        v135 = 0;
        v27 = refptr_PROTOTYPES__modelZboardZprototype95list_u3752[1];
        v53 = *refptr_PROTOTYPES__modelZboardZprototype95list_u3752;
        v54 = v27;
        v55 = refptr_PROTOTYPES__modelZboardZprototype95list_u3752[2];
        v135 = contains__modelZboardZboard_u10031(&v53, LOBYTE(v70[0]));
        if ( *v158 )
          break;
        if ( v135 == 1 )
        {
          v79 = 1106i64;
          v134 = 0i64;
          v134 = X5BX5D___modelZboardZprototype95list_u4239(
                   refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
                   LOBYTE(v70[0]));
          if ( *v158 )
            break;
          v79 = 1104i64;
          v169 = max__modelZtranslations_u5440_0(v169, (unsigned __int16)(LOWORD(v70[20]) + *(_WORD *)(v134 + 66)));
        }
        v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v164;
        v79 = 187i64;
        v133 = *(_QWORD *)a1;
        if ( v133 != v136 )
        {
          v56 = TM__CKxtw4nX41tlcDT9cZT8kGA_4;
          v57 = (char *)&TM__CKxtw4nX41tlcDT9cZT8kGA_3;
          failedAssertImpl__stdZassertions_u234(&v56);
          if ( *v158 )
            break;
        }
      }
      v79 = 34i64;
      v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      eqdestroy___modelZsave95mongerZversionsZv0_u145(v70);
      if ( *v158 )
        goto LABEL_135;
    }
    v56 = v58;
    v57 = v59;
    eqcopy___modelZsave95mongerZversionsZv0_u299(&v108, &v56);
    v79 = 1111i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    if ( v172 == 82 || v172 == 83 || v172 == 91 )
    {
      v79 = 1112i64;
      v132 = v108;
      if ( v108 <= 0 )
      {
        v79 = 1113i64;
        nimZeroMem_53(v70, 48i64);
        add__modelZsave95mongerZversionsZv7_u2572(&v108, v70);
      }
    }
    v79 = 1699i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v56 = v62;
    v57 = v63;
    eqcopy___system_u2661(&v106, &v56);
    v79 = 1117i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    v163 = v172 == 101;
    if ( v172 == 101 )
      v163 = v106 == 0;
    if ( v163 )
    {
      v79 = 1118i64;
      v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
      if ( v114 <= 0 )
      {
        raiseIndexError2(0i64, v114 - 1);
        goto LABEL_135;
      }
      v75 = 0i64;
      v76 = 0i64;
      dollar___systemZdollars_u59(&v75, *((_QWORD *)v115 + 1));
      if ( *v158 )
      {
        v56 = v75;
        v57 = v76;
        eqdestroy___system_u281_27(&v56);
        goto LABEL_135;
      }
      v79 = 1699i64;
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      v56 = v75;
      v57 = v76;
      eqsink___system_u2667(&v106, &v56);
    }
    v79 = 1120i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    nimZeroMem_53(v105, 560i64);
    v157 = v172;
    LOBYTE(v105[0]) = v172;
    v156 = a9;
    v105[49] = a9;
    v79 = 629i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    v104 = eqdup___modelZsave95mongerZcommon_u4321(a4);
    *(_DWORD *)((char *)v105 + 2) = v104;
    v155 = v69;
    BYTE6(v105[0]) = v69;
    v105[1] = v88;
    v85 = v114;
    v86 = (__int64)v115;
    v79 = 119i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
    eqwasMoved___modelZsave95mongerZserialize_u452(&v114);
    v105[21] = v85;
    v105[22] = v86;
    LOWORD(v105[20]) = v169;
    v79 = 1699i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v56 = v64;
    v57 = v65;
    eqdup___system_u2664(&v102, &v56);
    v105[24] = v102;
    v105[25] = v103;
    v83 = v106;
    v84 = v107;
    v79 = 1699i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    eqwasMoved___system_u2658(&v106);
    v105[26] = v83;
    v105[27] = (__int64)v84;
    v79 = 23i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v12.nim";
    v28 = a3[1];
    v50 = *a3;
    v51 = v28;
    v52 = a3[2];
    eqdup___modelZsave95mongerZversionsZv12_u295(&v53, &v50);
    v101[0] = v53;
    v101[1] = v54;
    v101[2] = v55;
    v105[46] = v53;
    v105[47] = v54;
    v105[48] = v55;
    v79 = 184i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    v100 = eqdup___modelZsave95mongerZcommon_u182(v87);
    v105[28] = v100;
    v79 = 1132i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    v105[29] = get_clamped_word_size__modelZboardZprototype95list_u4458(v172, v87, 0);
    if ( *v158 )
      goto LABEL_135;
    v79 = 123i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
    v29 = a15[1];
    v53 = *a15;
    v54 = v29;
    v55 = a15[2];
    eqdup___modelZsave95mongerZsave95monger_u880(&v50, &v53);
    v99[0] = v50;
    v99[1] = v51;
    v99[2] = v52;
    v105[53] = v50;
    v105[54] = v51;
    v105[55] = v52;
    v154 = v67;
    LOWORD(v105[23]) = v67;
    v79 = 34i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    v56 = v108;
    v57 = v109;
    eqdup___modelZsave95mongerZversionsZv0_u302(&v97, &v56);
    v105[30] = v97;
    v105[31] = v98;
    v131 = v108;
    v130 = v108;
    v79 = 1177i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
    if ( v108 < 0 )
    {
      raiseRangeErrorI(v130, 0i64, 0x7FFFFFFFFFFFFFFFi64);
      goto LABEL_135;
    }
    newSeq__modelZboardZboard_u21995(&v56, v130);
    v95 = v56;
    v96 = v57;
    v129 = 0i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v162 = 0i64;
    v79 = 129i64;
    while ( v162 < v130 )
    {
      v129 = v162;
      v79 = 934i64;
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v162 < 0 || v129 >= v95 )
      {
        raiseIndexError2(v129, v95 - 1);
        goto LABEL_135;
      }
      nimZeroMem_53(v70, 72i64);
      eqsink___modelZsave95mongerZversionsZv0_u523(&v96[72 * v129 + 8], v70);
      v79 = 131i64;
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v74 = v162 + 1;
      if ( __OFADD__(1i64, v162) )
        goto LABEL_120;
      v162 = v74;
    }
    v79 = 1136i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    v105[32] = v95;
    v105[33] = (__int64)v96;
    eqwasMoved___modelZsave95mongerZversionsZv0_u445(&v95);
    v79 = 1138i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    v128 = v111;
    v127 = v112;
    v82 = v111 + v112;
    if ( __OFADD__(v111, v112) )
    {
LABEL_120:
      raiseOverflow();
      goto LABEL_135;
    }
    v126 = v82;
    v79 = 1175i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
    if ( v82 < 0 )
    {
      raiseRangeErrorI(v126, 0i64, 0x7FFFFFFFFFFFFFFFi64);
      goto LABEL_135;
    }
    newSeqUninit__modelZboardZboard_u21887(&v56, v126);
    v93 = v56;
    v94 = v57;
    v125 = 0i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v161 = 0i64;
    v79 = 129i64;
    while ( v161 < v126 )
    {
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
      v125 = v161;
      v79 = 1179i64;
      if ( v161 < 0 || v125 >= v93 )
      {
        raiseIndexError2(v125, v93 - 1);
        goto LABEL_135;
      }
      v79 = 1138i64;
      v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
      nimZeroMem_53(v70, 80i64);
      v70[1] = 1i64;
      nimZeroMem_53(&v70[2], 8i64);
      v70[2] = 256i64;
      LOBYTE(v70[3]) = 1;
      v70[4] = 1i64;
      nimZeroMem_53(&v70[5], 8i64);
      v70[5] = 256i64;
      LOBYTE(v70[6]) = 1;
      v30 = &v94[80 * v125];
      v31 = v70[1];
      *((_QWORD *)v30 + 1) = v70[0];
      *((_QWORD *)v30 + 2) = v31;
      v32 = v70[3];
      *((_QWORD *)v30 + 3) = v70[2];
      *((_QWORD *)v30 + 4) = v32;
      v33 = v70[5];
      *((_QWORD *)v30 + 5) = v70[4];
      *((_QWORD *)v30 + 6) = v33;
      v34 = v70[7];
      *((_QWORD *)v30 + 7) = v70[6];
      *((_QWORD *)v30 + 8) = v34;
      v35 = v70[9];
      *((_QWORD *)v30 + 9) = v70[8];
      *((_QWORD *)v30 + 10) = v35;
      v79 = 131i64;
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v73 = v161 + 1;
      if ( __OFADD__(1i64, v161) )
        goto LABEL_120;
      v161 = v73;
    }
    v79 = 1137i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    v105[6] = v93;
    v105[7] = (__int64)v94;
    eqwasMoved___modelZsave95mongerZversionsZv0_u169(&v93);
    v124 = v113;
    v123 = v113;
    v79 = 1175i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
    if ( v113 < 0 )
    {
      raiseRangeErrorI(v123, 0i64, 0x7FFFFFFFFFFFFFFFi64);
      goto LABEL_135;
    }
    newSeqUninit__modelZboardZboard_u21887(&v56, v123);
    v91 = v56;
    v92 = v57;
    v122 = 0i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v160 = 0i64;
    v79 = 129i64;
    while ( v160 < v123 )
    {
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
      v122 = v160;
      v79 = 1179i64;
      if ( v160 < 0 || v122 >= v91 )
      {
        raiseIndexError2(v122, v91 - 1);
        goto LABEL_135;
      }
      v79 = 1140i64;
      v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
      nimZeroMem_53(v70, 80i64);
      v70[1] = 1i64;
      nimZeroMem_53(&v70[2], 8i64);
      v70[2] = 256i64;
      LOBYTE(v70[3]) = 1;
      v70[4] = 1i64;
      nimZeroMem_53(&v70[5], 8i64);
      v70[5] = 256i64;
      LOBYTE(v70[6]) = 1;
      v36 = &v92[80 * v122];
      v37 = v70[1];
      *((_QWORD *)v36 + 1) = v70[0];
      *((_QWORD *)v36 + 2) = v37;
      v38 = v70[3];
      *((_QWORD *)v36 + 3) = v70[2];
      *((_QWORD *)v36 + 4) = v38;
      v39 = v70[5];
      *((_QWORD *)v36 + 5) = v70[4];
      *((_QWORD *)v36 + 6) = v39;
      v40 = v70[7];
      *((_QWORD *)v36 + 7) = v70[6];
      *((_QWORD *)v36 + 8) = v40;
      v41 = v70[9];
      *((_QWORD *)v36 + 9) = v70[8];
      *((_QWORD *)v36 + 10) = v41;
      v79 = 131i64;
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v72 = v160 + 1;
      if ( __OFADD__(1i64, v160) )
        goto LABEL_120;
      v160 = v72;
    }
    v79 = 1140i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    v105[8] = v91;
    v105[9] = (__int64)v92;
    eqwasMoved___modelZsave95mongerZversionsZv0_u169(&v91);
    v79 = 131i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
    v42 = a13[1];
    v53 = *a13;
    v54 = v42;
    v55 = a13[2];
    eqdup___modelZsave95mongerZsave95monger_u901(&v50, &v53);
    v90[0] = v50;
    v90[1] = v51;
    v90[2] = v52;
    v105[50] = v50;
    v105[51] = v51;
    v105[52] = v52;
    v153 = v68;
    LOBYTE(v105[59]) = v68;
    v79 = 468i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    v43 = a12[1];
    v53 = *a12;
    v54 = v43;
    v55 = a12[2];
    eqdup___modelZsave95mongerZversionsZv0_u123(&v50, &v53);
    v89[0] = v50;
    v89[1] = v51;
    v89[2] = v52;
    v105[60] = v50;
    v105[61] = v51;
    v105[62] = v52;
    v79 = 1145i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    v152 = v66;
    BYTE1(v105[34]) = v66;
    nimZeroMem_53(&v105[10], 80i64);
    v105[11] = 1i64;
    nimZeroMem_53(&v105[12], 8i64);
    v105[12] = 256i64;
    LOBYTE(v105[13]) = 1;
    v105[14] = 1i64;
    nimZeroMem_53(&v105[15], 8i64);
    v105[15] = 256i64;
    LOBYTE(v105[16]) = 1;
    v79 = 1148i64;
    v121 = 0;
    v44 = *((_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788 + 1);
    v50 = *(_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788;
    v51 = v44;
    v52 = *((_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788 + 2);
    v121 = contains__modelZboardZmemory95manager_u414(&v50, LOBYTE(v105[0]));
    if ( *v158 )
      goto LABEL_135;
    if ( v121 == 1 )
    {
      v79 = 1149i64;
      v45 = refptr_DEFAULT_BUFFER__modelZboardZmemory95manager_u9[1];
      v105[39] = *refptr_DEFAULT_BUFFER__modelZboardZmemory95manager_u9;
      v105[40] = v45;
      v46 = refptr_DEFAULT_BUFFER__modelZboardZmemory95manager_u9[3];
      v105[41] = refptr_DEFAULT_BUFFER__modelZboardZmemory95manager_u9[2];
      v105[42] = v46;
      v47 = refptr_DEFAULT_BUFFER__modelZboardZmemory95manager_u9[5];
      v105[43] = refptr_DEFAULT_BUFFER__modelZboardZmemory95manager_u9[4];
      v105[44] = v47;
      v105[45] = refptr_DEFAULT_BUFFER__modelZboardZmemory95manager_u9[6];
    }
    v79 = 1151i64;
    if ( !*(_QWORD *)a1 )
    {
      v56 = TM__CKxtw4nX41tlcDT9cZT8kGA_10;
      v57 = (char *)&TM__CKxtw4nX41tlcDT9cZT8kGA_9;
      failedAssertImpl__stdZassertions_u234(&v56);
      if ( *v158 )
        goto LABEL_135;
    }
    v168 = a14;
    v79 = 1154i64;
    if ( a14 <= 0 )
    {
      v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
      v168 = 1i64;
      v79 = 1159i64;
      while ( 1 )
      {
        v159 = 0;
        v119 = *(_QWORD *)a1;
        v159 = v168 < v119;
        if ( v168 < v119 )
        {
          v79 = 1160i64;
          if ( v168 < 0 || v168 >= *(_QWORD *)a1 )
            goto LABEL_126;
          v159 = *(_BYTE *)(*(_QWORD *)(a1 + 8) + 560 * v168 + 8) != 0;
        }
        if ( !v159 )
          break;
        v79 = 1161i64;
        v71 = v168 + 1;
        if ( __OFADD__(1i64, v168) )
          goto LABEL_120;
        v168 = v71;
      }
      v79 = 1163i64;
      v118 = *(_QWORD *)a1 - 1i64;
      if ( v118 < v168 )
      {
        v79 = 1164i64;
        nimZeroMem_53(v70, 560i64);
        qmemcpy(v70, v105, 0x230ui64);
        v79 = 34i64;
        v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        eqwasMoved___modelZsave95mongerZversionsZv0_u142(v105, v105);
        v79 = 1164i64;
        v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
        add__modelZsave95mongerZversionsZv0_u1028(a1, v70);
        v79 = 1165i64;
        v117 = *(_QWORD *)a1 - 1i64;
        v168 = v117;
        goto LABEL_128;
      }
      v79 = 34i64;
      v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      if ( v168 < 0 || v168 >= *(_QWORD *)a1 )
        goto LABEL_126;
    }
    else
    {
      v79 = 34i64;
      v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      if ( v168 < 0 || v168 >= *(_QWORD *)a1 )
      {
LABEL_126:
        raiseIndexError2(v168, *(_QWORD *)a1 - 1i64);
        goto LABEL_135;
      }
    }
    eqsink___modelZsave95mongerZversionsZv0_u154(*(_QWORD *)(a1 + 8) + 560 * v168 + 8, v105);
    eqwasMoved___modelZsave95mongerZversionsZv0_u142(v105, v48);
LABEL_128:
    v79 = 1169i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    if ( v168
      || (v56 = TM__CKxtw4nX41tlcDT9cZT8kGA_13,
          v57 = (char *)&TM__CKxtw4nX41tlcDT9cZT8kGA_12,
          failedAssertImpl__stdZassertions_u234(&v56),
          !*v158) )
    {
      v79 = 1171i64;
      v116 = 0i64;
      v116 = X5BX5D___modelZboardZprototype95list_u4239(refptr_PROTOTYPES__modelZboardZprototype95list_u3752, v172);
      if ( !*v158 )
      {
        *(_WORD *)(a1 + 48) += *(_WORD *)(v116 + 66);
        v170 = v168;
        v79 = 34i64;
        v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        v56 = v91;
        v57 = v92;
        eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
        v56 = v93;
        v57 = v94;
        eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
        v56 = v95;
        v57 = v96;
        eqdestroy___modelZsave95mongerZversionsZv0_u448(&v56);
        eqdestroy___modelZsave95mongerZversionsZv0_u145(v105);
        v79 = 394i64;
        v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v107 && (*v107 & 0x4000000000000000i64) == 0 )
          deallocShared(v107);
        goto LABEL_138;
      }
    }
    goto LABEL_135;
  }
  v79 = 1093i64;
  v140 = 0;
  v140 = notin_custom_prototypes__modelZboardZcustom95prototype95list_u189(a9);
  if ( *v158 )
    goto LABEL_135;
  if ( v140 != 1 )
  {
    v79 = 1095i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    nimZeroMem_53(v70, 1448i64);
    get_custom_prototype__modelZboardZcustom95prototype95list_u451(a9, v70);
    if ( *v158 )
      goto LABEL_135;
    v79 = 170i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    eqsink___modelZboardZprototype95list_u3248(v110, v70);
    goto LABEL_37;
  }
  v170 = -1i64;
  v79 = 34i64;
  v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
  v56 = v91;
  v57 = v92;
  eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
  v56 = v93;
  v57 = v94;
  eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
  v56 = v95;
  v57 = v96;
  eqdestroy___modelZsave95mongerZversionsZv0_u448(&v56);
  eqdestroy___modelZsave95mongerZversionsZv0_u145(v105);
  v79 = 394i64;
  v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v107 && (*v107 & 0x4000000000000000i64) == 0 )
    deallocShared(v107);
  v79 = 34i64;
  v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
  v56 = v108;
  v57 = v109;
  eqdestroy___modelZsave95mongerZversionsZv0_u296(&v56);
  v79 = 170i64;
  v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  eqdestroy___modelZboardZprototype95list_u3239(v110);
  v79 = 119i64;
  v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
  v56 = v114;
  v57 = v115;
  eqdestroy___modelZsave95mongerZserialize_u455(&v56);
LABEL_139:
  popFrame_73();
  return v170;
}
