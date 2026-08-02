__int64 save_level_data__modelZutilities_u5679()
{
  __int64 v0; // rdx
  __int64 v1; // rax
  _QWORD *v2; // rdx
  __int64 v3; // rdx
  __int64 *address; // rbx
  _QWORD *v5; // rdx
  __int64 v7; // [rsp+20h] [rbp-60h] BYREF
  void *v8; // [rsp+28h] [rbp-58h]
  __int64 v9; // [rsp+30h] [rbp-50h] BYREF
  void *v10; // [rsp+38h] [rbp-48h]
  __int64 v11; // [rsp+40h] [rbp-40h] BYREF
  _QWORD *v12; // [rsp+48h] [rbp-38h]
  __int64 v13; // [rsp+50h] [rbp-30h] BYREF
  __int64 v14; // [rsp+58h] [rbp-28h]
  __int64 v15; // [rsp+60h] [rbp-20h]
  char v16[8]; // [rsp+70h] [rbp-10h] BYREF
  __int64 v17; // [rsp+78h] [rbp-8h]
  _QWORD *v18; // [rsp+80h] [rbp+0h]
  __int64 v19; // [rsp+A0h] [rbp+20h]
  __int64 v20; // [rsp+A8h] [rbp+28h]
  __int64 v21; // [rsp+C0h] [rbp+40h] BYREF
  _QWORD *v22; // [rsp+C8h] [rbp+48h]
  __int64 v23; // [rsp+D0h] [rbp+50h]
  _QWORD *v24; // [rsp+D8h] [rbp+58h]
  __int64 v25; // [rsp+E0h] [rbp+60h] BYREF
  _QWORD *v26; // [rsp+E8h] [rbp+68h]
  __int64 v27; // [rsp+F0h] [rbp+70h] BYREF
  _QWORD *v28; // [rsp+F8h] [rbp+78h]
  __int64 v29; // [rsp+100h] [rbp+80h] BYREF
  _QWORD *v30; // [rsp+108h] [rbp+88h]
  __int64 v31; // [rsp+110h] [rbp+90h] BYREF
  _QWORD *v32; // [rsp+118h] [rbp+98h]
  __int64 v33; // [rsp+120h] [rbp+A0h] BYREF
  _QWORD *v34; // [rsp+128h] [rbp+A8h]
  __int64 v35; // [rsp+130h] [rbp+B0h] BYREF
  _QWORD *v36; // [rsp+138h] [rbp+B8h]
  __int64 v37; // [rsp+140h] [rbp+C0h]
  _QWORD *v38; // [rsp+148h] [rbp+C8h]
  __int64 v39; // [rsp+150h] [rbp+D0h] BYREF
  _QWORD *v40; // [rsp+158h] [rbp+D8h]
  __int64 v41; // [rsp+160h] [rbp+E0h] BYREF
  _QWORD *v42; // [rsp+168h] [rbp+E8h]
  __int64 v43; // [rsp+170h] [rbp+F0h]
  _QWORD *v44; // [rsp+178h] [rbp+F8h]
  __int64 v45; // [rsp+180h] [rbp+100h] BYREF
  _QWORD *v46; // [rsp+188h] [rbp+108h]
  __int64 v47; // [rsp+190h] [rbp+110h]
  _QWORD *v48; // [rsp+198h] [rbp+118h]
  __int64 v49; // [rsp+1A8h] [rbp+128h]
  __int64 v50; // [rsp+1B0h] [rbp+130h] BYREF
  _QWORD *v51; // [rsp+1B8h] [rbp+138h]
  char v52[8]; // [rsp+1C0h] [rbp+140h] BYREF
  const char *v53; // [rsp+1C8h] [rbp+148h]
  __int64 v54; // [rsp+1D0h] [rbp+150h]
  const char *v55; // [rsp+1D8h] [rbp+158h]
  __int16 v56; // [rsp+1E0h] [rbp+160h]
  __int64 v57; // [rsp+1F0h] [rbp+170h] BYREF
  _QWORD *v58; // [rsp+1F8h] [rbp+178h]
  __int64 v59; // [rsp+200h] [rbp+180h]
  _QWORD *v60; // [rsp+208h] [rbp+188h]
  __int64 v61; // [rsp+210h] [rbp+190h] BYREF
  _QWORD *v62; // [rsp+218h] [rbp+198h]
  __int64 ready; // [rsp+220h] [rbp+1A0h]
  __int64 v64; // [rsp+228h] [rbp+1A8h]
  __int64 v65; // [rsp+230h] [rbp+1B0h]
  __int64 v66; // [rsp+238h] [rbp+1B8h]
  __int64 v67; // [rsp+240h] [rbp+1C0h]
  _QWORD *v68; // [rsp+248h] [rbp+1C8h]
  char v69; // [rsp+257h] [rbp+1D7h]
  __int64 v70; // [rsp+258h] [rbp+1D8h]
  __int64 v71; // [rsp+260h] [rbp+1E0h]
  __int64 v72; // [rsp+268h] [rbp+1E8h]
  __int64 v73; // [rsp+270h] [rbp+1F0h]
  _BYTE *v74; // [rsp+278h] [rbp+1F8h]
  __int64 v75; // [rsp+280h] [rbp+200h]
  __int64 v76; // [rsp+288h] [rbp+208h]

  v53 = "save_level_data";
  v55 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  v54 = 0i64;
  v56 = 0;
  nimFrame_145(v52);
  v74 = (_BYTE *)nimErrorFlag_141();
  v59 = 0i64;
  v60 = 0i64;
  v54 = 327i64;
  v55 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  v61 = 0i64;
  v62 = &TM__8FyyixzftvDEeBWCL79bP9aA_2;
  v50 = 0i64;
  v51 = 0i64;
  nimZeroMem_118(v16, 72i64);
  v54 = 767i64;
  v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
  v0 = *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 1);
  v13 = *(_QWORD *)refptr_level_progress__modelZmodel95types_u825;
  v14 = v0;
  v15 = *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 2);
  v73 = len__modelZutilities_u5736(&v13);
  if ( !*v74 )
  {
    v72 = 0i64;
    v71 = 0i64;
    v54 = 768i64;
    v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
    v70 = *(_QWORD *)refptr_level_progress__modelZmodel95types_u825 - 1i64;
    v71 = v70;
    v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v76 = 0i64;
    v54 = 97i64;
    while ( v76 <= v71 )
    {
      v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
      v72 = v76;
      v54 = 769i64;
      if ( v76 < 0 || v72 >= *(_QWORD *)refptr_level_progress__modelZmodel95types_u825 )
      {
LABEL_14:
        raiseIndexError2(v72, *(_QWORD *)refptr_level_progress__modelZmodel95types_u825 - 1i64);
        break;
      }
      v69 = 0;
      v69 = isFilled__pureZcollectionsZtables_u31_18(*(_QWORD *)(*((_QWORD *)refptr_level_progress__modelZmodel95types_u825
                                                                 + 1)
                                                               + 96 * v72
                                                               + 8));
      if ( *v74 )
        break;
      if ( v69 == 1 )
      {
        v54 = 1699i64;
        v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v72 < 0 )
          goto LABEL_14;
        if ( v72 >= *(_QWORD *)refptr_level_progress__modelZmodel95types_u825 )
          goto LABEL_14;
        v1 = *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 1) + 96 * v72;
        v2 = *(_QWORD **)(v1 + 24);
        v11 = *(_QWORD *)(v1 + 16);
        v12 = v2;
        eqcopy___system_u2661(&v50, &v11);
        v54 = 419i64;
        v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
        if ( v72 < 0 || v72 >= *(_QWORD *)refptr_level_progress__modelZmodel95types_u825 )
          goto LABEL_14;
        eqcopy___modelZboardZschematics_u2147(
          v16,
          *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 1) + 96 * v72 + 16 + 16);
        v47 = 0i64;
        v48 = 0i64;
        v45 = 0i64;
        v46 = 0i64;
        v43 = 0i64;
        v44 = 0i64;
        v41 = 0i64;
        v42 = 0i64;
        v39 = 0i64;
        v40 = 0i64;
        v37 = 0i64;
        v38 = 0i64;
        v54 = 330i64;
        v55 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
        v11 = v50;
        v12 = v51;
        v9 = TM__8FyyixzftvDEeBWCL79bP9aA_45;
        v10 = &TM__8FyyixzftvDEeBWCL79bP9aA_44;
        if ( (unsigned __int8)eqStrings_19(&v11, &v9) != 1 )
        {
          v54 = 333i64;
          v35 = 0i64;
          v36 = 0i64;
          v11 = v50;
          v12 = v51;
          v9 = TM__8FyyixzftvDEeBWCL79bP9aA_48;
          v10 = &TM__8FyyixzftvDEeBWCL79bP9aA_47;
          v7 = TM__8FyyixzftvDEeBWCL79bP9aA_50;
          v8 = &TM__8FyyixzftvDEeBWCL79bP9aA_49;
          nsuReplaceStr(&v45, &v11, &v9, &v7);
          if ( !*v74 )
          {
            rawNewString(&v11, v45 + 2);
            v35 = v11;
            v36 = v12;
            appendChar_4(&v35, 34i64);
            v11 = v45;
            v12 = v46;
            appendString_73(&v35, &v11);
            appendChar_4(&v35, 34i64);
            v47 = v35;
            v48 = v36;
            v54 = 334i64;
            v33 = 0i64;
            v34 = 0i64;
            v11 = v17;
            v12 = v18;
            v9 = TM__8FyyixzftvDEeBWCL79bP9aA_52;
            v10 = &TM__8FyyixzftvDEeBWCL79bP9aA_47;
            v7 = TM__8FyyixzftvDEeBWCL79bP9aA_53;
            v8 = &TM__8FyyixzftvDEeBWCL79bP9aA_49;
            nsuReplaceStr(&v41, &v11, &v9, &v7);
            if ( !*v74 )
            {
              rawNewString(&v11, v41 + 2);
              v33 = v11;
              v34 = v12;
              appendChar_4(&v33, 34i64);
              v11 = v41;
              v12 = v42;
              appendString_73(&v33, &v11);
              appendChar_4(&v33, 34i64);
              v43 = v33;
              v44 = v34;
              v54 = 335i64;
              v31 = 0i64;
              v32 = 0i64;
              nimBoolToStr(&v39, (unsigned __int8)v16[0]);
              rawNewString(&v11, v39 + v47 + v43 + 3);
              v31 = v11;
              v32 = v12;
              v11 = v47;
              v12 = v48;
              appendString_73(&v31, &v11);
              appendChar_4(&v31, 44i64);
              v11 = v39;
              v12 = v40;
              appendString_73(&v31, &v11);
              appendChar_4(&v31, 44i64);
              v11 = v43;
              v12 = v44;
              appendString_73(&v31, &v11);
              appendChar_4(&v31, 44i64);
              v37 = v31;
              v38 = v32;
              prepareAdd(&v61, v31);
              v11 = v37;
              v12 = v38;
              appendString_73(&v61, &v11);
              v68 = 0i64;
              v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              v75 = 0i64;
              v67 = v19;
              v66 = v19;
              v54 = 251i64;
              while ( v75 < v66 )
              {
                v54 = 337i64;
                v55 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
                if ( v75 < 0 || v75 >= v19 )
                {
                  raiseIndexError2(v75, v19 - 1);
                  goto LABEL_66;
                }
                v68 = (_QWORD *)(v20 + 24 * v75 + 8);
                v29 = 0i64;
                v30 = 0i64;
                v27 = 0i64;
                v28 = 0i64;
                v25 = 0i64;
                v26 = 0i64;
                v23 = 0i64;
                v24 = 0i64;
                v54 = 338i64;
                if ( (__int64)*v68 >= 0 )
                {
                  v54 = 340i64;
                  v21 = 0i64;
                  v22 = 0i64;
                  dollar___systemZdollars_u14(&v29, *v68);
                  if ( !*v74 )
                  {
                    dollar___systemZdollars_u14(&v27, v68[1]);
                    if ( !*v74 )
                    {
                      dollar___systemZdollars_u14(&v25, v68[2]);
                      if ( !*v74 )
                      {
                        rawNewString(&v11, v27 + v29 + v25 + 3);
                        v21 = v11;
                        v22 = v12;
                        v11 = v29;
                        v12 = v30;
                        appendString_73(&v21, &v11);
                        appendChar_4(&v21, 38i64);
                        v11 = v27;
                        v12 = v28;
                        appendString_73(&v21, &v11);
                        appendChar_4(&v21, 38i64);
                        v11 = v25;
                        v12 = v26;
                        appendString_73(&v21, &v11);
                        appendChar_4(&v21, 124i64);
                        v23 = v21;
                        v24 = v22;
                        prepareAdd(&v61, v21);
                        v11 = v23;
                        v12 = v24;
                        appendString_73(&v61, &v11);
                      }
                    }
                  }
                  v54 = 394i64;
                  v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                  if ( v24 && (*v24 & 0x4000000000000000i64) == 0 )
                    deallocShared(v24);
                  if ( v26 && (*v26 & 0x4000000000000000i64) == 0 )
                    deallocShared(v26);
                  if ( v28 && (*v28 & 0x4000000000000000i64) == 0 )
                    deallocShared(v28);
                  if ( v30 && (*v30 & 0x4000000000000000i64) == 0 )
                    deallocShared(v30);
                  if ( *v74 )
                    goto LABEL_66;
                }
                else
                {
                  v54 = 339i64;
                  v55 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
                }
                v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                ++v75;
                v54 = 254i64;
                v65 = v19;
                if ( v19 != v66 )
                {
                  v11 = TM__8FyyixzftvDEeBWCL79bP9aA_54;
                  v12 = &TM__8FyyixzftvDEeBWCL79bP9aA_31;
                  failedAssertImpl__stdZassertions_u234(&v11);
                  if ( *v74 )
                    goto LABEL_66;
                }
              }
              v54 = 342i64;
              v55 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
              nimAddCharV1_20(&v61, 10i64);
            }
          }
LABEL_66:
          v54 = 394i64;
          v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v38 && (*v38 & 0x4000000000000000i64) == 0 )
            deallocShared(v38);
          if ( v40 && (*v40 & 0x4000000000000000i64) == 0 )
            deallocShared(v40);
          if ( v42 && (*v42 & 0x4000000000000000i64) == 0 )
            deallocShared(v42);
          if ( v44 && (*v44 & 0x4000000000000000i64) == 0 )
            deallocShared(v44);
          if ( v46 && (*v46 & 0x4000000000000000i64) == 0 )
            deallocShared(v46);
          if ( v48 && (*v48 & 0x4000000000000000i64) == 0 )
            deallocShared(v48);
          if ( *v74 )
            break;
        }
        else
        {
          v54 = 394i64;
          v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v38 && (*v38 & 0x4000000000000000i64) == 0 )
            deallocShared(v38);
          if ( v40 && (*v40 & 0x4000000000000000i64) == 0 )
            deallocShared(v40);
          if ( v42 && (*v42 & 0x4000000000000000i64) == 0 )
            deallocShared(v42);
          if ( v44 && (*v44 & 0x4000000000000000i64) == 0 )
            deallocShared(v44);
          if ( v46 && (*v46 & 0x4000000000000000i64) == 0 )
            deallocShared(v46);
          if ( v48 && (*v48 & 0x4000000000000000i64) == 0 )
            deallocShared(v48);
          v54 = 331i64;
          v55 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
        }
        v54 = 771i64;
        v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
        v64 = 0i64;
        v3 = *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 1);
        v13 = *(_QWORD *)refptr_level_progress__modelZmodel95types_u825;
        v14 = v3;
        v15 = *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 2);
        v64 = len__modelZutilities_u5736(&v13);
        if ( *v74 )
          break;
        if ( v64 != v73 )
        {
          v11 = TM__8FyyixzftvDEeBWCL79bP9aA_57;
          v12 = &TM__8FyyixzftvDEeBWCL79bP9aA_56;
          failedAssertImpl__stdZassertions_u234(&v11);
          if ( *v74 )
            break;
        }
      }
      v54 = 102i64;
      v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v49 = v76 + 1;
      if ( __OFADD__(1i64, v76) )
      {
        raiseOverflow();
        break;
      }
      v76 = v49;
    }
  }
  v54 = 419i64;
  v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
  eqdestroy___modelZboardZschematics_u2144(v16);
  v54 = 394i64;
  v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v51 && (*v51 & 0x4000000000000000i64) == 0 )
    deallocShared(v51);
  if ( !*v74 )
  {
    v54 = 345i64;
    v55 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
    v57 = 0i64;
    v58 = 0i64;
    address = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_base_path__modelZmodel95types_u77);
    rawNewString(&v11, *address + 11);
    v57 = v11;
    v58 = v12;
    v5 = (_QWORD *)address[1];
    v11 = *address;
    v12 = v5;
    appendString_73(&v57, &v11);
    v11 = TM__8FyyixzftvDEeBWCL79bP9aA_60;
    v12 = &TM__8FyyixzftvDEeBWCL79bP9aA_59;
    appendString_73(&v57, &v11);
    v59 = v57;
    v60 = v58;
    v11 = v57;
    v12 = v58;
    ready = open_when_ready__modelZsave95mongerZsave95monger_u23(&v11, 2i64);
    if ( !*v74 )
    {
      v54 = 347i64;
      v11 = v61;
      v12 = v62;
      write__stdZsyncio_u272(ready, &v11);
      if ( !*v74 )
      {
        v54 = 348i64;
        flushFile__stdZsyncio_u299(ready);
        if ( !*v74 )
        {
          v54 = 350i64;
          close__stdZsyncio_u290(ready);
        }
      }
    }
  }
  v54 = 394i64;
  v55 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v60 && (*v60 & 0x4000000000000000i64) == 0 )
    deallocShared(v60);
  if ( v62 && (*v62 & 0x4000000000000000i64) == 0 )
    deallocShared(v62);
  return popFrame_145();
}
