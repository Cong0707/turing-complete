_QWORD *__fastcall get_output_z_value__modelZsimulationZcode95gen_u3951(_QWORD *a1, __int64 *a2, _QWORD *a3)
{
  __int64 v4; // rdx
  __int64 v5; // rdx
  __int64 v6; // rdx
  __int64 v7; // rdx
  __int64 v8; // rdx
  void *v9; // rdx
  __int64 v11; // [rsp+0h] [rbp-F0h] BYREF
  __int64 v12; // [rsp+20h] [rbp-D0h] BYREF
  void *v13; // [rsp+28h] [rbp-C8h]
  __int64 v14; // [rsp+30h] [rbp-C0h] BYREF
  __int64 v15; // [rsp+38h] [rbp-B8h]
  __int64 v16; // [rsp+40h] [rbp-B0h]
  __int64 v17; // [rsp+50h] [rbp-A0h] BYREF
  __int64 v18; // [rsp+58h] [rbp-98h]
  __int64 v19; // [rsp+60h] [rbp-90h]
  const char *v20; // [rsp+78h] [rbp-78h]
  __int64 v21; // [rsp+80h] [rbp-70h]
  const char *v22; // [rsp+88h] [rbp-68h]
  __int16 v23; // [rsp+90h] [rbp-60h]
  __int64 v24; // [rsp+A0h] [rbp-50h] BYREF
  void *v25; // [rsp+A8h] [rbp-48h]
  __int64 v26; // [rsp+B0h] [rbp-40h] BYREF
  _QWORD *v27; // [rsp+B8h] [rbp-38h]
  __int64 v28; // [rsp+C0h] [rbp-30h]
  void *v29; // [rsp+C8h] [rbp-28h]
  char v30; // [rsp+DEh] [rbp-12h]
  char v31; // [rsp+DFh] [rbp-11h]
  _QWORD *v32; // [rsp+E0h] [rbp-10h]
  _BYTE *v33; // [rsp+E8h] [rbp-8h]

  v20 = "get_output_z_value";
  v22 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v21 = 0i64;
  v23 = 0;
  nimFrame_88(&v11 + 14);
  v33 = (_BYTE *)nimErrorFlag_86();
  v28 = 0i64;
  v29 = 0i64;
  v32 = a3;
  v26 = 0i64;
  v27 = 0i64;
  v21 = 392i64;
  v31 = 0;
  v4 = a2[1];
  v17 = *a2;
  v18 = v4;
  v19 = a2[2];
  v5 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 1);
  v14 = *(_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435;
  v15 = v5;
  v16 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 2);
  v31 = eqeq___modelZsimulationZcontroller_u106(&v17, &v14);
  if ( v31 != 1 )
  {
    v21 = 393i64;
    v22 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v30 = 0;
    v6 = v32[8];
    v14 = v32[7];
    v15 = v6;
    v16 = v32[9];
    v7 = a2[1];
    v17 = *a2;
    v18 = v7;
    v19 = a2[2];
    v30 = contains__modelZsimulationZcode95gen_u3866(&v14, &v17);
    if ( !*v33 )
    {
      if ( !v30 )
      {
        v28 = 5i64;
        v29 = &TM__THWBxVSaWN2Zh7OMooFH0w_2021;
        v21 = 394i64;
        v22 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v27 && (*v27 & 0x4000000000000000i64) == 0 )
          goto LABEL_16;
        goto LABEL_17;
      }
      v22 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v21 = 395i64;
      v24 = 0i64;
      v25 = 0i64;
      v8 = a2[1];
      v14 = *a2;
      v15 = v8;
      v16 = a2[2];
      get_id__modelZsave95mongerZcommon_u5569(&v26, &v14);
      if ( !*v33 )
      {
        rawNewString(&v12, v26 + 2);
        v24 = v12;
        v25 = v13;
        v12 = TM__THWBxVSaWN2Zh7OMooFH0w_2026;
        v13 = &TM__THWBxVSaWN2Zh7OMooFH0w_2025;
        appendString_29(&v24, &v12);
        v12 = v26;
        v13 = v27;
        appendString_29(&v24, &v12);
        v28 = v24;
        v29 = v25;
        v21 = 394i64;
        v22 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v27 && (*v27 & 0x4000000000000000i64) == 0 )
          goto LABEL_16;
        goto LABEL_17;
      }
    }
    if ( v27 && (*v27 & 0x4000000000000000i64) == 0 )
      goto LABEL_16;
    goto LABEL_17;
  }
  v28 = 4i64;
  v29 = &TM__THWBxVSaWN2Zh7OMooFH0w_2019;
  v21 = 394i64;
  v22 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v27 && (*v27 & 0x4000000000000000i64) == 0 )
LABEL_16:
    deallocShared(v27);
LABEL_17:
  popFrame_88();
  v9 = v29;
  *a1 = v28;
  a1[1] = v9;
  return a1;
}
