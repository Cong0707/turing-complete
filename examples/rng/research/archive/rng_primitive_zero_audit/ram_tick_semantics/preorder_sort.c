__int64 __fastcall sort__modelZsimulationZpreorder_u27209(__int64 a1, __int64 a2, unsigned __int8 a3)
{
  __int64 v4[2]; // [rsp+20h] [rbp-60h] BYREF
  char v5[8]; // [rsp+30h] [rbp-50h] BYREF
  const char *v6; // [rsp+38h] [rbp-48h]
  __int64 v7; // [rsp+40h] [rbp-40h]
  const char *v8; // [rsp+48h] [rbp-38h]
  __int16 v9; // [rsp+50h] [rbp-30h]
  __int64 v10[4]; // [rsp+60h] [rbp-20h] BYREF

  v6 = "sort";
  v8 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\algorithm.nim";
  v7 = 0i64;
  v9 = 0;
  nimFrame_13(v5);
  v10[3] = nimErrorFlag_12();
  nimZeroMem_8(v10, 16i64);
  v10[0] = (__int64)refptr_cmp__system_u8512;
  v10[1] = 0i64;
  v4[0] = (__int64)refptr_cmp__system_u8512;
  v4[1] = 0i64;
  sort__modelZsimulationZpreorder_u27262(a1, a2, v4, a3);
  return popFrame_13();
}
