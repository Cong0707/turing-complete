// address: 0x1402a649c-0x1402a8226
// name: save__modelZsave_u2173
__int64 __fastcall save__modelZsave_u2173(__int64 a1)
{
  _QWORD *v1; // rdx
  _QWORD *v2; // rdx
  __int64 *address; // rax
  _QWORD *v4; // rdx
  int v5; // edx
  _QWORD *v6; // rax
  __int64 v8; // [rsp+30h] [rbp-50h] BYREF
  void *v9; // [rsp+38h] [rbp-48h]
  __int64 v10; // [rsp+40h] [rbp-40h] BYREF
  _QWORD *v11; // [rsp+48h] [rbp-38h]
  __int64 v12; // [rsp+58h] [rbp-28h]
  __int64 v13; // [rsp+60h] [rbp-20h] BYREF
  _QWORD *v14; // [rsp+68h] [rbp-18h]
  __int64 v15; // [rsp+70h] [rbp-10h] BYREF
  _QWORD *v16; // [rsp+78h] [rbp-8h]
  __int64 v17; // [rsp+80h] [rbp+0h] BYREF
  _QWORD *v18; // [rsp+88h] [rbp+8h]
  __int64 v19; // [rsp+90h] [rbp+10h] BYREF
  _QWORD *v20; // [rsp+98h] [rbp+18h]
  __int64 v21; // [rsp+A8h] [rbp+28h]
  __int64 v22; // [rsp+B0h] [rbp+30h] BYREF
  _QWORD *v23; // [rsp+B8h] [rbp+38h]
  __int64 v24; // [rsp+C0h] [rbp+40h] BYREF
  _QWORD *v25; // [rsp+C8h] [rbp+48h]
  __int64 v26; // [rsp+D0h] [rbp+50h] BYREF
  _QWORD *v27; // [rsp+D8h] [rbp+58h]
  __int64 v28; // [rsp+E0h] [rbp+60h] BYREF
  _QWORD *v29; // [rsp+E8h] [rbp+68h]
  __int64 v30; // [rsp+F0h] [rbp+70h] BYREF
  _QWORD *v31; // [rsp+F8h] [rbp+78h]
  __int64 v32; // [rsp+100h] [rbp+80h] BYREF
  _QWORD *v33; // [rsp+108h] [rbp+88h]
  __int64 v34; // [rsp+110h] [rbp+90h]
  _QWORD *v35; // [rsp+118h] [rbp+98h]
  __int64 v36; // [rsp+120h] [rbp+A0h]
  _QWORD *v37; // [rsp+128h] [rbp+A8h]
  __int64 v38; // [rsp+130h] [rbp+B0h]
  _QWORD *v39; // [rsp+138h] [rbp+B8h]
  __int64 v40; // [rsp+140h] [rbp+C0h]
  _QWORD *v41; // [rsp+148h] [rbp+C8h]
  __int64 v42; // [rsp+150h] [rbp+D0h]
  _QWORD *v43; // [rsp+158h] [rbp+D8h]
  __int64 v44; // [rsp+160h] [rbp+E0h]
  _QWORD *v45; // [rsp+168h] [rbp+E8h]
  __int64 v46; // [rsp+170h] [rbp+F0h]
  _QWORD *v47; // [rsp+178h] [rbp+F8h]
  __int64 v48; // [rsp+180h] [rbp+100h]
  _QWORD *v49; // [rsp+188h] [rbp+108h]
  __int64 v50; // [rsp+190h] [rbp+110h]
  _QWORD *v51; // [rsp+198h] [rbp+118h]
  __int64 v52; // [rsp+1A0h] [rbp+120h]
  _QWORD *v53; // [rsp+1A8h] [rbp+128h]
  __int64 v54; // [rsp+1B0h] [rbp+130h] BYREF
  _QWORD *v55; // [rsp+1B8h] [rbp+138h]
  __int64 v56; // [rsp+1C0h] [rbp+140h] BYREF
  _QWORD *v57; // [rsp+1C8h] [rbp+148h]
  __int64 v58; // [rsp+1D0h] [rbp+150h] BYREF
  _QWORD *v59; // [rsp+1D8h] [rbp+158h]
  __int64 v60; // [rsp+1E0h] [rbp+160h]
  _QWORD *v61; // [rsp+1E8h] [rbp+168h]
  __int64 v62; // [rsp+1F0h] [rbp+170h]
  _QWORD *v63; // [rsp+1F8h] [rbp+178h]
  __int64 v64; // [rsp+200h] [rbp+180h]
  _QWORD *v65; // [rsp+208h] [rbp+188h]
  char v66[8]; // [rsp+210h] [rbp+190h] BYREF
  const char *v67; // [rsp+218h] [rbp+198h]
  __int64 v68; // [rsp+220h] [rbp+1A0h]
  const char *v69; // [rsp+228h] [rbp+1A8h]
  __int16 v70; // [rsp+230h] [rbp+1B0h]
  __int64 v71; // [rsp+240h] [rbp+1C0h] BYREF
  _QWORD *v72; // [rsp+248h] [rbp+1C8h]
  __int64 v73; // [rsp+250h] [rbp+1D0h] BYREF
  _QWORD *v74; // [rsp+258h] [rbp+1D8h]
  __int64 v75; // [rsp+260h] [rbp+1E0h] BYREF
  _QWORD *v76; // [rsp+268h] [rbp+1E8h]
  __int64 v77; // [rsp+270h] [rbp+1F0h] BYREF
  _QWORD *v78; // [rsp+278h] [rbp+1F8h]
  __int64 v79; // [rsp+280h] [rbp+200h] BYREF
  _QWORD *v80; // [rsp+288h] [rbp+208h]
  __int64 v81; // [rsp+290h] [rbp+210h] BYREF
  _QWORD *v82; // [rsp+298h] [rbp+218h]
  __int64 v83; // [rsp+2A0h] [rbp+220h] BYREF
  _QWORD *v84; // [rsp+2A8h] [rbp+228h]
  __int64 v85; // [rsp+2B0h] [rbp+230h]
  _QWORD *v86; // [rsp+2B8h] [rbp+238h]
  __int64 v87; // [rsp+2C0h] [rbp+240h]
  _QWORD *v88; // [rsp+2C8h] [rbp+248h]
  __int64 v89; // [rsp+2D0h] [rbp+250h]
  _QWORD *v90; // [rsp+2D8h] [rbp+258h]
  __int64 v91; // [rsp+2E0h] [rbp+260h]
  _QWORD *v92; // [rsp+2E8h] [rbp+268h]
  __int64 v93; // [rsp+2F0h] [rbp+270h]
  _QWORD *v94; // [rsp+2F8h] [rbp+278h]
  __int64 v95; // [rsp+300h] [rbp+280h]
  _QWORD *v96; // [rsp+308h] [rbp+288h]
  __int64 v97; // [rsp+310h] [rbp+290h]
  _QWORD *v98; // [rsp+318h] [rbp+298h]
  __int64 v99; // [rsp+328h] [rbp+2A8h]
  __int64 v100; // [rsp+330h] [rbp+2B0h] BYREF
  _QWORD *v101; // [rsp+338h] [rbp+2B8h]
  __int64 v102; // [rsp+340h] [rbp+2C0h] BYREF
  _QWORD *v103; // [rsp+348h] [rbp+2C8h]
  __int64 v104; // [rsp+358h] [rbp+2D8h]
  __int64 v105; // [rsp+360h] [rbp+2E0h]
  __int64 command_setting__modelZsimulator95types_u123; // [rsp+368h] [rbp+2E8h]
  __int64 v107; // [rsp+370h] [rbp+2F0h]
  __int64 v108; // [rsp+378h] [rbp+2F8h]
  char v109; // [rsp+386h] [rbp+306h]
  char v110; // [rsp+387h] [rbp+307h]
  __int64 v111; // [rsp+388h] [rbp+308h]
  char v112; // [rsp+397h] [rbp+317h]
  _BYTE *v113; // [rsp+398h] [rbp+318h]
  __int64 v114; // [rsp+3A0h] [rbp+320h]
  bool v115; // [rsp+3AFh] [rbp+32Fh]

  v67 = "save";
  v69 = "D:\\TuringComplete_Phu\\model\\save.nim";
  v68 = 0i64;
  v70 = 0;
  nimFrame_77(v66);
  v113 = (_BYTE *)nimErrorFlag_75();
  v102 = 0i64;
  v103 = 0i64;
  v100 = 0i64;
  v101 = 0i64;
  v68 = 726i64;
  v112 = 0;
  v112 = immutable_loaded__modelZboardZboard_u17313();
  if ( *v113 )
    goto LABEL_153;
  if ( v112 == 1 )
  {
    v68 = 394i64;
    v69 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v101 && (*v101 & 0x4000000000000000i64) == 0 )
      deallocShared(v101);
    if ( v103 && (*v103 & 0x4000000000000000i64) == 0 )
      deallocShared(v103);
    return popFrame_77();
  }
  v68 = 729i64;
  v69 = "D:\\TuringComplete_Phu\\model\\save.nim";
  v111 = 0i64;
  v1 = (_QWORD *)refptr_loaded_level__modelZmodel95types_u830[1];
  v10 = *refptr_loaded_level__modelZmodel95types_u830;
  v11 = v1;
  v111 = X5BX5D___modelZboardZboard_u17368(refptr_campaign__modelZmodel95types_u817, &v10);
  if ( *v113 )
    goto LABEL_153;
  v110 = *(_BYTE *)(v111 + 64);
  v68 = 731i64;
  v2 = (_QWORD *)refptr_loaded_level__modelZmodel95types_u830[1];
  v10 = *refptr_loaded_level__modelZmodel95types_u830;
  v11 = v2;
  v8 = TM__8BatUf2mSnQIPowj6Jp47Q_455;
  v9 = &TM__8BatUf2mSnQIPowj6Jp47Q_454;
  if ( (unsigned __int8)eqStrings_10(&v10, &v8) == 1 )
  {
    v68 = 394i64;
    v69 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v101 && (*v101 & 0x4000000000000000i64) == 0 )
      deallocShared(v101);
    if ( v103 && (*v103 & 0x4000000000000000i64) == 0 )
      goto LABEL_158;
    return popFrame_77();
  }
  v68 = 735i64;
  v69 = "D:\\TuringComplete_Phu\\model\\save.nim";
  v115 = v110 == 4;
  if ( v110 == 4 )
    v115 = *(_BYTE *)(a1 + 32) == 1;
  if ( v115 )
  {
    v68 = 394i64;
    v69 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v101 && (*v101 & 0x4000000000000000i64) == 0 )
      deallocShared(v101);
    if ( v103 && (*v103 & 0x4000000000000000i64) == 0 )
      goto LABEL_158;
    return popFrame_77();
  }
  v68 = 739i64;
  v69 = "D:\\TuringComplete_Phu\\model\\save.nim";
  address = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_arch_path__modelZmodel95types_u79);
  v4 = (_QWORD *)address[1];
  v10 = *address;
  v11 = v4;
  as_sanitized_folder_name__modelZsanitized95path_u1302(&v102, &v10);
  if ( *v113 )
    goto LABEL_153;
  v68 = 741i64;
  v10 = v102;
  v11 = v103;
  to_absolute_path__modelZsanitized95path_u441(&v100, &v10);
  if ( *v113 )
    goto LABEL_153;
  v10 = v100;
  v11 = v101;
  noscreateDir(&v10);
  if ( *v113 )
    goto LABEL_153;
  v68 = 743i64;
  v99 = save_count__modelZsave_u11 + 1;
  if ( __OFADD__(1i64, save_count__modelZsave_u11) )
  {
    raiseOverflow();
    goto LABEL_153;
  }
  save_count__modelZsave_u11 = v99;
  v68 = 745i64;
  if ( *(_BYTE *)(a1 + 104) == 1 )
  {
    v68 = 746i64;
    *(_BYTE *)(a1 + 104) = 2;
  }
  v97 = 0i64;
  v98 = 0i64;
  v95 = 0i64;
  v96 = 0i64;
  v93 = 0i64;
  v94 = 0i64;
  v91 = 0i64;
  v92 = 0i64;
  v89 = 0i64;
  v90 = 0i64;
  v87 = 0i64;
  v88 = 0i64;
  v85 = 0i64;
  v86 = 0i64;
  v68 = 750i64;
  v83 = 0i64;
  v84 = 0i64;
  v10 = TM__8BatUf2mSnQIPowj6Jp47Q_458;
  v11 = &TM__8BatUf2mSnQIPowj6Jp47Q_457;
  as_circuit_path__modelZsanitized95path_u140(&v83, &v10);
  if ( *v113 )
  {
    v10 = v83;
    v11 = v84;
    eqdestroy___system_u281_29(&v10);
    goto LABEL_132;
  }
  v95 = v83;
  v96 = v84;
  v81 = 0i64;
  v82 = 0i64;
  v10 = v102;
  v11 = v103;
  v8 = v83;
  v9 = v84;
  slash___modelZsave_u2259(&v81, &v10, &v8);
  if ( *v113 )
  {
    v10 = v81;
    v11 = v82;
    eqdestroy___system_u281_29(&v10);
    goto LABEL_132;
  }
  v93 = v81;
  v94 = v82;
  v79 = 0i64;
  v80 = 0i64;
  v10 = v81;
  v11 = v82;
  to_absolute_path__modelZsave_u2267(&v79, &v10);
  if ( *v113 )
  {
    v10 = v79;
    v11 = v80;
    eqdestroy___system_u281_29(&v10);
    goto LABEL_132;
  }
  v97 = v79;
  v98 = v80;
  v68 = 751i64;
  v77 = 0i64;
  v78 = 0i64;
  v10 = TM__8BatUf2mSnQIPowj6Jp47Q_460;
  v11 = &TM__8BatUf2mSnQIPowj6Jp47Q_459;
  as_circuit_path__modelZsanitized95path_u140(&v77, &v10);
  if ( *v113 )
  {
    v10 = v77;
    v11 = v78;
    eqdestroy___system_u281_29(&v10);
    goto LABEL_132;
  }
  v89 = v77;
  v90 = v78;
  v75 = 0i64;
  v76 = 0i64;
  v10 = v102;
  v11 = v103;
  v8 = v77;
  v9 = v78;
  slash___modelZsave_u2259(&v75, &v10, &v8);
  if ( *v113 )
  {
    v10 = v75;
    v11 = v76;
    eqdestroy___system_u281_29(&v10);
    goto LABEL_132;
  }
  v87 = v75;
  v88 = v76;
  v73 = 0i64;
  v74 = 0i64;
  v10 = v75;
  v11 = v76;
  to_absolute_path__modelZsave_u2267(&v73, &v10);
  if ( *v113 )
  {
    v10 = v73;
    v11 = v74;
    eqdestroy___system_u281_29(&v10);
    goto LABEL_132;
  }
  v91 = v73;
  v92 = v74;
  v68 = 752i64;
  if ( save_count__modelZsave_u11 % 100 )
    goto LABEL_120;
  v64 = 0i64;
  v65 = 0i64;
  v62 = 0i64;
  v63 = 0i64;
  v60 = 0i64;
  v61 = 0i64;
  v114 = 3i64;
  v68 = 754i64;
  while ( v114 >= 0 )
  {
    v52 = 0i64;
    v53 = 0i64;
    v50 = 0i64;
    v51 = 0i64;
    v48 = 0i64;
    v49 = 0i64;
    v46 = 0i64;
    v47 = 0i64;
    v44 = 0i64;
    v45 = 0i64;
    v42 = 0i64;
    v43 = 0i64;
    v40 = 0i64;
    v41 = 0i64;
    v38 = 0i64;
    v39 = 0i64;
    v36 = 0i64;
    v37 = 0i64;
    v34 = 0i64;
    v35 = 0i64;
    v68 = 756i64;
    v32 = 0i64;
    v33 = 0i64;
    v30 = 0i64;
    v31 = 0i64;
    dollar___systemZdollars_u14(&v30, v114);
    if ( *v113 )
    {
      v10 = v30;
      v11 = v31;
      eqdestroy___system_u281_29(&v10);
      goto LABEL_71;
    }
    v50 = v30;
    v51 = v31;
    rawNewString(&v10, v30 + 20);
    v32 = v10;
    v33 = v11;
    v10 = TM__8BatUf2mSnQIPowj6Jp47Q_462;
    v11 = &TM__8BatUf2mSnQIPowj6Jp47Q_461;
    appendString_23(&v32, &v10);
    v10 = v50;
    v11 = v51;
    appendString_23(&v32, &v10);
    v10 = TM__8BatUf2mSnQIPowj6Jp47Q_464;
    v11 = &TM__8BatUf2mSnQIPowj6Jp47Q_463;
    appendString_23(&v32, &v10);
    v48 = v32;
    v49 = v33;
    v28 = 0i64;
    v29 = 0i64;
    v10 = v32;
    v11 = v33;
    as_circuit_path__modelZsanitized95path_u140(&v28, &v10);
    if ( *v113 )
    {
      v10 = v28;
      v11 = v29;
      eqdestroy___system_u281_29(&v10);
      goto LABEL_71;
    }
    v46 = v28;
    v47 = v29;
    v26 = 0i64;
    v27 = 0i64;
    v10 = v102;
    v11 = v103;
    v8 = v28;
    v9 = v29;
    slash___modelZsave_u2259(&v26, &v10, &v8);
    if ( *v113 )
    {
      v10 = v26;
      v11 = v27;
      eqdestroy___system_u281_29(&v10);
      goto LABEL_71;
    }
    v44 = v26;
    v45 = v27;
    v24 = 0i64;
    v25 = 0i64;
    v10 = v26;
    v11 = v27;
    to_absolute_path__modelZsave_u2267(&v24, &v10);
    if ( *v113 )
    {
      v10 = v24;
      v11 = v25;
      eqdestroy___system_u281_29(&v10);
      goto LABEL_71;
    }
    v52 = v24;
    v53 = v25;
    v68 = 757i64;
    v22 = 0i64;
    v23 = 0i64;
    v21 = v114 + 1;
    if ( __OFADD__(1i64, v114) )
    {
LABEL_57:
      raiseOverflow();
      goto LABEL_71;
    }
    v19 = 0i64;
    v20 = 0i64;
    dollar___systemZdollars_u14(&v19, v21);
    if ( *v113 )
    {
      v10 = v19;
      v11 = v20;
      eqdestroy___system_u281_29(&v10);
    }
    else
    {
      v40 = v19;
      v41 = v20;
      rawNewString(&v10, v19 + 20);
      v22 = v10;
      v23 = v11;
      v10 = TM__8BatUf2mSnQIPowj6Jp47Q_465;
      v11 = &TM__8BatUf2mSnQIPowj6Jp47Q_461;
      appendString_23(&v22, &v10);
      v10 = v40;
      v11 = v41;
      appendString_23(&v22, &v10);
      v10 = TM__8BatUf2mSnQIPowj6Jp47Q_467;
      v11 = &TM__8BatUf2mSnQIPowj6Jp47Q_463;
      appendString_23(&v22, &v10);
      v38 = v22;
      v39 = v23;
      v17 = 0i64;
      v18 = 0i64;
      v10 = v22;
      v11 = v23;
      as_circuit_path__modelZsanitized95path_u140(&v17, &v10);
      if ( *v113 )
      {
        v10 = v17;
        v11 = v18;
        eqdestroy___system_u281_29(&v10);
      }
      else
      {
        v36 = v17;
        v37 = v18;
        v15 = 0i64;
        v16 = 0i64;
        v10 = v102;
        v11 = v103;
        v8 = v17;
        v9 = v18;
        slash___modelZsave_u2259(&v15, &v10, &v8);
        if ( *v113 )
        {
          v10 = v15;
          v11 = v16;
          eqdestroy___system_u281_29(&v10);
        }
        else
        {
          v34 = v15;
          v35 = v16;
          v13 = 0i64;
          v14 = 0i64;
          v10 = v15;
          v11 = v16;
          to_absolute_path__modelZsave_u2267(&v13, &v10);
          if ( *v113 )
          {
            v10 = v13;
            v11 = v14;
            eqdestroy___system_u281_29(&v10);
          }
          else
          {
            v42 = v13;
            v43 = v14;
            v68 = 758i64;
            v109 = 0;
            v10 = v52;
            v11 = v53;
            v109 = nosfileExists(&v10);
            if ( *v113 )
              goto LABEL_71;
            if ( v109 == 1 )
            {
              v68 = 759i64;
              v10 = v52;
              v11 = v53;
              v8 = v42;
              v9 = v43;
              nosmoveFile(&v10, &v8);
              if ( *v113 )
                goto LABEL_71;
            }
            v68 = 760i64;
            v12 = v114 - 1;
            if ( __OFSUB__(v114, 1i64) )
              goto LABEL_57;
            v114 = v12;
          }
        }
      }
    }
LABEL_71:
    v68 = 394i64;
    v69 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v35 && (*v35 & 0x4000000000000000i64) == 0 )
      deallocShared(v35);
    if ( v37 && (*v37 & 0x4000000000000000i64) == 0 )
      deallocShared(v37);
    if ( v39 && (*v39 & 0x4000000000000000i64) == 0 )
      deallocShared(v39);
    if ( v41 && (*v41 & 0x4000000000000000i64) == 0 )
      deallocShared(v41);
    if ( v43 && (*v43 & 0x4000000000000000i64) == 0 )
      deallocShared(v43);
    if ( v45 && (*v45 & 0x4000000000000000i64) == 0 )
      deallocShared(v45);
    if ( v47 && (*v47 & 0x4000000000000000i64) == 0 )
      deallocShared(v47);
    if ( v49 && (*v49 & 0x4000000000000000i64) == 0 )
      deallocShared(v49);
    if ( v51 && (*v51 & 0x4000000000000000i64) == 0 )
      deallocShared(v51);
    if ( v53 && (*v53 & 0x4000000000000000i64) == 0 )
      deallocShared(v53);
    if ( *v113 )
      goto LABEL_110;
  }
  v69 = "D:\\TuringComplete_Phu\\model\\save.nim";
  v68 = 763i64;
  v58 = 0i64;
  v59 = 0i64;
  v10 = TM__8BatUf2mSnQIPowj6Jp47Q_470;
  v11 = &TM__8BatUf2mSnQIPowj6Jp47Q_469;
  as_circuit_path__modelZsanitized95path_u140(&v58, &v10);
  if ( *v113 )
  {
    v10 = v58;
    v11 = v59;
    eqdestroy___system_u281_29(&v10);
  }
  else
  {
    v64 = v58;
    v65 = v59;
    v56 = 0i64;
    v57 = 0i64;
    v10 = v102;
    v11 = v103;
    v8 = v58;
    v9 = v59;
    slash___modelZsave_u2259(&v56, &v10, &v8);
    if ( *v113 )
    {
      v10 = v56;
      v11 = v57;
      eqdestroy___system_u281_29(&v10);
    }
    else
    {
      v62 = v56;
      v63 = v57;
      v54 = 0i64;
      v55 = 0i64;
      v10 = v56;
      v11 = v57;
      to_absolute_path__modelZsave_u2267(&v54, &v10);
      if ( *v113 )
      {
        v10 = v54;
        v11 = v55;
        eqdestroy___system_u281_29(&v10);
      }
      else
      {
        v60 = v54;
        v61 = v55;
        v68 = 762i64;
        v10 = v91;
        v11 = v92;
        v8 = v54;
        v9 = v55;
        noscopyFile(&v10, &v8, 2i64, 0x4000i64);
      }
    }
  }
