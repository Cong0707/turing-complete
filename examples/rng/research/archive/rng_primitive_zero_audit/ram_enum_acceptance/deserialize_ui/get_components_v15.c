// address: 0x1401be0a7-0x1401be465
// name: get_components__modelZsave95mongerZversionsZv15_u282
_QWORD *__fastcall get_components__modelZsave95mongerZversionsZv15_u282(
        _QWORD *a1,
        __int64 *a2,
        __int64 a3,
        unsigned __int8 a4)
{
  __int64 v4; // rax
  __int64 v5; // rdx
  __int64 v6; // rax
  __int64 v7; // rdx
  __int64 v9[2]; // [rsp+20h] [rbp-60h] BYREF
  __int64 v10; // [rsp+30h] [rbp-50h]
  __int64 v11; // [rsp+38h] [rbp-48h]
  __int64 v12[70]; // [rsp+40h] [rbp-40h] BYREF
  char v13[560]; // [rsp+270h] [rbp+1F0h] BYREF
  __int64 v14; // [rsp+4A0h] [rbp+420h]
  __int64 v15; // [rsp+4A8h] [rbp+428h]
  char v16[8]; // [rsp+4B0h] [rbp+430h] BYREF
  const char *v17; // [rsp+4B8h] [rbp+438h]
  __int64 v18; // [rsp+4C0h] [rbp+440h]
  const char *v19; // [rsp+4C8h] [rbp+448h]
  __int16 v20; // [rsp+4D0h] [rbp+450h]
  __int64 v21; // [rsp+4E0h] [rbp+460h] BYREF
  __int64 v22; // [rsp+4E8h] [rbp+468h]
  __int64 v23; // [rsp+4F8h] [rbp+478h]
  __int64 v24; // [rsp+500h] [rbp+480h]
  __int64 i64__modelZsave95mongerZserialize_u49; // [rsp+508h] [rbp+488h]
  _BYTE *v26; // [rsp+510h] [rbp+490h]
  __int64 v27; // [rsp+518h] [rbp+498h]

  v4 = *a2;
  v5 = a2[1];
  v10 = v4;
  v11 = v5;
  v17 = "get_components";
  v19 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
  v18 = 0i64;
  v20 = 0;
  nimFrame_58(v16);
  v26 = (_BYTE *)nimErrorFlag_56();
  v21 = 0i64;
  v22 = 0i64;
  v18 = 86i64;
  v19 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
  if ( v11 )
    v6 = v11 + 8;
  else
    v6 = 0i64;
  i64__modelZsave95mongerZserialize_u49 = get_i64__modelZsave95mongerZserialize_u49(v6, v10, a3);
  if ( !*v26 )
  {
    v24 = 0i64;
    v23 = 0i64;
    v18 = 87i64;
    v19 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
    v15 = i64__modelZsave95mongerZserialize_u49 - 1;
    if ( __OFSUB__(i64__modelZsave95mongerZserialize_u49, 1i64) )
    {
      raiseOverflow();
    }
    else
    {
      v23 = v15;
      v19 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v27 = 0i64;
      v18 = 117i64;
      do
      {
        if ( v27 > v23 )
          break;
        nimZeroMem_42(v12, 560i64);
        v19 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
        v24 = v27;
        v18 = 88i64;
        v9[0] = v10;
        v9[1] = v11;
        get_component__modelZsave95mongerZversionsZv15_u3(v9, a3, a4, v12);
        if ( !*v26 )
        {
          v18 = 89i64;
          nimZeroMem_42(v13, 560i64);
          qmemcpy(v13, v12, sizeof(v13));
          v18 = 34i64;
          v19 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
          eqwasMoved___modelZsave95mongerZversionsZv0_u142(v12, v12);
          v18 = 89i64;
          v19 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
          add__modelZsave95mongerZversionsZv0_u1028(&v21, v13);
          v18 = 119i64;
          v19 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v14 = v27 + 1;
          if ( __OFADD__(1i64, v27) )
            raiseOverflow();
          else
            v27 = v14;
        }
        v18 = 34i64;
        v19 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        eqdestroy___modelZsave95mongerZversionsZv0_u145(v12);
      }
      while ( !*v26 );
    }
  }
  popFrame_58();
  v7 = v22;
  *a1 = v21;
  a1[1] = v7;
  return a1;
}
