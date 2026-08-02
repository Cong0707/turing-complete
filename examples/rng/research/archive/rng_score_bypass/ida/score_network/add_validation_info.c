__int64 __fastcall add_validation_info__modelZnetworkingZnetworking_u207(__int64 a1, __int64 *a2)
{
  void *v2; // rdx
  __int64 v3; // rdx
  __int64 v4; // rdx
  void *v5; // rdx
  __int64 v6; // rax
  __int64 v7; // rdx
  __int64 v9; // [rsp+0h] [rbp-80h] BYREF
  __int64 v10; // [rsp+20h] [rbp-60h] BYREF
  __int64 v11; // [rsp+28h] [rbp-58h]
  __int64 v12; // [rsp+30h] [rbp-50h]
  __int64 v13; // [rsp+40h] [rbp-40h] BYREF
  void *v14; // [rsp+48h] [rbp-38h]
  __int64 v15; // [rsp+50h] [rbp-30h]
  __int64 v16; // [rsp+58h] [rbp-28h] BYREF
  __int64 v17; // [rsp+60h] [rbp-20h] BYREF
  char *v18; // [rsp+68h] [rbp-18h]
  const char *v19; // [rsp+78h] [rbp-8h]
  __int64 v20; // [rsp+80h] [rbp+0h]
  const char *v21; // [rsp+88h] [rbp+8h]
  __int16 v22; // [rsp+90h] [rbp+10h]
  char v23[1024]; // [rsp+A0h] [rbp+20h] BYREF
  __int64 v24; // [rsp+4A0h] [rbp+420h]
  char v25; // [rsp+4AFh] [rbp+42Fh]
  __int64 v26; // [rsp+4B0h] [rbp+430h]
  __int64 v27; // [rsp+4B8h] [rbp+438h]
  __int64 v28; // [rsp+4C0h] [rbp+440h]
  __int64 v29; // [rsp+4C8h] [rbp+448h]
  __int64 v30; // [rsp+4D0h] [rbp+450h]
  __int64 v31; // [rsp+4D8h] [rbp+458h]
  __int64 v32; // [rsp+4E0h] [rbp+460h]
  __int64 v33; // [rsp+4E8h] [rbp+468h]
  __int64 v34; // [rsp+4F0h] [rbp+470h]
  __int64 v35; // [rsp+4F8h] [rbp+478h]
  __int64 v36; // [rsp+500h] [rbp+480h]
  _QWORD *v37; // [rsp+508h] [rbp+488h]
  __int64 v38; // [rsp+510h] [rbp+490h]
  _BYTE *v39; // [rsp+518h] [rbp+498h]
  __int64 v40; // [rsp+520h] [rbp+4A0h]
  __int64 v41; // [rsp+528h] [rbp+4A8h]

  v19 = "add_validation_info";
  v21 = "D:\\TuringComplete_Phu\\model\\networking\\networking.nim";
  v20 = 0i64;
  v22 = 0;
  nimFrame_90(&v9 + 14);
  v39 = (_BYTE *)nimErrorFlag_88();
  v20 = 204i64;
  v21 = "D:\\TuringComplete_Phu\\model\\networking\\networking.nim";
  v2 = (void *)a2[1];
  v13 = *a2;
  v14 = v2;
  add_string__modelZsave95mongerZserialize_u551(a1, &v13);
  if ( !*v39 )
  {
    nimZeroMem_68(v23, 1024i64);
    v20 = 207i64;
    add_schematic__modelZnetworkingZnetworking_u162(a1, 0, (_DWORD)a2 + 16, (int)v23);
    if ( !*v39 )
    {
      v20 = 209i64;
      v38 = a2[11];
      add_u16__modelZsave95mongerZserialize_u305(a1, (unsigned __int16)v38);
      if ( !*v39 )
      {
        v37 = 0i64;
        v36 = 0i64;
        v35 = 0i64;
        v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v41 = 0i64;
        v20 = 250i64;
        v34 = a2[11];
        v33 = v34;
        v20 = 251i64;
        while ( v41 < v33 )
        {
          v20 = 210i64;
          v21 = "D:\\TuringComplete_Phu\\model\\networking\\networking.nim";
          if ( v41 < 0
            || v41 >= a2[11]
            || (v37 = (_QWORD *)(a2[12] + 1104 * v41 + 8), v41 >= a2[11])
            || (v36 = a2[12] + 1104 * v41 + 16, v41 >= a2[11]) )
          {
            raiseIndexError2(v41, a2[11] - 1);
            return popFrame_90();
          }
          v35 = a2[12] + 1104 * v41 + 80 + 8;
          v20 = 211i64;
          add_schematic__modelZnetworkingZnetworking_u162(a1, *v37, v36, v35);
          if ( !*v39 )
          {
            v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v41;
            v20 = 254i64;
            v32 = a2[11];
            if ( v32 == v33 )
              continue;
            v13 = TM__aYI4vTGtkCKyC3NTAt9aNQw_76;
            v14 = &TM__aYI4vTGtkCKyC3NTAt9aNQw_75;
            failedAssertImpl__stdZassertions_u234(&v13);
            if ( !*v39 )
              continue;
          }
          return popFrame_90();
        }
        v20 = 213i64;
        v21 = "D:\\TuringComplete_Phu\\model\\networking\\networking.nim";
        v31 = 0i64;
        v3 = a2[14];
        v10 = a2[13];
        v11 = v3;
        v12 = a2[15];
        v31 = len__modelZnetworkingZnetworking_u279(&v10);
        if ( !*v39 )
        {
          add_u16__modelZsave95mongerZserialize_u305(a1, (unsigned __int16)v31);
          if ( !*v39 )
          {
            v17 = 0i64;
            v18 = 0i64;
            nimZeroMem_68(&v16, 8i64);
            v30 = 0i64;
            v20 = 767i64;
            v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
            v4 = a2[14];
            v10 = a2[13];
            v11 = v4;
            v12 = a2[15];
            v29 = len__modelZnetworkingZnetworking_u279(&v10);
            if ( !*v39 )
            {
              v28 = 0i64;
              v27 = 0i64;
              v20 = 768i64;
              v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
              v26 = a2[13] - 1;
              v27 = v26;
              v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
              v40 = 0i64;
              v20 = 97i64;
              while ( v40 <= v27 )
              {
                v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                v28 = v40;
                v20 = 769i64;
                if ( v40 < 0 || v28 >= a2[13] )
                {
LABEL_33:
                  raiseIndexError2(v28, a2[13] - 1);
                  return popFrame_90();
                }
                v25 = 0;
                v25 = isFilled__pureZcollectionsZtables_u31_11(*(_QWORD *)(a2[14] + 40 * v28 + 8));
                if ( *v39 )
                  return popFrame_90();
                if ( v25 == 1 )
                {
                  v20 = 214i64;
                  v21 = "D:\\TuringComplete_Phu\\model\\networking\\networking.nim";
                  if ( v28 < 0 )
                    goto LABEL_33;
                  if ( v28 >= a2[13] )
                    goto LABEL_33;
                  v16 = *(_QWORD *)(a2[14] + 40 * v28 + 16);
                  v20 = 1772i64;
                  v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\times.nim";
                  if ( v28 >= a2[13] )
                    goto LABEL_33;
                  v5 = *(void **)(a2[14] + 40 * v28 + 32);
                  v13 = *(_QWORD *)(a2[14] + 40 * v28 + 24);
                  v14 = v5;
                  eqcopy___pureZtimes_u2671(&v17, &v13);
                  v20 = 214i64;
                  v21 = "D:\\TuringComplete_Phu\\model\\networking\\networking.nim";
                  if ( v28 < 0 || v28 >= a2[13] )
                    goto LABEL_33;
                  v30 = *(_QWORD *)(a2[14] + 40 * v28 + 40);
                  v20 = 215i64;
                  add_i64__modelZsave95mongerZserialize_u264(a1, v16);
                  if ( *v39 )
                    return popFrame_90();
                  v20 = 216i64;
                  v6 = v18 ? (__int64)(v18 + 8) : 0i64;
                  add_long_seq_u8__modelZsave95mongerZserialize_u357(a1, v6, v17);
                  if ( *v39 )
                    return popFrame_90();
                  v20 = 217i64;
                  add_u64__modelZsave95mongerZserialize_u197(a1, v30);
                  if ( *v39 )
                    return popFrame_90();
                  v20 = 771i64;
                  v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                  v24 = 0i64;
                  v7 = a2[14];
                  v10 = a2[13];
                  v11 = v7;
                  v12 = a2[15];
                  v24 = len__modelZnetworkingZnetworking_u279(&v10);
                  if ( *v39 )
                    return popFrame_90();
                  if ( v24 != v29 )
                  {
                    v13 = TM__aYI4vTGtkCKyC3NTAt9aNQw_78;
                    v14 = &TM__aYI4vTGtkCKyC3NTAt9aNQw_77;
                    failedAssertImpl__stdZassertions_u234(&v13);
                    if ( *v39 )
                      return popFrame_90();
                  }
                }
                v20 = 102i64;
                v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                v15 = v40 + 1;
                if ( __OFADD__(1i64, v40) )
                {
                  raiseOverflow();
                  return popFrame_90();
                }
                v40 = v15;
              }
              v20 = 1772i64;
              v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\times.nim";
              v13 = v17;
              v14 = v18;
              eqdestroy___pureZtimes_u2668(&v13);
            }
          }
        }
      }
    }
  }
  return popFrame_90();
}
