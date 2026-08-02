__int64 __fastcall buf_alloc__modelZboardZmemory95manager_u329(_QWORD *a1, __int64 a2, __int64 a3)
{
  bool v4; // dl
  __int64 v6; // [rsp+0h] [rbp-C0h] BYREF
  __int64 v7; // [rsp+28h] [rbp-98h]
  const char *v8; // [rsp+38h] [rbp-88h]
  __int64 v9; // [rsp+40h] [rbp-80h]
  const char *v10; // [rsp+48h] [rbp-78h]
  __int16 v11; // [rsp+50h] [rbp-70h]
  __int64 v12; // [rsp+68h] [rbp-58h]
  __int64 v13; // [rsp+70h] [rbp-50h]
  __int64 v14; // [rsp+78h] [rbp-48h]
  __int64 v15; // [rsp+80h] [rbp-40h] BYREF
  __int64 v16; // [rsp+88h] [rbp-38h]
  __int64 v17; // [rsp+90h] [rbp-30h]
  __int64 v18; // [rsp+98h] [rbp-28h]
  char v19; // [rsp+A7h] [rbp-19h]
  __int64 v20; // [rsp+A8h] [rbp-18h]
  char v21; // [rsp+B6h] [rbp-Ah]
  char v22; // [rsp+B7h] [rbp-9h]
  _BYTE *v23; // [rsp+B8h] [rbp-8h]

  v8 = "buf_alloc";
  v10 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
  v9 = 0i64;
  v11 = 0;
  nimFrame_72(&v6 + 6);
  v23 = (_BYTE *)nimErrorFlag_70();
  nimZeroMem_52(a3, 56i64);
  nimZeroMem_52(&v15, 8i64);
  v22 = 0;
  v21 = 0;
  v20 = 0i64;
  v9 = 198i64;
  v10 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
  v7 = bytes__modelZsave95mongerZcommon_u195(0i64);
  if ( !*v23 )
  {
    v19 = 0;
    v19 = eqeq___modelZboardZmemory95manager_u146(*a1, v7);
    if ( v19 != 1 )
    {
      v9 = 200i64;
      v4 = __OFADD__(4096i64, *a1);
      v14 = *a1 + 4096i64;
      if ( v4 )
        goto LABEL_7;
      v18 = v14;
      v9 = 181i64;
      v10 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
      v15 = eqdup___modelZsave95mongerZcommon_u160(*a1);
      *(_QWORD *)a3 = v15;
      v9 = 204i64;
      v10 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
      v22 = *((_BYTE *)a1 + 8);
      *(_BYTE *)(a3 + 8) = v22;
      v9 = 205i64;
      v17 = 0i64;
      v17 = c_alloc(v18);
      v13 = v17 + 2048;
      if ( __OFADD__(2048i64, v17)
        || (*(_QWORD *)(a3 + 16) = v13,
            v9 = 206i64,
            v16 = 0i64,
            v16 = c_alloc(v18),
            v12 = v16 + 2048,
            __OFADD__(2048i64, v16)) )
      {
LABEL_7:
        raiseOverflow();
      }
      else
      {
        *(_QWORD *)(a3 + 24) = v12;
        v9 = 207i64;
        *(_QWORD *)(a3 + 32) = c_alloc(4096i64);
        v9 = 208i64;
        v21 = *((_BYTE *)a1 + 9);
        *(_BYTE *)(a3 + 40) = v21;
        v9 = 209i64;
        v20 = a1[2];
        *(_QWORD *)(a3 + 48) = v20;
      }
    }
  }
  return popFrame_72();
}
