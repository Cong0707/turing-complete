_QWORD *__fastcall amp___modelZsimulationZpreorder_u27374(_QWORD *a1, __int64 *a2, __int64 *a3)
{
  __int64 v3; // rax
  __int64 v4; // rdx
  __int64 v5; // rdx
  __int64 v6; // rdx
  __int64 v8; // [rsp+20h] [rbp-60h] BYREF
  __int64 v9; // [rsp+28h] [rbp-58h]
  __int64 v10; // [rsp+30h] [rbp-50h]
  __int64 v11; // [rsp+38h] [rbp-48h]
  __int64 v12; // [rsp+40h] [rbp-40h]
  __int64 v13; // [rsp+48h] [rbp-38h]
  __int64 v14; // [rsp+58h] [rbp-28h]
  __int64 v15; // [rsp+60h] [rbp-20h]
  __int64 v16; // [rsp+68h] [rbp-18h]
  __int64 v17; // [rsp+70h] [rbp-10h]
  __int64 v18; // [rsp+78h] [rbp-8h]
  _QWORD v19[2]; // [rsp+80h] [rbp+0h] BYREF
  __int64 v20; // [rsp+90h] [rbp+10h]
  const char *v21; // [rsp+98h] [rbp+18h]
  __int16 v22; // [rsp+A0h] [rbp+20h]
  __int64 v23; // [rsp+B8h] [rbp+38h]
  __int64 v24; // [rsp+C0h] [rbp+40h] BYREF
  __int64 v25; // [rsp+C8h] [rbp+48h]
  __int64 v26; // [rsp+D8h] [rbp+58h]
  __int64 v27; // [rsp+E0h] [rbp+60h]
  __int64 v28; // [rsp+E8h] [rbp+68h]
  __int64 v29; // [rsp+F0h] [rbp+70h]
  __int64 v30; // [rsp+F8h] [rbp+78h]
  __int64 v31; // [rsp+100h] [rbp+80h]
  __int64 v32; // [rsp+108h] [rbp+88h]
  __int64 v33; // [rsp+110h] [rbp+90h]
  __int64 v34; // [rsp+118h] [rbp+98h]
  __int64 v35; // [rsp+120h] [rbp+A0h]
  __int64 v36; // [rsp+128h] [rbp+A8h]

  v3 = *a2;
  v4 = a2[1];
  v12 = v3;
  v13 = v4;
  v5 = a3[1];
  v10 = *a3;
  v11 = v5;
  v19[1] = "&";
  v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  v20 = 0i64;
  v22 = 0;
  nimFrame_9(v19);
  v24 = 0i64;
  v25 = 0i64;
  v20 = 1490i64;
  v34 = v12;
  v33 = v10;
  v23 = v12 + v10;
  if ( __OFADD__(v12, v10) )
  {
LABEL_15:
    raiseOverflow();
    goto LABEL_31;
  }
  if ( v23 >= 0 )
  {
    newSeq__modelZsimulationZpreorder_u19081(&v24, v23);
    v32 = 0i64;
    v31 = 0i64;
    v20 = 1491i64;
    v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v30 = v12;
    v18 = v12 - 1;
    if ( __OFSUB__(v12, 1i64) )
      goto LABEL_15;
    v31 = v18;
    v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v36 = 0i64;
    v20 = 97i64;
    while ( v36 <= v31 )
    {
      v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      v32 = v36;
      v20 = 1492i64;
      if ( v36 < 0 || v32 >= v24 )
      {
        raiseIndexError2(v32, v24 - 1);
        goto LABEL_31;
      }
      if ( v32 < 0 || v32 >= v12 )
      {
        raiseIndexError2(v32, v12 - 1);
        goto LABEL_31;
      }
      *(_QWORD *)(v25 + 8 * v32 + 8) = *(_QWORD *)(v13 + 8 * v32 + 8);
      eqwasMoved___system_u8356(v13 + 8 * v32 + 8);
      v20 = 102i64;
      v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v17 = v36 + 1;
      if ( __OFADD__(1i64, v36) )
        goto LABEL_15;
      v36 = v17;
    }
    v29 = 0i64;
    v28 = 0i64;
    v20 = 1493i64;
    v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v27 = v10;
    v16 = v10 - 1;
    if ( __OFSUB__(v10, 1i64) )
      goto LABEL_15;
    v28 = v16;
    v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v35 = 0i64;
    v20 = 97i64;
    while ( v35 <= v28 )
    {
      v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      v29 = v35;
      v20 = 1494i64;
      v26 = v12;
      v15 = v35 + v12;
      if ( __OFADD__(v35, v12) )
        goto LABEL_15;
      if ( v15 < 0 || v24 <= v15 )
      {
        raiseIndexError2(v15, v24 - 1);
        goto LABEL_31;
      }
      if ( v29 < 0 || v29 >= v10 )
      {
        raiseIndexError2(v29, v10 - 1);
        goto LABEL_31;
      }
      *(_QWORD *)(v25 + 8 * v15 + 8) = *(_QWORD *)(v11 + 8 * v29 + 8);
      eqwasMoved___system_u8356(v11 + 8 * v29 + 8);
      v20 = 102i64;
      v21 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v14 = v35 + 1;
      if ( __OFADD__(1i64, v35) )
        goto LABEL_15;
      v35 = v14;
    }
    v20 = 982i64;
    v21 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    v8 = v10;
    v9 = v11;
    eqdestroy___modelZsave95mongerZcommon_u5612(&v8);
    v8 = v12;
    v9 = v13;
    eqdestroy___modelZsave95mongerZcommon_u5612(&v8);
  }
  else
  {
    raiseRangeErrorI(v23, 0i64, 0x7FFFFFFFFFFFFFFFi64);
  }
LABEL_31:
  popFrame_9();
  v6 = v25;
  *a1 = v24;
  a1[1] = v6;
  return a1;
}
