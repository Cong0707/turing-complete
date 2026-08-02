// address: 0x140671cb0-0x140671eb5
// name: set_byte_buffer_size__presenterZutilities_u40166
__int64 __fastcall set_byte_buffer_size__presenterZutilities_u40166(__int64 a1, __int64 a2, __int64 a3, __int64 a4)
{
  _QWORD v5[6]; // [rsp+0h] [rbp-80h] BYREF
  __int64 v6; // [rsp+30h] [rbp-50h]
  const char *v7; // [rsp+38h] [rbp-48h]
  __int16 v8; // [rsp+40h] [rbp-40h]
  __int64 v9[70]; // [rsp+50h] [rbp-30h] BYREF
  char v10; // [rsp+287h] [rbp+207h]
  __int64 v11; // [rsp+288h] [rbp+208h]

  v5[5] = "set_byte_buffer_size";
  v7 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
  v6 = 0i64;
  v8 = 0;
  nimFrame_162(&v5[4]);
  v11 = nimErrorFlag_157();
  nimZeroMem_132(v9, 560i64);
  v6 = 3442i64;
  if ( a3 >= 0 && a3 < *(_QWORD *)(a1 + 152) )
  {
    qmemcpy(v9, (const void *)(560 * a3 + *(_QWORD *)(a1 + 160) + 8), sizeof(v9));
    v6 = 3444i64;
    v10 = 0;
    v10 = eqeq___modelZboardZmemory95manager_u146(v9[39], a4);
    if ( v10 == 1 )
    {
      v6 = 3445i64;
      return popFrame_162();
    }
    v6 = 3447i64;
    if ( a3 >= 0 && a3 < *(_QWORD *)(a1 + 152) )
    {
      *(_QWORD *)(*(_QWORD *)(a1 + 160) + 560 * a3 + 376) = a4;
      v6 = 3448i64;
      upgrade__presenterZcontext_u2701(a2 + 4688, 48i64);
      return popFrame_162();
    }
  }
  raiseIndexError2(a3, *(_QWORD *)(a1 + 152) - 1i64);
  return popFrame_162();
}
