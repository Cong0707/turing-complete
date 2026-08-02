// address: 0x1404befe0-0x1404c1198
// name: serialize_server_request__modelZnetworkingZclient_u9
_QWORD *__fastcall serialize_server_request__modelZnetworkingZclient_u9(_QWORD *a1, __int64 a2)
{
  _BYTE *v2; // rdx
  __int64 v3; // rdx
  _BYTE *v4; // rdx
  __int64 v5; // rdx
  _BYTE *v6; // rdx
  _BYTE *v7; // rdx
  _BYTE *v8; // rdx
  __int64 v9; // rdx
  __int64 v10; // rdx
  __int64 v11; // rdx
  _BYTE *v12; // rdx
  __int64 v13; // rdx
  _BYTE *v14; // rdx
  _BYTE *v15; // rdx
  _BYTE *v16; // rdx
  _BYTE *v17; // rdx
  _BYTE *v18; // rdx
  __int64 v19; // rdx
  __int64 v20; // rdx
  _BYTE *v21; // rdx
  __int64 v23; // [rsp+20h] [rbp-60h] BYREF
  __int64 v24; // [rsp+28h] [rbp-58h]
  __int64 v25; // [rsp+30h] [rbp-50h] BYREF
  _BYTE *v26; // [rsp+38h] [rbp-48h]
  char v27[16]; // [rsp+40h] [rbp-40h] BYREF
  __int64 v28; // [rsp+50h] [rbp-30h]
  __int64 v29; // [rsp+70h] [rbp-10h]
  __int64 v30; // [rsp+78h] [rbp-8h]
  __int64 v31; // [rsp+80h] [rbp+0h]
  __int64 v32; // [rsp+88h] [rbp+8h]
  __int64 v33; // [rsp+90h] [rbp+10h]
  __int64 v34; // [rsp+98h] [rbp+18h]
  __int64 v35; // [rsp+A0h] [rbp+20h]
  __int64 v36; // [rsp+A8h] [rbp+28h]
  char v37[8]; // [rsp+B0h] [rbp+30h] BYREF
  const char *v38; // [rsp+B8h] [rbp+38h]
  __int64 v39; // [rsp+C0h] [rbp+40h]
  const char *v40; // [rsp+C8h] [rbp+48h]
  __int16 v41; // [rsp+D0h] [rbp+50h]
  __int64 v42; // [rsp+E8h] [rbp+68h]
  __int64 v43; // [rsp+F0h] [rbp+70h] BYREF
  _BYTE *v44; // [rsp+F8h] [rbp+78h]
  __int64 v45[2]; // [rsp+100h] [rbp+80h] BYREF
  __int64 v46[2]; // [rsp+110h] [rbp+90h] BYREF
  __int64 v47[2]; // [rsp+120h] [rbp+A0h] BYREF
  __int64 v48[2]; // [rsp+130h] [rbp+B0h] BYREF
  __int64 v49[2]; // [rsp+140h] [rbp+C0h] BYREF
  __int64 v50[2]; // [rsp+150h] [rbp+D0h] BYREF
  __int64 v51[2]; // [rsp+160h] [rbp+E0h] BYREF
  __int64 v52[2]; // [rsp+170h] [rbp+F0h] BYREF
  __int64 v53[2]; // [rsp+180h] [rbp+100h] BYREF
  __int64 v54[2]; // [rsp+190h] [rbp+110h] BYREF
  __int64 v55[2]; // [rsp+1A0h] [rbp+120h] BYREF
  __int64 v56[2]; // [rsp+1B0h] [rbp+130h] BYREF
  __int64 v57[2]; // [rsp+1C0h] [rbp+140h] BYREF
  __int64 v58[2]; // [rsp+1D0h] [rbp+150h] BYREF
  __int64 v59[2]; // [rsp+1E0h] [rbp+160h] BYREF
  __int64 v60[2]; // [rsp+1F0h] [rbp+170h] BYREF
  __int64 v61[2]; // [rsp+200h] [rbp+180h] BYREF
  __int64 v62[2]; // [rsp+210h] [rbp+190h] BYREF
  __int64 v63[2]; // [rsp+220h] [rbp+1A0h] BYREF
  __int64 v64[2]; // [rsp+230h] [rbp+1B0h] BYREF
  __int64 v65[2]; // [rsp+240h] [rbp+1C0h] BYREF
  __int64 v66[2]; // [rsp+250h] [rbp+1D0h] BYREF
  __int64 v67[2]; // [rsp+260h] [rbp+1E0h] BYREF
  __int64 v68[2]; // [rsp+270h] [rbp+1F0h] BYREF
  __int64 v69[2]; // [rsp+280h] [rbp+200h] BYREF
  __int64 v70[2]; // [rsp+290h] [rbp+210h] BYREF
  __int64 v71; // [rsp+2A0h] [rbp+220h]
  __int64 v72; // [rsp+2A8h] [rbp+228h]
  __int64 v73; // [rsp+2B0h] [rbp+230h]
  __int64 v74; // [rsp+2B8h] [rbp+238h]
  __int64 v75; // [rsp+2C0h] [rbp+240h]
  __int64 *v76; // [rsp+2C8h] [rbp+248h]
  __int64 v77; // [rsp+2D0h] [rbp+250h]
  __int64 v78; // [rsp+2D8h] [rbp+258h]
  __int64 v79; // [rsp+2E0h] [rbp+260h]
  __int64 v80; // [rsp+2E8h] [rbp+268h]
  __int64 *v81; // [rsp+2F0h] [rbp+270h]
  __int64 v82; // [rsp+2F8h] [rbp+278h]
  __int64 v83; // [rsp+300h] [rbp+280h]
  __int64 v84; // [rsp+308h] [rbp+288h]
  __int64 v85; // [rsp+310h] [rbp+290h]
  __int64 *v86; // [rsp+318h] [rbp+298h]
  __int64 v87; // [rsp+320h] [rbp+2A0h]
  __int64 v88; // [rsp+328h] [rbp+2A8h]
  __int64 v89; // [rsp+330h] [rbp+2B0h]
  __int64 v90; // [rsp+338h] [rbp+2B8h]
  __int64 v91; // [rsp+340h] [rbp+2C0h]
  __int64 *v92; // [rsp+348h] [rbp+2C8h]
  _QWORD *v93; // [rsp+350h] [rbp+2D0h]
  __int64 v94; // [rsp+358h] [rbp+2D8h]
  __int64 v95; // [rsp+360h] [rbp+2E0h]
  __int64 v96; // [rsp+368h] [rbp+2E8h]
  __int64 *v97; // [rsp+370h] [rbp+2F0h]
  __int64 v98; // [rsp+378h] [rbp+2F8h]
  _BYTE *v99; // [rsp+380h] [rbp+300h]
  __int64 v100; // [rsp+388h] [rbp+308h]
  __int64 v101; // [rsp+390h] [rbp+310h]
  __int64 v102; // [rsp+398h] [rbp+318h]
  __int64 v103; // [rsp+3A0h] [rbp+320h]
  __int64 v104; // [rsp+3A8h] [rbp+328h]

  v38 = "serialize_server_request";
  v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
  v39 = 0i64;
  v41 = 0;
  nimFrame_91(v37);
  v99 = (_BYTE *)nimErrorFlag_89();
  v39 = 11i64;
  v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
  newSeq__stdZsysrand_u55(&v25, 8i64);
  v43 = v25;
  v44 = v26;
  v39 = 12i64;
  add_u8__modelZsave95mongerZserialize_u343(&v43, *(unsigned __int8 *)(a2 + 24));
  if ( !*v99 )
  {
    v39 = 13i64;
    v2 = *(_BYTE **)(a2 + 16);
    v25 = *(_QWORD *)(a2 + 8);
    v26 = v2;
    add_string__modelZsave95mongerZserialize_u551(&v43, &v25);
    if ( !*v99 )
    {
      v39 = 15i64;
      switch ( *(_BYTE *)(a2 + 24) )
      {
        case 0:
        case 4:
          goto LABEL_158;
        case 1:
          v39 = 54i64;
          v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_90;
          v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_89;
          serialize_level_design_dir__modelZnetworkingZclient_u36(&v25, &v43);
          if ( *v99 )
            goto LABEL_177;
          v39 = 56i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 1i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v45, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_92;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_91;
            v23 = v45[0];
            v24 = v45[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          v82 = *(_QWORD *)(a2 + 32);
          add_u16__modelZsave95mongerZserialize_u305(&v43, (unsigned __int16)v82);
          if ( *v99 )
            goto LABEL_177;
          v35 = 0i64;
          v36 = 0i64;
          v81 = 0i64;
          v39 = 57i64;
          v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 1i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v46, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_93;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_91;
            v23 = v46[0];
            v24 = v46[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          v3 = *(_QWORD *)(a2 + 40);
          v35 = *(_QWORD *)(a2 + 32);
          v36 = v3;
          v40 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          v104 = 0i64;
          v80 = v35;
          v79 = v35;
          v39 = 251i64;
          while ( 2 )
          {
            if ( v104 < v79 )
            {
              v39 = 57i64;
              v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
              if ( v104 >= 0 && v104 < v35 )
              {
                v81 = (__int64 *)(v36 + 16 * v104 + 8);
                v39 = 58i64;
                v4 = *(_BYTE **)(v36 + 16 * v104 + 16);
                v25 = *v81;
                v26 = v4;
                add_string__modelZsave95mongerZserialize_u551(&v43, &v25);
                if ( *v99 )
                  goto LABEL_177;
                v40 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                ++v104;
                v39 = 254i64;
                v78 = v35;
                if ( v35 != v79 )
                {
                  v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_94;
                  v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_86;
                  failedAssertImpl__stdZassertions_u234(&v25);
                  if ( *v99 )
                    goto LABEL_177;
                }
                continue;
              }
              raiseIndexError2(v104, v35 - 1);
              goto LABEL_177;
            }
            break;
          }
          v39 = 60i64;
          v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 1i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v47, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_96;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_95;
            v23 = v47[0];
            v24 = v47[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          v77 = *(_QWORD *)(a2 + 48);
          add_u16__modelZsave95mongerZserialize_u305(&v43, (unsigned __int16)v77);
          if ( *v99 )
            goto LABEL_177;
          v33 = 0i64;
          v34 = 0i64;
          v76 = 0i64;
          v39 = 61i64;
          v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 1i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v48, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_97;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_95;
            v23 = v48[0];
            v24 = v48[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          v5 = *(_QWORD *)(a2 + 56);
          v33 = *(_QWORD *)(a2 + 48);
          v34 = v5;
          v40 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          v103 = 0i64;
          v75 = v33;
          v74 = v33;
          v39 = 251i64;
          while ( v103 < v74 )
          {
            v39 = 61i64;
            v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
            if ( v103 < 0 || v103 >= v33 )
            {
              raiseIndexError2(v103, v33 - 1);
              goto LABEL_177;
            }
            v76 = (__int64 *)(v34 + 16 * v103 + 8);
            v39 = 62i64;
            v6 = *(_BYTE **)(v34 + 16 * v103 + 16);
            v25 = *v76;
            v26 = v6;
            add_string__modelZsave95mongerZserialize_u551(&v43, &v25);
            if ( !*v99 )
            {
              v40 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v103;
              v39 = 254i64;
              v73 = v33;
              if ( v33 == v74 )
                continue;
              v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_98;
              v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_86;
              failedAssertImpl__stdZassertions_u234(&v25);
              if ( !*v99 )
                continue;
            }
            goto LABEL_177;
          }
          goto LABEL_158;
        case 2:
          v39 = 80i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 2i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v59, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_120;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_119;
            v23 = v59[0];
            v24 = v59[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          v87 = *(_QWORD *)(a2 + 32);
          add_u16__modelZsave95mongerZserialize_u305(&v43, (unsigned __int16)v87);
          if ( *v99 )
            goto LABEL_177;
          v31 = 0i64;
          v32 = 0i64;
          v86 = 0i64;
          v39 = 81i64;
          v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 2i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v60, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_121;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_119;
            v23 = v60[0];
            v24 = v60[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          v11 = *(_QWORD *)(a2 + 40);
          v31 = *(_QWORD *)(a2 + 32);
          v32 = v11;
          v40 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          v102 = 0i64;
          v85 = v31;
          v84 = v31;
          v39 = 251i64;
          while ( 2 )
          {
            if ( v102 >= v84 )
              goto LABEL_158;
            v39 = 81i64;
            v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
            if ( v102 >= 0 && v102 < v31 )
            {
              v86 = (__int64 *)(v32 + 16 * v102 + 8);
              v39 = 82i64;
              v12 = *(_BYTE **)(v32 + 16 * v102 + 16);
              v25 = *v86;
              v26 = v12;
              add_string__modelZsave95mongerZserialize_u551(&v43, &v25);
              if ( *v99 )
                goto LABEL_177;
              v40 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v102;
              v39 = 254i64;
              v83 = v31;
              if ( v31 != v84 )
              {
                v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_122;
                v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_86;
                failedAssertImpl__stdZassertions_u234(&v25);
                if ( *v99 )
                  goto LABEL_177;
              }
              continue;
            }
            break;
          }
          raiseIndexError2(v102, v31 - 1);
          goto LABEL_177;
        case 3:
          v39 = 84i64;
          v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 3i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v61, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_124;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_123;
            v23 = v61[0];
            v24 = v61[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          v98 = *(_QWORD *)(a2 + 32);
          add_u16__modelZsave95mongerZserialize_u305(&v43, (unsigned __int16)v98);
          if ( *v99 )
            goto LABEL_177;
          v29 = 0i64;
          v30 = 0i64;
          v97 = 0i64;
          v39 = 85i64;
          v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 3i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v62, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_125;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_123;
            v23 = v62[0];
            v24 = v62[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          v13 = *(_QWORD *)(a2 + 40);
          v29 = *(_QWORD *)(a2 + 32);
          v30 = v13;
          v40 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          v101 = 0i64;
          v96 = v29;
          v95 = v29;
          v39 = 251i64;
          break;
        case 5:
          v39 = 66i64;
          v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 5i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v49, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_100;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_99;
            v23 = v49[0];
            v24 = v49[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          add_u32__modelZsave95mongerZserialize_u267(&v43, *(unsigned int *)(a2 + 32));
          if ( *v99 )
            goto LABEL_177;
          goto LABEL_158;
        case 6:
        case 0xD:
        case 0xE:
        case 0xF:
        case 0x10:
        case 0x11:
        case 0x12:
        case 0x13:
        case 0x14:
        case 0x15:
        case 0x17:
          v39 = 105i64;
          v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
          v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_145;
          v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_144;
          failedAssertImpl__stdZassertions_u234(&v25);
          if ( !*v99 )
            goto LABEL_158;
          goto LABEL_177;
        case 7:
          v39 = 75i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 7i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v56, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_114;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_113;
            v23 = v56[0];
            v24 = v56[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          add_i8__modelZsave95mongerZserialize_u350(&v43, (unsigned int)*(char *)(a2 + 32));
          if ( *v99 )
            goto LABEL_177;
          v39 = 76i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 7i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v57, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_116;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_115;
            v23 = v57[0];
            v24 = v57[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          add_u32__modelZsave95mongerZserialize_u267(&v43, *(unsigned int *)(a2 + 36));
          if ( *v99 )
            goto LABEL_177;
          goto LABEL_158;
        case 8:
          v39 = 78i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 8i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v58, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_118;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_117;
            v23 = v58[0];
            v24 = v58[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          add_u32__modelZsave95mongerZserialize_u267(&v43, *(unsigned int *)(a2 + 32));
          if ( *v99 )
            goto LABEL_177;
          goto LABEL_158;
        case 9:
          v39 = 94i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 9i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v64, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_131;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_130;
            v23 = v64[0];
            v24 = v64[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          add_u16__modelZsave95mongerZserialize_u305(&v43, *(unsigned __int8 *)(a2 + 32));
          if ( *v99 )
            goto LABEL_177;
          v39 = 95i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 9i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v65, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_133;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_132;
            v23 = v65[0];
            v24 = v65[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          v15 = *(_BYTE **)(a2 + 48);
          v25 = *(_QWORD *)(a2 + 40);
          v26 = v15;
          add_string__modelZsave95mongerZserialize_u551(&v43, &v25);
          if ( *v99 )
            goto LABEL_177;
          goto LABEL_158;
        case 0xA:
          nimZeroMem_69(v27, 48i64);
          v39 = 97i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 10i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v66, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_135;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_134;
            v23 = v66[0];
            v24 = v66[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          v16 = *(_BYTE **)(a2 + 40);
          v25 = *(_QWORD *)(a2 + 32);
          v26 = v16;
          getOrDefault__modelZnetworkingZclient_u464(refptr_LANGUAGE_CODES__modelZtranslations_u2041, &v25, v27);
          if ( !*v99 )
          {
            add_u8__modelZsave95mongerZserialize_u343(&v43, (unsigned __int8)v28);
            if ( !*v99 )
              goto LABEL_156;
          }
          goto LABEL_177;
        case 0xB:
          nimZeroMem_69(v27, 48i64);
          v39 = 99i64;
          v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 11i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v67, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_137;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_136;
            v23 = v67[0];
            v24 = v67[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          v17 = *(_BYTE **)(a2 + 40);
          v25 = *(_QWORD *)(a2 + 32);
          v26 = v17;
          getOrDefault__modelZnetworkingZclient_u464(refptr_LANGUAGE_CODES__modelZtranslations_u2041, &v25, v27);
          if ( !*v99 )
          {
            add_u8__modelZsave95mongerZserialize_u343(&v43, (unsigned __int8)v28);
            if ( !*v99 )
              goto LABEL_156;
          }
          goto LABEL_177;
        case 0xC:
          nimZeroMem_69(v27, 48i64);
          v39 = 101i64;
          v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 12i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v68, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_139;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_138;
            v23 = v68[0];
            v24 = v68[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          v18 = *(_BYTE **)(a2 + 40);
          v25 = *(_QWORD *)(a2 + 32);
          v26 = v18;
          getOrDefault__modelZnetworkingZclient_u464(refptr_LANGUAGE_CODES__modelZtranslations_u2041, &v25, v27);
          if ( *v99 )
            goto LABEL_177;
          add_u8__modelZsave95mongerZserialize_u343(&v43, (unsigned __int8)v28);
          if ( *v99 )
            goto LABEL_177;
          v39 = 102i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 12i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v69, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_141;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_140;
            v23 = v69[0];
            v24 = v69[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          if ( *(_QWORD *)(a2 + 56) )
            v19 = *(_QWORD *)(a2 + 56) + 8i64;
          else
            v19 = 0i64;
          add_long_seq_u8__modelZsave95mongerZserialize_u357(&v43, v19, *(_QWORD *)(a2 + 48));
          if ( *v99 )
            goto LABEL_177;
          v39 = 103i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 12i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v70, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_143;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_142;
            v23 = v70[0];
            v24 = v70[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          if ( *(_QWORD *)(a2 + 72) )
            v20 = *(_QWORD *)(a2 + 72) + 8i64;
          else
            v20 = 0i64;
          add_long_seq_u8__modelZsave95mongerZserialize_u357(&v43, v20, *(_QWORD *)(a2 + 64));
          if ( *v99 )
            goto LABEL_177;
LABEL_156:
          v39 = 170i64;
          v40 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          eqdestroy___modelZtranslations_u1434(v27);
          goto LABEL_158;
        case 0x16:
          v39 = 68i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 22i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v50, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_102;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_101;
            v23 = v50[0];
            v24 = v50[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          add_u32__modelZsave95mongerZserialize_u267(&v43, *(unsigned int *)(a2 + 32));
          if ( *v99 )
            goto LABEL_177;
          v39 = 69i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 22i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v51, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_104;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_103;
            v23 = v51[0];
            v24 = v51[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          add_u8__modelZsave95mongerZserialize_u343(&v43, *(unsigned __int8 *)(a2 + 36));
          if ( *v99 )
            goto LABEL_177;
          v39 = 70i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 22i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v52, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_106;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_105;
            v23 = v52[0];
            v24 = v52[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          v7 = *(_BYTE **)(a2 + 64);
          v25 = *(_QWORD *)(a2 + 56);
          v26 = v7;
          add_string__modelZsave95mongerZserialize_u551(&v43, &v25);
          if ( *v99 )
            goto LABEL_177;
          v39 = 71i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 22i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v53, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_108;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_107;
            v23 = v53[0];
            v24 = v53[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          v8 = *(_BYTE **)(a2 + 80);
          v25 = *(_QWORD *)(a2 + 72);
          v26 = v8;
          add_string__modelZsave95mongerZserialize_u551(&v43, &v25);
          if ( *v99 )
            goto LABEL_177;
          v39 = 72i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 22i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v54, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_110;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_109;
            v23 = v54[0];
            v24 = v54[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          if ( *(_QWORD *)(a2 + 96) )
            v9 = *(_QWORD *)(a2 + 96) + 8i64;
          else
            v9 = 0i64;
          add_long_seq_u8__modelZsave95mongerZserialize_u357(&v43, v9, *(_QWORD *)(a2 + 88));
          if ( *v99 )
            goto LABEL_177;
          v39 = 73i64;
          if ( (*(_BYTE *)(a2 + 24) & 0x1F) != 22i64 )
          {
            dollar___modelZnetworkingZnetworking_u20(v55, *(unsigned __int8 *)(a2 + 24));
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_112;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_111;
            v23 = v55[0];
            v24 = v55[1];
            raiseFieldErrorStr(&v25, &v23);
            goto LABEL_177;
          }
          if ( *(_QWORD *)(a2 + 112) )
            v10 = *(_QWORD *)(a2 + 112) + 8i64;
          else
            v10 = 0i64;
          add_long_seq_u8__modelZsave95mongerZserialize_u357(&v43, v10, *(_QWORD *)(a2 + 104));
          if ( *v99 )
            goto LABEL_177;
          goto LABEL_158;
      }
      while ( v101 < v95 )
      {
        v39 = 85i64;
        v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
        if ( v101 < 0 || v101 >= v29 )
        {
          raiseIndexError2(v101, v29 - 1);
          goto LABEL_177;
        }
        v97 = (__int64 *)(v30 + 32 * v101 + 8);
        v39 = 86i64;
        v14 = *(_BYTE **)(v30 + 32 * v101 + 16);
        v25 = *v97;
        v26 = v14;
        add_string__modelZsave95mongerZserialize_u551(&v43, &v25);
        if ( !*v99 )
        {
          v39 = 87i64;
          v94 = v97[2];
          add_u16__modelZsave95mongerZserialize_u305(&v43, (unsigned __int16)v94);
          if ( !*v99 )
          {
            v93 = 0i64;
            v40 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            v92 = v97 + 2;
            v100 = 0i64;
            v39 = 250i64;
            v91 = v97[2];
            v90 = v91;
            v39 = 251i64;
            while ( v100 < v90 )
            {
              v39 = 88i64;
              v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
              if ( v100 < 0 || v100 >= *v92 )
              {
                raiseIndexError2(v100, *v92 - 1);
                goto LABEL_177;
              }
              v93 = (_QWORD *)(v92[1] + 16 * v100 + 8);
              v39 = 89i64;
              add_u64__modelZsave95mongerZserialize_u197(&v43, *v93);
              if ( !*v99 )
              {
                v39 = 90i64;
                add_u64__modelZsave95mongerZserialize_u197(&v43, v93[1]);
                if ( !*v99 )
                {
                  v40 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                  ++v100;
                  v39 = 254i64;
                  v89 = *v92;
                  if ( v89 == v90 )
                    continue;
                  v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_126;
                  v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_86;
                  failedAssertImpl__stdZassertions_u234(&v25);
                  if ( !*v99 )
                    continue;
                }
              }
              goto LABEL_177;
            }
            ++v101;
            v39 = 254i64;
            v88 = v29;
            if ( v29 == v95 )
              continue;
            v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_127;
            v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_86;
            failedAssertImpl__stdZassertions_u234(&v25);
            if ( !*v99 )
              continue;
          }
        }
        goto LABEL_177;
      }
      v39 = 92i64;
      v40 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
      if ( (*(_BYTE *)(a2 + 24) & 0x1F) == 3i64 )
      {
        add_validation_info__modelZnetworkingZnetworking_u207((__int64)&v43, (__int64 *)(a2 + 48));
        if ( !*v99 )
        {
LABEL_158:
          v39 = 107i64;
          v72 = v43;
          v42 = v43 - 8;
          if ( __OFSUB__(v43, 8i64) )
          {
            raiseOverflow();
          }
          else
          {
            v71 = v42;
            v39 = 109i64;
            if ( v43 > 0 )
            {
              v44[8] = v71;
              v39 = 110i64;
              if ( v43 > 1 )
              {
                v44[9] = BYTE1(v71);
                v39 = 111i64;
                if ( v43 > 2 )
                {
                  v44[10] = BYTE2(v71);
                  v39 = 112i64;
                  if ( v43 > 3 )
                  {
                    v44[11] = BYTE3(v71);
                    v39 = 113i64;
                    if ( v43 > 4 )
                    {
                      v44[12] = BYTE4(v71);
                      v39 = 114i64;
                      if ( v43 > 5 )
                      {
                        v44[13] = BYTE5(v71);
                        v39 = 115i64;
                        if ( v43 > 6 )
                        {
                          v44[14] = BYTE6(v71);
                          v39 = 116i64;
                          if ( v43 > 7 )
                            v44[15] = HIBYTE(v71);
                          else
                            raiseIndexError2(7i64, v43 - 1);
                        }
                        else
                        {
                          raiseIndexError2(6i64, v43 - 1);
                        }
                      }
                      else
                      {
                        raiseIndexError2(5i64, v43 - 1);
                      }
                    }
                    else
                    {
                      raiseIndexError2(4i64, v43 - 1);
                    }
                  }
                  else
                  {
                    raiseIndexError2(3i64, v43 - 1);
                  }
                }
                else
                {
                  raiseIndexError2(2i64, v43 - 1);
                }
              }
              else
              {
                raiseIndexError2(1i64, v43 - 1);
              }
            }
            else
            {
              raiseIndexError2(0i64, v43 - 1);
            }
          }
        }
      }
      else
      {
        dollar___modelZnetworkingZnetworking_u20(v63, *(unsigned __int8 *)(a2 + 24));
        v25 = TM__LJ9cWUOIKdJkv7vFbyFx9a6g_129;
        v26 = &TM__LJ9cWUOIKdJkv7vFbyFx9a6g_128;
        v23 = v63[0];
        v24 = v63[1];
        raiseFieldErrorStr(&v25, &v23);
      }
    }
  }
LABEL_177:
  popFrame_91();
  v21 = v44;
  *a1 = v43;
  a1[1] = v21;
  return a1;
}
