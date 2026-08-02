__int64 __fastcall create_buffer_for_component__modelZboardZmemory95manager_u351(
        __int64 *a1,
        unsigned __int8 *a2,
        __int64 *a3,
        __int64 *a4,
        __int64 *a5,
        __int64 a6)
{
  __int64 v6; // rdx
  __int64 v7; // rdx
  __int64 v8; // rdx
  unsigned int v9; // r8d
  __int64 v10; // rdx
  __int64 v11; // rdx
  __int64 v12; // rdx
  __int64 v13; // rbx
  __int64 v14; // rbx
  __int64 v15; // rbx
  __int64 v16; // rbx
  __int64 v17; // rbx
  __int64 v18; // rbx
  __int64 v19; // rdx
  void *v20; // rdx
  __int64 v21; // rbx
  __int64 v22; // rbx
  __int64 v23; // rbx
  __int64 v25; // [rsp+20h] [rbp-60h] BYREF
  void *v26; // [rsp+28h] [rbp-58h]
  __int64 v27[4]; // [rsp+30h] [rbp-50h] BYREF
  __int64 v28; // [rsp+50h] [rbp-30h] BYREF
  void *v29; // [rsp+58h] [rbp-28h]
  __int64 v30; // [rsp+60h] [rbp-20h] BYREF
  __int64 v31; // [rsp+68h] [rbp-18h]
  __int64 v32; // [rsp+70h] [rbp-10h]
  __int64 v33; // [rsp+80h] [rbp+0h]
  void *v34; // [rsp+88h] [rbp+8h]
  __int64 v35; // [rsp+90h] [rbp+10h]
  void *v36; // [rsp+98h] [rbp+18h]
  __int64 v37; // [rsp+A0h] [rbp+20h]
  void *v38; // [rsp+A8h] [rbp+28h]
  __int64 v39; // [rsp+B0h] [rbp+30h] BYREF
  __int64 v40; // [rsp+B8h] [rbp+38h]
  __int64 v41; // [rsp+C0h] [rbp+40h]
  __int64 v42; // [rsp+C8h] [rbp+48h]
  __int64 v43; // [rsp+D0h] [rbp+50h]
  __int64 v44; // [rsp+D8h] [rbp+58h]
  __int64 v45; // [rsp+E0h] [rbp+60h]
  __int64 v46[20]; // [rsp+F0h] [rbp+70h] BYREF
  char v47; // [rsp+190h] [rbp+110h]
  char v48; // [rsp+191h] [rbp+111h]
  __int64 v49; // [rsp+198h] [rbp+118h]
  __int64 v50; // [rsp+1A0h] [rbp+120h]
  __int64 v51; // [rsp+1A8h] [rbp+128h]
  __int64 v52; // [rsp+1B0h] [rbp+130h] BYREF
  __int64 v53; // [rsp+1B8h] [rbp+138h]
  __int64 v54[4]; // [rsp+1C0h] [rbp+140h] BYREF
  __int64 v55; // [rsp+1E0h] [rbp+160h] BYREF
  void *v56; // [rsp+1E8h] [rbp+168h]
  char v57[8]; // [rsp+1F0h] [rbp+170h] BYREF
  const char *v58; // [rsp+1F8h] [rbp+178h]
  __int64 v59; // [rsp+200h] [rbp+180h]
  const char *v60; // [rsp+208h] [rbp+188h]
  __int16 v61; // [rsp+210h] [rbp+190h]
  __int64 v62[17]; // [rsp+220h] [rbp+1A0h] BYREF
  unsigned __int8 v63; // [rsp+2A8h] [rbp+228h]
  __int64 v64; // [rsp+2B0h] [rbp+230h]
  void *v65; // [rsp+2B8h] [rbp+238h]
  char v66; // [rsp+2C0h] [rbp+240h]
  char v67; // [rsp+2C1h] [rbp+241h]
  __int64 v68[8]; // [rsp+2D0h] [rbp+250h] BYREF
  __int64 v69; // [rsp+310h] [rbp+290h] BYREF
  __int64 v70; // [rsp+318h] [rbp+298h]
  __int64 v71; // [rsp+320h] [rbp+2A0h]
  __int64 v72; // [rsp+328h] [rbp+2A8h]
  __int64 v73; // [rsp+330h] [rbp+2B0h]
  __int64 v74; // [rsp+338h] [rbp+2B8h]
  __int64 v75; // [rsp+340h] [rbp+2C0h]
  __int64 v76; // [rsp+350h] [rbp+2D0h]
  __int64 v77; // [rsp+358h] [rbp+2D8h]
  __int64 v78; // [rsp+360h] [rbp+2E0h]
  __int64 v79; // [rsp+370h] [rbp+2F0h] BYREF
  _QWORD *v80; // [rsp+378h] [rbp+2F8h]
  __int64 v81; // [rsp+380h] [rbp+300h] BYREF
  _QWORD *v82; // [rsp+388h] [rbp+308h]
  __int64 v83; // [rsp+398h] [rbp+318h]
  char v84; // [rsp+3A7h] [rbp+327h]
  __int64 v85; // [rsp+3A8h] [rbp+328h]
  bool v86; // [rsp+3B3h] [rbp+333h]
  bool v87; // [rsp+3B4h] [rbp+334h]
  bool v88; // [rsp+3B5h] [rbp+335h]
  bool v89; // [rsp+3B6h] [rbp+336h]
  char v90; // [rsp+3B7h] [rbp+337h]
  _QWORD *v91; // [rsp+3B8h] [rbp+338h]
  __int64 v92; // [rsp+3C0h] [rbp+340h]
  char v93; // [rsp+3CEh] [rbp+34Eh]
  char v94; // [rsp+3CFh] [rbp+34Fh]
  _QWORD *v95; // [rsp+3D0h] [rbp+350h]
  char v96; // [rsp+3DEh] [rbp+35Eh]
  unsigned __int8 v97; // [rsp+3DFh] [rbp+35Fh]
  _BYTE *v98; // [rsp+3E0h] [rbp+360h]
  bool v99; // [rsp+3EBh] [rbp+36Bh]
  bool v100; // [rsp+3ECh] [rbp+36Ch]
  bool v101; // [rsp+3EDh] [rbp+36Dh]
  char v102; // [rsp+3EEh] [rbp+36Eh]
  char v103; // [rsp+3EFh] [rbp+36Fh]

  v6 = a3[1];
  v37 = *a3;
  v38 = (void *)v6;
  v7 = a4[1];
  v35 = *a4;
  v36 = (void *)v7;
  v8 = a5[1];
  v33 = *a5;
  v34 = (void *)v8;
  v58 = "create_buffer_for_component";
  v60 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
  v59 = 0i64;
  v61 = 0;
  nimFrame_72(v57);
  v98 = (_BYTE *)nimErrorFlag_70();
  v81 = 0i64;
  v82 = 0i64;
  v97 = 0;
  v79 = 0i64;
  v80 = 0i64;
  v59 = 224i64;
  v96 = 0;
  v9 = *a2;
  v10 = *((_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788 + 1);
  v30 = *(_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788;
  v31 = v10;
  v32 = *((_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788 + 2);
  v96 = contains__modelZboardZmemory95manager_u414(&v30, v9);
  if ( *v98 )
    goto LABEL_52;
  if ( !v96 )
  {
    v59 = 394i64;
    v60 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v80 && (*v80 & 0x4000000000000000i64) == 0 )
      deallocShared(v80);
    if ( v82 && (*v82 & 0x4000000000000000i64) == 0 )
      deallocShared(v82);
    return popFrame_72();
  }
  v59 = 226i64;
  v60 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
  if ( *((__int64 *)a2 + 46) <= 7 )
  {
    v59 = 227i64;
    v95 = 0i64;
    v95 = (_QWORD *)X5BX5D___modelZboardZmemory95manager_u501(
                      refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788,
                      *a2);
    if ( *v98 )
      goto LABEL_52;
    *((_QWORD *)a2 + 46) = *v95;
  }
  v59 = 1699i64;
  v60 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  v28 = v37;
  v29 = v38;
  eqcopy___system_u2661(&v81, &v28);
  v59 = 230i64;
  v60 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
  v94 = 0;
  v94 = is_immutable_data__modelZsave95mongerZcommon_u5429(a2);
  if ( *v98 )
    goto LABEL_52;
  if ( v94 == 1 )
  {
    v59 = 231i64;
    v60 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
    v55 = 0i64;
    v56 = 0i64;
    rawNewString(&v28, v35 + 1);
    v55 = v28;
    v56 = v29;
    v28 = v35;
    v29 = v36;
    appendString_20(&v55, &v28);
    v28 = TM__L0TtlZGGNBsNJ2HmEX3X7A_6;
    v29 = &TM__L0TtlZGGNBsNJ2HmEX3X7A_5;
    appendString_20(&v55, &v28);
    v59 = 1699i64;
    v60 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v28 = v55;
    v29 = v56;
    eqsink___system_u2667(&v81, &v28);
  }
  v59 = 233i64;
  v60 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
  v11 = *((_QWORD *)a2 + 47);
  v76 = *((_QWORD *)a2 + 46);
  v77 = v11;
  v78 = *((_QWORD *)a2 + 48);
  v59 = 235i64;
  v93 = 0;
  v12 = a1[1];
  v30 = *a1;
  v31 = v12;
  v32 = a1[2];
  v93 = contains__modelZboardZmemory95manager_u622(&v30, *((_QWORD *)a2 + 1));
  if ( *v98 )
    goto LABEL_52;
  if ( v93 != 1 )
  {
LABEL_42:
    nimZeroMem_52(&v69, 56i64);
    v59 = 265i64;
    nimZeroMem_52(v68, 56i64);
    v30 = v76;
    v31 = v77;
    v32 = v78;
    buf_alloc__modelZboardZmemory95manager_u329(&v30, *((_QWORD *)a2 + 1), (__int64)v68);
    v69 = v68[0];
    v70 = v68[1];
    v71 = v68[2];
    v72 = v68[3];
    v73 = v68[4];
    v74 = v68[5];
    v75 = v68[6];
    if ( !*v98 )
    {
      v21 = v70;
      *((_QWORD *)a2 + 39) = v69;
      *((_QWORD *)a2 + 40) = v21;
      v22 = v72;
      *((_QWORD *)a2 + 41) = v71;
      *((_QWORD *)a2 + 42) = v22;
      v23 = v74;
      *((_QWORD *)a2 + 43) = v73;
      *((_QWORD *)a2 + 44) = v23;
      *((_QWORD *)a2 + 45) = v75;
      v59 = 269i64;
      v84 = 0;
      v28 = v81;
      v29 = v82;
      v84 = nosdirExists(&v28);
      if ( !*v98 )
      {
        if ( v84 || (v59 = 270i64, v28 = v81, v29 = v82, noscreateDir(&v28), !*v98) )
        {
          v59 = 272i64;
          nimZeroMem_52(v62, 168i64);
          v62[0] = v76;
          v62[1] = v77;
          v62[2] = v78;
          v62[3] = v69;
          v62[4] = v70;
          v62[5] = v71;
          v62[6] = v72;
          v62[7] = v73;
          v62[8] = v74;
          v62[9] = v75;
          v59 = 275i64;
          v25 = v81;
          v26 = v82;
          default_file_path__modelZboardZmemory95manager_u16(&v28, &v25, a2);
          v64 = v28;
          v65 = v29;
          if ( !*v98 )
          {
            v59 = 276i64;
            v97 = a2[377];
            v63 = v97;
            v59 = 277i64;
            v28 = v33;
            v29 = v34;
            v25 = TM__L0TtlZGGNBsNJ2HmEX3X7A_19;
            v26 = &TM__L0TtlZGGNBsNJ2HmEX3X7A_8;
            v66 = eqStrings_7(&v28, &v25);
            v59 = 278i64;
            v67 = is_immutable_data__modelZsave95mongerZcommon_u5429(a2);
            if ( !*v98 )
            {
              v59 = 272i64;
              X5BX5Deq___modelZboardZmemory95manager_u1342(a1, *((_QWORD *)a2 + 1), v62);
              if ( !*v98 )
              {
                v59 = 281i64;
                v83 = 0i64;
                v83 = X5BX5D___modelZboardZmemory95manager_u1131(a1, *((_QWORD *)a2 + 1));
                if ( !*v98 )
                {
                  v28 = v81;
                  v29 = v82;
                  default_file_path__modelZboardZmemory95manager_u16(&v79, &v28, a2);
                  if ( !*v98 )
                  {
                    v28 = v79;
                    v29 = v80;
                    load_reset_data_from_file__modelZboardZmemory95manager_u131(*((_QWORD *)a2 + 1), v83, &v28);
                  }
                }
              }
            }
          }
        }
      }
    }
    goto LABEL_52;
  }
  nimZeroMem_52(v54, 24i64);
  v92 = 0i64;
  v52 = 0i64;
  v53 = 0i64;
  nimZeroMem_52(&v39, 56i64);
  v59 = 236i64;
  v91 = 0i64;
  v91 = (_QWORD *)X5BX5D___modelZboardZmemory95manager_u1131(a1, *((_QWORD *)a2 + 1));
  if ( *v98 )
    goto LABEL_52;
  v13 = v91[4];
  v39 = v91[3];
  v40 = v13;
  v14 = v91[6];
  v41 = v91[5];
  v42 = v14;
  v15 = v91[8];
  v43 = v91[7];
  v44 = v15;
  v45 = v91[9];
  v103 = BYTE1(v77);
  v102 = v15;
  v59 = 241i64;
  if ( BYTE1(v77) == 2 || v103 == 3 )
  {
    v59 = 242i64;
    v103 = 4;
  }
  v59 = 243i64;
  if ( v102 == 2 || v102 == 3 )
  {
    v59 = 244i64;
    v102 = 4;
  }
  v59 = 246i64;
  v90 = 0;
  v90 = eqeq___modelZboardZmemory95manager_u146(v76, v39);
  v89 = v90 == 0;
  v88 = (_BYTE)v77 != (unsigned __int8)v40;
  v87 = v103 != v102;
  v86 = v78 != v45;
  v59 = 251i64;
  v101 = 0;
  v100 = 0;
  v99 = v90 != 0;
  if ( v90 )
    v99 = !v88;
  v100 = v99;
  if ( v99 )
    v100 = !v87;
  v101 = v100;
  if ( v100 )
    v101 = !v86;
  if ( v101 )
  {
    v16 = v40;
    *((_QWORD *)a2 + 39) = v39;
    *((_QWORD *)a2 + 40) = v16;
    v17 = v42;
    *((_QWORD *)a2 + 41) = v41;
    *((_QWORD *)a2 + 42) = v17;
    v18 = v44;
    *((_QWORD *)a2 + 43) = v43;
    *((_QWORD *)a2 + 44) = v18;
    *((_QWORD *)a2 + 45) = v45;
    v59 = 394i64;
    v60 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v80 && (*v80 & 0x4000000000000000i64) == 0 )
      deallocShared(v80);
    if ( v82 && (*v82 & 0x4000000000000000i64) == 0 )
      deallocShared(v82);
    return popFrame_72();
  }
  v59 = 255i64;
  v60 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
  v19 = *((_QWORD *)a2 + 1);
  v49 = v19 + a6;
  if ( !__OFADD__(v19, a6) )
  {
    v50 = v49;
    v51 = v49;
    v59 = 256i64;
    nimZeroMem_52(v46, 168i64);
    v59 = 23i64;
    v60 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v12.nim";
    v27[0] = v76;
    v27[1] = v77;
    v27[2] = v78;
    eqdup___modelZsave95mongerZversionsZv12_u295(&v30, v27);
    v54[0] = v30;
    v54[1] = v31;
    v54[2] = v32;
    v46[0] = v30;
    v46[1] = v31;
    v46[2] = v32;
    v46[3] = v39;
    v46[4] = v40;
    v46[5] = v41;
    v46[6] = v42;
    v46[7] = v43;
    v46[8] = v44;
    v46[9] = v45;
    v92 = a6;
    v46[16] = a6;
    v59 = 260i64;
    v60 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
    v85 = 0i64;
    v85 = X5BX5D___modelZboardZmemory95manager_u1131(a1, *((_QWORD *)a2 + 1));
    if ( *v98 )
      goto LABEL_52;
    v59 = 1699i64;
    v60 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v20 = *(void **)(v85 + 152);
    v28 = *(_QWORD *)(v85 + 144);
    v29 = v20;
    eqdup___system_u2664(&v52, &v28);
    v46[18] = v52;
    v46[19] = v53;
    v59 = 261i64;
    v60 = "D:\\TuringComplete_Phu\\model\\board\\memory_manager.nim";
    v28 = v33;
    v29 = v34;
    v25 = TM__L0TtlZGGNBsNJ2HmEX3X7A_9;
    v26 = &TM__L0TtlZGGNBsNJ2HmEX3X7A_8;
    v47 = eqStrings_7(&v28, &v25);
    v59 = 262i64;
    v48 = is_immutable_data__modelZsave95mongerZcommon_u5429(a2);
    if ( *v98 )
      goto LABEL_52;
    v59 = 256i64;
    X5BX5Deq___modelZboardZmemory95manager_u1342(a1, v51, v46);
    if ( *v98 )
      goto LABEL_52;
    goto LABEL_42;
  }
  raiseOverflow();
LABEL_52:
  v59 = 394i64;
  v60 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v80 && (*v80 & 0x4000000000000000i64) == 0 )
    deallocShared(v80);
  if ( v82 && (*v82 & 0x4000000000000000i64) == 0 )
    deallocShared(v82);
  return popFrame_72();
}
