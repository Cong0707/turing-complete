__int64 __fastcall complete_level__modelZutilities_u8913(signed __int64 *a1)
{
  void *v1; // rdx
  void *v2; // rdx
  void *v3; // rdx
  signed __int64 v4; // rax
  char v5; // dl
  bool v6; // of
  __int64 v7; // rax
  void *v8; // rdx
  void *v9; // rdx
  unsigned __int8 v10; // cl
  void *v11; // rdx
  void *v12; // rdx
  void *v13; // rdx
  _QWORD *v14; // rax
  __int64 v15; // rdx
  void *v16; // rdx
  void *v17; // rdx
  void *v18; // rdx
  void *v19; // rdx
  __int64 v21[4]; // [rsp+20h] [rbp-60h] BYREF
  __int64 v22; // [rsp+40h] [rbp-40h] BYREF
  void *v23; // [rsp+48h] [rbp-38h]
  __int64 v24; // [rsp+50h] [rbp-30h]
  void *v25; // [rsp+58h] [rbp-28h]
  __int64 v26; // [rsp+60h] [rbp-20h] BYREF
  char *v27; // [rsp+68h] [rbp-18h]
  __int64 v28; // [rsp+78h] [rbp-8h]
  __int64 v29; // [rsp+80h] [rbp+0h]
  void *v30; // [rsp+88h] [rbp+8h]
  __int64 v31; // [rsp+90h] [rbp+10h]
  __int64 v32; // [rsp+98h] [rbp+18h]
  __int64 v33; // [rsp+A0h] [rbp+20h]
  char v34[8]; // [rsp+B0h] [rbp+30h] BYREF
  const char *v35; // [rsp+B8h] [rbp+38h]
  __int64 v36; // [rsp+C0h] [rbp+40h]
  const char *v37; // [rsp+C8h] [rbp+48h]
  __int16 v38; // [rsp+D0h] [rbp+50h]
  char v39[24]; // [rsp+E0h] [rbp+60h] BYREF
  signed __int64 v40; // [rsp+F8h] [rbp+78h]
  unsigned __int64 v41; // [rsp+100h] [rbp+80h]
  __int64 v42; // [rsp+108h] [rbp+88h]
  char v43; // [rsp+120h] [rbp+A0h]
  _BYTE *v44; // [rsp+128h] [rbp+A8h]
  __int64 v45; // [rsp+130h] [rbp+B0h]
  __int64 v46; // [rsp+138h] [rbp+B8h]
  __int64 v47; // [rsp+140h] [rbp+C0h]
  __int64 v48; // [rsp+148h] [rbp+C8h]
  __int64 v49; // [rsp+150h] [rbp+D0h]
  __int64 v50; // [rsp+158h] [rbp+D8h]
  __int64 v51; // [rsp+160h] [rbp+E0h]
  __int64 v52; // [rsp+168h] [rbp+E8h]
  __int64 v53; // [rsp+170h] [rbp+F0h]
  __int64 v54; // [rsp+178h] [rbp+F8h]
  unsigned __int8 *v55; // [rsp+180h] [rbp+100h]
  __int64 v56; // [rsp+188h] [rbp+108h]
  __int64 level_score__modelZscores_u2620; // [rsp+190h] [rbp+110h]
  __int64 v58; // [rsp+198h] [rbp+118h]
  void *v59; // [rsp+1A0h] [rbp+120h]
  signed __int64 v60; // [rsp+1A8h] [rbp+128h]
  __int64 v61; // [rsp+1B0h] [rbp+130h]
  __int64 v62; // [rsp+1B8h] [rbp+138h]
  _BYTE *v63; // [rsp+1C0h] [rbp+140h]
  char updated; // [rsp+1CFh] [rbp+14Fh]
  __int64 v65; // [rsp+1D0h] [rbp+150h]
  bool v66; // [rsp+1DFh] [rbp+15Fh]
  __int64 v67; // [rsp+1E0h] [rbp+160h]
  char v68; // [rsp+1EDh] [rbp+16Dh]
  char v69; // [rsp+1EEh] [rbp+16Eh]
  unsigned __int8 v70; // [rsp+1EFh] [rbp+16Fh]

  v35 = "complete_level";
  v37 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  v36 = 0i64;
  v38 = 0;
  nimFrame_145(v34);
  v63 = (_BYTE *)nimErrorFlag_141();
  v70 = 0;
  nimZeroMem_118(v39, 72i64);
  v36 = 859i64;
  v37 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  v62 = 0i64;
  v1 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
  v22 = *refptr_loaded_level__modelZmodel95types_u830;
  v23 = v1;
  v62 = X5BX5D___modelZcampaigns_u16467(refptr_level_progress__modelZmodel95types_u825, &v22);
  if ( *v63 )
    goto LABEL_47;
  v36 = 419i64;
  v37 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
  eqcopy___modelZboardZschematics_u2147(v39, v62);
  v36 = 861i64;
  v37 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  v68 = v43;
  if ( !v43 )
    v68 = v39[0] == 0;
  v69 = v68;
  v36 = 863i64;
  v61 = 0i64;
  v2 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
  v22 = *refptr_loaded_level__modelZmodel95types_u830;
  v23 = v2;
  v61 = X5BX5D___modelZboardZboard_u17368(refptr_campaign__modelZmodel95types_u817, &v22);
  if ( *v63 )
    goto LABEL_47;
  if ( !*(_BYTE *)(v61 + 88) )
  {
    v36 = 864i64;
    v60 = *a1;
    v36 = 865i64;
    v59 = (void *)a1[1];
    v67 = 1i64;
    v36 = 868i64;
    v58 = 0i64;
    v3 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
    v22 = *refptr_loaded_level__modelZmodel95types_u830;
    v23 = v3;
    v58 = X5BX5D___modelZboardZboard_u17368(refptr_campaign__modelZmodel95types_u817, &v22);
    if ( *v63 )
    {
LABEL_47:
      eqdestroy___modelZboardZschematics_u2144(v39);
      goto LABEL_48;
    }
    if ( *(_BYTE *)(v58 + 64) == 3 )
    {
      v36 = 869i64;
      v4 = a1[88];
      v5 = 0;
      v6 = __OFADD__(1i64, v4);
      v7 = v4 + 1;
      if ( v6 )
        v5 = 1;
      v28 = v7;
      if ( (v5 & 1) != 0 )
      {
        raiseOverflow();
        goto LABEL_47;
      }
      v67 = v28;
    }
    v36 = 871i64;
    level_score__modelZscores_u2620 = get_level_score__modelZscores_u2620(v40, v41, v42);
    if ( *v63 )
      goto LABEL_47;
    v36 = 874i64;
    v56 = get_level_score__modelZscores_u2620(v60, (unsigned __int64)v59, v67);
    if ( *v63 )
      goto LABEL_47;
    v66 = v56 < level_score__modelZscores_u2620;
    v36 = 878i64;
    if ( v43 == 1 )
    {
      v36 = 880i64;
      v66 = 1;
    }
    v31 = v60;
    v32 = (__int64)v59;
    v33 = v67;
    v29 = v60;
    v30 = v59;
    v26 = 0i64;
    v27 = 0i64;
    v55 = 0i64;
    v36 = 884i64;
    v37 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
    v54 = 0i64;
    v8 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
    v22 = *refptr_loaded_level__modelZmodel95types_u830;
    v23 = v8;
    v54 = X5BX5D___modelZboardZboard_u17368(refptr_campaign__modelZmodel95types_u817, &v22);
    if ( !*v63 )
    {
      v36 = 635i64;
      v37 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
      v9 = *(void **)(v54 + 288);
      v22 = *(_QWORD *)(v54 + 280);
      v23 = v9;
      eqcopy___modelZmodel95types_u2181(&v26, &v22);
      v37 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      v65 = 0i64;
      v53 = v26;
      v52 = v26;
      v36 = 251i64;
      while ( v65 < v52 )
      {
        v36 = 884i64;
        v37 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
        if ( v65 < 0 || v65 >= v26 )
        {
          raiseIndexError2(v65, v26 - 1);
          break;
        }
        v55 = (unsigned __int8 *)&v27[v65 + 8];
        v36 = 885i64;
        v10 = *v55;
        v22 = v29;
        v23 = v30;
        add_cost__modelZscores_u2110(v10, &v22);
        if ( !*v63 )
        {
          v37 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          ++v65;
          v36 = 254i64;
          v51 = v26;
          if ( v26 == v52 )
            continue;
          v22 = TM__8FyyixzftvDEeBWCL79bP9aA_143;
          v23 = &TM__8FyyixzftvDEeBWCL79bP9aA_31;
          failedAssertImpl__stdZassertions_u234(&v22);
          if ( !*v63 )
            continue;
        }
        break;
      }
    }
    v36 = 635i64;
    v37 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
    v22 = v26;
    v23 = v27;
    eqdestroy___modelZmodel95types_u2178(&v22);
    if ( *v63 )
      goto LABEL_47;
    v36 = 887i64;
    v37 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
    v50 = 0i64;
    v11 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
    v22 = *refptr_loaded_level__modelZmodel95types_u830;
    v23 = v11;
    v50 = X5BX5D___modelZboardZboard_u17368(refptr_campaign__modelZmodel95types_u817, &v22);
    if ( *v63 )
      goto LABEL_47;
    if ( *(_BYTE *)(v50 + 64) == 3 )
    {
      if ( v66 )
      {
        v36 = 894i64;
        v37 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
        v48 = 0i64;
        v13 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
        v22 = *refptr_loaded_level__modelZmodel95types_u830;
        v23 = v13;
        v48 = X5BX5D___modelZcampaigns_u16467(refptr_level_progress__modelZmodel95types_u825, &v22);
        if ( *v63 )
          goto LABEL_47;
        v25 = 0i64;
        v24 = 1i64;
        v14 = (_QWORD *)newSeqPayload(1i64, 24i64, 8i64);
        v25 = v14;
        v15 = v32;
        v14[1] = v31;
        v14[2] = v15;
        v14[3] = v33;
        v36 = 636i64;
        v37 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
        v22 = v24;
        v23 = v25;
        eqsink___modelZmodel95types_u4153(v48 + 48, &v22);
      }
    }
    else
    {
      v36 = 889i64;
      updated = v69;
      if ( !v69 )
      {
        v36 = 891i64;
        v49 = 0i64;
        v12 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
        v22 = *refptr_loaded_level__modelZmodel95types_u830;
        v23 = v12;
        v49 = X5BX5D___modelZcampaigns_u16467(refptr_level_progress__modelZmodel95types_u825, &v22);
        if ( *v63 )
          goto LABEL_47;
        v36 = 890i64;
        v21[0] = v31;
        v21[1] = v32;
        v21[2] = v33;
        updated = update_efficient_frontier__modelZutilities_u8881((_QWORD *)(v49 + 48), v21);
        if ( *v63 )
          goto LABEL_47;
      }
      v69 = updated;
    }
    v36 = 896i64;
    v37 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
    if ( v66 )
    {
      v69 = 1;
      v36 = 898i64;
      v47 = 0i64;
      v16 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
      v22 = *refptr_loaded_level__modelZmodel95types_u830;
      v23 = v16;
      v47 = X5BX5D___modelZcampaigns_u16467(refptr_level_progress__modelZmodel95types_u825, &v22);
      if ( *v63 )
        goto LABEL_47;
      *(_QWORD *)(v47 + 24) = v60;
      v36 = 899i64;
      v46 = 0i64;
      v17 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
      v22 = *refptr_loaded_level__modelZmodel95types_u830;
      v23 = v17;
      v46 = X5BX5D___modelZcampaigns_u16467(refptr_level_progress__modelZmodel95types_u825, &v22);
      if ( *v63 )
        goto LABEL_47;
      *(_QWORD *)(v46 + 32) = v59;
      v36 = 900i64;
      v45 = 0i64;
      v18 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
      v22 = *refptr_loaded_level__modelZmodel95types_u830;
      v23 = v18;
      v45 = X5BX5D___modelZcampaigns_u16467(refptr_level_progress__modelZmodel95types_u825, &v22);
      if ( *v63 )
        goto LABEL_47;
      *(_QWORD *)(v45 + 40) = v67;
    }
  }
  v36 = 902i64;
  v44 = 0i64;
  v19 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
  v22 = *refptr_loaded_level__modelZmodel95types_u830;
  v23 = v19;
  v44 = (_BYTE *)X5BX5D___modelZcampaigns_u16467(refptr_level_progress__modelZmodel95types_u825, &v22);
  if ( *v63 )
    goto LABEL_47;
  *v44 = 1;
  v36 = 904i64;
  if ( v69 != 1 )
    goto LABEL_47;
  v36 = 905i64;
  save_level_data__modelZutilities_u5679();
  if ( *v63 )
    goto LABEL_47;
  v70 = 1;
  v36 = 419i64;
  v37 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
  eqdestroy___modelZboardZschematics_u2144(v39);
LABEL_48:
  popFrame_145();
  return v70;
}
