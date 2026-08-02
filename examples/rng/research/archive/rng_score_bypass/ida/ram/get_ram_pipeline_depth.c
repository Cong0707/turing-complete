__int64 __fastcall get_ram_pipeline_depth__modelZmodel95types_u1723(__int64 a1)
{
  char v2[8]; // [rsp+20h] [rbp-50h] BYREF
  const char *v3; // [rsp+28h] [rbp-48h]
  __int64 v4; // [rsp+30h] [rbp-40h]
  const char *v5; // [rsp+38h] [rbp-38h]
  __int16 v6; // [rsp+40h] [rbp-30h]
  __int64 v7; // [rsp+58h] [rbp-18h]
  bool v8; // [rsp+67h] [rbp-9h]
  __int64 v9; // [rsp+68h] [rbp-8h]

  v3 = "get_ram_pipeline_depth";
  v5 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
  v4 = 0i64;
  v6 = 0;
  nimFrame_67(v2);
  v9 = 0i64;
  v4 = 868i64;
  v8 = 0;
  v7 = *(_QWORD *)(a1 + 168);
  v8 = v7 > 0;
  if ( v7 > 0 )
  {
    v4 = 869i64;
    if ( *(__int64 *)(a1 + 168) <= 0 )
    {
      raiseIndexError2(0i64, *(_QWORD *)(a1 + 168) - 1i64);
      goto LABEL_11;
    }
    v8 = *(_QWORD *)(*(_QWORD *)(a1 + 176) + 8i64) == 1i64;
  }
  if ( v8 )
  {
    v4 = 870i64;
    if ( *(__int64 *)(a1 + 168) > 1 )
    {
      if ( *(__int64 *)(*(_QWORD *)(a1 + 176) + 16i64) >= 0 )
        v9 = *(_QWORD *)(*(_QWORD *)(a1 + 176) + 16i64);
      else
        raiseRangeErrorNoArgs();
    }
    else
    {
      raiseIndexError2(1i64, *(_QWORD *)(a1 + 168) - 1i64);
    }
  }
LABEL_11:
  popFrame_67();
  return v9;
}
