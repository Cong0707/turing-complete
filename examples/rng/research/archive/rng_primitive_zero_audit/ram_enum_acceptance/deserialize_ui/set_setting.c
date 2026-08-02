// address: 0x1405db3df-0x1405db531
// name: set_setting__presenterZutilitiesZhelper95functions_u2766
__int64 __fastcall set_setting__presenterZutilitiesZhelper95functions_u2766(
        __int64 a1,
        __int64 a2,
        __int64 a3,
        __int64 a4)
{
  char v5[8]; // [rsp+20h] [rbp-40h] BYREF
  const char *v6; // [rsp+28h] [rbp-38h]
  __int64 v7; // [rsp+30h] [rbp-30h]
  const char *v8; // [rsp+38h] [rbp-28h]
  __int16 v9; // [rsp+40h] [rbp-20h]
  __int64 v10; // [rsp+58h] [rbp-8h]

  v6 = "set_setting";
  v8 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
  v7 = 0i64;
  v9 = 0;
  nimFrame_149(v5);
  v7 = 363i64;
  v10 = *(_QWORD *)(a1 + 152) - 1i64;
  if ( a3 <= v10 )
  {
    v7 = 364i64;
    if ( a3 >= 0 && a3 < *(_QWORD *)(a1 + 152) )
    {
      if ( a2 >= 0 && a2 < *(_QWORD *)(*(_QWORD *)(a1 + 160) + 560 * a3 + 176) )
        *(_QWORD *)(*(_QWORD *)(*(_QWORD *)(a1 + 160) + 560 * a3 + 184) + 8 * a2 + 8) = a4;
      else
        raiseIndexError2(a2, *(_QWORD *)(*(_QWORD *)(a1 + 160) + 560 * a3 + 176) - 1i64);
    }
    else
    {
      raiseIndexError2(a3, *(_QWORD *)(a1 + 152) - 1i64);
    }
  }
  return popFrame_149();
}
