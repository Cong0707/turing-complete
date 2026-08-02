__int64 __fastcall load_and_output__modelZsimulationZcode95gen_u3940(
        __int64 a1,
        __int64 a2,
        __int64 a3,
        __int64 *a4,
        __int64 a5)
{
  __int64 v5; // rdx
  __int64 v6; // rdx
  __int64 v7; // rdx
  __int64 v8; // rdx
  __int64 v10[2]; // [rsp+30h] [rbp-50h] BYREF
  __int64 v11; // [rsp+40h] [rbp-40h] BYREF
  _QWORD *v12; // [rsp+48h] [rbp-38h]
  __int64 v13; // [rsp+50h] [rbp-30h] BYREF
  __int64 v14; // [rsp+58h] [rbp-28h]
  __int64 v15; // [rsp+60h] [rbp-20h]
  __int64 v16; // [rsp+70h] [rbp-10h]
  __int64 v17; // [rsp+78h] [rbp-8h]
  __int64 v18; // [rsp+80h] [rbp+0h] BYREF
  _QWORD *v19; // [rsp+88h] [rbp+8h]
  __int64 (__fastcall *v20)(); // [rsp+90h] [rbp+10h] BYREF
  __int64 v21; // [rsp+98h] [rbp+18h]
  __int64 v22; // [rsp+A0h] [rbp+20h] BYREF
  _QWORD *v23; // [rsp+A8h] [rbp+28h]
  __int64 (__fastcall *v24)(); // [rsp+B0h] [rbp+30h] BYREF
  __int64 v25; // [rsp+B8h] [rbp+38h]
  __int64 v26; // [rsp+C0h] [rbp+40h] BYREF
  _QWORD *v27; // [rsp+C8h] [rbp+48h]
  __int64 v28; // [rsp+D0h] [rbp+50h]
  _QWORD *v29; // [rsp+D8h] [rbp+58h]
  __int64 v30; // [rsp+E0h] [rbp+60h] BYREF
  _QWORD *v31; // [rsp+E8h] [rbp+68h]
  __int64 v32; // [rsp+F0h] [rbp+70h]
  _QWORD *v33; // [rsp+F8h] [rbp+78h]
  __int64 v34; // [rsp+100h] [rbp+80h] BYREF
  _QWORD *v35; // [rsp+108h] [rbp+88h]
  __int64 v36; // [rsp+110h] [rbp+90h] BYREF
  _QWORD *v37; // [rsp+118h] [rbp+98h]
  __int64 v38; // [rsp+120h] [rbp+A0h] BYREF
  _QWORD *v39; // [rsp+128h] [rbp+A8h]
  __int64 v40; // [rsp+130h] [rbp+B0h] BYREF
  _QWORD *v41; // [rsp+138h] [rbp+B8h]
  __int64 v42; // [rsp+140h] [rbp+C0h] BYREF
  _QWORD *v43; // [rsp+148h] [rbp+C8h]
  __int64 v44; // [rsp+150h] [rbp+D0h] BYREF
  _QWORD *v45; // [rsp+158h] [rbp+D8h]
  char v46[8]; // [rsp+160h] [rbp+E0h] BYREF
  const char *v47; // [rsp+168h] [rbp+E8h]
  __int64 v48; // [rsp+170h] [rbp+F0h]
  const char *v49; // [rsp+178h] [rbp+F8h]
  __int16 v50; // [rsp+180h] [rbp+100h]
  void (__fastcall *v51)(__int64, __int64, __int64, __int64 *, __int64 *); // [rsp+190h] [rbp+110h] BYREF
  __int64 v52; // [rsp+198h] [rbp+118h]
  __int64 output_word_size__modelZboardZprototype95list_u4333; // [rsp+1A8h] [rbp+128h]
  __int64 v54; // [rsp+1B0h] [rbp+130h]
  _QWORD *v55; // [rsp+1B8h] [rbp+138h]
  __int64 v56; // [rsp+1C8h] [rbp+148h]
  __int64 v57; // [rsp+1D0h] [rbp+150h]
  __int64 state_index__modelZsave95mongerZcommon_u5502; // [rsp+1D8h] [rbp+158h]
  __int64 v59; // [rsp+1E0h] [rbp+160h]
  _BYTE *v60; // [rsp+1E8h] [rbp+168h]

  v5 = a4[1];
  v16 = *a4;
  v17 = v5;
  v47 = "load_and_output";
  v49 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v48 = 0i64;
  v50 = 0;
  nimFrame_88(v46);
  v60 = (_BYTE *)nimErrorFlag_86();
  v59 = a5;
  v54 = 0i64;
  v55 = 0i64;
  v48 = 378i64;
  output_word_size__modelZboardZprototype95list_u4333 = get_output_word_size__modelZboardZprototype95list_u4333(
                                                          *(_BYTE *)a1,
                                                          a3,
                                                          *(_QWORD *)(a1 + 224));
  if ( !*v60 )
  {
    v48 = 379i64;
    if ( output_word_size__modelZboardZprototype95list_u4333 <= 0 )
    {
      v48 = 394i64;
      v49 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v55 && (*v55 & 0x4000000000000000i64) == 0 )
        deallocShared(v55);
      return popFrame_88();
    }
    v48 = 382i64;
    v49 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( *(_BYTE *)(v59 + 24) == 1 )
    {
      v44 = 0i64;
      v45 = 0i64;
      v42 = 0i64;
      v43 = 0i64;
      v48 = 383i64;
      v40 = 0i64;
      v41 = 0i64;
      dollar___modelZsave95mongerZcommon_u260(&v44, output_word_size__modelZboardZprototype95list_u4333);
      if ( !*v60 )
      {
        state_index__modelZsave95mongerZcommon_u5502 = 0i64;
        v6 = *(_QWORD *)(a1 + 120);
        v13 = *(_QWORD *)(a1 + 112);
        v14 = v6;
        v15 = *(_QWORD *)(a1 + 128);
        state_index__modelZsave95mongerZcommon_u5502 = get_state_index__modelZsave95mongerZcommon_u5502(&v13, 0i64);
        if ( !*v60 )
        {
          dollar___systemZdollars_u14(&v42, state_index__modelZsave95mongerZcommon_u5502);
          if ( !*v60 )
          {
            rawNewString(&v11, v44 + v42 + 31);
            v40 = v11;
            v41 = v12;
            v11 = TM__THWBxVSaWN2Zh7OMooFH0w_918;
            v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_327;
            appendString_29(&v40, &v11);
            v11 = v44;
            v12 = v45;
            appendString_29(&v40, &v11);
            v11 = TM__THWBxVSaWN2Zh7OMooFH0w_919;
            v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_305;
            appendString_29(&v40, &v11);
            v11 = v42;
            v12 = v43;
            appendString_29(&v40, &v11);
            v11 = TM__THWBxVSaWN2Zh7OMooFH0w_920;
            v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_325;
            appendString_29(&v40, &v11);
            v54 = v40;
            v55 = v41;
            v48 = 394i64;
            v49 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v43 && (*v43 & 0x4000000000000000i64) == 0 )
              deallocShared(v43);
            if ( v45 && (*v45 & 0x4000000000000000i64) == 0 )
              deallocShared(v45);
LABEL_48:
            v48 = 389i64;
            v49 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
            nimZeroMem_66(&v51, 16i64);
            v51 = (void (__fastcall *)(__int64, __int64, __int64, __int64 *, __int64 *))store_output__modelZsimulationZcode95gen_u2221;
            v52 = v59;
            v11 = v54;
            v12 = v55;
            v10[0] = v16;
            v10[1] = v17;
            if ( v59 )
              ((void (__fastcall *)(__int64, __int64, __int64, __int64 *, __int64 *, __int64))v51)(
                a1,
                a2,
                a3,
                &v11,
                v10,
                v52);
            else
              v51(a1, a2, a3, &v11, v10);
          }
        }
      }
    }
    else
    {
      v38 = 0i64;
      v39 = 0i64;
      v36 = 0i64;
      v37 = 0i64;
      v34 = 0i64;
      v35 = 0i64;
      v32 = 0i64;
      v33 = 0i64;
      v30 = 0i64;
      v31 = 0i64;
      v28 = 0i64;
      v29 = 0i64;
      v48 = 385i64;
      v49 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v26 = 0i64;
      v27 = 0i64;
      dollar___systemZdollars_u14(&v38, a2);
      if ( !*v60 )
      {
        rawNewString(&v11, v38 + 6);
        v26 = v11;
        v27 = v12;
        v11 = TM__THWBxVSaWN2Zh7OMooFH0w_921;
        v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_706;
        appendString_29(&v26, &v11);
        v11 = v38;
        v12 = v39;
        appendString_29(&v26, &v11);
        v54 = v26;
        v55 = v27;
        v48 = 386i64;
        nimZeroMem_66(&v24, 16i64);
        v24 = add_line__modelZsimulationZcode95gen_u2131;
        v25 = v59;
        v22 = 0i64;
        v23 = 0i64;
        dollar___modelZsave95mongerZcommon_u260(&v36, output_word_size__modelZboardZprototype95list_u4333);
        if ( !*v60 )
        {
          v57 = 0i64;
          v7 = *(_QWORD *)(a1 + 96);
          v13 = *(_QWORD *)(a1 + 88);
          v14 = v7;
          v15 = *(_QWORD *)(a1 + 104);
          v57 = get_state_index__modelZsave95mongerZcommon_u5502(&v13, 0i64);
          if ( !*v60 )
          {
            dollar___systemZdollars_u14(&v34, v57);
            if ( !*v60 )
            {
              rawNewString(&v11, v36 + v54 + v34 + 38);
              v22 = v11;
              v23 = v12;
              v11 = TM__THWBxVSaWN2Zh7OMooFH0w_922;
              v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_708;
              appendString_29(&v22, &v11);
              v11 = v54;
              v12 = v55;
              appendString_29(&v22, &v11);
              v11 = TM__THWBxVSaWN2Zh7OMooFH0w_924;
              v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_923;
              appendString_29(&v22, &v11);
              v11 = v36;
              v12 = v37;
              appendString_29(&v22, &v11);
              v11 = TM__THWBxVSaWN2Zh7OMooFH0w_925;
              v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_305;
              appendString_29(&v22, &v11);
              v11 = v34;
              v12 = v35;
              appendString_29(&v22, &v11);
              v11 = TM__THWBxVSaWN2Zh7OMooFH0w_926;
              v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_325;
              appendString_29(&v22, &v11);
              v32 = v22;
              v33 = v23;
              v11 = v22;
              v12 = v23;
              if ( v25 )
                ((void (__fastcall *)(__int64 *, __int64))v24)(&v11, v25);
              else
                ((void (__fastcall *)(__int64 *))v24)(&v11);
              if ( !*v60 )
              {
                v48 = 387i64;
                nimZeroMem_66(&v20, 16i64);
                v20 = add_line__modelZsimulationZcode95gen_u2131;
                v21 = v59;
                v18 = 0i64;
                v19 = 0i64;
                v56 = 0i64;
                v8 = *(_QWORD *)(a1 + 120);
                v13 = *(_QWORD *)(a1 + 112);
                v14 = v8;
                v15 = *(_QWORD *)(a1 + 128);
                v56 = get_state_index__modelZsave95mongerZcommon_u5502(&v13, 0i64);
                if ( !*v60 )
                {
                  dollar___systemZdollars_u14(&v30, v56);
                  if ( !*v60 )
                  {
                    rawNewString(&v11, v30 + v54 + 45);
                    v18 = v11;
                    v19 = v12;
                    v11 = TM__THWBxVSaWN2Zh7OMooFH0w_928;
                    v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_536;
                    appendString_29(&v18, &v11);
                    v11 = v30;
                    v12 = v31;
                    appendString_29(&v18, &v11);
                    v11 = TM__THWBxVSaWN2Zh7OMooFH0w_929;
                    v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_41;
                    appendString_29(&v18, &v11);
                    v11 = v54;
                    v12 = v55;
                    appendString_29(&v18, &v11);
                    v11 = TM__THWBxVSaWN2Zh7OMooFH0w_931;
                    v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_930;
                    appendString_29(&v18, &v11);
                    v28 = v18;
                    v29 = v19;
                    v11 = v18;
                    v12 = v19;
                    if ( v21 )
                      ((void (__fastcall *)(__int64 *, __int64))v20)(&v11, v21);
                    else
                      ((void (__fastcall *)(__int64 *))v20)(&v11);
                    if ( !*v60 )
                    {
                      v48 = 394i64;
                      v49 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                      if ( v29 && (*v29 & 0x4000000000000000i64) == 0 )
                        deallocShared(v29);
                      if ( v31 && (*v31 & 0x4000000000000000i64) == 0 )
                        deallocShared(v31);
                      if ( v33 && (*v33 & 0x4000000000000000i64) == 0 )
                        deallocShared(v33);
                      if ( v35 && (*v35 & 0x4000000000000000i64) == 0 )
                        deallocShared(v35);
                      if ( v37 && (*v37 & 0x4000000000000000i64) == 0 )
                        deallocShared(v37);
                      if ( v39 && (*v39 & 0x4000000000000000i64) == 0 )
                        deallocShared(v39);
                      goto LABEL_48;
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  v48 = 394i64;
  v49 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v55 && (*v55 & 0x4000000000000000i64) == 0 )
    deallocShared(v55);
  return popFrame_88();
}