LABEL_110:
  v68 = 394i64;
  v69 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v61 && (*v61 & 0x4000000000000000i64) == 0 )
    deallocShared(v61);
  if ( v63 && (*v63 & 0x4000000000000000i64) == 0 )
    deallocShared(v63);
  if ( v65 && (*v65 & 0x4000000000000000i64) == 0 )
    deallocShared(v65);
  if ( !*v113 )
  {
LABEL_120:
    v68 = 766i64;
    v69 = "D:\\TuringComplete_Phu\\model\\save.nim";
    v108 = 0i64;
    v10 = v97;
    v11 = v98;
    v108 = open__stdZsyncio_u566(&v10, 1i64, -1i64);
    if ( !*v113 )
    {
      v107 = v108;
      v68 = 768i64;
      command_setting__modelZsimulator95types_u123 = 0i64;
      command_setting__modelZsimulator95types_u123 = get_command_setting__modelZsimulator95types_u123(2i64);
      if ( !*v113 )
      {
        v68 = 767i64;
        v71 = 0i64;
        v72 = 0i64;
        schematic_state_to_binary__modelZboardZschematics_u1724(
          (unsigned int)&v71,
          a1,
          *(_QWORD *)(a1 + 72),
          a1 + 152,
          command_setting__modelZsimulator95types_u123);
        if ( *v113 )
        {
          v10 = v71;
          v11 = v72;
          eqdestroy___pureZtimes_u2668(&v10);
        }
        else
        {
          v85 = v71;
          v86 = v72;
          v68 = 770i64;
          v105 = v71;
          if ( v71 >= 0 )
          {
            v104 = 0i64;
            if ( v86 )
              v5 = (_DWORD)v86 + 8;
            else
              v5 = 0;
            v104 = writeBytes__modelZboardZschematics_u26(v107, v5, v85, 0, v105);
            if ( !*v113 )
            {
              v68 = 771i64;
              close__stdZsyncio_u290(v107);
              if ( !*v113 )
              {
                v68 = 772i64;
                v10 = v97;
                v11 = v98;
                v8 = v91;
                v9 = v92;
                nosmoveFile(&v10, &v8);
              }
            }
          }
          else
          {
            raiseRangeErrorI(v105, 0i64, 0x7FFFFFFFFFFFFFFFi64);
          }
        }
      }
    }
  }
