__int64 __fastcall pop__modelZsimulationZpreorder_u21011(__int64 *a1)
{
  char v2[8]; // [rsp+20h] [rbp-50h] BYREF
  const char *v3; // [rsp+28h] [rbp-48h]
  __int64 v4; // [rsp+30h] [rbp-40h]
  const char *v5; // [rsp+38h] [rbp-38h]
  __int16 v6; // [rsp+40h] [rbp-30h]
  __int64 v7; // [rsp+50h] [rbp-20h]
  __int64 v8; // [rsp+58h] [rbp-18h]
  __int64 v9; // [rsp+60h] [rbp-10h]
  __int64 v10; // [rsp+68h] [rbp-8h]

  v3 = "pop";
  v5 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  v4 = 0i64;
  v6 = 0;
  nimFrame_80(v2);
  v10 = 0i64;
  v4 = 1795i64;
  v5 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  v9 = *a1;
  v7 = v9 - 1;
  if ( __OFSUB__(v9, 1i64) )
  {
    raiseOverflow();
  }
  else
  {
    v8 = v7;
    v4 = 1797i64;
    if ( v7 >= 0 && v8 < *a1 )
    {
      v10 = *(_QWORD *)(a1[1] + 8 * v8 + 8);
      eqwasMoved___system_u8356(a1[1] + 8 * v8 + 8);
      v4 = 1798i64;
      if ( v8 >= 0 )
        shrink__modelZsave95mongerZcommon_u5639(a1, v8);
      else
        raiseRangeErrorI(v8, 0i64, 0x7FFFFFFFFFFFFFFFi64);
    }
    else
    {
      raiseIndexError2(v8, *a1 - 1);
    }
  }
  popFrame_80();
  return v10;
}
