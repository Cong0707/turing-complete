// address: 0x1405dbba9-0x1405dbd75
// name: get_byte_buffer_size__presenterZutilitiesZhelper95functions_u2774
__int64 __fastcall get_byte_buffer_size__presenterZutilitiesZhelper95functions_u2774(__int64 a1, __int64 a2)
{
  _QWORD v3[6]; // [rsp+0h] [rbp-80h] BYREF
  __int64 v4; // [rsp+30h] [rbp-50h]
  const char *v5; // [rsp+38h] [rbp-48h]
  __int16 v6; // [rsp+40h] [rbp-40h]
  __int64 v7[71]; // [rsp+50h] [rbp-30h] BYREF
  __int64 v8; // [rsp+288h] [rbp+208h] BYREF
  __int64 *v9; // [rsp+290h] [rbp+210h]
  _BYTE *v10; // [rsp+298h] [rbp+218h]

  v3[5] = "get_byte_buffer_size";
  v5 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
  v4 = 0i64;
  v6 = 0;
  nimFrame_149(&v3[4]);
  v10 = (_BYTE *)nimErrorFlag_144();
  nimZeroMem_121(&v8, 8i64);
  nimZeroMem_121(v7, 560i64);
  v4 = 367i64;
  v5 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
  if ( a2 >= 0 && a2 < *(_QWORD *)(a1 + 152) )
  {
    qmemcpy(v7, (const void *)(560 * a2 + *(_QWORD *)(a1 + 160) + 8), 0x230ui64);
    v4 = 368i64;
    if ( v7[46] > 7 )
    {
      v4 = 370i64;
      v8 = v7[46];
    }
    else
    {
      v4 = 369i64;
      v9 = 0i64;
      v9 = (__int64 *)X5BX5D___modelZboardZmemory95manager_u501(
                        refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788,
                        LOBYTE(v7[0]));
      if ( !*v10 )
        v8 = *v9;
    }
  }
  else
  {
    raiseIndexError2(a2, *(_QWORD *)(a1 + 152) - 1i64);
  }
  popFrame_149();
  return v8;
}