LABEL_132:
  v68 = 1772i64;
  v69 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\times.nim";
  v10 = v85;
  v11 = v86;
  eqdestroy___pureZtimes_u2668(&v10);
  v68 = 394i64;
  v69 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v88 && (*v88 & 0x4000000000000000i64) == 0 )
    deallocShared(v88);
  if ( v90 && (*v90 & 0x4000000000000000i64) == 0 )
    deallocShared(v90);
  if ( v92 && (*v92 & 0x4000000000000000i64) == 0 )
    deallocShared(v92);
  if ( v94 && (*v94 & 0x4000000000000000i64) == 0 )
    deallocShared(v94);
  if ( v96 && (*v96 & 0x4000000000000000i64) == 0 )
    deallocShared(v96);
  if ( v98 && (*v98 & 0x4000000000000000i64) == 0 )
    deallocShared(v98);
  if ( *v113 )
  {
    v6 = (_QWORD *)nimBorrowCurrentException_2();
    if ( (unsigned __int8)isObjDisplayCheck_4(*v6, 2i64, 1721001728i64) )
    {
      *v113 = 0;
      popCurrentException_5();
    }
  }
LABEL_153:
  if ( v101 && (*v101 & 0x4000000000000000i64) == 0 )
    deallocShared(v101);
  if ( v103 && (*v103 & 0x4000000000000000i64) == 0 )
LABEL_158:
    deallocShared(v103);
  return popFrame_77();
}
