// address: 0x140681a0b-0x14068359b
// name: recursive_load__presenterZutilities_u35829
__int64 __fastcall recursive_load__presenterZutilities_u35829(__int64 *a1, __int64 a2, _QWORD *a3)
{
  _QWORD *v3; // rbx
  __int64 v4; // rcx
  _QWORD *v5; // rdx
  __int64 v6; // rcx
  _QWORD *v7; // rdx
  void *v8; // rdx
  void *v9; // rdx
  __int64 v10; // r8
  void *v11; // rdx
  __int64 v12; // rax
  __int64 v13; // r10
  __int64 v14; // rcx
  __int64 v16[4]; // [rsp+20h] [rbp-60h] BYREF
  __int64 v17[2]; // [rsp+40h] [rbp-40h] BYREF
  __int64 (__fastcall *v18)(); // [rsp+50h] [rbp-30h] BYREF
  void *v19; // [rsp+58h] [rbp-28h]
  __int64 (__fastcall *v20)(); // [rsp+60h] [rbp-20h] BYREF
  _QWORD *v21; // [rsp+68h] [rbp-18h]
  __int64 (__fastcall *v22)(); // [rsp+70h] [rbp-10h]
  _QWORD *v23; // [rsp+78h] [rbp-8h]
  _WORD v24[22]; // [rsp+80h] [rbp+0h] BYREF
  int v25; // [rsp+ACh] [rbp+2Ch] BYREF
  __int64 (__fastcall *v26)(__int64 (__fastcall **)(), __int64); // [rsp+2D0h] [rbp+250h] BYREF
  _QWORD *v27; // [rsp+2D8h] [rbp+258h]
  __int64 v28; // [rsp+2E8h] [rbp+268h] BYREF
  __int64 (__fastcall *v29)(); // [rsp+2F0h] [rbp+270h] BYREF
  _QWORD *v30; // [rsp+2F8h] [rbp+278h]
  __int64 (__fastcall *v31)(); // [rsp+300h] [rbp+280h] BYREF
  _QWORD *v32; // [rsp+308h] [rbp+288h]
  __int64 v33; // [rsp+310h] [rbp+290h] BYREF
  _QWORD *v34; // [rsp+318h] [rbp+298h]
  __int64 (__fastcall *v35)(); // [rsp+320h] [rbp+2A0h] BYREF
  _QWORD *v36; // [rsp+328h] [rbp+2A8h]
  unsigned __int64 v37; // [rsp+348h] [rbp+2C8h]
  __int64 v38; // [rsp+350h] [rbp+2D0h]
  __int64 v39; // [rsp+358h] [rbp+2D8h]
  __int64 (__fastcall *v40)(); // [rsp+360h] [rbp+2E0h] BYREF
  _QWORD *v41; // [rsp+368h] [rbp+2E8h]
  __int64 (__fastcall *v42)(); // [rsp+370h] [rbp+2F0h] BYREF
  _QWORD *v43; // [rsp+378h] [rbp+2F8h]
  __int64 (__fastcall *v44)(); // [rsp+380h] [rbp+300h] BYREF
  _QWORD *v45; // [rsp+388h] [rbp+308h]
  __int64 (__fastcall *v46)(); // [rsp+390h] [rbp+310h] BYREF
  _QWORD *v47; // [rsp+398h] [rbp+318h]
  __int64 (__fastcall *v48)(); // [rsp+3A0h] [rbp+320h] BYREF
  _QWORD *v49; // [rsp+3A8h] [rbp+328h]
  __int64 (__fastcall *v50)(); // [rsp+3B0h] [rbp+330h] BYREF
  _QWORD *v51; // [rsp+3B8h] [rbp+338h]
  __int64 (__fastcall *v52)(); // [rsp+3C0h] [rbp+340h] BYREF
  _QWORD *v53; // [rsp+3C8h] [rbp+348h]
  __int64 (__fastcall *v54)(); // [rsp+3D0h] [rbp+350h] BYREF
  _QWORD *v55; // [rsp+3D8h] [rbp+358h]
  __int64 (__fastcall *v56)(); // [rsp+3E0h] [rbp+360h] BYREF
  _QWORD *v57; // [rsp+3E8h] [rbp+368h]
  __int64 (__fastcall *v58)(); // [rsp+3F0h] [rbp+370h] BYREF
  _QWORD *v59; // [rsp+3F8h] [rbp+378h]
  char v60[8]; // [rsp+400h] [rbp+380h] BYREF
  const char *v61; // [rsp+408h] [rbp+388h]
  __int64 v62; // [rsp+410h] [rbp+390h]
  const char *v63; // [rsp+418h] [rbp+398h]
  __int16 v64; // [rsp+420h] [rbp+3A0h]
  __int64 (__fastcall *v65)(); // [rsp+430h] [rbp+3B0h] BYREF
  _QWORD *v66; // [rsp+438h] [rbp+3B8h]
  __int64 (__fastcall *v67)(); // [rsp+440h] [rbp+3C0h]
  _QWORD *v68; // [rsp+448h] [rbp+3C8h]
  __int64 v69; // [rsp+450h] [rbp+3D0h]
  _QWORD *v70; // [rsp+458h] [rbp+3D8h]
  __int64 v71[4]; // [rsp+460h] [rbp+3E0h] BYREF
  __int64 (__fastcall *v72)(); // [rsp+480h] [rbp+400h]
  _QWORD *v73; // [rsp+488h] [rbp+408h]
  __int64 (__fastcall *v74)(); // [rsp+490h] [rbp+410h] BYREF
  _QWORD *v75; // [rsp+498h] [rbp+418h]
  __int64 (__fastcall *v76)(); // [rsp+4A0h] [rbp+420h] BYREF
  _QWORD *v77; // [rsp+4A8h] [rbp+428h]
  __int64 v78; // [rsp+4B0h] [rbp+430h] BYREF
  _QWORD *v79; // [rsp+4B8h] [rbp+438h]
  char v80; // [rsp+4C3h] [rbp+443h]
  unsigned int v81; // [rsp+4C4h] [rbp+444h]
  int v82; // [rsp+4C8h] [rbp+448h]
  char v83; // [rsp+4CFh] [rbp+44Fh]
  __int64 v84; // [rsp+4D0h] [rbp+450h]
  __int64 v85; // [rsp+4D8h] [rbp+458h]
  char Data__stdZprivateZoscommon_u33_10; // [rsp+4E7h] [rbp+467h]
  __int64 FirstFile__stdZprivateZoscommon_u24; // [rsp+4E8h] [rbp+468h]
  unsigned __int8 v88; // [rsp+4F7h] [rbp+477h]
  __int64 v89; // [rsp+4F8h] [rbp+478h]
  __int64 v90; // [rsp+500h] [rbp+480h]
  __int64 v91; // [rsp+508h] [rbp+488h]
  __int64 v92; // [rsp+510h] [rbp+490h]
  _QWORD *v93; // [rsp+518h] [rbp+498h]
  __int64 v94; // [rsp+520h] [rbp+4A0h]
  char v95; // [rsp+52Fh] [rbp+4AFh]
  __int64 v96; // [rsp+530h] [rbp+4B0h]
  __int64 v97; // [rsp+538h] [rbp+4B8h]
  __int64 *v98; // [rsp+540h] [rbp+4C0h]
  char v99; // [rsp+54Fh] [rbp+4CFh]
  __int64 v100; // [rsp+550h] [rbp+4D0h]
  _QWORD *v101; // [rsp+558h] [rbp+4D8h]
  char *v102; // [rsp+560h] [rbp+4E0h]
  __int64 v103; // [rsp+568h] [rbp+4E8h]
  __int64 v104; // [rsp+570h] [rbp+4F0h]
  __int64 v105; // [rsp+578h] [rbp+4F8h]
  char v106; // [rsp+584h] [rbp+504h]
  unsigned __int8 v107; // [rsp+585h] [rbp+505h]
  char v108; // [rsp+586h] [rbp+506h]
  char v109; // [rsp+587h] [rbp+507h]
  __int64 v110; // [rsp+588h] [rbp+508h]

  v3 = (_QWORD *)a1[1];
  v22 = (__int64 (__fastcall *)())*a1;
  v23 = v3;
  v61 = "recursive_load";
  v63 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
  v62 = 0i64;
  v64 = 0;
  nimFrame_162(v60);
  v102 = (char *)nimErrorFlag_157();
  v103 = 0i64;
  v101 = a3;
  v78 = 0i64;
  v79 = 0i64;
  v76 = 0i64;
  v77 = 0i64;
  v74 = 0i64;
  v75 = 0i64;
  v72 = 0i64;
  v73 = 0i64;
  nimZeroMem_132(v71, 24i64);
  v78 = 0i64;
  v79 = &TM__8FyyixzftvDEeBWCL79bP9aA_59_0;
  v62 = 3041i64;
  v18 = v22;
  v19 = v3;
  file_name__presenterZutilities_u35836(&v20, &v18);
  v76 = v20;
  v77 = v21;
  if ( !*v102 )
  {
    v62 = 3042i64;
    v100 = 0i64;
    v100 = nimNewObj(64i64, 8i64);
    v69 = v78;
    v70 = v79;
    v62 = 1699i64;
    v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    eqwasMoved___system_u2658(&v78);
    v4 = v100;
    v5 = v70;
    *(_QWORD *)v100 = v69;
    *(_QWORD *)(v4 + 8) = v5;
    v67 = v76;
    v68 = v77;
    v62 = 1699i64;
    v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    eqwasMoved___system_u2658(&v76);
    v6 = v100;
    v7 = v68;
    *(_QWORD *)(v100 + 16) = v67;
    *(_QWORD *)(v6 + 24) = v7;
    v62 = 3042i64;
    v63 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
    v106 = a2 != 0;
    if ( a2 )
      v106 = *(_BYTE *)(a2 + 56);
    *(_BYTE *)(v100 + 56) = v106;
    v103 = v100;
    v62 = 3044i64;
    v58 = 0i64;
    v59 = 0i64;
    v20 = v22;
    v21 = v23;
    to_string__modelZsanitized95path_u445(&v74, &v20);
    if ( !*v102 )
    {
      rawNewString(&v20, (char *)v74 + 8);
      v58 = v20;
      v59 = v21;
      v20 = v74;
      v21 = v75;
      appendString_79(&v58, &v20);
      v20 = (__int64 (__fastcall *)())TM__8FyyixzftvDEeBWCL79bP9aA_741;
      v21 = &TM__8FyyixzftvDEeBWCL79bP9aA_740;
      appendString_79(&v58, &v20);
      v72 = v58;
      v73 = v59;
      v99 = 0;
      v20 = v58;
      v21 = v59;
      v99 = nosfileExists(&v20);
      if ( !*v102 )
      {
        if ( v99 != 1 )
          goto LABEL_32;
        v56 = 0i64;
        v57 = 0i64;
        v54 = 0i64;
        v55 = 0i64;
        v52 = 0i64;
        v53 = 0i64;
        v62 = 3045i64;
        v20 = v22;
        v21 = v23;
        v8 = (void *)v101[4];
        v18 = (__int64 (__fastcall *)())v101[3];
        v19 = v8;
        minus___modelZutilities_u7455(&v54, &v20, &v18);
        if ( !*v102 )
        {
          v20 = v54;
          v21 = v55;
          to_string__modelZsanitized95path_u445(&v52, &v20);
          if ( !*v102 )
          {
            v20 = v52;
            v21 = v53;
            toLower__pureZunicode_u7800_3(&v56, &v20);
            if ( !*v102 )
            {
              v98 = 0i64;
              v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              v105 = 0i64;
              v62 = 250i64;
              v97 = v101[1];
              v96 = v97;
              v62 = 251i64;
              while ( v105 < v96 )
              {
                v62 = 3046i64;
                v63 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                if ( v105 < 0 || v105 >= v101[1] )
                {
                  raiseIndexError2(v105, v101[1] - 1i64);
                  break;
                }
                v98 = (__int64 *)(v101[2] + 16 * v105 + 8);
                v62 = 3047i64;
                v95 = 0;
                v20 = v56;
                v21 = v57;
                v9 = (void *)v98[1];
                v18 = (__int64 (__fastcall *)())*v98;
                v19 = v9;
                v95 = nsuStartsWith(&v20, &v18);
                if ( *v102 )
                  break;
                if ( v95 == 1 )
                {
                  *(_BYTE *)(v103 + 32) = 1;
                  v62 = 3049i64;
                  break;
                }
                v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                ++v105;
                v62 = 254i64;
                v94 = v101[1];
                if ( v94 != v96 )
                {
                  v20 = (__int64 (__fastcall *)())TM__8FyyixzftvDEeBWCL79bP9aA_742;
                  v21 = &TM__8FyyixzftvDEeBWCL79bP9aA_140_0;
                  failedAssertImpl__stdZassertions_u234(&v20);
                  if ( *v102 )
                    break;
                }
              }
            }
          }
        }
        v62 = 394i64;
        v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v53 && (*v53 & 0x4000000000000000i64) == 0 )
          deallocShared(v53);
        if ( v55 && (*v55 & 0x4000000000000000i64) == 0 )
          deallocShared(v55);
        if ( v57 && (*v57 & 0x4000000000000000i64) == 0 )
          deallocShared(v57);
        if ( !*v102 )
        {
LABEL_32:
          v62 = 3052i64;
          v63 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
          if ( a2 )
          {
            v93 = 0i64;
            v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            v104 = 0i64;
            v62 = 250i64;
            v92 = *(_QWORD *)(a2 + 40);
            v91 = v92;
            v62 = 251i64;
            while ( 1 )
            {
              if ( v104 >= v91 )
                goto LABEL_50;
              v50 = 0i64;
              v51 = 0i64;
              v48 = 0i64;
              v49 = 0i64;
              v90 = 0i64;
              v62 = 3053i64;
              v63 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
              if ( v104 < 0 || v104 >= *(_QWORD *)(a2 + 40) )
                break;
              v93 = (_QWORD *)(*(_QWORD *)(a2 + 48) + 8 * v104 + 8);
              v62 = 3054i64;
              v10 = *v93;
              v20 = v22;
              v21 = v23;
              v11 = *(void **)(v10 + 24);
              v18 = *(__int64 (__fastcall **)())(v10 + 16);
              v19 = v11;
              slash___modelZsanitized95path_u1477(&v50, &v20, &v18);
              if ( *v102 )
                goto LABEL_130;
              v20 = v50;
              v21 = v51;
              to_string__modelZsanitized95path_u445(&v48, &v20);
              if ( *v102 )
                goto LABEL_130;
              v62 = 934i64;
              v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              v90 = eqdup___presenterZutilities_u22971(*v93, 1i64);
              if ( *v102 )
                goto LABEL_130;
              v62 = 3054i64;
              v63 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
              v20 = v48;
              v21 = v49;
              X5BX5Deq___presenterZutilities_u35966(v71, &v20, v90);
              if ( *v102 )
                goto LABEL_130;
              v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v104;
              v62 = 254i64;
              v89 = *(_QWORD *)(a2 + 40);
              if ( v89 != v91 )
              {
                v20 = (__int64 (__fastcall *)())TM__8FyyixzftvDEeBWCL79bP9aA_743;
                v21 = &TM__8FyyixzftvDEeBWCL79bP9aA_140_0;
                failedAssertImpl__stdZassertions_u234(&v20);
                if ( *v102 )
                  goto LABEL_130;
              }
              v62 = 394i64;
              v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              if ( v49 && (*v49 & 0x4000000000000000i64) == 0 )
                deallocShared(v49);
              if ( v51 && (*v51 & 0x4000000000000000i64) == 0 )
                deallocShared(v51);
            }
            raiseIndexError2(v104, *(_QWORD *)(a2 + 40) - 1i64);
            goto LABEL_130;
          }
LABEL_50:
          v46 = 0i64;
          v47 = 0i64;
          v44 = 0i64;
          v45 = 0i64;
          v42 = 0i64;
          v43 = 0i64;
          v88 = 0;
          v62 = 3056i64;
          v63 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
          v20 = v22;
          v21 = v23;
          to_string__modelZsanitized95path_u445(&v44, &v20);
          if ( *v102 )
            goto LABEL_116;
          nimZeroMem_132(v24, 592i64);
          v62 = 201i64;
          v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\std\\private\\osdirs.nim";
          v20 = v44;
          v21 = v45;
          v18 = (__int64 (__fastcall *)())TM__8FyyixzftvDEeBWCL79bP9aA_744;
          v19 = &TM__8FyyixzftvDEeBWCL79bP9aA_438;
          slash___stdZprivateZospaths2_u87_18(&v42, &v20, &v18);
          if ( *v102
            || (v20 = v42,
                v21 = v43,
                FirstFile__stdZprivateZoscommon_u24 = findFirstFile__stdZprivateZoscommon_u24(&v20, v24),
                *v102) )
          {
LABEL_116:
            v62 = 394i64;
            v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v43 && (*v43 & 0x4000000000000000i64) == 0 )
              deallocShared(v43);
            if ( v45 && (*v45 & 0x4000000000000000i64) == 0 )
              deallocShared(v45);
            if ( v47 && (*v47 & 0x4000000000000000i64) == 0 )
              deallocShared(v47);
            if ( !*v102 )
            {
              v62 = 3066i64;
              v63 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
              nimZeroMem_132(&v65, 16i64);
              v65 = colonanonymous___presenterZutilities_u38160;
              v66 = 0i64;
              v13 = *(_QWORD *)(v103 + 40);
              if ( *(_QWORD *)(v103 + 48) )
                v14 = *(_QWORD *)(v103 + 48) + 8i64;
              else
                v14 = 0i64;
              v20 = v65;
              v21 = v66;
              sort__presenterZutilities_u37910(v14, v13, &v20, 1i64);
            }
            goto LABEL_130;
          }
          v62 = 202i64;
          if ( FirstFile__stdZprivateZoscommon_u24 == -1 )
          {
            v62 = 203i64;
            goto LABEL_116;
          }
          v62 = 207i64;
          while ( 1 )
          {
            v107 = 0;
            v62 = 209i64;
            Data__stdZprivateZoscommon_u33_10 = 0;
            Data__stdZprivateZoscommon_u33_10 = skipFindData__stdZprivateZoscommon_u33_10(v24);
            if ( *v102 )
            {
LABEL_115:
              v62 = 206i64;
              ((void (__fastcall *)(__int64))*refptr_Dl_1744830719_)(FirstFile__stdZprivateZoscommon_u24);
              goto LABEL_116;
            }
            if ( !Data__stdZprivateZoscommon_u33_10 )
              break;
LABEL_110:
            v62 = 217i64;
            v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\std\\private\\osdirs.nim";
            v82 = 0;
            v82 = ((__int64 (__fastcall *)(__int64, _WORD *))*refptr_Dl_1744830716_)(
                    FirstFile__stdZprivateZoscommon_u24,
                    v24);
            if ( !v82 )
            {
              v62 = 218i64;
              v81 = ((__int64 (*)(void))*refptr_Dl_1744830633_)();
              v62 = 219i64;
              if ( v81 == 18 )
                goto LABEL_115;
              v62 = 220i64;
              v20 = (__int64 (__fastcall *)())TM__8FyyixzftvDEeBWCL79bP9aA_757;
              v21 = &TM__8FyyixzftvDEeBWCL79bP9aA_59_0;
              raiseOSError__stdZoserrors_u122(v81, &v20);
              if ( *v102 )
                goto LABEL_115;
            }
          }
          v40 = 0i64;
          v41 = 0i64;
          v62 = 210i64;
          if ( (v24[0] & 0x10) != 0 )
          {
            v62 = 211i64;
            v107 = 2;
          }
          v62 = 212i64;
          if ( (v24[0] & 0x400) != 0 )
          {
            v62 = 213i64;
            v37 = v107 + 1i64;
            if ( v37 >= 4 )
            {
              raiseOverflow();
              goto LABEL_106;
            }
            v107 = v37;
          }
          v38 = 0i64;
          v39 = 0i64;
          v35 = 0i64;
          v36 = 0i64;
          v33 = 0i64;
          v34 = 0i64;
          v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\std\\private\\osdirs.nim";
          v62 = 215i64;
          dollar___stdZwidestrs_u394(&v35, &v25);
          if ( !*v102 )
          {
            v20 = v35;
            v21 = v36;
            nosextractFilename(&v33, &v20);
            if ( !*v102 )
            {
              v18 = v44;
              v19 = v45;
              v17[0] = v33;
              v17[1] = (__int64)v34;
              slash___stdZprivateZospaths2_u87_18(&v20, &v18, v17);
              v40 = v20;
              v41 = v21;
              if ( !*v102 )
              {
                v62 = 394i64;
                v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                if ( v34 && (*v34 & 0x4000000000000000i64) == 0 )
                  deallocShared(v34);
                if ( v36 && (*v36 & 0x4000000000000000i64) == 0 )
                  deallocShared(v36);
                v88 = v107;
                v62 = 1699i64;
                v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                v20 = v40;
                v21 = v41;
                eqsink___system_u2667(&v46, &v20);
                eqwasMoved___system_u2658(&v40);
                v31 = 0i64;
                v32 = 0i64;
                v110 = 0i64;
                v29 = 0i64;
                v30 = 0i64;
                v28 = 0i64;
                v62 = 3057i64;
                v63 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                if ( v88 == 2 )
                {
                  v62 = 3060i64;
                  v20 = v46;
                  v21 = v47;
                  as_sanitized_folder_name__modelZsanitized95path_u1302(&v31, &v20);
                  if ( !*v102 )
                  {
                    v62 = 3061i64;
                    v20 = v31;
                    v21 = v32;
                    to_string__modelZsanitized95path_u445(&v29, &v20);
                    if ( !*v102 )
                    {
                      v16[0] = v71[0];
                      v16[1] = v71[1];
                      v16[2] = v71[2];
                      v20 = v29;
                      v21 = v30;
                      v110 = getOrDefault__presenterZutilities_u37565(v16, &v20);
                      if ( !*v102 )
                      {
                        v62 = 3062i64;
                        nimZeroMem_132(&v26, 16i64);
                        v26 = (__int64 (__fastcall *)(__int64 (__fastcall **)(), __int64))recursive_load__presenterZutilities_u37639;
                        v27 = v101;
                        v20 = v31;
                        v21 = v32;
                        v12 = v101
                            ? ((__int64 (__fastcall *)(__int64 (__fastcall **)(), __int64, _QWORD *))v26)(
                                &v20,
                                v110,
                                v27)
                            : v26(&v20, v110);
                        v28 = v12;
                        if ( !*v102 )
                        {
                          v62 = 3063i64;
                          v109 = v28 != 0;
                          if ( v28 )
                          {
                            v108 = 0;
                            v85 = *(_QWORD *)(v28 + 40);
                            v108 = v85 > 0;
                            if ( v85 <= 0 )
                              v108 = *(_BYTE *)(v28 + 32);
                            v109 = v108;
                          }
                          if ( v109 == 1 )
                          {
                            v62 = 3064i64;
                            v84 = v28;
                            nimMarkCyclic_1(v28);
                            v62 = 934i64;
                            v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                            eqwasMoved___presenterZutilities_u22961(&v28);
                            if ( !*v102 )
                            {
                              v62 = 3064i64;
                              v63 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                              add__presenterZutilities_u37852(v103 + 40, v84);
                            }
                          }
                        }
                      }
                    }
                  }
                  v83 = *v102;
                  *v102 = 0;
                  v62 = 934i64;
                  v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                  eqdestroy___presenterZutilities_u22964(v28);
                  if ( !*v102 )
                  {
                    v62 = 394i64;
                    if ( v30 && (*v30 & 0x4000000000000000i64) == 0 )
                      deallocShared(v30);
                    v62 = 934i64;
                    eqdestroy___presenterZutilities_u22964(v110);
                    if ( !*v102 )
                    {
                      v62 = 394i64;
                      if ( v32 && (*v32 & 0x4000000000000000i64) == 0 )
                        deallocShared(v32);
                      *v102 = v83;
                    }
                  }
                }
                else
                {
                  v62 = 934i64;
                  v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                  eqdestroy___presenterZutilities_u22964(v28);
                  if ( !*v102 )
                  {
                    v62 = 394i64;
                    if ( v30 && (*v30 & 0x4000000000000000i64) == 0 )
                      deallocShared(v30);
                    v62 = 934i64;
                    eqdestroy___presenterZutilities_u22964(v110);
                    if ( !*v102 )
                    {
                      v62 = 394i64;
                      if ( v32 && (*v32 & 0x4000000000000000i64) == 0 )
                        deallocShared(v32);
                      v62 = 3058i64;
                      v63 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                    }
                  }
                }
              }
            }
          }
LABEL_106:
          if ( v41 && (*v41 & 0x4000000000000000i64) == 0 )
            deallocShared(v41);
          if ( *v102 )
            goto LABEL_115;
          goto LABEL_110;
        }
      }
    }
  }
LABEL_130:
  v80 = *v102;
  *v102 = 0;
  v62 = 3051i64;
  eqdestroy___presenterZutilities_u38089(v71);
  if ( !*v102 )
  {
    v62 = 394i64;
    v63 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v73 && (*v73 & 0x4000000000000000i64) == 0 )
      deallocShared(v73);
    if ( v75 && (*v75 & 0x4000000000000000i64) == 0 )
      deallocShared(v75);
    if ( v77 && (*v77 & 0x4000000000000000i64) == 0 )
      deallocShared(v77);
    if ( v79 && (*v79 & 0x4000000000000000i64) == 0 )
      deallocShared(v79);
    *v102 = v80;
  }
  popFrame_162();
  return v103;
}
