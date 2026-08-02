// address: 0x14061e2fd-0x14061f683
// name: deserialize__modelZpk95save95mongerZpk95versionsZv0_u52
__int64 __fastcall deserialize__modelZpk95save95mongerZpk95versionsZv0_u52(
        __int64 *a1,
        __int64 *a2,
        __int64 *a3,
        __int64 *a4,
        __int64 *a5,
        char a6,
        unsigned __int8 *a7)
{
  __int64 v7; // rbx
  __int64 v8; // rax
  __int64 v9; // rdx
  __int64 v10; // rdx
  __int64 v11; // rdx
  __int64 v12; // rdx
  __int64 v13; // r10
  _QWORD *v14; // rax
  __int64 v15; // rdx
  __int64 v16; // rax
  __int64 v17; // rdx
  const char *v18; // rdx
  __int64 v20; // [rsp+20h] [rbp-60h] BYREF
  const char *v21; // [rsp+28h] [rbp-58h]
  __int64 v22; // [rsp+30h] [rbp-50h] BYREF
  const char *v23; // [rsp+38h] [rbp-48h]
  char v24; // [rsp+4Ch] [rbp-34h]
  __int64 v25; // [rsp+50h] [rbp-30h]
  const char *v26; // [rsp+58h] [rbp-28h]
  __int64 v27; // [rsp+60h] [rbp-20h]
  const char *v28; // [rsp+68h] [rbp-18h]
  __int64 v29; // [rsp+70h] [rbp-10h]
  const char *v30; // [rsp+78h] [rbp-8h]
  __int64 v31; // [rsp+80h] [rbp+0h]
  const char *v32; // [rsp+88h] [rbp+8h]
  __int64 v33; // [rsp+90h] [rbp+10h]
  __int64 v34; // [rsp+98h] [rbp+18h]
  __int64 (__fastcall *v35)(); // [rsp+A0h] [rbp+20h] BYREF
  _QWORD *v36; // [rsp+A8h] [rbp+28h]
  __int64 v37; // [rsp+B0h] [rbp+30h] BYREF
  const char *v38; // [rsp+B8h] [rbp+38h]
  __int64 v39; // [rsp+C0h] [rbp+40h] BYREF
  const char *v40; // [rsp+C8h] [rbp+48h]
  __int64 v41; // [rsp+D0h] [rbp+50h] BYREF
  const char *v42; // [rsp+D8h] [rbp+58h]
  __int64 v43; // [rsp+E0h] [rbp+60h]
  const char *v44; // [rsp+E8h] [rbp+68h]
  __int64 v45; // [rsp+F0h] [rbp+70h]
  const char *v46; // [rsp+F8h] [rbp+78h]
  __int64 v47; // [rsp+100h] [rbp+80h]
  const char *v48; // [rsp+108h] [rbp+88h]
  __int64 (__fastcall *v49)(); // [rsp+110h] [rbp+90h] BYREF
  _QWORD *v50; // [rsp+118h] [rbp+98h]
  __int64 v51; // [rsp+120h] [rbp+A0h] BYREF
  const char *v52; // [rsp+128h] [rbp+A8h]
  __int64 v53; // [rsp+130h] [rbp+B0h] BYREF
  const char *v54; // [rsp+138h] [rbp+B8h]
  __int64 v55; // [rsp+140h] [rbp+C0h]
  const char *v56; // [rsp+148h] [rbp+C8h]
  __int64 v57; // [rsp+150h] [rbp+D0h]
  const char *v58; // [rsp+158h] [rbp+D8h]
  __int64 v59; // [rsp+160h] [rbp+E0h] BYREF
  const char *v60; // [rsp+168h] [rbp+E8h]
  char v61[8]; // [rsp+170h] [rbp+F0h] BYREF
  const char *v62; // [rsp+178h] [rbp+F8h]
  __int64 v63; // [rsp+180h] [rbp+100h]
  const char *v64; // [rsp+188h] [rbp+108h]
  __int16 v65; // [rsp+190h] [rbp+110h]
  __int64 v66; // [rsp+1A0h] [rbp+120h] BYREF
  const char *v67; // [rsp+1A8h] [rbp+128h]
  __int64 v68; // [rsp+1B0h] [rbp+130h] BYREF
  const char *v69; // [rsp+1B8h] [rbp+138h]
  __int64 v70; // [rsp+1C0h] [rbp+140h] BYREF
  const char *v71; // [rsp+1C8h] [rbp+148h]
  __int64 v72; // [rsp+1D0h] [rbp+150h] BYREF
  const char *v73; // [rsp+1D8h] [rbp+158h]
  __int64 v74[2]; // [rsp+1E0h] [rbp+160h] BYREF
  __int64 v75; // [rsp+1F0h] [rbp+170h]
  const char *v76; // [rsp+1F8h] [rbp+178h]
  __int64 v77; // [rsp+200h] [rbp+180h]
  __int64 v78; // [rsp+208h] [rbp+188h]
  __int64 v79; // [rsp+210h] [rbp+190h]
  const char *v80; // [rsp+218h] [rbp+198h]
  __int64 v81; // [rsp+220h] [rbp+1A0h]
  const char *v82; // [rsp+228h] [rbp+1A8h]
  __int64 v83[2]; // [rsp+230h] [rbp+1B0h] BYREF
  __int64 v84[2]; // [rsp+240h] [rbp+1C0h] BYREF
  __int64 v85[2]; // [rsp+250h] [rbp+1D0h] BYREF
  __int64 v86[2]; // [rsp+260h] [rbp+1E0h] BYREF
  __int64 v87[2]; // [rsp+270h] [rbp+1F0h] BYREF
  __int64 v88[3]; // [rsp+280h] [rbp+200h] BYREF
  unsigned __int16 v89; // [rsp+29Ah] [rbp+21Ah]
  unsigned __int16 v90; // [rsp+29Ch] [rbp+21Ch]
  unsigned __int16 u16__modelZsave95mongerZserialize_u81; // [rsp+29Eh] [rbp+21Eh]
  __int64 v92; // [rsp+2A0h] [rbp+220h]
  _QWORD *v93; // [rsp+2A8h] [rbp+228h]
  _BYTE *v94; // [rsp+2B0h] [rbp+230h]
  unsigned __int16 v95; // [rsp+2BEh] [rbp+23Eh]

  v7 = a1[1];
  v33 = *a1;
  v34 = v7;
  v8 = *a2;
  v9 = a2[1];
  v31 = v8;
  v32 = (const char *)v9;
  v10 = a3[1];
  v29 = *a3;
  v30 = (const char *)v10;
  v11 = a4[1];
  v27 = *a4;
  v28 = (const char *)v11;
  v12 = a5[1];
  v25 = *a5;
  v26 = (const char *)v12;
  v24 = a6;
  v62 = "deserialize";
  v64 = "D:\\TuringComplete_Phu\\model\\pk_save_monger\\pk_versions\\v0.nim";
  v63 = 0i64;
  v65 = 0;
  nimFrame_157(v61);
  v94 = (_BYTE *)nimErrorFlag_152();
  nimZeroMem_128(a7, 64i64);
  v93 = 0i64;
  v81 = 0i64;
  v82 = 0i64;
  v79 = 0i64;
  v80 = 0i64;
  v63 = 25i64;
  v64 = "D:\\TuringComplete_Phu\\model\\pk_save_monger\\pk_versions\\v0.nim";
  v92 = 0i64;
  v92 = nimNewObj(64i64, 8i64);
  *(_QWORD *)v92 = &NTIv2__F1WLGd88Wzb9aeVoXH7qaZg_;
  v93 = (_QWORD *)v92;
  *(_BYTE *)(v92 + 56) = v24;
  v63 = 23i64;
  if ( (*a7 & 7) != 0 )
  {
    dollar___modelZpk95save95mongerZpk95versionsZcommon_u31(v83, *a7);
    v22 = TM__9arg57IJrbcrD9cqxe1wKKZg_4;
    v23 = "F";
    v20 = v83[0];
    v21 = (const char *)v83[1];
    raiseFieldErrorStr(&v22, &v20);
    goto LABEL_87;
  }
  a7[8] = 0;
  v77 = 0i64;
  v78 = 0i64;
  v75 = 0i64;
  v76 = 0i64;
  v63 = 27i64;
  v64 = "D:\\TuringComplete_Phu\\model\\pk_save_monger\\pk_versions\\v0.nim";
  dotdot___stdZenumutils_u105_25(v74, 1i64, 1i64);
  v72 = 0i64;
  v73 = 0i64;
  if ( v34 )
    v13 = v34 + 8;
  else
    v13 = 0i64;
  v20 = v74[0];
  v21 = (const char *)v74[1];
  ((void (__fastcall *)(__int64 *, __int64, __int64, __int64 *))X5BX5D___modelZsave95mongerZversionsZv2_u125)(
    &v72,
    v13,
    v33,
    &v20);
  if ( *v94 )
  {
    v20 = v72;
    v21 = v73;
    eqdestroy___pureZtimes_u2668(&v20);
  }
  else
  {
    v75 = v72;
    v76 = v73;
    v70 = 0i64;
    v71 = 0i64;
    v20 = v72;
    v21 = v73;
    uncompress__modelZsupersnappyZsupersnappy_u502(&v70, &v20, 1000000000i64);
    if ( *v94 )
    {
      v20 = v70;
      v21 = v71;
      eqdestroy___pureZtimes_u2668(&v20);
    }
    else
    {
      v63 = 1772i64;
      v64 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\times.nim";
      v20 = v70;
      v21 = v71;
      eqsink___pureZtimes_u2677(v93 + 1, &v20);
    }
  }
  v20 = v75;
  v21 = v76;
  eqdestroy___pureZtimes_u2668(&v20);
  if ( !*v94
    || (v14 = (_QWORD *)nimBorrowCurrentException_8(), !(unsigned __int8)isObjDisplayCheck_10(*v14, 4i64, 3288731392i64)) )
  {
    if ( *v94 )
      goto LABEL_87;
    v93[3] = 0i64;
    v63 = 1699i64;
    v64 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( (*a7 & 7) != 0 )
    {
      dollar___modelZpk95save95mongerZpk95versionsZcommon_u31(v84, *a7);
      v20 = TM__9arg57IJrbcrD9cqxe1wKKZg_5;
      v21 = "F";
      v22 = v84[0];
      v23 = (const char *)v84[1];
      raiseFieldErrorStr(&v20, &v22);
      goto LABEL_87;
    }
    v63 = 33i64;
    v64 = "D:\\TuringComplete_Phu\\model\\pk_save_monger\\pk_versions\\v0.nim";
    v59 = 0i64;
    v60 = 0i64;
    if ( v93[2] )
      v15 = v93[2] + 8i64;
    else
      v15 = 0i64;
    get_string__modelZsave95mongerZserialize_u180(&v59, v15, v93[1], v93 + 3);
    if ( *v94 )
    {
      v20 = v59;
      v21 = v60;
      eqdestroy___system_u281_41(&v20);
      goto LABEL_87;
    }
    v63 = 1699i64;
    v64 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v20 = v59;
    v21 = v60;
    eqsink___system_u2667(a7 + 16, &v20);
    v63 = 34i64;
    v64 = "D:\\TuringComplete_Phu\\model\\pk_save_monger\\pk_versions\\v0.nim";
    if ( v27 )
    {
      v63 = 1699i64;
      v64 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( (*a7 & 7) != 0 )
      {
        dollar___modelZpk95save95mongerZpk95versionsZcommon_u31(v85, *a7);
        v20 = TM__9arg57IJrbcrD9cqxe1wKKZg_6;
        v21 = "F";
        v22 = v85[0];
        v23 = (const char *)v85[1];
        raiseFieldErrorStr(&v20, &v22);
LABEL_87:
        if ( v80 && (*(_QWORD *)v80 & 0x4000000000000000i64) == 0 )
          deallocShared(v80);
        if ( v82 && (*(_QWORD *)v82 & 0x4000000000000000i64) == 0 )
          deallocShared(v82);
        v63 = 15i64;
        v64 = "D:\\TuringComplete_Phu\\model\\pk_save_monger\\pk_versions\\v0.nim";
        eqdestroy___modelZpk95save95mongerZpk95versionsZv0_u821(v93);
        return popFrame_157();
      }
      v20 = v27;
      v21 = v28;
      eqcopy___system_u2661(a7 + 16, &v20);
    }
    v63 = 79i64;
    v64 = "D:\\TuringComplete_Phu\\model\\pk_save_monger\\pk_versions\\v0.nim";
    v68 = 0i64;
    v69 = 0i64;
    v20 = v29;
    v21 = v30;
    v22 = TM__9arg57IJrbcrD9cqxe1wKKZg_8;
    v23 = (const char *)&TM__9arg57IJrbcrD9cqxe1wKKZg_7;
    slash___stdZprivateZospaths2_u87_14(&v68, &v20, &v22);
    if ( *v94 )
    {
      v20 = v68;
      v21 = v69;
      eqdestroy___system_u281_41(&v20);
    }
    else
    {
      v79 = v68;
      v80 = v69;
      v66 = 0i64;
      v67 = 0i64;
      v20 = v68;
      v21 = v69;
      v22 = v25;
      v23 = v26;
      slash___stdZprivateZospaths2_u87_14(&v66, &v20, &v22);
      if ( *v94 )
      {
        v20 = v66;
        v21 = v67;
        eqdestroy___system_u281_41(&v20);
      }
      else
      {
        v81 = v66;
        v82 = v67;
        v63 = 81i64;
        u16__modelZsave95mongerZserialize_u81 = 0;
        if ( v93[2] )
          v16 = v93[2] + 8i64;
        else
          v16 = 0i64;
        u16__modelZsave95mongerZserialize_u81 = get_u16__modelZsave95mongerZserialize_u81(v16, v93[1], v93 + 3);
        if ( !*v94 )
        {
          v90 = u16__modelZsave95mongerZserialize_u81;
          v89 = 0;
          v64 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v95 = 0;
          v63 = 129i64;
          while ( v95 < v90 )
          {
            v57 = 0i64;
            v58 = 0i64;
            v55 = 0i64;
            v56 = 0i64;
            v64 = "D:\\TuringComplete_Phu\\model\\pk_save_monger\\pk_versions\\v0.nim";
            v89 = v95;
            v63 = 83i64;
            v53 = 0i64;
            v54 = 0i64;
            if ( v93[2] )
              v17 = v93[2] + 8i64;
            else
              v17 = 0i64;
            get_string__modelZsave95mongerZserialize_u180(&v53, v17, v93[1], v93 + 3);
            if ( *v94 )
            {
              v20 = v53;
              v21 = v54;
              eqdestroy___system_u281_41(&v20);
            }
            else
            {
              v55 = v53;
              v56 = v54;
              v51 = 0i64;
              v52 = 0i64;
              v20 = v81;
              v21 = v82;
              v22 = v53;
              v23 = v54;
              slash___stdZprivateZospaths2_u87_14(&v51, &v20, &v22);
              if ( *v94 )
              {
                v20 = v51;
                v21 = v52;
                eqdestroy___system_u281_41(&v20);
              }
              else
              {
                v57 = v51;
                v58 = v52;
                v63 = 84i64;
                nimZeroMem_128(&v49, 16i64);
                v49 = get_file_and_store__modelZpk95save95mongerZpk95versionsZv0_u81;
                v50 = v93;
                if ( (*a7 & 7) != 0 )
                {
                  dollar___modelZpk95save95mongerZpk95versionsZcommon_u31(v86, *a7);
                  v20 = TM__9arg57IJrbcrD9cqxe1wKKZg_23;
                  v21 = "F";
                  v22 = v86[0];
                  v23 = (const char *)v86[1];
                  raiseFieldErrorStr(&v20, &v22);
                }
                else
                {
                  v20 = v57;
                  v21 = v58;
                  if ( v50 )
                    ((void (__fastcall *)(__int64 *, unsigned __int8 *, _QWORD *))v49)(&v20, a7 + 8, v50);
                  else
                    ((void (__fastcall *)(__int64 *, unsigned __int8 *))v49)(&v20, a7 + 8);
                  if ( !*v94 )
                  {
                    v63 = 131i64;
                    v64 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                    ++v95;
                  }
                }
              }
            }
            v63 = 394i64;
            v64 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v56 && (*(_QWORD *)v56 & 0x4000000000000000i64) == 0 )
              deallocShared(v56);
            if ( v58 && (*(_QWORD *)v58 & 0x4000000000000000i64) == 0 )
              deallocShared(v58);
            if ( *v94 )
              goto LABEL_87;
          }
          v47 = 0i64;
          v48 = 0i64;
          v45 = 0i64;
          v46 = 0i64;
          v43 = 0i64;
          v44 = 0i64;
          v64 = "D:\\TuringComplete_Phu\\model\\pk_save_monger\\pk_versions\\v0.nim";
          v63 = 88i64;
          v41 = 0i64;
          v42 = 0i64;
          v20 = v29;
          v21 = v30;
          v22 = TM__9arg57IJrbcrD9cqxe1wKKZg_25;
          v23 = (const char *)&TM__9arg57IJrbcrD9cqxe1wKKZg_7;
          slash___stdZprivateZospaths2_u87_14(&v41, &v20, &v22);
          if ( *v94 )
          {
            v20 = v41;
            v21 = v42;
            eqdestroy___system_u281_41(&v20);
          }
          else
          {
            v45 = v41;
            v46 = v42;
            if ( (*a7 & 7) != 0 )
            {
              dollar___modelZpk95save95mongerZpk95versionsZcommon_u31(v87, *a7);
              v20 = TM__9arg57IJrbcrD9cqxe1wKKZg_26;
              v21 = "F";
              v22 = v87[0];
              v23 = (const char *)v87[1];
              raiseFieldErrorStr(&v20, &v22);
            }
            else
            {
              v39 = 0i64;
              v40 = 0i64;
              v20 = v45;
              v21 = v46;
              v18 = (const char *)*((_QWORD *)a7 + 3);
              v22 = *((_QWORD *)a7 + 2);
              v23 = v18;
              slash___stdZprivateZospaths2_u87_14(&v39, &v20, &v22);
              if ( *v94 )
              {
                v20 = v39;
                v21 = v40;
                eqdestroy___system_u281_41(&v20);
              }
              else
              {
                v43 = v39;
                v44 = v40;
                v37 = 0i64;
                v38 = 0i64;
                v20 = v39;
                v21 = v40;
                v22 = v31;
                v23 = v32;
                slash___stdZprivateZospaths2_u87_14(&v37, &v20, &v22);
                if ( *v94 )
                {
                  v20 = v37;
                  v21 = v38;
                  eqdestroy___system_u281_41(&v20);
                }
                else
                {
                  v47 = v37;
                  v48 = v38;
                  v63 = 89i64;
                  v20 = v37;
                  v21 = v38;
                  noscreateDir(&v20);
                  if ( !*v94 )
                  {
                    v63 = 90i64;
                    nimZeroMem_128(&v35, 16i64);
                    v35 = get_file_and_store__modelZpk95save95mongerZpk95versionsZv0_u81;
                    v36 = v93;
                    if ( (*a7 & 7) != 0 )
                    {
                      dollar___modelZpk95save95mongerZpk95versionsZcommon_u31(v88, *a7);
                      v20 = TM__9arg57IJrbcrD9cqxe1wKKZg_27;
                      v21 = "F";
                      v22 = v88[0];
                      v23 = (const char *)v88[1];
                      raiseFieldErrorStr(&v20, &v22);
                    }
                    else
                    {
                      v20 = v47;
                      v21 = v48;
                      if ( v36 )
                        ((void (__fastcall *)(__int64 *, unsigned __int8 *, _QWORD *))v35)(&v20, a7 + 8, v36);
                      else
                        ((void (__fastcall *)(__int64 *, unsigned __int8 *))v35)(&v20, a7 + 8);
                    }
                  }
                }
              }
            }
          }
          v63 = 394i64;
          v64 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v44 && (*(_QWORD *)v44 & 0x4000000000000000i64) == 0 )
            deallocShared(v44);
          if ( v46 && (*(_QWORD *)v46 & 0x4000000000000000i64) == 0 )
            deallocShared(v46);
          if ( v48 && (*(_QWORD *)v48 & 0x4000000000000000i64) == 0 )
            deallocShared(v48);
        }
      }
    }
    goto LABEL_87;
  }
  *v94 = 0;
  v64 = "D:\\TuringComplete_Phu\\model\\pk_save_monger\\pk_versions\\v0.nim";
  v63 = 29i64;
  nimZeroMem_128(a7, 64i64);
  *a7 = 1;
  v63 = 394i64;
  v64 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v80 && (*(_QWORD *)v80 & 0x4000000000000000i64) == 0 )
    deallocShared(v80);
  if ( v82 && (*(_QWORD *)v82 & 0x4000000000000000i64) == 0 )
    deallocShared(v82);
  v63 = 15i64;
  v64 = "D:\\TuringComplete_Phu\\model\\pk_save_monger\\pk_versions\\v0.nim";
  eqdestroy___modelZpk95save95mongerZpk95versionsZv0_u821(v93);
  popCurrentException_13();
  return popFrame_157();
}
