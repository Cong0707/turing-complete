// address: 0x1401bc87f-0x1401be0a7
// name: get_component__modelZsave95mongerZversionsZv15_u3
__int64 __fastcall get_component__modelZsave95mongerZversionsZv15_u3(__int64 *a1, __int64 a2, __int64 a3, __int64 *a4)
{
  __int64 v4; // rbx
  __int64 v5; // rax
  __int64 v6; // rax
  __int64 v7; // rax
  __int64 v8; // rax
  __int64 v9; // rdx
  __int64 v10; // rdx
  __int64 v11; // rax
  __int64 v12; // rax
  __int64 v13; // rax
  __int64 v14; // rax
  __int64 v15; // rax
  __int64 v16; // rax
  __int64 v17; // rax
  __int64 v18; // rax
  __int64 v19; // rax
  __int64 v20; // rax
  __int64 v21; // rax
  __int64 v22; // rax
  __int64 v23; // rax
  __int64 v24; // rdx
  __int64 v25; // rax
  __int64 v26; // rax
  __int64 v27; // rax
  __int64 v28; // rdx
  __int64 v29; // rdx
  __int64 v30; // rax
  __int64 v31; // rax
  __int64 v32; // rax
  __int64 v33; // rax
  bool v34; // al
  __int64 v35; // rdx
  __int64 v37[4]; // [rsp+20h] [rbp-60h] BYREF
  __int64 v38[2]; // [rsp+40h] [rbp-40h] BYREF
  __int64 v39; // [rsp+50h] [rbp-30h] BYREF
  _QWORD *v40; // [rsp+58h] [rbp-28h]
  __int64 v41; // [rsp+60h] [rbp-20h]
  __int64 v42; // [rsp+68h] [rbp-18h]
  __int64 v43[6]; // [rsp+70h] [rbp-10h] BYREF
  __int64 v44; // [rsp+A0h] [rbp+20h] BYREF
  _QWORD *v45; // [rsp+A8h] [rbp+28h]
  __int64 v46; // [rsp+B0h] [rbp+30h] BYREF
  _QWORD *v47; // [rsp+B8h] [rbp+38h]
  __int64 v48; // [rsp+C0h] [rbp+40h]
  __int64 v49; // [rsp+C8h] [rbp+48h]
  __int64 v50; // [rsp+D0h] [rbp+50h]
  _QWORD *v51; // [rsp+D8h] [rbp+58h]
  __int64 v52; // [rsp+E0h] [rbp+60h] BYREF
  _QWORD *v53; // [rsp+E8h] [rbp+68h]
  __int64 v54; // [rsp+F8h] [rbp+78h]
  __int64 v55; // [rsp+100h] [rbp+80h]
  __int64 v56; // [rsp+108h] [rbp+88h]
  __int64 v57; // [rsp+110h] [rbp+90h]
  __int64 v58[4]; // [rsp+120h] [rbp+A0h] BYREF
  __int64 v59[3]; // [rsp+140h] [rbp+C0h] BYREF
  __int64 v60; // [rsp+158h] [rbp+D8h]
  char v61[8]; // [rsp+160h] [rbp+E0h] BYREF
  const char *v62; // [rsp+168h] [rbp+E8h]
  __int64 v63; // [rsp+170h] [rbp+F0h]
  const char *v64; // [rsp+178h] [rbp+F8h]
  __int16 v65; // [rsp+180h] [rbp+100h]
  __int64 bits__modelZsave95mongerZcommon_u5744; // [rsp+190h] [rbp+110h] BYREF
  __int64 bytes__modelZsave95mongerZcommon_u5751; // [rsp+198h] [rbp+118h] BYREF
  __int64 v68; // [rsp+1A0h] [rbp+120h] BYREF
  _QWORD *v69; // [rsp+1A8h] [rbp+128h]
  __int64 v70; // [rsp+1B0h] [rbp+130h] BYREF
  _QWORD *v71; // [rsp+1B8h] [rbp+138h]
  __int64 v72; // [rsp+1C0h] [rbp+140h] BYREF
  int point__modelZsave95mongerZcommon_u5788; // [rsp+1CCh] [rbp+14Ch] BYREF
  __int64 v74; // [rsp+1D0h] [rbp+150h] BYREF
  __int64 v75; // [rsp+1D8h] [rbp+158h]
  __int64 v76; // [rsp+1E0h] [rbp+160h]
  __int64 v77[71]; // [rsp+1F0h] [rbp+170h] BYREF
  __int64 v78; // [rsp+428h] [rbp+3A8h]
  _QWORD *v79; // [rsp+430h] [rbp+3B0h]
  __int64 v80; // [rsp+438h] [rbp+3B8h]
  __int64 v81; // [rsp+440h] [rbp+3C0h]
  __int64 v82; // [rsp+448h] [rbp+3C8h]
  __int64 v83; // [rsp+450h] [rbp+3D0h]
  __int64 v84; // [rsp+458h] [rbp+3D8h]
  unsigned __int16 v85; // [rsp+466h] [rbp+3E6h]
  __int64 v86; // [rsp+468h] [rbp+3E8h]
  unsigned __int16 v87; // [rsp+476h] [rbp+3F6h]
  __int64 v88; // [rsp+478h] [rbp+3F8h]
  __int64 v89; // [rsp+480h] [rbp+400h]
  __int64 v90; // [rsp+488h] [rbp+408h]
  __int64 v91; // [rsp+490h] [rbp+410h]
  unsigned __int16 v92; // [rsp+49Ch] [rbp+41Ch]
  char init_data__modelZsave95mongerZcommon_u5762; // [rsp+49Eh] [rbp+41Eh]
  char v94; // [rsp+49Fh] [rbp+41Fh]
  __int64 v95; // [rsp+4A0h] [rbp+420h]
  __int64 v96; // [rsp+4A8h] [rbp+428h]
  char bool__modelZsave95mongerZserialize_u1; // [rsp+4B5h] [rbp+435h]
  __int16 i16__modelZsave95mongerZserialize_u97; // [rsp+4B6h] [rbp+436h]
  __int64 u64__modelZsave95mongerZserialize_u9; // [rsp+4B8h] [rbp+438h]
  unsigned __int16 v100; // [rsp+4C6h] [rbp+446h]
  __int64 i64__modelZsave95mongerZserialize_u49; // [rsp+4C8h] [rbp+448h]
  char u8__modelZsave95mongerZserialize_u101; // [rsp+4D7h] [rbp+457h]
  __int64 v103; // [rsp+4D8h] [rbp+458h]
  unsigned __int16 u16__modelZsave95mongerZserialize_u81; // [rsp+4E6h] [rbp+466h]
  _BYTE *v105; // [rsp+4E8h] [rbp+468h]
  bool v106; // [rsp+4F3h] [rbp+473h]
  unsigned __int16 v107; // [rsp+4F4h] [rbp+474h]
  unsigned __int16 v108; // [rsp+4F6h] [rbp+476h]
  __int64 v109; // [rsp+4F8h] [rbp+478h]
  __int64 v110; // [rsp+500h] [rbp+480h]
  char v111; // [rsp+50Fh] [rbp+48Fh]

  v4 = a1[1];
  v41 = *a1;
  v42 = v4;
  v62 = "get_component";
  v64 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
  v63 = 0i64;
  v65 = 0;
  nimFrame_58(v61);
  v105 = (_BYTE *)nimErrorFlag_56();
  nimZeroMem_42(a4, 560i64);
  nimZeroMem_42(v77, 560i64);
  v63 = 5i64;
  v64 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
  u16__modelZsave95mongerZserialize_u81 = 0;
  if ( v4 )
    v5 = v42 + 8;
  else
    v5 = 0i64;
  u16__modelZsave95mongerZserialize_u81 = get_u16__modelZsave95mongerZserialize_u81(v5, v41, a2);
  if ( *v105 )
    goto LABEL_173;
  v103 = u16__modelZsave95mongerZserialize_u81;
  v111 = 0;
  v63 = 7i64;
  if ( u16__modelZsave95mongerZserialize_u81 <= 0x7Cui64 )
  {
    v63 = 8i64;
    if ( v103 > 124 )
    {
      raiseRangeErrorI(v103, 0i64, 124i64);
LABEL_173:
      eqdestroy___modelZsave95mongerZversionsZv0_u145(v77);
      return popFrame_58();
    }
    v111 = v103;
  }
  v63 = 10i64;
  nimZeroMem_42(v77, 560i64);
  LOBYTE(v77[0]) = v111;
  nimZeroMem_42(&v77[10], 80i64);
  v77[11] = 1i64;
  nimZeroMem_42(&v77[12], 8i64);
  v77[12] = 256i64;
  LOBYTE(v77[13]) = 1;
  v77[14] = 1i64;
  nimZeroMem_42(&v77[15], 8i64);
  v77[15] = 256i64;
  LOBYTE(v77[16]) = 1;
  nimZeroMem_42(&v77[60], 24i64);
  LOBYTE(v77[60]) = 0;
  v63 = 11i64;
  nimZeroMem_42(&v74, 24i64);
  v63 = 13i64;
  nimZeroMem_42(&point__modelZsave95mongerZcommon_u5788, 4i64);
  if ( v42 )
    v6 = v42 + 8;
  else
    v6 = 0i64;
  point__modelZsave95mongerZcommon_u5788 = get_point__modelZsave95mongerZcommon_u5788(v6, v41, a2);
  if ( *v105 )
    goto LABEL_173;
  *(_DWORD *)((char *)v77 + 2) = point__modelZsave95mongerZcommon_u5788;
  v63 = 14i64;
  u8__modelZsave95mongerZserialize_u101 = 0;
  v7 = v42 ? v42 + 8 : 0i64;
  u8__modelZsave95mongerZserialize_u101 = get_u8__modelZsave95mongerZserialize_u101(v7, v41, a2);
  if ( *v105 )
    goto LABEL_173;
  BYTE6(v77[0]) = u8__modelZsave95mongerZserialize_u101;
  v63 = 15i64;
  i64__modelZsave95mongerZserialize_u49 = 0i64;
  v8 = v42 ? v42 + 8 : 0i64;
  i64__modelZsave95mongerZserialize_u49 = get_i64__modelZsave95mongerZserialize_u49(v8, v41, a2);
  if ( *v105 )
    goto LABEL_173;
  nimZeroMem_42(&v72, 8i64);
  v72 = id__modelZsave95mongerZcommon_u3362(i64__modelZsave95mongerZserialize_u49);
  if ( *v105 )
    goto LABEL_173;
  v77[1] = v72;
  v63 = 16i64;
  v64 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
  v70 = 0i64;
  v71 = 0i64;
  if ( v42 )
    v9 = v42 + 8;
  else
    v9 = 0i64;
  get_string__modelZsave95mongerZserialize_u180(&v70, v9, v41, a2);
  if ( *v105 )
  {
    v39 = v70;
    v40 = v71;
    eqdestroy___system_u281_23(&v39);
    goto LABEL_173;
  }
  v63 = 1699i64;
  v64 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  v39 = v70;
  v40 = v71;
  eqsink___system_u2667(&v77[24], &v39);
  v63 = 17i64;
  v64 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
  v68 = 0i64;
  v69 = 0i64;
  if ( v42 )
    v10 = v42 + 8;
  else
    v10 = 0i64;
  get_string__modelZsave95mongerZserialize_u180(&v68, v10, v41, a2);
  if ( *v105 )
  {
    v39 = v68;
    v40 = v69;
    eqdestroy___system_u281_23(&v39);
    goto LABEL_173;
  }
  v63 = 1699i64;
  v64 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  v39 = v68;
  v40 = v69;
  eqsink___system_u2667(&v77[26], &v39);
  v63 = 19i64;
  v64 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
  if ( v42 )
    v11 = v42 + 8;
  else
    v11 = 0i64;
  v100 = get_u16__modelZsave95mongerZserialize_u81(v11, v41, a2);
  if ( *v105 )
    goto LABEL_173;
  v110 = 0i64;
  v63 = 21i64;
  while ( v110 < v100 )
  {
    v63 = 22i64;
    u64__modelZsave95mongerZserialize_u9 = 0i64;
    if ( v42 )
      v12 = v42 + 8;
    else
      v12 = 0i64;
    u64__modelZsave95mongerZserialize_u9 = get_u64__modelZsave95mongerZserialize_u9(v12, v41, a2);
    if ( *v105 )
      goto LABEL_173;
    add__modelZsave95mongerZserialize_u151(&v77[21], u64__modelZsave95mongerZserialize_u9);
    v63 = 23i64;
    v60 = v110 + 1;
    if ( __OFADD__(1i64, v110) )
    {
LABEL_43:
      raiseOverflow();
      goto LABEL_173;
    }
    v110 = v60;
  }
  v63 = 24i64;
  nimZeroMem_42(&bytes__modelZsave95mongerZcommon_u5751, 8i64);
  v13 = v42 ? v42 + 8 : 0i64;
  bytes__modelZsave95mongerZcommon_u5751 = get_bytes__modelZsave95mongerZcommon_u5751(v13, v41, a2);
  if ( *v105 )
    goto LABEL_173;
  v74 = bytes__modelZsave95mongerZcommon_u5751;
  v63 = 25i64;
  i16__modelZsave95mongerZserialize_u97 = 0;
  v14 = v42 ? v42 + 8 : 0i64;
  i16__modelZsave95mongerZserialize_u97 = get_i16__modelZsave95mongerZserialize_u97(v14, v41, a2);
  if ( *v105 )
    goto LABEL_173;
  LOWORD(v77[23]) = i16__modelZsave95mongerZserialize_u97;
  v63 = 26i64;
  nimZeroMem_42(&bits__modelZsave95mongerZcommon_u5744, 8i64);
  v15 = v42 ? v42 + 8 : 0i64;
  bits__modelZsave95mongerZcommon_u5744 = get_bits__modelZsave95mongerZcommon_u5744(v15, v41, a2);
  if ( *v105 )
    goto LABEL_173;
  v77[28] = bits__modelZsave95mongerZcommon_u5744;
  v63 = 27i64;
  bool__modelZsave95mongerZserialize_u1 = 0;
  v16 = v42 ? v42 + 8 : 0i64;
  bool__modelZsave95mongerZserialize_u1 = get_bool__modelZsave95mongerZserialize_u1(v16, v41, a2);
  if ( *v105 )
    goto LABEL_173;
  LOBYTE(v77[59]) = bool__modelZsave95mongerZserialize_u1;
  v63 = 29i64;
  v17 = v42 ? v42 + 8 : 0i64;
  v96 = get_i64__modelZsave95mongerZserialize_u49(v17, v41, a2);
  if ( *v105 )
    goto LABEL_173;
  v63 = 30i64;
  v18 = v42 ? v42 + 8 : 0i64;
  v95 = get_i64__modelZsave95mongerZserialize_u49(v18, v41, a2);
  if ( *v105 )
    goto LABEL_173;
  v63 = 31i64;
  if ( v96 >= 0 )
  {
    v63 = 33i64;
    if ( v95 >= 0 )
    {
      v63 = 36i64;
      LOBYTE(v55) = 2;
      v56 = v96;
      v57 = v95;
      v77[60] = v55;
      v77[61] = v96;
      v77[62] = v95;
    }
    else
    {
      v63 = 34i64;
      nimZeroMem_42(v58, 24i64);
      LOBYTE(v58[0]) = 1;
      v77[60] = v58[0];
      v77[61] = v58[1];
      v77[62] = v58[2];
    }
  }
  else
  {
    v63 = 32i64;
    nimZeroMem_42(v59, 24i64);
    LOBYTE(v59[0]) = 0;
    v77[60] = v59[0];
    v77[61] = v59[1];
    v77[62] = v59[2];
  }
  v63 = 38i64;
  v94 = 0;
  v19 = v42 ? v42 + 8 : 0i64;
  v94 = get_bool__modelZsave95mongerZserialize_u1(v19, v41, a2);
  if ( *v105 )
    goto LABEL_173;
  LOBYTE(v75) = v94;
  v63 = 39i64;
  init_data__modelZsave95mongerZcommon_u5762 = 0;
  v20 = v42 ? v42 + 8 : 0i64;
  init_data__modelZsave95mongerZcommon_u5762 = get_init_data__modelZsave95mongerZcommon_u5762(v20, v41, a2);
  if ( *v105 )
    goto LABEL_173;
  BYTE1(v75) = init_data__modelZsave95mongerZcommon_u5762;
  v63 = 41i64;
  v92 = 0;
  v21 = v42 ? v42 + 8 : 0i64;
  v92 = get_u16__modelZsave95mongerZserialize_u81(v21, v41, a2);
  if ( *v105 )
    goto LABEL_173;
  v91 = v92;
  v109 = 0i64;
  v63 = 43i64;
  while ( v109 < v91 )
  {
    v63 = 45i64;
    v90 = 0i64;
    if ( v42 )
      v22 = v42 + 8;
    else
      v22 = 0i64;
    v90 = get_i64__modelZsave95mongerZserialize_u49(v22, v41, a2);
    if ( *v105 )
      goto LABEL_173;
    v43[0] = id__modelZsave95mongerZcommon_u3362(v90);
    if ( *v105 )
      goto LABEL_173;
    v63 = 46i64;
    v89 = 0i64;
    v23 = v42 ? v42 + 8 : 0i64;
    v89 = get_i64__modelZsave95mongerZserialize_u49(v23, v41, a2);
    if ( *v105 )
      goto LABEL_173;
    v43[1] = id__modelZsave95mongerZcommon_u3362(v89);
    if ( *v105 )
      goto LABEL_173;
    v63 = 47i64;
    v24 = v42 ? v42 + 8 : 0i64;
    get_string__modelZsave95mongerZserialize_u180(&v39, v24, v41, a2);
    v43[2] = v39;
    v43[3] = (__int64)v40;
    if ( *v105 )
      goto LABEL_173;
    v63 = 48i64;
    v88 = 0i64;
    v25 = v42 ? v42 + 8 : 0i64;
    v88 = get_i64__modelZsave95mongerZserialize_u49(v25, v41, a2);
    if ( *v105 )
      goto LABEL_173;
    v43[4] = v88;
    v63 = 49i64;
    v26 = v42 ? v42 + 8 : 0i64;
    v43[5] = get_bits__modelZsave95mongerZcommon_u5744(v26, v41, a2);
    if ( *v105 )
      goto LABEL_173;
    v63 = 44i64;
    add__modelZsave95mongerZversionsZv7_u2572(&v77[30], v43);
    v63 = 51i64;
    v54 = v109 + 1;
    if ( __OFADD__(1i64, v109) )
      goto LABEL_43;
    v109 = v54;
  }
  v63 = 54i64;
  v27 = v42 ? v42 + 8 : 0i64;
  v87 = get_u16__modelZsave95mongerZserialize_u81(v27, v41, a2);
  if ( *v105 )
    goto LABEL_173;
  v108 = 0;
  v63 = 56i64;
  while ( v108 < v87 )
  {
    v52 = 0i64;
    v53 = 0i64;
    v63 = 57i64;
    if ( v42 )
      v28 = v42 + 8;
    else
      v28 = 0i64;
    get_string__modelZsave95mongerZserialize_u180(&v52, v28, v41, a2);
    if ( *v105 )
      goto LABEL_173;
    v63 = 58i64;
    v29 = v42 ? v42 + 8 : 0i64;
    get_string__modelZsave95mongerZserialize_u180(&v39, v29, v41, a2);
    v50 = v39;
    v51 = v40;
    if ( *v105 )
      goto LABEL_173;
    v39 = v52;
    v40 = v53;
    v38[0] = v50;
    v38[1] = (__int64)v51;
    X5BX5Deq___modelZsave95mongerZversionsZv7_u1345(&v77[53], &v39, v38);
    if ( *v105 )
      goto LABEL_173;
    ++v108;
    v63 = 394i64;
    v64 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v53 && (*v53 & 0x4000000000000000i64) == 0 )
      deallocShared(v53);
  }
  v63 = 61i64;
  v64 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
  if ( LOBYTE(v77[0]) == 78 )
  {
    v63 = 63i64;
    v86 = 0i64;
    if ( v42 )
      v30 = v42 + 8;
    else
      v30 = 0i64;
    v86 = get_i64__modelZsave95mongerZserialize_u49(v30, v41, a2);
    if ( *v105 )
      goto LABEL_173;
    v77[49] = v86;
    v107 = 0;
    v63 = 65i64;
    v31 = v42 ? v42 + 8 : 0i64;
    v85 = get_u16__modelZsave95mongerZserialize_u81(v31, v41, a2);
    if ( *v105 )
      goto LABEL_173;
    v63 = 66i64;
    while ( v107 < v85 )
    {
      v63 = 67i64;
      v84 = 0i64;
      if ( v42 )
        v32 = v42 + 8;
      else
        v32 = 0i64;
      v84 = get_i64__modelZsave95mongerZserialize_u49(v32, v41, a2);
      if ( *v105 )
        goto LABEL_173;
      v49 = id__modelZsave95mongerZcommon_u3362(v84);
      if ( *v105 )
        goto LABEL_173;
      v63 = 68i64;
      v33 = v42 ? v42 + 8 : 0i64;
      v48 = get_bits__modelZsave95mongerZcommon_u5744(v33, v41, a2);
      if ( *v105 )
        goto LABEL_173;
      v63 = 69i64;
      X5BX5Deq___modelZsave95mongerZversionsZv7_u70(&v77[50], v49, v48);
      if ( *v105 )
        goto LABEL_173;
      v63 = 70i64;
      ++v107;
    }
    v63 = 71i64;
    v107 = 0;
  }
  v63 = 75i64;
  v106 = 0;
  v34 = LOBYTE(v77[0]) == 82 || LOBYTE(v77[0]) == 83 || LOBYTE(v77[0]) == 91;
  v106 = v34;
  if ( v34 )
  {
    v83 = v77[30];
    v106 = v77[30] == 0;
  }
  if ( v106 )
  {
    v63 = 76i64;
    nimZeroMem_42(v43, 48i64);
    add__modelZsave95mongerZversionsZv7_u2572(&v77[30], v43);
  }
  v46 = 0i64;
  v47 = 0i64;
  v63 = 78i64;
  while ( 1 )
  {
    v82 = v77[21];
    v63 = 78i64;
    v64 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
    v44 = 0i64;
    v45 = 0i64;
    v35 = *((_QWORD *)refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347 + 1);
    v37[0] = *(_QWORD *)refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347;
    v37[1] = v35;
    v37[2] = *((_QWORD *)refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347 + 2);
    getOrDefault__modelZsave95mongerZversionsZv7_u2672(&v44, v37, LOBYTE(v77[0]));
    if ( *v105 )
    {
      v39 = v44;
      v40 = v45;
      eqdestroy___modelZsave95mongerZserialize_u455(&v39);
      goto LABEL_171;
    }
    v63 = 119i64;
    v64 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
    v39 = v44;
    v40 = v45;
    eqsink___modelZsave95mongerZserialize_u464(&v46, &v39);
    v81 = v46;
    if ( v82 >= v46 )
      goto LABEL_171;
    v80 = 0i64;
    v63 = 79i64;
    v64 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
    v79 = 0i64;
    v79 = (_QWORD *)X5BX5D___modelZsave95mongerZversionsZv7_u2794(
                      refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347,
                      LOBYTE(v77[0]));
    if ( *v105 )
      goto LABEL_171;
    v78 = v77[21];
    if ( v77[21] < 0 || v78 >= *v79 )
      break;
    v80 = *(_QWORD *)(v79[1] + 8 * v78 + 8);
    add__modelZsave95mongerZserialize_u151(&v77[21], v80);
  }
  raiseIndexError2(v78, *v79 - 1i64);
LABEL_171:
  v63 = 119i64;
  v64 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
  v39 = v46;
  v40 = v47;
  eqdestroy___modelZsave95mongerZserialize_u455(&v39);
  if ( *v105 )
    goto LABEL_173;
  v77[46] = v74;
  v77[47] = v75;
  v77[48] = v76;
  qmemcpy(a4, v77, 0x230ui64);
  v63 = 34i64;
  v64 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
  eqwasMoved___modelZsave95mongerZversionsZv0_u142(v77, 70i64);
  eqdestroy___modelZsave95mongerZversionsZv0_u145(v77);
  return popFrame_58();
}
