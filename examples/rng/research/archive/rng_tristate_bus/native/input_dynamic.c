_QWORD *__fastcall input__modelZsimulationZcode95gen_u4258(
        _QWORD *a1,
        __int64 a2,
        __int64 a3,
        __int64 a4,
        unsigned __int8 a5,
        __int64 a6)
{
  __int64 v6; // rdx
  __int64 v8[3]; // [rsp+30h] [rbp-90h] BYREF
  unsigned __int8 v9; // [rsp+4Ch] [rbp-74h]
  char v10[8]; // [rsp+50h] [rbp-70h] BYREF
  const char *v11; // [rsp+58h] [rbp-68h]
  __int64 v12; // [rsp+60h] [rbp-60h]
  const char *v13; // [rsp+68h] [rbp-58h]
  __int16 v14; // [rsp+70h] [rbp-50h]
  __int64 v15; // [rsp+88h] [rbp-38h]
  _QWORD *(__fastcall *v16)(__int64 *, __int64, __int64, __int64, char, __int64); // [rsp+90h] [rbp-30h] BYREF
  __int64 v17; // [rsp+98h] [rbp-28h]
  __int64 v18; // [rsp+A0h] [rbp-20h] BYREF
  __int64 v19; // [rsp+A8h] [rbp-18h]
  __int64 v20; // [rsp+B0h] [rbp-10h]
  _BYTE *v21; // [rsp+B8h] [rbp-8h]

  v9 = a5;
  v11 = "input";
  v13 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v12 = 0i64;
  v14 = 0;
  nimFrame_88(v10);
  v21 = (_BYTE *)nimErrorFlag_86();
  v18 = 0i64;
  v19 = 0i64;
  v20 = a6;
  v13 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v12 = 439i64;
  nimZeroMem_66(&v16, 16i64);
  v16 = input__modelZsimulationZcode95gen_u4122;
  v17 = v20;
  v15 = bits__modelZsave95mongerZcommon_u192(a4);
  if ( !*v21 )
  {
    if ( v17 )
    {
      v16(&v18, a2, a3, v15, v9, v17);
    }
    else
    {
      ((void (__fastcall *)(__int64 *, __int64, __int64, __int64, _DWORD))v16)(v8, a2, a3, v15, v9);
      v18 = v8[0];
      v19 = v8[1];
    }
  }
  popFrame_88();
  v6 = v19;
  *a1 = v18;
  a1[1] = v6;
  return a1;
}
