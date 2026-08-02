__int64 __fastcall set_critical_path__modelZsimulationZpreorder_u2428(
        __int64 *a1,
        __int64 *a2,
        __int64 *a3,
        _QWORD *a4,
        __int64 *a5,
        __int64 *a6,
        __int64 a7,
        char a8)
{
  __int64 v9; // rdx
  __int64 v10; // rdx
  __int64 v11; // rdx
  __int64 v12; // rdx
  __int64 v13; // rdx
  __int64 v14; // rdx
  __int64 v15; // rdx
  __int64 v16; // rdx
  bool v17; // al
  __int64 v18; // rdx
  bool v19; // al
  __int64 v20; // rdx
  __int64 v21; // rdx
  __int64 v22; // rdx
  __int64 v23; // rdx
  __int64 v24; // rdx
  __int64 v26; // [rsp+20h] [rbp-60h] BYREF
  void *v27; // [rsp+28h] [rbp-58h]
  __int64 v28; // [rsp+30h] [rbp-50h] BYREF
  __int64 v29; // [rsp+38h] [rbp-48h]
  __int64 v30; // [rsp+40h] [rbp-40h]
  char v31; // [rsp+5Ch] [rbp-24h]
  __int64 v32; // [rsp+60h] [rbp-20h]
  __int64 v33; // [rsp+68h] [rbp-18h]
  __int64 v34; // [rsp+70h] [rbp-10h] BYREF
  void *v35; // [rsp+78h] [rbp-8h]
  __int64 v36; // [rsp+80h] [rbp+0h]
  __int64 v37; // [rsp+88h] [rbp+8h]
  __int64 v38; // [rsp+2A8h] [rbp+228h]
  __int64 v39; // [rsp+2B0h] [rbp+230h] BYREF
  __int64 v40; // [rsp+2B8h] [rbp+238h]
  __int64 v41; // [rsp+2C0h] [rbp+240h]
  __int64 v42; // [rsp+2C8h] [rbp+248h]
  __int64 (__fastcall *v43)(); // [rsp+2D0h] [rbp+250h] BYREF
  _QWORD *v44; // [rsp+2D8h] [rbp+258h]
  __int64 (__fastcall *v45)(); // [rsp+2E0h] [rbp+260h] BYREF
  _QWORD *v46; // [rsp+2E8h] [rbp+268h]
  __int64 v47; // [rsp+2F0h] [rbp+270h]
  void *v48; // [rsp+2F8h] [rbp+278h]
  __int64 v49; // [rsp+300h] [rbp+280h]
  void *v50; // [rsp+308h] [rbp+288h]
  __int64 v51; // [rsp+318h] [rbp+298h]
  __int64 v52; // [rsp+320h] [rbp+2A0h] BYREF
  __int64 v53; // [rsp+328h] [rbp+2A8h]
  __int64 v54; // [rsp+330h] [rbp+2B0h]
  char v55[8]; // [rsp+340h] [rbp+2C0h] BYREF
  const char *v56; // [rsp+348h] [rbp+2C8h]
  __int64 v57; // [rsp+350h] [rbp+2D0h]
  const char *v58; // [rsp+358h] [rbp+2D8h]
  __int16 v59; // [rsp+360h] [rbp+2E0h]
  __int64 v60; // [rsp+370h] [rbp+2F0h]
  __int64 v61; // [rsp+378h] [rbp+2F8h]
  __int64 v62; // [rsp+380h] [rbp+300h]
  __int64 v63; // [rsp+388h] [rbp+308h]
  char v64; // [rsp+397h] [rbp+317h]
  __int64 v65; // [rsp+398h] [rbp+318h]
  char v66; // [rsp+3A7h] [rbp+327h]
  __int64 v67; // [rsp+3A8h] [rbp+328h]
  __int64 v68; // [rsp+3B0h] [rbp+330h]
  __int64 v69; // [rsp+3B8h] [rbp+338h]
  __int64 v70; // [rsp+3C0h] [rbp+340h]
  __int64 v71; // [rsp+3C8h] [rbp+348h]
  __int64 v72; // [rsp+3D0h] [rbp+350h]
  char v73; // [rsp+3DFh] [rbp+35Fh]
  __int64 v74; // [rsp+3E0h] [rbp+360h]
  __int64 v75; // [rsp+3E8h] [rbp+368h]
  __int64 v76; // [rsp+3F0h] [rbp+370h]
  __int64 v77; // [rsp+3F8h] [rbp+378h]
  __int64 v78; // [rsp+400h] [rbp+380h]
  __int64 v79; // [rsp+408h] [rbp+388h]
  __int64 v80; // [rsp+410h] [rbp+390h]
  bool v81; // [rsp+41Eh] [rbp+39Eh]
  bool v82; // [rsp+41Fh] [rbp+39Fh]
  __int64 *v83; // [rsp+420h] [rbp+3A0h]
  char v84; // [rsp+42Fh] [rbp+3AFh]
  __int64 v85; // [rsp+430h] [rbp+3B0h]
  __int64 v86; // [rsp+438h] [rbp+3B8h]
  __int64 v87; // [rsp+440h] [rbp+3C0h]
  __int64 v88; // [rsp+448h] [rbp+3C8h]
  __int64 v89; // [rsp+450h] [rbp+3D0h]
  _QWORD *v90; // [rsp+458h] [rbp+3D8h]
  _QWORD *v91; // [rsp+460h] [rbp+3E0h]
  _BYTE *v92; // [rsp+468h] [rbp+3E8h]
  char v93; // [rsp+477h] [rbp+3F7h]
  __int64 v94; // [rsp+478h] [rbp+3F8h]
  __int64 v95; // [rsp+480h] [rbp+400h]
  __int64 v96; // [rsp+488h] [rbp+408h]
  bool v97; // [rsp+497h] [rbp+417h]
  __int64 v98; // [rsp+498h] [rbp+418h]
  bool v99; // [rsp+4A7h] [rbp+427h]
  __int64 v100; // [rsp+4A8h] [rbp+428h]

  v9 = a3[1];
  v32 = *a3;
  v33 = v9;
  v31 = a8;
  v56 = "set_critical_path";
  v58 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v57 = 0i64;
  v59 = 0;
  nimFrame_80(v55);
  v92 = (_BYTE *)nimErrorFlag_78();
  v100 = 0i64;
  v91 = 0i64;
  v57 = 240i64;
  v58 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v90 = 0i64;
  v90 = (_QWORD *)nimNewObj(80i64, 8i64);
  *v90 = &NTIv2__3xzM7BvmdnPNSAJ1wXdBeA_;
  v91 = v90;
  v57 = 441i64;
  v58 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  v10 = a1[1];
  v28 = *a1;
  v29 = v10;
  v30 = a1[2];
  eqcopy___modelZboardZboard_u15248(v90 + 4, &v28);
  v57 = 214i64;
  v58 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v11 = a5[1];
  v28 = *a5;
  v29 = v11;
  v30 = a5[2];
  eqcopy___modelZsimulationZpreorder_u4966(v91 + 1, &v28);
  v57 = 215i64;
  v12 = a6[1];
  v28 = *a6;
  v29 = v12;
  v30 = a6[2];
  eqcopy___modelZsimulationZpreorder_u4987(v91 + 7, &v28);
  v99 = 1;
  v57 = 221i64;
  while ( v99 )
  {
    nimZeroMem_60(&v52, 24i64);
    v57 = 225i64;
    nimZeroMem_60(&v52, 24i64);
    v89 = 0i64;
    v57 = 268i64;
    v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sets.nim";
    v13 = a2[1];
    v28 = *a2;
    v29 = v13;
    v30 = a2[2];
    v88 = len__modelZboardZboard_u15042(&v28);
    if ( !*v92 )
    {
      v87 = 0i64;
      v86 = 0i64;
      v57 = 269i64;
      v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sets.nim";
      v85 = *a2 - 1;
      v86 = v85;
      v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v98 = 0i64;
      v57 = 97i64;
      while ( v98 <= v86 )
      {
        v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sets.nim";
        v87 = v98;
        v57 = 270i64;
        if ( v98 < 0 || v87 >= *a2 )
        {
LABEL_8:
          raiseIndexError2(v87, *a2 - 1);
          goto LABEL_38;
        }
        v84 = 0;
        v84 = isFilled__pureZcollectionsZsets_u39_2(*(_QWORD *)(a2[1] + 16 * v87 + 8));
        if ( *v92 )
          goto LABEL_38;
        if ( v84 == 1 )
        {
          v57 = 237i64;
          v58 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          if ( v87 < 0 || v87 >= *a2 )
            goto LABEL_8;
          v89 = *(_QWORD *)(a2[1] + 16 * v87 + 16);
          nimZeroMem_60(&v34, 32i64);
          v57 = 238i64;
          v83 = 0i64;
          v83 = (__int64 *)X5BX5D___modelZsimulationZpreorder_u3899(a7, v89);
          if ( *v92 )
            goto LABEL_38;
          v14 = v83[1];
          v34 = *v83;
          v35 = (void *)v14;
          v15 = v83[3];
          v36 = v83[2];
          v37 = v15;
          v49 = v34;
          v50 = v35;
          v47 = v36;
          v48 = (void *)v15;
          v57 = 240i64;
          v97 = 0;
          nimZeroMem_60(&v45, 16i64);
          v45 = is_critical__modelZsimulationZpreorder_u2464;
          v46 = v91;
          v82 = 0;
          v16 = a2[1];
          v28 = *a2;
          v29 = v16;
          v30 = a2[2];
          v26 = v49;
          v27 = v50;
          v17 = v91
              ? ((unsigned __int8 (__fastcall *)(__int64 *, __int64 *, __int64, _QWORD *))v45)(&v28, &v26, v89, v46) != 0
              : ((unsigned __int8 (__fastcall *)(__int64 *, __int64 *, __int64))v45)(&v28, &v26, v89) != 0;
          v82 = v17;
          if ( *v92 )
            goto LABEL_38;
          v97 = !v82;
          if ( v82 )
          {
            v57 = 241i64;
            nimZeroMem_60(&v43, 16i64);
            v43 = is_critical__modelZsimulationZpreorder_u2464;
            v44 = v91;
            v81 = 0;
            v18 = a2[1];
            v28 = *a2;
            v29 = v18;
            v30 = a2[2];
            v26 = v47;
            v27 = v48;
            if ( v91 )
              v19 = ((unsigned __int8 (__fastcall *)(__int64 *, __int64 *, __int64, _QWORD *))v43)(&v28, &v26, v89, v44) != 0;
            else
              v19 = ((unsigned __int8 (__fastcall *)(__int64 *, __int64 *, __int64))v43)(&v28, &v26, v89) != 0;
            v81 = v19;
            if ( *v92 )
              goto LABEL_38;
            v97 = !v81;
          }
          if ( v97 )
          {
            v57 = 242i64;
            incl__modelZboardZboard_u11061(&v52, v89);
            if ( *v92 )
              goto LABEL_38;
          }
          v57 = 272i64;
          v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sets.nim";
          v80 = 0i64;
          v20 = a2[1];
          v28 = *a2;
          v29 = v20;
          v30 = a2[2];
          v80 = len__modelZboardZboard_u15042(&v28);
          if ( *v92 )
            goto LABEL_38;
          if ( v80 != v88 )
          {
            v26 = TM__8dO79bDlK9csFzRs49cEE7wlw_199;
            v27 = &TM__8dO79bDlK9csFzRs49cEE7wlw_198;
            failedAssertImpl__stdZassertions_u234(&v26);
            if ( *v92 )
              goto LABEL_38;
          }
        }
        v57 = 102i64;
        v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
        v51 = v98 + 1;
        if ( __OFADD__(1i64, v98) )
        {
          raiseOverflow();
          goto LABEL_38;
        }
        v98 = v51;
      }
      v57 = 244i64;
      v58 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      v28 = v52;
      v29 = v53;
      v30 = v54;
      excl__modelZsimulationZpreorder_u4378(a2, &v28);
      if ( !*v92 )
      {
        v57 = 246i64;
        v79 = 0i64;
        v28 = v52;
        v29 = v53;
        v30 = v54;
        v79 = len__modelZboardZboard_u15042(&v28);
        if ( !*v92 )
          v99 = v79 > 0;
      }
    }
LABEL_38:
    v57 = 441i64;
    v58 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    eqdestroy___modelZboardZboard_u15245(&v52);
    if ( *v92 )
      goto LABEL_102;
  }
  v57 = 248i64;
  v58 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  if ( v31 != 1 )
  {
    nimZeroMem_60(&v39, 24i64);
    v71 = 0i64;
    v57 = 268i64;
    v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sets.nim";
    v23 = a2[1];
    v28 = *a2;
    v29 = v23;
    v30 = a2[2];
    v70 = len__modelZboardZboard_u15042(&v28);
    if ( !*v92 )
    {
      v69 = 0i64;
      v68 = 0i64;
      v57 = 269i64;
      v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sets.nim";
      v67 = *a2 - 1;
      v68 = v67;
      v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v95 = 0i64;
      v57 = 97i64;
      while ( v95 <= v68 )
      {
        v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sets.nim";
        v69 = v95;
        v57 = 270i64;
        if ( v95 < 0 || v69 >= *a2 )
        {
LABEL_66:
          raiseIndexError2(v69, *a2 - 1);
          goto LABEL_101;
        }
        v66 = 0;
        v66 = isFilled__pureZcollectionsZsets_u39_2(*(_QWORD *)(a2[1] + 16 * v69 + 8));
        if ( *v92 )
          goto LABEL_101;
        if ( v66 == 1 )
        {
          v57 = 253i64;
          v58 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          if ( v69 < 0 || v69 >= *a2 )
            goto LABEL_66;
          v71 = *(_QWORD *)(a2[1] + 16 * v69 + 16);
          v57 = 254i64;
          if ( v71 < 0 || v71 >= *a4 )
            goto LABEL_74;
          incl__modelZsave95mongerZsave95monger_u1438(&v39, *(_QWORD *)(a4[1] + 104 * v71 + 104));
          if ( *v92 )
            goto LABEL_101;
          v57 = 255i64;
          if ( v71 < 0 || v71 >= *a4 )
          {
LABEL_74:
            raiseIndexError2(v71, *a4 - 1i64);
            goto LABEL_101;
          }
          *(_BYTE *)(a4[1] + 104 * v71 + 97) = 1;
          v57 = 272i64;
          v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sets.nim";
          v65 = 0i64;
          v24 = a2[1];
          v28 = *a2;
          v29 = v24;
          v30 = a2[2];
          v65 = len__modelZboardZboard_u15042(&v28);
          if ( *v92 )
            goto LABEL_101;
          if ( v65 != v70 )
          {
            v26 = TM__8dO79bDlK9csFzRs49cEE7wlw_203;
            v27 = &TM__8dO79bDlK9csFzRs49cEE7wlw_198;
            failedAssertImpl__stdZassertions_u234(&v26);
            if ( *v92 )
              goto LABEL_101;
          }
        }
        v57 = 102i64;
        v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
        v38 = v95 + 1;
        if ( __OFADD__(1i64, v95) )
        {
          raiseOverflow();
          goto LABEL_101;
        }
        v95 = v38;
      }
      v57 = 257i64;
      v58 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      v64 = 0;
      v28 = v39;
      v29 = v40;
      v30 = v41;
      v64 = contains__modelZsave95mongerZsave95monger_u1046(
              &v28,
              *(_QWORD *)refptr_NO_ID__modelZsave95mongerZcommon_u3361);
      if ( !*v92 && !v64 )
      {
        nimZeroMem_60(&v34, 560i64);
        v63 = 0i64;
        v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v94 = 0i64;
        v62 = v32;
        v61 = v32;
        v57 = 184i64;
        while ( v94 < v61 )
        {
          v63 = v94;
          v57 = 34i64;
          v58 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
          if ( v94 < 0 || v94 >= v32 )
          {
            raiseIndexError2(v94, v32 - 1);
            break;
          }
          eqcopy___modelZsave95mongerZversionsZv0_u148(&v34, v33 + 560 * v94 + 8);
          v57 = 259i64;
          v58 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          v93 = (_BYTE)v34 == 78;
          if ( (_BYTE)v34 != 78
            || (v28 = v39, v29 = v40, v30 = v41, v93 = contains__modelZsave95mongerZsave95monger_u1046(&v28, v35), !*v92) )
          {
            if ( v93 == 1 )
            {
              v100 = v63;
              v57 = 34i64;
              v58 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
              eqdestroy___modelZsave95mongerZversionsZv0_u145(&v34);
              v57 = 160i64;
              v58 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
              eqdestroy___modelZsave95mongerZsave95monger_u2597(&v39);
              v57 = 209i64;
              v58 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
              eqdestroy___modelZsimulationZpreorder_u32578(v91);
              goto LABEL_103;
            }
            v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v94;
            v57 = 187i64;
            v60 = v32;
            if ( v32 == v61 )
              continue;
            v26 = TM__8dO79bDlK9csFzRs49cEE7wlw_205;
            v27 = &TM__8dO79bDlK9csFzRs49cEE7wlw_3;
            failedAssertImpl__stdZassertions_u234(&v26);
            if ( !*v92 )
              continue;
          }
          break;
        }
        v57 = 34i64;
        v58 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        eqdestroy___modelZsave95mongerZversionsZv0_u145(&v34);
      }
    }
LABEL_101:
    v57 = 160i64;
    v58 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
    eqdestroy___modelZsave95mongerZsave95monger_u2597(&v39);
  }
  else
  {
    v78 = 0i64;
    v57 = 268i64;
    v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sets.nim";
    v21 = a2[1];
    v28 = *a2;
    v29 = v21;
    v30 = a2[2];
    v77 = len__modelZboardZboard_u15042(&v28);
    if ( !*v92 )
    {
      v76 = 0i64;
      v75 = 0i64;
      v57 = 269i64;
      v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sets.nim";
      v74 = *a2 - 1;
      v75 = v74;
      v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v96 = 0i64;
      v57 = 97i64;
      while ( v96 <= v75 )
      {
        v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sets.nim";
        v76 = v96;
        v57 = 270i64;
        if ( v96 < 0 || v76 >= *a2 )
        {
LABEL_46:
          raiseIndexError2(v76, *a2 - 1);
          break;
        }
        v73 = 0;
        v73 = isFilled__pureZcollectionsZsets_u39_2(*(_QWORD *)(a2[1] + 16 * v76 + 8));
        if ( *v92 )
          break;
        if ( v73 == 1 )
        {
          v57 = 249i64;
          v58 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          if ( v76 < 0 || v76 >= *a2 )
            goto LABEL_46;
          v78 = *(_QWORD *)(a2[1] + 16 * v76 + 16);
          v57 = 250i64;
          if ( v78 < 0 || v78 >= *a4 )
          {
            raiseIndexError2(v78, *a4 - 1i64);
            break;
          }
          *(_BYTE *)(a4[1] + 104 * v78 + 96) = 1;
          v57 = 272i64;
          v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sets.nim";
          v72 = 0i64;
          v22 = a2[1];
          v28 = *a2;
          v29 = v22;
          v30 = a2[2];
          v72 = len__modelZboardZboard_u15042(&v28);
          if ( *v92 )
            break;
          if ( v72 != v77 )
          {
            v26 = TM__8dO79bDlK9csFzRs49cEE7wlw_201;
            v27 = &TM__8dO79bDlK9csFzRs49cEE7wlw_198;
            failedAssertImpl__stdZassertions_u234(&v26);
            if ( *v92 )
              break;
          }
        }
        v57 = 102i64;
        v58 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
        v42 = v96 + 1;
        if ( __OFADD__(1i64, v96) )
        {
          raiseOverflow();
          break;
        }
        v96 = v42;
      }
    }
  }
LABEL_102:
  v57 = 209i64;
  v58 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  eqdestroy___modelZsimulationZpreorder_u32578(v91);
LABEL_103:
  popFrame_80();
  return v100;
}
