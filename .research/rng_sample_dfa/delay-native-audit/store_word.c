__int64 __fastcall store_word__modelZsimulationZcode95gen_u2201(
        __int64 *a1,
        __int64 a2,
        unsigned __int16 a3,
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
  char v19[8]; // [rsp+90h] [rbp+10h] BYREF
  const char *v20; // [rsp+98h] [rbp+18h]
  __int64 v21; // [rsp+A0h] [rbp+20h]
  const char *v22; // [rsp+A8h] [rbp+28h]
  __int16 v23; // [rsp+B0h] [rbp+30h]
  __int64 v24; // [rsp+C0h] [rbp+40h] BYREF
  _QWORD *v25; // [rsp+C8h] [rbp+48h]
  __int64 (__fastcall *v26)(); // [rsp+D0h] [rbp+50h] BYREF
  __int64 v27; // [rsp+D8h] [rbp+58h]
  __int64 output_word_size__modelZboardZprototype95list_u4333; // [rsp+E8h] [rbp+68h]
  __int64 v29; // [rsp+F0h] [rbp+70h]
  _QWORD *v30; // [rsp+F8h] [rbp+78h]
  __int64 v31; // [rsp+100h] [rbp+80h] BYREF
  _QWORD *v32; // [rsp+108h] [rbp+88h]
  __int64 v33; // [rsp+110h] [rbp+90h] BYREF
  _QWORD *v34; // [rsp+118h] [rbp+98h]
  __int64 v35[70]; // [rsp+120h] [rbp+A0h] BYREF
  __int64 state_index__modelZsave95mongerZcommon_u5502; // [rsp+350h] [rbp+2D0h]
  char v37; // [rsp+35Fh] [rbp+2DFh]
  __int64 v38; // [rsp+360h] [rbp+2E0h]
  _BYTE *v39; // [rsp+368h] [rbp+2E8h]

  v5 = a1[1];
  v17 = *a1;
  v18 = v5;
  v6 = a4[1];
  v15 = *a4;
  v16 = (_QWORD *)v6;
  v20 = "store_word";
  v22 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v21 = 0i64;
  v23 = 0;
  nimFrame_88(v19);
  v39 = (_BYTE *)nimErrorFlag_86();
  v38 = a5;
  nimZeroMem_66(v35, 560i64);
  v33 = 0i64;
  v34 = 0i64;
  v31 = 0i64;
  v32 = 0i64;
  v29 = 0i64;
  v30 = 0i64;
  v21 = 239i64;
  v22 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  if ( *(_BYTE *)(v38 + 24) == 1 )
  {
    v21 = 394i64;
    v22 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    return popFrame_88();
  }
  v21 = 241i64;
  v22 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  if ( a2 >= 0 && a2 < v17 )
  {
    qmemcpy(v35, (const void *)(560 * a2 + v18 + 8), sizeof(v35));
    v21 = 243i64;
    v37 = 0;
    v14[0] = v35[11];
    v14[1] = v35[12];
    v14[2] = v35[13];
    v7 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 1);
    v11 = *(_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435;
    v12 = v7;
    v13 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 2);
    v37 = eqeq___modelZsimulationZcontroller_u106(v14, &v11);
    if ( v37 != 1
      || (v9 = TM__THWBxVSaWN2Zh7OMooFH0w_949,
          v10 = &TM__THWBxVSaWN2Zh7OMooFH0w_948,
          failedAssertImpl__stdZassertions_u234(&v9),
          !*v39) )
    {
      v21 = 245i64;
      output_word_size__modelZboardZprototype95list_u4333 = get_output_word_size__modelZboardZprototype95list_u4333(
                                                              v35[0],
                                                              a3,
                                                              v35[28]);
      if ( !*v39 )
      {
        v21 = 246i64;
        if ( output_word_size__modelZboardZprototype95list_u4333 <= 0 )
        {
          v21 = 394i64;
          v22 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v30 && (*v30 & 0x4000000000000000i64) == 0 )
            deallocShared(v30);
          if ( v32 && (*v32 & 0x4000000000000000i64) == 0 )
            deallocShared(v32);
          if ( v34 && (*v34 & 0x4000000000000000i64) == 0 )
            goto LABEL_33;
          return popFrame_88();
        }
        v21 = 248i64;
        v22 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        nimZeroMem_66(&v26, 16i64);
        v26 = add_line__modelZsimulationZcode95gen_u2131;
        v27 = v38;
        v24 = 0i64;
        v25 = 0i64;
        state_index__modelZsave95mongerZcommon_u5502 = 0i64;
        v11 = v35[11];
        v12 = v35[12];
        v13 = v35[13];
        state_index__modelZsave95mongerZcommon_u5502 = get_state_index__modelZsave95mongerZcommon_u5502(&v11, 0i64);
        if ( !*v39 )
        {
          dollar___systemZdollars_u14(&v33, state_index__modelZsave95mongerZcommon_u5502);
          if ( !*v39 )
          {
            dollar___modelZsave95mongerZcommon_u260(&v31, output_word_size__modelZboardZprototype95list_u4333);
            if ( !*v39 )
            {
              rawNewString(&v9, v31 + v33 + v15 + 33);
              v24 = v9;
              v25 = v10;
              v9 = TM__THWBxVSaWN2Zh7OMooFH0w_950;
              v10 = &TM__THWBxVSaWN2Zh7OMooFH0w_536;
              appendString_29(&v24, &v9);
              v9 = v33;
              v10 = v34;
              appendString_29(&v24, &v9);
              v9 = TM__THWBxVSaWN2Zh7OMooFH0w_952;
              v10 = &TM__THWBxVSaWN2Zh7OMooFH0w_951;
              appendString_29(&v24, &v9);
              v9 = v31;
              v10 = v32;
              appendString_29(&v24, &v9);
              v9 = TM__THWBxVSaWN2Zh7OMooFH0w_953;
              v10 = &TM__THWBxVSaWN2Zh7OMooFH0w_348;
              appendString_29(&v24, &v9);
              v9 = v15;
              v10 = v16;
              appendString_29(&v24, &v9);
              v9 = TM__THWBxVSaWN2Zh7OMooFH0w_954;
              v10 = &TM__THWBxVSaWN2Zh7OMooFH0w_307;
              appendString_29(&v24, &v9);
              v29 = v24;
              v30 = v25;
              v9 = v24;
              v10 = v25;
              if ( v27 )
                ((void (__fastcall *)(__int64 *, __int64))v26)(&v9, v27);
              else
                ((void (__fastcall *)(__int64 *))v26)(&v9);
            }
          }
        }
      }
    }
  }
  else
  {
    raiseIndexError2(a2, v17 - 1);
  }
  v21 = 394i64;
  v22 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v30 && (*v30 & 0x4000000000000000i64) == 0 )
    deallocShared(v30);
  if ( v32 && (*v32 & 0x4000000000000000i64) == 0 )
    deallocShared(v32);
  if ( v34 && (*v34 & 0x4000000000000000i64) == 0 )
LABEL_33:
    deallocShared(v34);
  return popFrame_88();
}
