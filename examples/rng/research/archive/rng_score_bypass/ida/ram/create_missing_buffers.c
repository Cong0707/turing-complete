__int64 __fastcall create_missing_buffers__modelZboardZmemory95manager_u2550(
        __int64 *a1,
        __int64 *a2,
        __int64 *a3,
        __int64 *a4,
        __int64 *a5,
        __int64 a6)
{
  __int64 v6; // rdx
  __int64 v7; // rdx
  __int64 v8; // rdx
  __int64 v10; // [rsp+0h] [rbp-F0h] BYREF
  __int64 v11[2]; // [rsp+30h] [rbp-C0h] BYREF
  __int64 v12[2]; // [rsp+40h] [rbp-B0h] BYREF
  __int64 v13; // [rsp+50h] [rbp-A0h] BYREF
  void *v14; // [rsp+58h] [rbp-98h]
  __int64 v15; // [rsp+60h] [rbp-90h]
  __int64 v16; // [rsp+68h] [rbp-88h]
  __int64 v17; // [rsp+70h] [rbp-80h]
  __int64 v18; // [rsp+78h] [rbp-78h]
  __int64 v19; // [rsp+80h] [rbp-70h]
  void *v20; // [rsp+88h] [rbp-68h]
  const char *v21; // [rsp+98h] [rbp-58h]
  __int64 v22; // [rsp+A0h] [rbp-50h]
  const char *v23; // [rsp+A8h] [rbp-48h]
  __int16 v24; // [rsp+B0h] [rbp-40h]
  __int64 v25; // [rsp+C0h] [rbp-30h]
  __int64 v26; // [rsp+C8h] [rbp-28h]
  __int64 v27; // [rsp+D0h] [rbp-20h]
  unsigned __int8 *v28; // [rsp+D8h] [rbp-18h]
  _BYTE *v29; // [rsp+E0h] [rbp-10h]
  __int64 v30; // [rsp+E8h] [rbp-8h]

  v6 = a3[1];
  v19 = *a3;
  v20 = (void *)v6;
  v7 = a4[1];
  v17 = *a4;
  v18 = v7;
  v8 = a5[1];
  v15 = *a5;
  v16 = v8;
  v21 = "create_missing_buffers";
  v23 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
  v22 = 0i64;
  v24 = 0;
  nimFrame_72(&v10 + 18);
  v29 = (_BYTE *)nimErrorFlag_70();
  v28 = 0i64;
  v23 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v30 = 0i64;
  v22 = 259i64;
  v27 = *a2;
  v26 = v27;
  v22 = 260i64;
  while ( v30 < v26 )
  {
    v22 = 284i64;
    v23 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
    if ( v30 < 0 || v30 >= *a2 )
    {
      raiseIndexError2(v30, *a2 - 1);
      return popFrame_72();
    }
    v28 = (unsigned __int8 *)(a2[1] + 560 * v30 + 8);
    v22 = 285i64;
    v13 = v19;
    v14 = v20;
    v12[0] = v17;
    v12[1] = v18;
    v11[0] = v15;
    v11[1] = v16;
    create_buffer_for_component__modelZboardZmemory95manager_u351(a1, v28, &v13, v12, v11, a6);
    if ( !*v29 )
    {
      v23 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      ++v30;
      v22 = 263i64;
      v25 = *a2;
      if ( v25 == v26 )
        continue;
      v13 = TM__L0TtlZGGNBsNJ2HmEX3X7A_39;
      v14 = &TM__L0TtlZGGNBsNJ2HmEX3X7A_38;
      failedAssertImpl__stdZassertions_u234(&v13);
      if ( !*v29 )
        continue;
    }
    return popFrame_72();
  }
  return popFrame_72();
}
