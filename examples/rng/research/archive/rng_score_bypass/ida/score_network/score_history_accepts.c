__int64 __fastcall update_efficient_frontier__modelZutilities_u8881(_QWORD *a1, __int64 *a2)
{
  __int64 v3; // rdx
  __int64 v5; // [rsp+0h] [rbp-F0h] BYREF
  __int64 v6; // [rsp+20h] [rbp-D0h] BYREF
  __int64 v7; // [rsp+28h] [rbp-C8h]
  __int64 v8; // [rsp+30h] [rbp-C0h]
  __int64 v9; // [rsp+40h] [rbp-B0h] BYREF
  __int64 v10; // [rsp+48h] [rbp-A8h]
  __int64 v11; // [rsp+50h] [rbp-A0h]
  __int64 v12; // [rsp+68h] [rbp-88h]
  const char *v13; // [rsp+78h] [rbp-78h]
  __int64 v14; // [rsp+80h] [rbp-70h]
  const char *v15; // [rsp+88h] [rbp-68h]
  __int16 v16; // [rsp+90h] [rbp-60h]
  __int64 v17[4]; // [rsp+A0h] [rbp-50h] BYREF
  __int64 v18; // [rsp+C0h] [rbp-30h]
  __int64 v19; // [rsp+C8h] [rbp-28h]
  __int64 v20; // [rsp+D0h] [rbp-20h]
  bool v21; // [rsp+DEh] [rbp-12h]
  bool v22; // [rsp+DFh] [rbp-11h]
  __int64 v23; // [rsp+E0h] [rbp-10h]
  unsigned __int8 v24; // [rsp+EFh] [rbp-1h]

  v13 = "update_efficient_frontier";
  v15 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  v14 = 0i64;
  v16 = 0;
  nimFrame_145(&v5 + 14);
  v24 = 0;
  nimZeroMem_118(v17, 24i64);
  v20 = 0i64;
  v19 = 0i64;
  v14 = 849i64;
  v15 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  v18 = *a1 - 1i64;
  v19 = v18;
  v15 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
  v23 = v18;
  v14 = 34i64;
  while ( v23 >= 0 )
  {
    v15 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
    v20 = v23;
    v14 = 850i64;
    v22 = 0;
    if ( v23 >= *a1 )
      goto LABEL_13;
    v22 = *(_QWORD *)(a1[1] + 24 * v20 + 8) <= *a2;
    if ( v22 )
    {
      if ( v20 >= *a1 )
        goto LABEL_13;
      v22 = *(_QWORD *)(a1[1] + 24 * v20 + 16) <= a2[1];
    }
    if ( v22 )
    {
      v14 = 851i64;
      v24 = 0;
      goto LABEL_21;
    }
    v14 = 852i64;
    v21 = 0;
    if ( v20 >= *a1 )
    {
LABEL_13:
      raiseIndexError2(v20, *a1 - 1i64);
      goto LABEL_21;
    }
    v21 = *a2 <= *(_QWORD *)(a1[1] + 24 * v20 + 8);
    if ( v21 )
    {
      if ( v20 >= *a1 )
        goto LABEL_13;
      v21 = a2[1] <= *(_QWORD *)(a1[1] + 24 * v20 + 16);
    }
    if ( v21 )
    {
      v14 = 853i64;
      del__modelZutilities_u8894(a1, v20);
    }
    v14 = 39i64;
    v15 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v12 = v23 - 1;
    if ( __OFSUB__(v23, 1i64) )
    {
      raiseOverflow();
      goto LABEL_21;
    }
    v23 = v12;
  }
  v14 = 176i64;
  v15 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
  v3 = a2[1];
  v6 = *a2;
  v7 = v3;
  v8 = a2[2];
  eqdup___modelZnetworkingZclient_u1795(&v9, &v6);
  v17[0] = v9;
  v17[1] = v10;
  v17[2] = v11;
  v14 = 855i64;
  v15 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  v6 = v9;
  v7 = v10;
  v8 = v11;
  add__modelZnetworkingZclient_u1345(a1, &v6);
  v14 = 856i64;
  v24 = 1;
LABEL_21:
  popFrame_145();
  return v24;
}
