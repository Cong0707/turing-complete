_QWORD *__fastcall input__modelZsimulationZcode95gen_u4122(
        _QWORD *a1,
        __int64 a2,
        __int64 a3,
        __int64 a4,
        char a5,
        __int64 a6)
{
  _QWORD *v6; // rax
  __int64 v7; // rbx
  __int64 v8; // rbx
  __int64 v9; // rbx
  __int64 v10; // rbx
  __int64 v11; // rdx
  __int64 v12; // rdx
  __int64 v13; // rdx
  __int64 v14; // rdx
  void *v15; // rdx
  __int64 v17; // [rsp+20h] [rbp-60h] BYREF
  void *v18; // [rsp+28h] [rbp-58h]
  __int64 v19; // [rsp+30h] [rbp-50h] BYREF
  __int64 v20; // [rsp+38h] [rbp-48h]
  __int64 v21; // [rsp+40h] [rbp-40h]
  __int64 v22; // [rsp+50h] [rbp-30h] BYREF
  __int64 v23; // [rsp+58h] [rbp-28h]
  __int64 v24; // [rsp+60h] [rbp-20h]
  char v25; // [rsp+7Ch] [rbp-4h]
  __int64 v26; // [rsp+80h] [rbp+0h] BYREF
  void *v27; // [rsp+88h] [rbp+8h]
  __int64 v28; // [rsp+90h] [rbp+10h] BYREF
  _QWORD *v29; // [rsp+98h] [rbp+18h]
  __int64 v30; // [rsp+A0h] [rbp+20h] BYREF
  void *v31; // [rsp+A8h] [rbp+28h]
  __int64 v32; // [rsp+B0h] [rbp+30h] BYREF
  _QWORD *v33; // [rsp+B8h] [rbp+38h]
  __int64 v34; // [rsp+C0h] [rbp+40h] BYREF
  void *v35; // [rsp+C8h] [rbp+48h]
  __int64 v36; // [rsp+D0h] [rbp+50h] BYREF
  _QWORD *v37; // [rsp+D8h] [rbp+58h]
  __int64 v38; // [rsp+E0h] [rbp+60h] BYREF
  void *v39; // [rsp+E8h] [rbp+68h]
  __int64 v40; // [rsp+F0h] [rbp+70h] BYREF
  _QWORD *v41; // [rsp+F8h] [rbp+78h]
  __int64 v42; // [rsp+100h] [rbp+80h] BYREF
  _QWORD *v43; // [rsp+108h] [rbp+88h]
  __int64 v44; // [rsp+110h] [rbp+90h]
  _QWORD *v45; // [rsp+118h] [rbp+98h]
  __int64 v46; // [rsp+120h] [rbp+A0h] BYREF
  _QWORD *v47; // [rsp+128h] [rbp+A8h]
  __int64 v48; // [rsp+130h] [rbp+B0h] BYREF
  _QWORD *v49; // [rsp+138h] [rbp+B8h]
  __int64 v50; // [rsp+140h] [rbp+C0h] BYREF
  _QWORD *v51; // [rsp+148h] [rbp+C8h]
  __int64 v52; // [rsp+150h] [rbp+D0h]
  _QWORD *v53; // [rsp+158h] [rbp+D8h]
  __int64 v54; // [rsp+160h] [rbp+E0h] BYREF
  _QWORD *v55; // [rsp+168h] [rbp+E8h]
  __int64 v56; // [rsp+170h] [rbp+F0h] BYREF
  _QWORD *v57; // [rsp+178h] [rbp+F8h]
  __int64 v58; // [rsp+180h] [rbp+100h] BYREF
  void *v59; // [rsp+188h] [rbp+108h]
  __int64 v60; // [rsp+190h] [rbp+110h] BYREF
  _QWORD *v61; // [rsp+198h] [rbp+118h]
  __int64 v62; // [rsp+1A0h] [rbp+120h] BYREF
  void *v63; // [rsp+1A8h] [rbp+128h]
  __int64 v64; // [rsp+1B0h] [rbp+130h] BYREF
  _QWORD *v65; // [rsp+1B8h] [rbp+138h]
  __int64 v66; // [rsp+1C0h] [rbp+140h] BYREF
  void *v67; // [rsp+1C8h] [rbp+148h]
  __int64 v68; // [rsp+1D0h] [rbp+150h] BYREF
  _QWORD *v69; // [rsp+1D8h] [rbp+158h]
  char v70[8]; // [rsp+1E0h] [rbp+160h] BYREF
  const char *v71; // [rsp+1E8h] [rbp+168h]
  __int64 v72; // [rsp+1F0h] [rbp+170h]
  const char *v73; // [rsp+1F8h] [rbp+178h]
  __int16 v74; // [rsp+200h] [rbp+180h]
  __int64 v75; // [rsp+218h] [rbp+198h]
  __int64 v76; // [rsp+220h] [rbp+1A0h]
  __int64 v77; // [rsp+228h] [rbp+1A8h]
  __int64 v78; // [rsp+230h] [rbp+1B0h]
  __int64 v79; // [rsp+238h] [rbp+1B8h]
  __int64 v80; // [rsp+240h] [rbp+1C0h]
  __int64 v81; // [rsp+248h] [rbp+1C8h]
  __int64 v82; // [rsp+250h] [rbp+1D0h]
  __int64 v83; // [rsp+260h] [rbp+1E0h] BYREF
  __int64 v84; // [rsp+268h] [rbp+1E8h]
  __int64 v85; // [rsp+270h] [rbp+1F0h]
  __int64 v86; // [rsp+278h] [rbp+1F8h]
  __int64 v87; // [rsp+280h] [rbp+200h]
  __int64 v88; // [rsp+288h] [rbp+208h]
  __int64 v89; // [rsp+290h] [rbp+210h]
  __int64 v90; // [rsp+298h] [rbp+218h]
  __int64 v91; // [rsp+2A0h] [rbp+220h]
  __int64 v92; // [rsp+2A8h] [rbp+228h]
  __int64 v93; // [rsp+2B0h] [rbp+230h] BYREF
  void *v94; // [rsp+2B8h] [rbp+238h]
  char v95; // [rsp+2C7h] [rbp+247h]
  __int64 z_state_index__modelZsave95mongerZcommon_u5499; // [rsp+2C8h] [rbp+248h]
  char v97; // [rsp+2D7h] [rbp+257h]
  __int64 state_index__modelZsave95mongerZcommon_u5502; // [rsp+2D8h] [rbp+258h]
  char v99; // [rsp+2E6h] [rbp+266h]
  char v100; // [rsp+2E7h] [rbp+267h]
  __int64 v101; // [rsp+2E8h] [rbp+268h]
  _BYTE *v102; // [rsp+2F0h] [rbp+270h]
  char v103; // [rsp+2FFh] [rbp+27Fh]

  v25 = a5;
  v71 = "input";
  v73 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v72 = 0i64;
  v74 = 0;
  nimFrame_88(v70);
  v102 = (_BYTE *)nimErrorFlag_86();
  v93 = 0i64;
  v94 = 0i64;
  v101 = a6;
  nimZeroMem_66(&v83, 80i64);
  v72 = 406i64;
  v73 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  if ( a3 < 0 || a3 >= *(_QWORD *)(a2 + 48) )
  {
    raiseIndexError2(a3, *(_QWORD *)(a2 + 48) - 1i64);
    goto LABEL_98;
  }
  v6 = (_QWORD *)(*(_QWORD *)(a2 + 56) + 80 * a3);
  v7 = v6[2];
  v83 = v6[1];
  v84 = v7;
  v8 = v6[4];
  v85 = v6[3];
  v86 = v8;
  v9 = v6[6];
  v87 = v6[5];
  v88 = v9;
  v10 = v6[8];
  v89 = v6[7];
  v90 = v10;
  v11 = v6[10];
  v91 = v6[9];
  v92 = v11;
  v80 = v84;
  v81 = v85;
  v82 = v86;
  v72 = 409i64;
  v78 = bits__modelZsave95mongerZcommon_u192(1i64);
  if ( *v102 )
    goto LABEL_98;
  v79 = max__modelZsave95mongerZcommon_u225(v78, a4);
  if ( *v102 )
    goto LABEL_98;
  v72 = 411i64;
  v100 = 0;
  v22 = v80;
  v23 = v81;
  v24 = v82;
  v12 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 1);
  v19 = *(_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435;
  v20 = v12;
  v21 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 2);
  v100 = eqeq___modelZsimulationZcontroller_u106(&v22, &v19);
  if ( v100 == 1 )
  {
    v68 = 0i64;
    v69 = 0i64;
    v72 = 412i64;
    v66 = 0i64;
    v67 = 0i64;
    dollar___modelZsave95mongerZcommon_u260(&v68, v79);
    if ( !*v102 )
    {
      rawNewString(&v17, v68 + 7);
      v66 = v17;
      v67 = v18;
      v17 = TM__THWBxVSaWN2Zh7OMooFH0w_314;
      v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_313;
      appendString_29(&v66, &v17);
      v17 = v68;
      v18 = v69;
      appendString_29(&v66, &v17);
      v17 = TM__THWBxVSaWN2Zh7OMooFH0w_316;
      v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_315;
      appendString_29(&v66, &v17);
      v93 = v66;
      v94 = v67;
      v72 = 394i64;
      v73 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v69 && (*v69 & 0x4000000000000000i64) == 0 )
        deallocShared(v69);
      goto LABEL_98;
    }
    if ( v69 && (*v69 & 0x4000000000000000i64) == 0 )
      deallocShared(v69);
    if ( *v102 )
      goto LABEL_98;
  }
  v72 = 414i64;
  v73 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v76 = bits__modelZsave95mongerZcommon_u192(1i64);
  if ( *v102 )
    goto LABEL_98;
  v75 = min__modelZsave95mongerZcommon_u221(v90, v79);
  if ( *v102 )
    goto LABEL_98;
  v77 = max__modelZsave95mongerZcommon_u225(v76, v75);
  if ( *v102 )
    goto LABEL_98;
  v72 = 417i64;
  if ( *(_BYTE *)(v101 + 24) )
  {
    v48 = 0i64;
    v49 = 0i64;
    v46 = 0i64;
    v47 = 0i64;
    v44 = 0i64;
    v45 = 0i64;
    v72 = 425i64;
    v73 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v42 = 0i64;
    v43 = 0i64;
    dollar___modelZsave95mongerZcommon_u260(&v48, v77);
    if ( *v102 )
      goto LABEL_98;
    state_index__modelZsave95mongerZcommon_u5502 = 0i64;
    v19 = v80;
    v20 = v81;
    v21 = v82;
    state_index__modelZsave95mongerZcommon_u5502 = get_state_index__modelZsave95mongerZcommon_u5502(&v19, 0i64);
    if ( *v102 )
      goto LABEL_98;
    dollar___systemZdollars_u14(&v46, state_index__modelZsave95mongerZcommon_u5502);
    if ( *v102 )
      goto LABEL_98;
    rawNewString(&v17, v48 + v46 + 31);
    v42 = v17;
    v43 = v18;
    v17 = TM__THWBxVSaWN2Zh7OMooFH0w_328;
    v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_327;
    appendString_29(&v42, &v17);
    v17 = v48;
    v18 = v49;
    appendString_29(&v42, &v17);
    v17 = TM__THWBxVSaWN2Zh7OMooFH0w_329;
    v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_305;
    appendString_29(&v42, &v17);
    v17 = v46;
    v18 = v47;
    appendString_29(&v42, &v17);
    v17 = TM__THWBxVSaWN2Zh7OMooFH0w_330;
    v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_325;
    appendString_29(&v42, &v17);
    v44 = v42;
    v45 = v43;
    prepareAdd(&v93, v42);
    v17 = v44;
    v18 = v45;
    appendString_29(&v93, &v17);
    v72 = 394i64;
    v73 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v45 && (*v45 & 0x4000000000000000i64) == 0 )
      deallocShared(v45);
    if ( v47 && (*v47 & 0x4000000000000000i64) == 0 )
      deallocShared(v47);
    if ( v49 && (*v49 & 0x4000000000000000i64) == 0 )
      deallocShared(v49);
  }
  else
  {
    v72 = 418i64;
    v99 = 0;
    v13 = *(_QWORD *)(v101 + 40);
    v19 = *(_QWORD *)(v101 + 32);
    v20 = v13;
    v21 = *(_QWORD *)(v101 + 48);
    v22 = v80;
    v23 = v81;
    v24 = v82;
    v99 = contains__modelZsimulationZcode95gen_u3866(&v19, &v22);
    if ( *v102 )
      goto LABEL_98;
    if ( v99 )
    {
      v56 = 0i64;
      v57 = 0i64;
      v54 = 0i64;
      v55 = 0i64;
      v52 = 0i64;
      v53 = 0i64;
      v72 = 423i64;
      v73 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v50 = 0i64;
      v51 = 0i64;
      dollar___modelZsave95mongerZcommon_u260(&v56, v77);
      if ( *v102 )
        goto LABEL_98;
      v19 = v80;
      v20 = v81;
      v21 = v82;
      get_id__modelZsave95mongerZcommon_u5569(&v54, &v19);
      if ( *v102 )
        goto LABEL_98;
      rawNewString(&v17, v56 + v54 + 5);
      v50 = v17;
      v51 = v18;
      v17 = TM__THWBxVSaWN2Zh7OMooFH0w_322;
      v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_313;
      appendString_29(&v50, &v17);
      v17 = v56;
      v18 = v57;
      appendString_29(&v50, &v17);
      v17 = TM__THWBxVSaWN2Zh7OMooFH0w_324;
      v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_323;
      appendString_29(&v50, &v17);
      v17 = v54;
      v18 = v55;
      appendString_29(&v50, &v17);
      v17 = TM__THWBxVSaWN2Zh7OMooFH0w_326;
      v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_325;
      appendString_29(&v50, &v17);
      v52 = v50;
      v53 = v51;
      prepareAdd(&v93, v50);
      v17 = v52;
      v18 = v53;
      appendString_29(&v93, &v17);
      v72 = 394i64;
      v73 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v53 && (*v53 & 0x4000000000000000i64) == 0 )
        deallocShared(v53);
      if ( v55 && (*v55 & 0x4000000000000000i64) == 0 )
        deallocShared(v55);
      if ( v57 && (*v57 & 0x4000000000000000i64) == 0 )
        deallocShared(v57);
    }
    else
    {
      v64 = 0i64;
      v65 = 0i64;
      v72 = 419i64;
      if ( v25 != 1 )
        goto LABEL_33;
      v60 = 0i64;
      v61 = 0i64;
      v72 = 420i64;
      v58 = 0i64;
      v59 = 0i64;
      dollar___modelZsave95mongerZcommon_u260(&v60, v77);
      if ( !*v102 )
      {
        rawNewString(&v17, v60 + 5);
        v58 = v17;
        v59 = v18;
        v17 = TM__THWBxVSaWN2Zh7OMooFH0w_317;
        v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_313;
        appendString_29(&v58, &v17);
        v17 = v60;
        v18 = v61;
        appendString_29(&v58, &v17);
        v17 = TM__THWBxVSaWN2Zh7OMooFH0w_319;
        v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_318;
        appendString_29(&v58, &v17);
        v93 = v58;
        v94 = v59;
        v72 = 394i64;
        v73 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v61 && (*v61 & 0x4000000000000000i64) == 0 )
          deallocShared(v61);
        if ( v65 && (*v65 & 0x4000000000000000i64) == 0 )
          deallocShared(v65);
        goto LABEL_98;
      }
      if ( v61 && (*v61 & 0x4000000000000000i64) == 0 )
        deallocShared(v61);
      if ( !*v102 )
      {
LABEL_33:
        v72 = 421i64;
        v73 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        v62 = 0i64;
        v63 = 0i64;
        dollar___modelZsave95mongerZcommon_u260(&v64, v77);
        if ( !*v102 )
        {
          rawNewString(&v17, v64 + 5);
          v62 = v17;
          v63 = v18;
          v17 = TM__THWBxVSaWN2Zh7OMooFH0w_320;
          v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_313;
          appendString_29(&v62, &v17);
          v17 = v64;
          v18 = v65;
          appendString_29(&v62, &v17);
          v17 = TM__THWBxVSaWN2Zh7OMooFH0w_321;
          v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_318;
          appendString_29(&v62, &v17);
          v93 = v62;
          v94 = v63;
        }
      }
      v72 = 394i64;
      v73 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v65 && (*v65 & 0x4000000000000000i64) == 0 )
        deallocShared(v65);
      if ( *v102 )
        goto LABEL_98;
    }
  }
  v72 = 427i64;
  v73 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v103 = v25;
  if ( v25 == 1 )
    v103 = (_BYTE)v83 == 1;
  if ( v103 != 1 )
  {
LABEL_93:
    v72 = 435i64;
    v73 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v95 = 0;
    v95 = eqeq___modelZmodel95types_u853(v79, v90);
    if ( !v95 )
    {
      v28 = 0i64;
      v29 = 0i64;
      v72 = 436i64;
      v73 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v26 = 0i64;
      v27 = 0i64;
      dollar___modelZsave95mongerZcommon_u260(&v28, v79);
      if ( !*v102 )
      {
        rawNewString(&v17, v28 + v93 + 6);
        v26 = v17;
        v27 = v18;
        v17 = TM__THWBxVSaWN2Zh7OMooFH0w_347;
        v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_313;
        appendString_29(&v26, &v17);
        v17 = v28;
        v18 = v29;
        appendString_29(&v26, &v17);
        v17 = TM__THWBxVSaWN2Zh7OMooFH0w_349;
        v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_348;
        appendString_29(&v26, &v17);
        v17 = v93;
        v18 = v94;
        appendString_29(&v26, &v17);
        v17 = TM__THWBxVSaWN2Zh7OMooFH0w_350;
        v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_307;
        appendString_29(&v26, &v17);
        v72 = 1699i64;
        v73 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v17 = v26;
        v18 = v27;
        eqsink___system_u2667(&v93, &v17);
        v72 = 394i64;
        if ( v29 )
        {
          if ( (*v29 & 0x4000000000000000i64) == 0 )
            deallocShared(v29);
        }
      }
    }
    goto LABEL_98;
  }
  v72 = 428i64;
  if ( *(_BYTE *)(v101 + 24) )
  {
    v32 = 0i64;
    v33 = 0i64;
    v72 = 433i64;
    v73 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v30 = 0i64;
    v31 = 0i64;
    z_state_index__modelZsave95mongerZcommon_u5499 = 0i64;
    v19 = v80;
    v20 = v81;
    v21 = v82;
    z_state_index__modelZsave95mongerZcommon_u5499 = get_z_state_index__modelZsave95mongerZcommon_u5499(&v19);
    if ( *v102 )
      goto LABEL_98;
    dollar___systemZdollars_u14(&v32, z_state_index__modelZsave95mongerZcommon_u5499);
    if ( *v102 )
      goto LABEL_98;
    rawNewString(&v17, v32 + v93 + 54);
    v30 = v17;
    v31 = v18;
    v17 = TM__THWBxVSaWN2Zh7OMooFH0w_342;
    v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_341;
    appendString_29(&v30, &v17);
    v17 = v32;
    v18 = v33;
    appendString_29(&v30, &v17);
    v17 = TM__THWBxVSaWN2Zh7OMooFH0w_344;
    v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_343;
    appendString_29(&v30, &v17);
    v17 = v93;
    v18 = v94;
    appendString_29(&v30, &v17);
    v17 = TM__THWBxVSaWN2Zh7OMooFH0w_346;
    v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_345;
    appendString_29(&v30, &v17);
    v72 = 1699i64;
    v73 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v17 = v30;
    v18 = v31;
    eqsink___system_u2667(&v93, &v17);
    v72 = 394i64;
    if ( v33 && (*v33 & 0x4000000000000000i64) == 0 )
      deallocShared(v33);
    goto LABEL_93;
  }
  v40 = 0i64;
  v41 = 0i64;
  v72 = 429i64;
  v97 = 0;
  v14 = *(_QWORD *)(v101 + 64);
  v19 = *(_QWORD *)(v101 + 56);
  v20 = v14;
  v21 = *(_QWORD *)(v101 + 72);
  v22 = v80;
  v23 = v81;
  v24 = v82;
  v97 = contains__modelZsimulationZcode95gen_u3866(&v19, &v22);
  if ( !*v102 )
  {
    if ( v97 )
      goto LABEL_81;
    v36 = 0i64;
    v37 = 0i64;
    v72 = 430i64;
    v34 = 0i64;
    v35 = 0i64;
    dollar___modelZsave95mongerZcommon_u260(&v36, v77);
    if ( !*v102 )
    {
      rawNewString(&v17, v36 + 3);
      v34 = v17;
      v35 = v18;
      v17 = TM__THWBxVSaWN2Zh7OMooFH0w_332;
      v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_331;
      appendString_29(&v34, &v17);
      v17 = v36;
      v18 = v37;
      appendString_29(&v34, &v17);
      v17 = TM__THWBxVSaWN2Zh7OMooFH0w_334;
      v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_333;
      appendString_29(&v34, &v17);
      v93 = v34;
      v94 = v35;
      v72 = 394i64;
      v73 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v37 && (*v37 & 0x4000000000000000i64) == 0 )
        deallocShared(v37);
      if ( v41 && (*v41 & 0x4000000000000000i64) == 0 )
        deallocShared(v41);
      goto LABEL_98;
    }
    if ( v37 && (*v37 & 0x4000000000000000i64) == 0 )
      deallocShared(v37);
    if ( !*v102 )
    {
LABEL_81:
      v72 = 431i64;
      v73 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v38 = 0i64;
      v39 = 0i64;
      v19 = v80;
      v20 = v81;
      v21 = v82;
      get_id__modelZsave95mongerZcommon_u5569(&v40, &v19);
      if ( !*v102 )
      {
        rawNewString(&v17, v40 + v93 + 10);
        v38 = v17;
        v39 = v18;
        v17 = TM__THWBxVSaWN2Zh7OMooFH0w_336;
        v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_335;
        appendString_29(&v38, &v17);
        v17 = v40;
        v18 = v41;
        appendString_29(&v38, &v17);
        v17 = TM__THWBxVSaWN2Zh7OMooFH0w_338;
        v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_337;
        appendString_29(&v38, &v17);
        v17 = v93;
        v18 = v94;
        appendString_29(&v38, &v17);
        v17 = TM__THWBxVSaWN2Zh7OMooFH0w_340;
        v18 = &TM__THWBxVSaWN2Zh7OMooFH0w_339;
        appendString_29(&v38, &v17);
        v72 = 1699i64;
        v73 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v17 = v38;
        v18 = v39;
        eqsink___system_u2667(&v93, &v17);
      }
    }
  }
  v72 = 394i64;
  if ( v41 && (*v41 & 0x4000000000000000i64) == 0 )
    deallocShared(v41);
  if ( !*v102 )
    goto LABEL_93;
LABEL_98:
  popFrame_88();
  v15 = v94;
  *a1 = v93;
  a1[1] = v15;
  return a1;
}
