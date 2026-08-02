__int64 __fastcall add_schematic__modelZnetworkingZnetworking_u162(__int64 a1, int a2, int a3, int a4)
{
  char *v4; // rax
  __int64 v6[2]; // [rsp+70h] [rbp-10h] BYREF
  __int64 v7[2]; // [rsp+80h] [rbp+0h] BYREF
  __int64 v8; // [rsp+90h] [rbp+10h] BYREF
  char *v9; // [rsp+98h] [rbp+18h]
  char v10[8]; // [rsp+A0h] [rbp+20h] BYREF
  const char *v11; // [rsp+A8h] [rbp+28h]
  __int64 v12; // [rsp+B0h] [rbp+30h]
  const char *v13; // [rsp+B8h] [rbp+38h]
  __int16 v14; // [rsp+C0h] [rbp+40h]
  __int64 v15; // [rsp+D0h] [rbp+50h] BYREF
  char *v16; // [rsp+D8h] [rbp+58h]
  __int64 v17; // [rsp+E0h] [rbp+60h] BYREF
  char *v18; // [rsp+E8h] [rbp+68h]
  _BYTE *v19; // [rsp+F8h] [rbp+78h]

  v11 = "add_schematic";
  v13 = "D:\\TuringComplete_Phu\\model\\networking\\networking.nim";
  v12 = 0i64;
  v14 = 0;
  nimFrame_90(v10);
  v19 = (_BYTE *)nimErrorFlag_88();
  v17 = 0i64;
  v18 = 0i64;
  v15 = 0i64;
  v16 = 0i64;
  v12 = 154i64;
  v13 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
  newSeq__stdZsysrand_u55(&v15, 0i64);
  v12 = 193i64;
  v13 = "D:\\TuringComplete_Phu\\model\\networking\\networking.nim";
  v8 = TM__aYI4vTGtkCKyC3NTAt9aNQw_73;
  v9 = (char *)&TM__aYI4vTGtkCKyC3NTAt9aNQw_72;
  v7[0] = TM__aYI4vTGtkCKyC3NTAt9aNQw_74;
  v7[1] = (__int64)&TM__aYI4vTGtkCKyC3NTAt9aNQw_72;
  v6[0] = v15;
  v6[1] = (__int64)v16;
  state_to_binary__modelZsave95mongerZsave95monger_u916(
    (unsigned int)&v17,
    a2,
    a3,
    a4,
    0i64,
    0i64,
    1,
    0i64,
    (__int64)&v8,
    0,
    (__int64)v7,
    0,
    (__int64)v6);
  if ( !*v19 )
  {
    v12 = 194i64;
    if ( v18 )
      v4 = v18 + 8;
    else
      v4 = 0i64;
    add_long_seq_u8__modelZsave95mongerZserialize_u357(a1, v4, v17);
  }
  v12 = 1772i64;
  v13 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\times.nim";
  v8 = v15;
  v9 = v16;
  eqdestroy___pureZtimes_u2668(&v8);
  v8 = v17;
  v9 = v18;
  eqdestroy___pureZtimes_u2668(&v8);
  return popFrame_90();
}
