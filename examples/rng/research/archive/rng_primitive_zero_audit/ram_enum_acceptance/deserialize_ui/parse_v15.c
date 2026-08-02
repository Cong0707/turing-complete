// address: 0x1401beb42-0x1401bf9e8
// name: parse__modelZsave95mongerZversionsZv15_u321
__int64 __fastcall parse__modelZsave95mongerZversionsZv15_u321(__int64 *a1, char a2, unsigned __int8 a3, __int64 a4)
{
  __int64 v4; // rbx
  __int64 v5; // r10
  __int64 v6; // rax
  __int64 v7; // rax
  __int64 v8; // rax
  __int64 v9; // rax
  __int64 v10; // rax
  __int64 v11; // rax
  __int64 v12; // rdx
  __int64 v13; // rdx
  __int64 v14; // rax
  __int64 v15; // rax
  __int64 v16; // rdx
  __int64 v17; // rdx
  __int64 v18; // rax
  __int64 v20; // [rsp+20h] [rbp-60h] BYREF
  __int64 v21; // [rsp+28h] [rbp-58h]
  __int64 v22; // [rsp+30h] [rbp-50h]
  __int64 v23; // [rsp+38h] [rbp-48h]
  __int64 v24; // [rsp+48h] [rbp-38h]
  unsigned __int64 v25; // [rsp+50h] [rbp-30h]
  unsigned __int64 v26; // [rsp+58h] [rbp-28h]
  unsigned __int64 v27; // [rsp+60h] [rbp-20h]
  __int64 v28; // [rsp+68h] [rbp-18h]
  __int64 v29; // [rsp+70h] [rbp-10h] BYREF
  __int64 v30; // [rsp+78h] [rbp-8h]
  __int64 v31; // [rsp+80h] [rbp+0h] BYREF
  __int64 v32; // [rsp+88h] [rbp+8h]
  char v33[8]; // [rsp+90h] [rbp+10h] BYREF
  const char *v34; // [rsp+98h] [rbp+18h]
  __int64 v35; // [rsp+A0h] [rbp+20h]
  const char *v36; // [rsp+A8h] [rbp+28h]
  __int16 v37; // [rsp+B0h] [rbp+30h]
  __int64 v38; // [rsp+C0h] [rbp+40h] BYREF
  __int64 v39; // [rsp+C8h] [rbp+48h]
  __int64 v40; // [rsp+D0h] [rbp+50h] BYREF
  __int64 v41; // [rsp+D8h] [rbp+58h]
  __int64 v42; // [rsp+E0h] [rbp+60h] BYREF
  __int64 v43; // [rsp+E8h] [rbp+68h]
  __int64 v44; // [rsp+F0h] [rbp+70h] BYREF
  __int64 v45; // [rsp+F8h] [rbp+78h]
  __int64 v46; // [rsp+108h] [rbp+88h] BYREF
  __int64 v47[2]; // [rsp+110h] [rbp+90h] BYREF
  __int64 v48; // [rsp+120h] [rbp+A0h] BYREF
  __int64 v49; // [rsp+128h] [rbp+A8h]
  __int64 v50; // [rsp+130h] [rbp+B0h] BYREF
  __int64 v51; // [rsp+138h] [rbp+B8h]
  char u8__modelZsave95mongerZserialize_u101; // [rsp+14Fh] [rbp+CFh]
  unsigned __int64 v53; // [rsp+150h] [rbp+D0h]
  unsigned __int64 v54; // [rsp+158h] [rbp+D8h]
  __int16 u16__modelZsave95mongerZserialize_u81; // [rsp+164h] [rbp+E4h]
  char sync_state__modelZsave95mongerZcommon_u5803; // [rsp+167h] [rbp+E7h]
  __int64 u64__modelZsave95mongerZserialize_u9; // [rsp+168h] [rbp+E8h]
  char bool__modelZsave95mongerZserialize_u1; // [rsp+177h] [rbp+F7h]
  __int64 v59; // [rsp+178h] [rbp+F8h]
  __int64 v60; // [rsp+180h] [rbp+100h]
  int u32__modelZsave95mongerZserialize_u53; // [rsp+18Ch] [rbp+10Ch]
  __int64 i64__modelZsave95mongerZserialize_u49; // [rsp+190h] [rbp+110h]
  _BYTE *v63; // [rsp+198h] [rbp+118h]
  __int64 v64; // [rsp+1A0h] [rbp+120h]
  __int64 v65; // [rsp+1A8h] [rbp+128h]

  v4 = a1[1];
  v22 = *a1;
  v23 = v4;
  v34 = "parse";
  v36 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
  v35 = 0i64;
  v37 = 0;
  nimFrame_58(v33);
  v63 = (_BYTE *)nimErrorFlag_56();
  v50 = 0i64;
  v51 = 0i64;
  v48 = 0i64;
  v49 = 0i64;
  v35 = 121i64;
  v36 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
  dotdot___stdZenumutils_u105_15(v47, 1i64, 1i64);
  if ( v4 )
    v5 = v23 + 8;
  else
    v5 = 0i64;
  v20 = v47[0];
  v21 = v47[1];
  ((void (__fastcall *)(__int64 *, __int64, __int64, __int64 *))X5BX5D___modelZsave95mongerZversionsZv2_u125)(
    &v48,
    v5,
    v22,
    &v20);
  if ( !*v63 )
  {
    v20 = v48;
    v21 = v49;
    uncompress__modelZsave95mongerZlibrariesZsupersnappyZsupersnappy_u515_12(&v50, &v20, 0xFFFFFFFFi64);
    if ( !*v63 )
    {
      v46 = 0i64;
      v35 = 124i64;
      i64__modelZsave95mongerZserialize_u49 = 0i64;
      v6 = v51 ? v51 + 8 : 0i64;
      i64__modelZsave95mongerZserialize_u49 = get_i64__modelZsave95mongerZserialize_u49(v6, v50, &v46);
      if ( !*v63 )
      {
        *(_QWORD *)(a4 + 80) = i64__modelZsave95mongerZserialize_u49;
        v35 = 125i64;
        u32__modelZsave95mongerZserialize_u53 = 0;
        v7 = v51 ? v51 + 8 : 0i64;
        u32__modelZsave95mongerZserialize_u53 = get_u32__modelZsave95mongerZserialize_u53(v7, v50, &v46);
        if ( !*v63 )
        {
          *(_DWORD *)(a4 + 88) = u32__modelZsave95mongerZserialize_u53;
          v35 = 126i64;
          v60 = 0i64;
          v8 = v51 ? v51 + 8 : 0i64;
          v60 = get_i64__modelZsave95mongerZserialize_u49(v8, v50, &v46);
          if ( !*v63 )
          {
            *(_QWORD *)(a4 + 112) = v60;
            v35 = 127i64;
            v59 = 0i64;
            v9 = v51 ? v51 + 8 : 0i64;
            v59 = get_i64__modelZsave95mongerZserialize_u49(v9, v50, &v46);
            if ( !*v63 )
            {
              *(_QWORD *)(a4 + 120) = v59;
              v35 = 128i64;
              bool__modelZsave95mongerZserialize_u1 = 0;
              v10 = v51 ? v51 + 8 : 0i64;
              bool__modelZsave95mongerZserialize_u1 = get_bool__modelZsave95mongerZserialize_u1(v10, v50, &v46);
              if ( !*v63 )
              {
                *(_BYTE *)(a4 + 128) = bool__modelZsave95mongerZserialize_u1;
                v35 = 129i64;
                u64__modelZsave95mongerZserialize_u9 = 0i64;
                v11 = v51 ? v51 + 8 : 0i64;
                u64__modelZsave95mongerZserialize_u9 = get_u64__modelZsave95mongerZserialize_u9(v11, v50, &v46);
                if ( !*v63 )
                {
                  *(_QWORD *)(a4 + 136) = u64__modelZsave95mongerZserialize_u9;
                  v35 = 130i64;
                  v36 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
                  v44 = 0i64;
                  v45 = 0i64;
                  if ( v51 )
                    v12 = v51 + 8;
                  else
                    v12 = 0i64;
                  get_seq_int__modelZsave95mongerZcommon_u5711(&v44, v12, v50, &v46);
                  if ( *v63 )
                  {
                    v20 = v44;
                    v21 = v45;
                    eqdestroy___modelZsave95mongerZcommon_u5612(&v20);
                  }
                  else
                  {
                    v35 = 982i64;
                    v36 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
                    v20 = v44;
                    v21 = v45;
                    eqsink___modelZsave95mongerZcommon_u5621(a4 + 144, &v20);
                    v35 = 131i64;
                    v36 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
                    v42 = 0i64;
                    v43 = 0i64;
                    if ( v51 )
                      v13 = v51 + 8;
                    else
                      v13 = 0i64;
                    get_string__modelZsave95mongerZserialize_u180(&v42, v13, v50, &v46);
                    if ( *v63 )
                    {
                      v20 = v42;
                      v21 = v43;
                      eqdestroy___system_u281_23(&v20);
                    }
                    else
                    {
                      v35 = 1699i64;
                      v36 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                      v20 = v42;
                      v21 = v43;
                      eqsink___system_u2667(a4 + 160, &v20);
                      v35 = 132i64;
                      v36 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
                      sync_state__modelZsave95mongerZcommon_u5803 = 0;
                      if ( v51 )
                        v14 = v51 + 8;
                      else
                        v14 = 0i64;
                      sync_state__modelZsave95mongerZcommon_u5803 = get_sync_state__modelZsave95mongerZcommon_u5803(
                                                                      v14,
                                                                      v50,
                                                                      &v46);
                      if ( !*v63 )
                      {
                        *(_BYTE *)(a4 + 192) = sync_state__modelZsave95mongerZcommon_u5803;
                        v35 = 133i64;
                        u16__modelZsave95mongerZserialize_u81 = 0;
                        v15 = v51 ? v51 + 8 : 0i64;
                        u16__modelZsave95mongerZserialize_u81 = get_u16__modelZsave95mongerZserialize_u81(
                                                                  v15,
                                                                  v50,
                                                                  &v46);
                        if ( !*v63 )
                        {
                          v35 = 134i64;
                          v36 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
                          v40 = 0i64;
                          v41 = 0i64;
                          if ( v51 )
                            v16 = v51 + 8;
                          else
                            v16 = 0i64;
                          get_seq_u8__modelZsave95mongerZserialize_u131(&v40, v16, v50, &v46);
                          if ( *v63 )
                          {
                            v20 = v40;
                            v21 = v41;
                            eqdestroy___pureZtimes_u2668(&v20);
                          }
                          else
                          {
                            v35 = 1772i64;
                            v36 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\times.nim";
                            v20 = v40;
                            v21 = v41;
                            eqsink___pureZtimes_u2677(a4 + 176, &v20);
                            v35 = 135i64;
                            v36 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
                            v38 = 0i64;
                            v39 = 0i64;
                            if ( v51 )
                              v17 = v51 + 8;
                            else
                              v17 = 0i64;
                            get_string__modelZsave95mongerZserialize_u180(&v38, v17, v50, &v46);
                            if ( *v63 )
                            {
                              v20 = v38;
                              v21 = v39;
                              eqdestroy___system_u281_23(&v20);
                            }
                            else
                            {
                              v35 = 1699i64;
                              v36 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                              v20 = v38;
                              v21 = v39;
                              eqsink___system_u2667(a4 + 96, &v20);
                              v35 = 137i64;
                              v36 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
                              if ( !a2 )
                              {
                                v31 = 0i64;
                                v32 = 0i64;
                                v35 = 138i64;
                                if ( *(_QWORD *)(a4 + 80) )
                                {
                                  v54 = 0i64;
                                  v36 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                                  v65 = 0i64;
                                  v35 = 129i64;
                                  while ( v65 <= 31 )
                                  {
                                    v54 = v65;
                                    v53 = 0i64;
                                    v36 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                                    v64 = 0i64;
                                    v35 = 129i64;
                                    while ( v64 <= 15 )
                                    {
                                      v36 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
                                      v53 = v64;
                                      v35 = 141i64;
                                      if ( v51 )
                                        v18 = v51 + 8;
                                      else
                                        v18 = 0i64;
                                      u8__modelZsave95mongerZserialize_u101 = get_u8__modelZsave95mongerZserialize_u101(
                                                                                v18,
                                                                                v50,
                                                                                &v46);
                                      if ( *v63 )
                                        goto LABEL_89;
                                      v35 = 142i64;
                                      if ( v54 > 0x1F )
                                      {
LABEL_69:
                                        raiseIndexError2(v54, 31i64);
                                        goto LABEL_89;
                                      }
                                      v27 = 2 * v53;
                                      if ( !is_mul_ok(v53, 2ui64) )
                                        goto LABEL_83;
                                      if ( v27 > 0x1F )
                                      {
                                        raiseIndexError2(v27, 31i64);
                                        goto LABEL_89;
                                      }
                                      *(_BYTE *)(v27 + a4 + 32 * v54 + 193) = u8__modelZsave95mongerZserialize_u101 & 0xF0;
                                      v35 = 143i64;
                                      if ( v54 > 0x1F )
                                        goto LABEL_69;
                                      v26 = 2 * v53;
                                      if ( !is_mul_ok(v53, 2ui64) )
                                        goto LABEL_83;
                                      v25 = v26 + 1;
                                      if ( __OFADD__(1i64, v26) )
                                        goto LABEL_83;
                                      if ( v25 > 0x1F )
                                      {
                                        raiseIndexError2(v25, 31i64);
                                        goto LABEL_89;
                                      }
                                      *(_BYTE *)(v25 + a4 + 32 * v54 + 193) = 16 * u8__modelZsave95mongerZserialize_u101;
                                      v35 = 131i64;
                                      v36 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                                      v24 = v64 + 1;
                                      if ( __OFADD__(1i64, v64) )
                                        goto LABEL_83;
                                      v64 = v24;
                                    }
                                    v28 = v65 + 1;
                                    if ( __OFADD__(1i64, v65) )
                                    {
LABEL_83:
                                      raiseOverflow();
                                      goto LABEL_89;
                                    }
                                    v65 = v28;
                                  }
                                }
                                v35 = 145i64;
                                v36 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
                                v29 = 0i64;
                                v30 = 0i64;
                                v20 = v50;
                                v21 = v51;
                                get_components__modelZsave95mongerZversionsZv15_u282(&v29, &v20, (__int64)&v46, a3);
                                if ( *v63 )
                                {
                                  v20 = v29;
                                  v21 = v30;
                                  eqdestroy___modelZsave95mongerZversionsZv0_u1076(&v20);
                                }
                                else
                                {
                                  v35 = 72i64;
                                  v36 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                                  v20 = v29;
                                  v21 = v30;
                                  eqsink___modelZsave95mongerZversionsZv0_u1085(a4 + 8, &v20);
                                  v35 = 146i64;
                                  v36 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v15.nim";
                                  v20 = v50;
                                  v21 = v51;
                                  get_wires__modelZsave95mongerZversionsZv15_u311(&v31, &v20, &v46);
                                  if ( !*v63 )
                                  {
                                    v20 = v31;
                                    v21 = v32;
                                    add_wires__modelZsave95mongerZcommon_u4139(a4 + 8, &v20);
                                  }
                                }
LABEL_89:
                                v35 = 536i64;
                                v36 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
                                v20 = v31;
                                v21 = v32;
                                eqdestroy___modelZsave95mongerZcommon_u3872(&v20);
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
          }
        }
      }
    }
  }
  v35 = 1772i64;
  v36 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\times.nim";
  v20 = v48;
  v21 = v49;
  eqdestroy___pureZtimes_u2668(&v20);
  v20 = v50;
  v21 = v51;
  eqdestroy___pureZtimes_u2668(&v20);
  return popFrame_58();
}
