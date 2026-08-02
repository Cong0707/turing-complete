__int64 atmmodelatsboardatsprototype_listdotnim_Init000()
{
  __int64 v1; // [rsp+0h] [rbp-80h] BYREF
  __int64 v2; // [rsp+20h] [rbp-60h] BYREF
  _QWORD *v3; // [rsp+28h] [rbp-58h]
  __int64 v4; // [rsp+30h] [rbp-50h] BYREF
  void *v5; // [rsp+38h] [rbp-48h]
  __int64 v6; // [rsp+40h] [rbp-40h]
  const char *v7; // [rsp+58h] [rbp-28h]
  __int64 v8; // [rsp+60h] [rbp-20h]
  const char *v9; // [rsp+68h] [rbp-18h]
  __int16 v10; // [rsp+70h] [rbp-10h]
  __int64 v11; // [rsp+80h] [rbp+0h] BYREF
  _QWORD *v12; // [rsp+88h] [rbp+8h]
  __int64 v13; // [rsp+90h] [rbp+10h]
  _QWORD *v14; // [rsp+98h] [rbp+18h]
  __int64 v15; // [rsp+A0h] [rbp+20h] BYREF
  _QWORD *v16; // [rsp+A8h] [rbp+28h]
  __int64 v17; // [rsp+B0h] [rbp+30h] BYREF
  _QWORD *v18; // [rsp+B8h] [rbp+38h]
  __int64 v19; // [rsp+C0h] [rbp+40h] BYREF
  _QWORD *v20; // [rsp+C8h] [rbp+48h]
  __int64 v21; // [rsp+D0h] [rbp+50h]
  _QWORD *v22; // [rsp+D8h] [rbp+58h]
  __int64 v23; // [rsp+E0h] [rbp+60h] BYREF
  _QWORD *v24; // [rsp+E8h] [rbp+68h]
  __int64 v25; // [rsp+F0h] [rbp+70h] BYREF
  _QWORD *v26; // [rsp+F8h] [rbp+78h]
  __int64 v27; // [rsp+100h] [rbp+80h]
  _QWORD *v28; // [rsp+108h] [rbp+88h]
  __int64 v29; // [rsp+110h] [rbp+90h] BYREF
  _QWORD *v30; // [rsp+118h] [rbp+98h]
  __int64 v31; // [rsp+120h] [rbp+A0h] BYREF
  _QWORD *v32; // [rsp+128h] [rbp+A8h]
  __int64 v33; // [rsp+130h] [rbp+B0h]
  _QWORD *v34; // [rsp+138h] [rbp+B8h]
  __int64 v35; // [rsp+140h] [rbp+C0h] BYREF
  _QWORD *v36; // [rsp+148h] [rbp+C8h]
  __int64 v37; // [rsp+158h] [rbp+D8h]
  __int64 v38; // [rsp+160h] [rbp+E0h]
  __int16 v39; // [rsp+16Eh] [rbp+EEh]
  __int64 v40; // [rsp+170h] [rbp+F0h]
  __int64 v41; // [rsp+178h] [rbp+F8h]
  __int64 v42; // [rsp+180h] [rbp+100h]
  __int64 v43; // [rsp+188h] [rbp+108h]
  __int64 v44; // [rsp+190h] [rbp+110h]
  __int64 v45; // [rsp+198h] [rbp+118h]
  __int64 v46; // [rsp+1A0h] [rbp+120h]
  __int64 v47; // [rsp+1A8h] [rbp+128h]
  __int64 v48; // [rsp+1B0h] [rbp+130h]
  char v49; // [rsp+1BFh] [rbp+13Fh]
  __int64 v50; // [rsp+1C0h] [rbp+140h]
  unsigned __int64 v51; // [rsp+1C8h] [rbp+148h]
  __int64 v52; // [rsp+1D0h] [rbp+150h]
  _BYTE *v53; // [rsp+1D8h] [rbp+158h]
  __int64 v54; // [rsp+1E0h] [rbp+160h]
  __int64 v55; // [rsp+1E8h] [rbp+168h]
  __int64 v56; // [rsp+1F0h] [rbp+170h]
  __int64 v57; // [rsp+1F8h] [rbp+178h]

  v7 = "prototype_list";
  v9 = "D:\\TuringComplete_Phu\\model\\board\\prototype_list.nim";
  v8 = 0i64;
  v10 = 0;
  nimFrame_68(&v1 + 10);
  v53 = (_BYTE *)nimErrorFlag_66();
  v8 = 767i64;
  v9 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
  v4 = PROTOTYPES__modelZboardZprototype95list_u3752;
  v5 = &TM__wUqL1Kpuf69c1ieeyVFJbBQ_3391;
  v6 = 125i64;
  v52 = len__modelZboardZprototype95list_u3797(&v4);
  if ( !*v53 )
  {
    v51 = 0i64;
    v50 = 255i64;
    v9 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v57 = 0i64;
    v8 = 97i64;
    while ( v57 <= v50 )
    {
      v9 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
      v51 = v57;
      v8 = 769i64;
      if ( v57 < 0 || (__int64)v51 >= 256 )
      {
LABEL_10:
        raiseIndexError2(v51, 255i64);
        goto LABEL_86;
      }
      v49 = 0;
      v49 = isFilled__pureZcollectionsZtables_u31_1(*((_QWORD *)&TM__wUqL1Kpuf69c1ieeyVFJbBQ_3391 + 183 * v51 + 1));
      if ( *v53 )
        goto LABEL_86;
      if ( v49 == 1 )
      {
        v8 = 2376i64;
        v9 = "D:\\TuringComplete_Phu\\model\\board\\prototype_list.nim";
        if ( v51 >= 0x100 )
          goto LABEL_10;
        kind__modelZboardZprototype95list_u4098 = *((_BYTE *)&TM__wUqL1Kpuf69c1ieeyVFJbBQ_3391 + 1464 * v51 + 16);
        v8 = 170i64;
        v9 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        eqcopy___modelZboardZprototype95list_u3242(
          &prototype__modelZboardZprototype95list_u4099,
          (char *)&TM__wUqL1Kpuf69c1ieeyVFJbBQ_3391 + 1464 * v51 + 24);
        pin__modelZboardZprototype95list_u4121 = 0i64;
        v9 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v56 = 0i64;
        v48 = qword_140C3E4E0;
        v47 = qword_140C3E4E0;
        v8 = 251i64;
        while ( v56 < v47 )
        {
          v8 = 2377i64;
          v9 = "D:\\TuringComplete_Phu\\model\\board\\prototype_list.nim";
          if ( v56 < 0 || v56 >= qword_140C3E4E0 )
          {
            raiseIndexError2(v56, qword_140C3E4E0 - 1);
            goto LABEL_86;
          }
          pin__modelZboardZprototype95list_u4121 = qword_140C3E4E8 + 56 * v56 + 8;
          v8 = 2378i64;
          if ( *(_BYTE *)(qword_140C3E4E8 + 56 * v56 + 8) && *(_BYTE *)pin__modelZboardZprototype95list_u4121 != 4 )
          {
            v35 = 0i64;
            v36 = 0i64;
            v33 = 0i64;
            v34 = 0i64;
            v31 = 0i64;
            v32 = 0i64;
            dollar___modelZsave95mongerZcommon_u132(&v35, (unsigned __int8)kind__modelZboardZprototype95list_u4098);
            rawNewString(&v2, v35 + 102);
            v31 = v2;
            v32 = v3;
            v2 = TM__wUqL1Kpuf69c1ieeyVFJbBQ_3393;
            v3 = &TM__wUqL1Kpuf69c1ieeyVFJbBQ_3392;
            appendString_19(&v31, &v2);
            v2 = v35;
            v3 = v36;
            appendString_19(&v31, &v2);
            v33 = v31;
            v34 = v32;
            v2 = v31;
            v3 = v32;
            failedAssertImpl__stdZassertions_u234(&v2);
            if ( *v53 )
              goto LABEL_86;
            v8 = 394i64;
            v9 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v34 && (*v34 & 0x4000000000000000i64) == 0 )
              deallocShared(v34);
            if ( v36 && (*v36 & 0x4000000000000000i64) == 0 )
              deallocShared(v36);
          }
          v9 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          ++v56;
          v8 = 254i64;
          v46 = qword_140C3E4E0;
          if ( qword_140C3E4E0 != v47 )
          {
            v2 = TM__wUqL1Kpuf69c1ieeyVFJbBQ_3396;
            v3 = &TM__wUqL1Kpuf69c1ieeyVFJbBQ_3395;
            failedAssertImpl__stdZassertions_u234(&v2);
            if ( *v53 )
              goto LABEL_86;
          }
        }
        pin__modelZboardZprototype95list_u4138 = 0i64;
        v55 = 0i64;
        v45 = qword_140C3E4F0;
        v44 = qword_140C3E4F0;
        v8 = 251i64;
        while ( v55 < v44 )
        {
          v8 = 2379i64;
          v9 = "D:\\TuringComplete_Phu\\model\\board\\prototype_list.nim";
          if ( v55 < 0 || v55 >= qword_140C3E4F0 )
          {
            raiseIndexError2(v55, qword_140C3E4F0 - 1);
            goto LABEL_86;
          }
          pin__modelZboardZprototype95list_u4138 = qword_140C3E4F8 + 56 * v55 + 8;
          v8 = 2380i64;
          if ( *(_BYTE *)(qword_140C3E4F8 + 56 * v55 + 8) != 1 )
          {
            v29 = 0i64;
            v30 = 0i64;
            v27 = 0i64;
            v28 = 0i64;
            v25 = 0i64;
            v26 = 0i64;
            dollar___modelZsave95mongerZcommon_u132(&v29, (unsigned __int8)kind__modelZboardZprototype95list_u4098);
            rawNewString(&v2, v29 + 93);
            v25 = v2;
            v26 = v3;
            v2 = TM__wUqL1Kpuf69c1ieeyVFJbBQ_3398;
            v3 = &TM__wUqL1Kpuf69c1ieeyVFJbBQ_3397;
            appendString_19(&v25, &v2);
            v2 = v29;
            v3 = v30;
            appendString_19(&v25, &v2);
            v27 = v25;
            v28 = v26;
            v2 = v25;
            v3 = v26;
            failedAssertImpl__stdZassertions_u234(&v2);
            if ( *v53 )
              goto LABEL_86;
            v8 = 394i64;
            v9 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v28 && (*v28 & 0x4000000000000000i64) == 0 )
              deallocShared(v28);
            if ( v30 && (*v30 & 0x4000000000000000i64) == 0 )
              deallocShared(v30);
          }
          v9 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          ++v55;
          v8 = 254i64;
          v43 = qword_140C3E4F0;
          if ( qword_140C3E4F0 != v44 )
          {
            v2 = TM__wUqL1Kpuf69c1ieeyVFJbBQ_3399;
            v3 = &TM__wUqL1Kpuf69c1ieeyVFJbBQ_3395;
            failedAssertImpl__stdZassertions_u234(&v2);
            if ( *v53 )
              goto LABEL_86;
          }
        }
        pin__modelZboardZprototype95list_u4154 = 0i64;
        v54 = 0i64;
        v42 = qword_140C3E500;
        v41 = qword_140C3E500;
        v8 = 251i64;
        while ( v54 < v41 )
        {
          v8 = 2381i64;
          v9 = "D:\\TuringComplete_Phu\\model\\board\\prototype_list.nim";
          if ( v54 < 0 || v54 >= qword_140C3E500 )
          {
            raiseIndexError2(v54, qword_140C3E500 - 1);
            goto LABEL_86;
          }
          pin__modelZboardZprototype95list_u4154 = qword_140C3E508 + 56 * v54 + 8;
          v8 = 2382i64;
          if ( *(_BYTE *)(qword_140C3E508 + 56 * v54 + 8) != 2
            && *(_BYTE *)pin__modelZboardZprototype95list_u4154 != 3
            && *(_BYTE *)pin__modelZboardZprototype95list_u4154 != 4 )
          {
            v23 = 0i64;
            v24 = 0i64;
            v21 = 0i64;
            v22 = 0i64;
            v19 = 0i64;
            v20 = 0i64;
            dollar___modelZsave95mongerZcommon_u132(&v23, (unsigned __int8)kind__modelZboardZprototype95list_u4098);
            rawNewString(&v2, v23 + 117);
            v19 = v2;
            v20 = v3;
            v2 = TM__wUqL1Kpuf69c1ieeyVFJbBQ_3401;
            v3 = &TM__wUqL1Kpuf69c1ieeyVFJbBQ_3400;
            appendString_19(&v19, &v2);
            v2 = v23;
            v3 = v24;
            appendString_19(&v19, &v2);
            v21 = v19;
            v22 = v20;
            v2 = v19;
            v3 = v20;
            failedAssertImpl__stdZassertions_u234(&v2);
            if ( *v53 )
              goto LABEL_86;
            v8 = 394i64;
            v9 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v22 && (*v22 & 0x4000000000000000i64) == 0 )
              deallocShared(v22);
            if ( v24 && (*v24 & 0x4000000000000000i64) == 0 )
              deallocShared(v24);
          }
          v9 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          ++v54;
          v8 = 254i64;
          v40 = qword_140C3E500;
          if ( qword_140C3E500 != v41 )
          {
            v2 = TM__wUqL1Kpuf69c1ieeyVFJbBQ_3402;
            v3 = &TM__wUqL1Kpuf69c1ieeyVFJbBQ_3395;
            failedAssertImpl__stdZassertions_u234(&v2);
            if ( *v53 )
              goto LABEL_86;
          }
        }
        current_max__modelZboardZprototype95list_u4167 = 0;
        v8 = 2384i64;
        v9 = "D:\\TuringComplete_Phu\\model\\board\\prototype_list.nim";
        v39 = 0;
        v2 = qword_140C3E4C8;
        v3 = (_QWORD *)qword_140C3E4D0;
        v39 = max_radius__modelZsave95mongerZcommon_u4545(&v2);
        if ( *v53 )
          goto LABEL_86;
        current_max__modelZboardZprototype95list_u4167 = v39;
        v8 = 2386i64;
        if ( word_140C3E4D8 != v39 )
        {
          v17 = 0i64;
          v18 = 0i64;
          v15 = 0i64;
          v16 = 0i64;
          v13 = 0i64;
          v14 = 0i64;
          v11 = 0i64;
          v12 = 0i64;
          dollar___modelZsave95mongerZcommon_u132(&v17, (unsigned __int8)kind__modelZboardZprototype95list_u4098);
          dollar___systemZdollars_u24(&v15, (unsigned int)current_max__modelZboardZprototype95list_u4167);
          if ( *v53 )
            goto LABEL_86;
          rawNewString(&v2, v17 + v15 + 115);
          v11 = v2;
          v12 = v3;
          v2 = TM__wUqL1Kpuf69c1ieeyVFJbBQ_3404;
          v3 = &TM__wUqL1Kpuf69c1ieeyVFJbBQ_3403;
          appendString_19(&v11, &v2);
          v2 = v17;
          v3 = v18;
          appendString_19(&v11, &v2);
          v2 = TM__wUqL1Kpuf69c1ieeyVFJbBQ_3406;
          v3 = &TM__wUqL1Kpuf69c1ieeyVFJbBQ_3405;
          appendString_19(&v11, &v2);
          v2 = v15;
          v3 = v16;
          appendString_19(&v11, &v2);
          v2 = TM__wUqL1Kpuf69c1ieeyVFJbBQ_3408;
          v3 = &TM__wUqL1Kpuf69c1ieeyVFJbBQ_3407;
          appendString_19(&v11, &v2);
          v13 = v11;
          v14 = v12;
          v2 = v11;
          v3 = v12;
          failedAssertImpl__stdZassertions_u234(&v2);
          if ( *v53 )
            goto LABEL_86;
          v8 = 394i64;
          v9 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v14 && (*v14 & 0x4000000000000000i64) == 0 )
            deallocShared(v14);
          if ( v16 && (*v16 & 0x4000000000000000i64) == 0 )
            deallocShared(v16);
          if ( v18 && (*v18 & 0x4000000000000000i64) == 0 )
            deallocShared(v18);
        }
        v8 = 771i64;
        v9 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
        v38 = 0i64;
        v4 = PROTOTYPES__modelZboardZprototype95list_u3752;
        v5 = &TM__wUqL1Kpuf69c1ieeyVFJbBQ_3391;
        v6 = 125i64;
        v38 = len__modelZboardZprototype95list_u3797(&v4);
        if ( *v53 )
          goto LABEL_86;
        if ( v38 != v52 )
        {
          v2 = TM__wUqL1Kpuf69c1ieeyVFJbBQ_3410;
          v3 = &TM__wUqL1Kpuf69c1ieeyVFJbBQ_3409;
          failedAssertImpl__stdZassertions_u234(&v2);
          if ( *v53 )
            goto LABEL_86;
        }
      }
      v8 = 102i64;
      v9 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v37 = v57 + 1;
      if ( __OFADD__(1i64, v57) )
      {
        raiseOverflow();
        goto LABEL_86;
      }
      v57 = v37;
    }
    v8 = 170i64;
    v9 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    eqdestroy___modelZboardZprototype95list_u3239(&prototype__modelZboardZprototype95list_u4099);
  }
LABEL_86:
  nimTestErrorFlag();
  return popFrame_68();
}
