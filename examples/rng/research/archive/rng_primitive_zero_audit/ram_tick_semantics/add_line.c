__int64 __fastcall add_line__modelZsimulationZcode95gen_u2131(__int64 *a1, __int64 a2)
{
  __int64 v2; // rbx
  __int64 v4; // [rsp+0h] [rbp-B0h] BYREF
  __int64 v5; // [rsp+20h] [rbp-90h] BYREF
  _QWORD *v6; // [rsp+28h] [rbp-88h]
  __int64 v7; // [rsp+30h] [rbp-80h]
  _QWORD *v8; // [rsp+38h] [rbp-78h]
  const char *v9; // [rsp+48h] [rbp-68h]
  __int64 v10; // [rsp+50h] [rbp-60h]
  const char *v11; // [rsp+58h] [rbp-58h]
  __int16 v12; // [rsp+60h] [rbp-50h]
  __int64 v13; // [rsp+70h] [rbp-40h] BYREF
  _QWORD *v14; // [rsp+78h] [rbp-38h]
  __int64 v15; // [rsp+80h] [rbp-30h]
  _QWORD *v16; // [rsp+88h] [rbp-28h]
  __int64 v17; // [rsp+90h] [rbp-20h] BYREF
  _QWORD *v18; // [rsp+98h] [rbp-18h]
  __int64 v19; // [rsp+A0h] [rbp-10h]
  _BYTE *v20; // [rsp+A8h] [rbp-8h]

  v2 = a1[1];
  v7 = *a1;
  v8 = (_QWORD *)v2;
  v9 = "add_line";
  v11 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v10 = 0i64;
  v12 = 0;
  nimFrame_88(&v4 + 8);
  v20 = (_BYTE *)nimErrorFlag_86();
  v19 = a2;
  v17 = 0i64;
  v18 = 0i64;
  v15 = 0i64;
  v16 = 0i64;
  v10 = 199i64;
  v11 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v13 = 0i64;
  v14 = 0i64;
  if ( *(__int64 *)(a2 + 96) >= 0 )
  {
    nsuRepeatChar(&v17, 32i64, *(_QWORD *)(v19 + 96));
    if ( !*v20 )
    {
      rawNewString(&v5, v17 + v7 + 1);
      v13 = v5;
      v14 = v6;
      v5 = v17;
      v6 = v18;
      appendString_29(&v13, &v5);
      v5 = v7;
      v6 = v8;
      appendString_29(&v13, &v5);
      v5 = TM__THWBxVSaWN2Zh7OMooFH0w_510;
      v6 = &TM__THWBxVSaWN2Zh7OMooFH0w_14;
      appendString_29(&v13, &v5);
      v15 = v13;
      v16 = v14;
      prepareAdd(v19 + 8, v13);
      v5 = v15;
      v6 = v16;
      appendString_29(v19 + 8, &v5);
      v10 = 394i64;
      v11 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v16 && (*v16 & 0x4000000000000000i64) == 0 )
        deallocShared(v16);
      if ( v18 && (*v18 & 0x4000000000000000i64) == 0 )
        deallocShared(v18);
    }
  }
  else
  {
    raiseRangeErrorI(*(_QWORD *)(v19 + 96), 0i64, 0x7FFFFFFFFFFFFFFFi64);
  }
  return popFrame_88();
}
