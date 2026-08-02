__int64 __fastcall store_bit__modelZsimulationZcode95gen_u2179(
        __int64 *a1,
        __int64 a2,
        __int64 a3,
        __int64 *a4,
        __int64 a5)
{
  __int64 v5; // rbx
  __int64 v6; // rdx
  __int64 v7; // rdx
  __int64 v9; // [rsp+20h] [rbp-60h] BYREF
  _QWORD *v10; // [rsp+28h] [rbp-58h]
  __int64 v11; // [rsp+30h] [rbp-50h] BYREF
  __int64 v12; // [rsp+38h] [rbp-48h]
  __int64 v13; // [rsp+40h] [rbp-40h]
  __int64 v14[4]; // [rsp+50h] [rbp-30h] BYREF
  __int64 v15; // [rsp+70h] [rbp-10h]
  _QWORD *v16; // [rsp+78h] [rbp-8h]
  __int64 v17; // [rsp+80h] [rbp+0h]
  __int64 v18; // [rsp+88h] [rbp+8h]
  __int64 v19; // [rsp+90h] [rbp+10h] BYREF
  _QWORD *v20; // [rsp+98h] [rbp+18h]
  __int64 v21; // [rsp+A0h] [rbp+20h]
  _QWORD *v22; // [rsp+A8h] [rbp+28h]
  __int64 v23; // [rsp+B0h] [rbp+30h] BYREF
  _QWORD *v24; // [rsp+B8h] [rbp+38h]
  __int64 v25; // [rsp+C0h] [rbp+40h] BYREF
  _QWORD *v26; // [rsp+C8h] [rbp+48h]
  char v27[8]; // [rsp+D0h] [rbp+50h] BYREF
  const char *v28; // [rsp+D8h] [rbp+58h]
  __int64 v29; // [rsp+E0h] [rbp+60h]
  const char *v30; // [rsp+E8h] [rbp+68h]
  __int16 v31; // [rsp+F0h] [rbp+70h]
  __int64 v32; // [rsp+100h] [rbp+80h] BYREF
  _QWORD *v33; // [rsp+108h] [rbp+88h]
  __int64 (__fastcall *v34)(); // [rsp+110h] [rbp+90h] BYREF
  __int64 v35; // [rsp+118h] [rbp+98h]
  __int64 v36; // [rsp+120h] [rbp+A0h]
  _QWORD *v37; // [rsp+128h] [rbp+A8h]
  __int64 v38; // [rsp+130h] [rbp+B0h] BYREF
  _QWORD *v39; // [rsp+138h] [rbp+B8h]
  __int64 v40[70]; // [rsp+140h] [rbp+C0h] BYREF
  __int64 state_index__modelZsave95mongerZcommon_u5502; // [rsp+370h] [rbp+2F0h]
  char v42; // [rsp+37Fh] [rbp+2FFh]
  __int64 v43; // [rsp+380h] [rbp+300h]
  _BYTE *v44; // [rsp+388h] [rbp+308h]

  v5 = a1[1];
  v17 = *a1;
  v18 = v5;
  v6 = a4[1];
  v15 = *a4;
  v16 = (_QWORD *)v6;
  v28 = "store_bit";
  v30 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v29 = 0i64;
  v31 = 0;
  nimFrame_88(v27);
  v44 = (_BYTE *)nimErrorFlag_86();
  v43 = a5;
  nimZeroMem_66(v40, 560i64);
  v38 = 0i64;
  v39 = 0i64;
  v36 = 0i64;
  v37 = 0i64;
  v29 = 227i64;
  v30 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  if ( *(_BYTE *)(v43 + 24) == 1 )
  {
    v29 = 394i64;
    v30 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    return popFrame_88();
  }
  v29 = 229i64;
  v30 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  if ( a2 < 0 || a2 >= v17 )
  {
    raiseIndexError2(a2, v17 - 1);
    goto LABEL_22;
  }
  qmemcpy(v40, (const void *)(560 * a2 + v18 + 8), sizeof(v40));
  v29 = 231i64;
  v42 = 0;
  v14[0] = v40[11];
  v14[1] = v40[12];
  v14[2] = v40[13];
  v7 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 1);
  v11 = *(_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435;
  v12 = v7;
  v13 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 2);
  v42 = eqeq___modelZsimulationZcontroller_u106(v14, &v11);
  if ( v42 != 1 )
  {
LABEL_17:
    v29 = 234i64;
    v30 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    nimZeroMem_66(&v34, 16i64);
    v34 = add_line__modelZsimulationZcode95gen_u2131;
    v35 = v43;
    v32 = 0i64;
    v33 = 0i64;
    state_index__modelZsave95mongerZcommon_u5502 = 0i64;
    v11 = v40[11];
    v12 = v40[12];
    v13 = v40[13];
    state_index__modelZsave95mongerZcommon_u5502 = get_state_index__modelZsave95mongerZcommon_u5502(&v11, 0i64);
    if ( !*v44 )
    {
      dollar___systemZdollars_u14(&v38, state_index__modelZsave95mongerZcommon_u5502);
      if ( !*v44 )
      {
        rawNewString(&v9, v38 + v15 + 32);
        v32 = v9;
        v33 = v10;
        v9 = TM__THWBxVSaWN2Zh7OMooFH0w_939;
        v10 = &TM__THWBxVSaWN2Zh7OMooFH0w_536;
        appendString_29(&v32, &v9);
        v9 = v38;
        v10 = v39;
        appendString_29(&v32, &v9);
        v9 = TM__THWBxVSaWN2Zh7OMooFH0w_941;
        v10 = &TM__THWBxVSaWN2Zh7OMooFH0w_940;
        appendString_29(&v32, &v9);
        v9 = v15;
        v10 = v16;
        appendString_29(&v32, &v9);
        v9 = TM__THWBxVSaWN2Zh7OMooFH0w_942;
        v10 = &TM__THWBxVSaWN2Zh7OMooFH0w_325;
        appendString_29(&v32, &v9);
        v36 = v32;
        v37 = v33;
        v9 = v32;
        v10 = v33;
        if ( v35 )
          ((void (__fastcall *)(__int64 *, __int64))v34)(&v9, v35);
        else
          ((void (__fastcall *)(__int64 *))v34)(&v9);
      }
    }
    goto LABEL_22;
  }
  v25 = 0i64;
  v26 = 0i64;
  v23 = 0i64;
  v24 = 0i64;
  v21 = 0i64;
  v22 = 0i64;
  v19 = 0i64;
  v20 = 0i64;
  dollar___modelZsave95mongerZcommon_u132(&v25, LOBYTE(v40[0]));
  nimBoolToStr(&v23, LOBYTE(v40[4]));
  rawNewString(&v9, v25 + v23 + 98);
  v19 = v9;
  v20 = v10;
  v9 = TM__THWBxVSaWN2Zh7OMooFH0w_937;
  v10 = &TM__THWBxVSaWN2Zh7OMooFH0w_936;
  appendString_29(&v19, &v9);
  v9 = v25;
  v10 = v26;
  appendString_29(&v19, &v9);
  v9 = TM__THWBxVSaWN2Zh7OMooFH0w_938;
  v10 = &TM__THWBxVSaWN2Zh7OMooFH0w_58;
  appendString_29(&v19, &v9);
  v9 = v23;
  v10 = v24;
  appendString_29(&v19, &v9);
  v21 = v19;
  v22 = v20;
  v9 = v19;
  v10 = v20;
  failedAssertImpl__stdZassertions_u234(&v9);
  if ( !*v44 )
  {
    v29 = 394i64;
    v30 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v22 && (*v22 & 0x4000000000000000i64) == 0 )
      deallocShared(v22);
    if ( v24 && (*v24 & 0x4000000000000000i64) == 0 )
      deallocShared(v24);
    if ( v26 && (*v26 & 0x4000000000000000i64) == 0 )
      deallocShared(v26);
    goto LABEL_17;
  }
LABEL_22:
  v29 = 394i64;
  v30 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v37 && (*v37 & 0x4000000000000000i64) == 0 )
    deallocShared(v37);
  if ( v39 && (*v39 & 0x4000000000000000i64) == 0 )
    deallocShared(v39);
  return popFrame_88();
}
