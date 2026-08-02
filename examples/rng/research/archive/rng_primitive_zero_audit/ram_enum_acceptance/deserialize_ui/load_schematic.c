// address: 0x14027e073-0x14027e3f3
// name: load_schematic__modelZboardZschematics_u1650
__int64 __fastcall load_schematic__modelZboardZschematics_u1650(
        __int64 a1,
        __int16 a2,
        __int64 *a3,
        char a4,
        __int64 a5)
{
  __int64 v6; // rdx
  __int64 v8; // [rsp+0h] [rbp-80h] BYREF
  __int64 v9; // [rsp+30h] [rbp-50h] BYREF
  void *v10; // [rsp+38h] [rbp-48h]
  __int64 v11; // [rsp+40h] [rbp-40h]
  void *v12; // [rsp+48h] [rbp-38h]
  const char *v13; // [rsp+58h] [rbp-28h]
  __int64 v14; // [rsp+60h] [rbp-20h]
  const char *v15; // [rsp+68h] [rbp-18h]
  __int16 v16; // [rsp+70h] [rbp-10h]
  _QWORD v17[10]; // [rsp+80h] [rbp+0h] BYREF
  char v18[8]; // [rsp+D0h] [rbp+50h] BYREF
  __int64 v19[10]; // [rsp+D8h] [rbp+58h] BYREF
  int v20; // [rsp+128h] [rbp+A8h]
  __int64 v21[4]; // [rsp+130h] [rbp+B0h] BYREF
  char v22; // [rsp+150h] [rbp+D0h]
  __int64 v23; // [rsp+158h] [rbp+D8h]
  __int64 v24[4]; // [rsp+170h] [rbp+F0h] BYREF
  char v25; // [rsp+190h] [rbp+110h]
  _BYTE *v26; // [rsp+5A0h] [rbp+520h]
  __int64 v27; // [rsp+5A8h] [rbp+528h]
  __int16 v29; // [rsp+5D8h] [rbp+558h]

  v6 = a3[1];
  v11 = *a3;
  v12 = (void *)v6;
  v29 = a2;
  v13 = "load_schematic";
  v15 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
  v14 = 0i64;
  v16 = 0;
  nimFrame_75(&v8 + 10);
  v26 = (_BYTE *)nimErrorFlag_73();
  v27 = 0i64;
  nimZeroMem_55(v18, 1224i64);
  v14 = 121i64;
  v15 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
  v9 = v11;
  v10 = v12;
  parse_state__modelZsave95mongerZsave95monger_u73(&v9, 0i64, 0i64, v18);
  if ( *v26 )
    goto LABEL_6;
  v14 = 123i64;
  v15 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
  nimZeroMem_55(v17, 72i64);
  load_schematic_raw__modelZboardZschematics_u34(v29, v19, a4, a5, v17);
  if ( *v26 )
    goto LABEL_6;
  v14 = 173i64;
  v15 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
  eqsink___modelZsave95mongerZsave95monger_u2646(a1 + 152, v17);
  v15 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
  *(_QWORD *)(a1 + 72) = v19[9];
  v14 = 128i64;
  if ( *(_QWORD *)(a1 + 72) )
    goto LABEL_5;
  v9 = TM__DRGBjVoeyzCuYwSWCgAUCw_15;
  v10 = &TM__DRGBjVoeyzCuYwSWCgAUCw_14;
  failedAssertImpl__stdZassertions_u234(&v9);
  if ( *v26 )
  {
LABEL_6:
    eqdestroy___modelZboardZschematics_u1681(v18);
  }
  else
  {
LABEL_5:
    *(_BYTE *)(a1 + 64) = v22;
    v14 = 1699i64;
    v15 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v9 = v24[0];
    v10 = (void *)v24[1];
    eqsink___system_u2667(a1 + 112, &v9);
    eqwasMoved___system_u2658(v24);
    *(_DWORD *)(a1 + 80) = v20;
    v14 = 1699i64;
    v15 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v9 = v21[0];
    v10 = (void *)v21[1];
    eqsink___system_u2667(a1 + 88, &v9);
    eqwasMoved___system_u2658(v21);
    v15 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
    *(_BYTE *)(a1 + 104) = v25;
    v27 = v23;
    v14 = 121i64;
    eqdestroy___modelZboardZschematics_u1681(v18);
  }
  popFrame_75();
  return v27;
}
