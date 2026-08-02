// address: 0x1406698b6-0x1406699b8
// name: component_panel__presenterZutilities_u16086
__int64 __fastcall component_panel__presenterZutilities_u16086(__int64 a1, __int64 a2, __int64 a3)
{
  char v4[8]; // [rsp+20h] [rbp-40h] BYREF
  const char *v5; // [rsp+28h] [rbp-38h]
  __int64 v6; // [rsp+30h] [rbp-30h]
  const char *v7; // [rsp+38h] [rbp-28h]
  __int16 v8; // [rsp+40h] [rbp-20h]
  char v9; // [rsp+57h] [rbp-9h]
  __int64 v10; // [rsp+58h] [rbp-8h]

  v5 = "component_panel";
  v7 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
  v6 = 0i64;
  v8 = 0;
  nimFrame_162(v4);
  v10 = 0i64;
  v6 = 1170i64;
  v7 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
  if ( a2 >= 0 && a2 < *(_QWORD *)(a1 + 152) )
  {
    v9 = *(_BYTE *)(*(_QWORD *)(a1 + 160) + 560 * a2 + 8);
    v6 = 1171i64;
    nimZeroMem_132(a3, 72i64);
    v10 = a2;
    *(_QWORD *)a3 = a2;
    *(_BYTE *)(a3 + 8) = v9;
  }
  else
  {
    raiseIndexError2(a2, *(_QWORD *)(a1 + 152) - 1i64);
  }
  return popFrame_162();
}
