// address: 0x1405dbd75-0x1405dbe88
// name: get_setting__presenterZutilitiesZhelper95functions_u2758
__int64 __fastcall get_setting__presenterZutilitiesZhelper95functions_u2758(__int64 a1, __int64 a2)
{
  __int64 v2; // rdx
  char v4[8]; // [rsp+20h] [rbp-50h] BYREF
  const char *v5; // [rsp+28h] [rbp-48h]
  __int64 v6; // [rsp+30h] [rbp-40h]
  const char *v7; // [rsp+38h] [rbp-38h]
  __int16 v8; // [rsp+40h] [rbp-30h]
  __int64 v9; // [rsp+50h] [rbp-20h]
  __int64 v10; // [rsp+58h] [rbp-18h]
  __int64 v11; // [rsp+60h] [rbp-10h]
  __int64 v12; // [rsp+68h] [rbp-8h]

  v5 = "get_setting";
  v7 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
  v6 = 0i64;
  v8 = 0;
  nimFrame_149(v4);
  v9 = 0i64;
  v10 = 0i64;
  v6 = 356i64;
  v2 = *(_QWORD *)(a2 + 176);
  v9 = *(_QWORD *)(a2 + 168);
  v10 = v2;
  v6 = 357i64;
  v11 = v9 - 1;
  if ( a1 > v9 - 1 )
  {
    v6 = 360i64;
    v12 = 0i64;
  }
  else
  {
    v6 = 358i64;
    if ( a1 >= 0 && a1 < v9 )
      v12 = *(_QWORD *)(v10 + 8 * a1 + 8);
    else
      raiseIndexError2(a1, v9 - 1);
  }
  popFrame_149();
  return v12;
}
