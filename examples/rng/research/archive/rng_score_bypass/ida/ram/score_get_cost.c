_QWORD *__fastcall get_cost__modelZscores_u2321(_QWORD *a1, __int64 a2)
{
  __int64 v2; // rdx
  unsigned __int64 *v3; // rdx
  unsigned __int64 v4; // rax
  __int64 v5; // rdx
  __int64 v6; // rdx
  __int64 v7; // rdx
  __int64 *v8; // rdx
  __int64 v9; // rax
  __int64 v10; // rdx
  __int64 *v11; // rdx
  __int64 v12; // rax
  __int64 v13; // rdx
  __int64 *v14; // rdx
  __int64 v15; // rax
  __int64 v16; // rdx
  __int64 *v17; // rdx
  __int64 v18; // rax
  __int64 v19; // rdx
  __int64 *v20; // rdx
  __int64 v21; // rax
  __int64 v22; // rdx
  __int64 *v23; // rdx
  __int64 v24; // rax
  __int64 v25; // rdx
  __int64 v26; // rdx
  __int64 v28; // [rsp+20h] [rbp-60h] BYREF
  __int64 v29; // [rsp+28h] [rbp-58h]
  __int64 v30; // [rsp+30h] [rbp-50h] BYREF
  void *v31; // [rsp+38h] [rbp-48h]
  char v32[1456]; // [rsp+40h] [rbp-40h] BYREF
  __int64 v33; // [rsp+5F0h] [rbp+570h]
  __int64 v34; // [rsp+5F8h] [rbp+578h]
  unsigned __int64 v35; // [rsp+608h] [rbp+588h]
  __int64 v36; // [rsp+610h] [rbp+590h]
  __int64 v37; // [rsp+618h] [rbp+598h]
  __int64 v38; // [rsp+628h] [rbp+5A8h]
  __int64 v39; // [rsp+630h] [rbp+5B0h]
  __int64 v40; // [rsp+638h] [rbp+5B8h]
  __int64 v41; // [rsp+640h] [rbp+5C0h]
  __int64 v42; // [rsp+648h] [rbp+5C8h]
  unsigned __int64 v43; // [rsp+658h] [rbp+5D8h]
  __int64 v44; // [rsp+660h] [rbp+5E0h]
  __int64 v45; // [rsp+668h] [rbp+5E8h]
  __int64 v46; // [rsp+670h] [rbp+5F0h]
  __int64 v47; // [rsp+678h] [rbp+5F8h]
  __int64 v48; // [rsp+680h] [rbp+600h]
  __int64 v49; // [rsp+688h] [rbp+608h]
  unsigned __int64 v50; // [rsp+690h] [rbp+610h]
  __int64 v51; // [rsp+698h] [rbp+618h]
  __int64 v52; // [rsp+6A0h] [rbp+620h]
  __int64 v53; // [rsp+6A8h] [rbp+628h]
  unsigned __int64 v54; // [rsp+6B0h] [rbp+630h]
  __int64 v55; // [rsp+6B8h] [rbp+638h]
  __int64 v56; // [rsp+6C0h] [rbp+640h]
  __int64 v57; // [rsp+6C8h] [rbp+648h]
  unsigned __int64 v58; // [rsp+6D8h] [rbp+658h]
  __int64 v59; // [rsp+6E0h] [rbp+660h]
  __int64 v60; // [rsp+6E8h] [rbp+668h]
  __int64 v61; // [rsp+6F0h] [rbp+670h]
  __int64 v62; // [rsp+6F8h] [rbp+678h]
  __int64 v63; // [rsp+700h] [rbp+680h]
  __int64 v64; // [rsp+708h] [rbp+688h]
  __int64 v65; // [rsp+710h] [rbp+690h]
  unsigned __int64 v66; // [rsp+718h] [rbp+698h]
  __int64 v67; // [rsp+720h] [rbp+6A0h]
  __int64 v68; // [rsp+728h] [rbp+6A8h]
  __int64 v69; // [rsp+730h] [rbp+6B0h]
  __int64 v70; // [rsp+738h] [rbp+6B8h]
  __int64 v71; // [rsp+740h] [rbp+6C0h]
  __int64 v72; // [rsp+748h] [rbp+6C8h]
  __int64 v73; // [rsp+750h] [rbp+6D0h]
  __int64 v74; // [rsp+758h] [rbp+6D8h]
  __int64 gate_cost__modelZscores_u2304; // [rsp+760h] [rbp+6E0h]
  __int64 delay_cost__modelZscores_u2316; // [rsp+768h] [rbp+6E8h]
  __int64 v77; // [rsp+770h] [rbp+6F0h]
  __int64 v78; // [rsp+778h] [rbp+6F8h]
  char v79[8]; // [rsp+780h] [rbp+700h] BYREF
  const char *v80; // [rsp+788h] [rbp+708h]
  __int64 v81; // [rsp+790h] [rbp+710h]
  const char *v82; // [rsp+798h] [rbp+718h]
  __int16 v83; // [rsp+7A0h] [rbp+720h]
  __int64 v84; // [rsp+7B0h] [rbp+730h]
  __int64 v85; // [rsp+7B8h] [rbp+738h]
  __int64 v86; // [rsp+7C0h] [rbp+740h]
  unsigned __int64 v87; // [rsp+7D0h] [rbp+750h]
  __int64 v88; // [rsp+7D8h] [rbp+758h]
  __int64 v89; // [rsp+7E0h] [rbp+760h] BYREF
  __int64 v90; // [rsp+7E8h] [rbp+768h]
  __int64 v91[2]; // [rsp+7F0h] [rbp+770h] BYREF
  __int64 v92[2]; // [rsp+800h] [rbp+780h] BYREF
  __int64 v93; // [rsp+810h] [rbp+790h]
  unsigned __int64 v94; // [rsp+818h] [rbp+798h]
  unsigned __int64 v95; // [rsp+820h] [rbp+7A0h]
  unsigned __int64 v96; // [rsp+828h] [rbp+7A8h]
  unsigned __int64 v97; // [rsp+830h] [rbp+7B0h]
  __int64 v98; // [rsp+838h] [rbp+7B8h]
  unsigned __int64 v99; // [rsp+840h] [rbp+7C0h]
  __int64 *v100; // [rsp+848h] [rbp+7C8h]
  const void *v101; // [rsp+850h] [rbp+7D0h]
  __int64 *v102; // [rsp+858h] [rbp+7D8h]
  unsigned __int8 v103; // [rsp+867h] [rbp+7E7h]
  _BYTE *v104; // [rsp+868h] [rbp+7E8h]
  bool v105; // [rsp+877h] [rbp+7F7h]
  unsigned __int64 v106; // [rsp+878h] [rbp+7F8h]
  unsigned __int64 v107; // [rsp+880h] [rbp+800h]
  unsigned __int64 v108; // [rsp+888h] [rbp+808h]

  v80 = "get_cost";
  v82 = "D:\\TuringComplete_Phu\\model\\scores.nim";
  v81 = 0i64;
  v83 = 0;
  nimFrame_74(v79);
  v104 = (_BYTE *)nimErrorFlag_72();
  nimZeroMem_54(&v89, 16i64);
  v81 = 513i64;
  v103 = *(_BYTE *)a2;
  v81 = 515i64;
  if ( ((TM__cWnRfAoMBYzrX9aW9aZjMzkg_3[v103 >> 3] >> (v103 & 7)) & 1) != 0 )
  {
    v81 = 516i64;
    v102 = 0i64;
    v102 = (__int64 *)X5BX5D___modelZscores_u1990(&DEFAULT_COMPONENT_SCORES__modelZscores_u1605, v103);
    if ( !*v104 )
    {
      v2 = v102[1];
      v77 = *v102;
      v78 = v2;
      v81 = 518i64;
      gate_cost__modelZscores_u2304 = get_gate_cost__modelZscores_u2304((unsigned __int8 *)a2, v77);
      if ( !*v104 )
      {
        v81 = 519i64;
        delay_cost__modelZscores_u2316 = get_delay_cost__modelZscores_u2316((unsigned __int8 *)a2, v78);
        if ( !*v104 )
        {
          v89 = gate_cost__modelZscores_u2304;
          v90 = delay_cost__modelZscores_u2316;
        }
      }
    }
    goto LABEL_87;
  }
  v81 = 522i64;
  v3 = (unsigned __int64 *)((char *)&component_costs__modelZscores_u10 + 16 * v103);
  v4 = *v3;
  v5 = v3[1];
  v87 = v4;
  v88 = v5;
  v81 = 523i64;
  if ( !v5 )
  {
    nimZeroMem_54(v32, 1448i64);
    v81 = 524i64;
    v101 = 0i64;
    v101 = (const void *)X5BX5D___modelZboardZprototype95list_u4239(
                           refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
                           v103);
    if ( !*v104 )
    {
      qmemcpy(v32, v101, 0x5A8ui64);
      v81 = 525i64;
      if ( v32[0] == 5 )
      {
        v81 = 526i64;
      }
      else
      {
        v81 = 527i64;
        v100 = 0i64;
        v100 = (__int64 *)X5BX5D___modelZscores_u1990(&DEFAULT_COMPONENT_SCORES__modelZscores_u1605, v103);
        if ( !*v104 )
        {
          v6 = v100[1];
          v73 = *v100;
          v74 = v6;
          v81 = 529i64;
          v71 = get_gate_cost__modelZscores_u2304((unsigned __int8 *)a2, v73);
          if ( !*v104 )
          {
            v81 = 530i64;
            v72 = get_delay_cost__modelZscores_u2316((unsigned __int8 *)a2, v74);
            if ( !*v104 )
            {
              v89 = v71;
              v90 = v72;
            }
          }
        }
      }
    }
    goto LABEL_87;
  }
  v81 = 533i64;
  v7 = *(_QWORD *)(a2 + 488);
  v84 = *(_QWORD *)(a2 + 480);
  v85 = v7;
  v86 = *(_QWORD *)(a2 + 496);
  v81 = 534i64;
  if ( (unsigned __int8)v84 == 2 )
  {
    v99 = 0i64;
    v98 = 0i64;
    v81 = 577i64;
    v82 = "D:\\TuringComplete_Phu\\model\\scores.nim";
    v38 = v87 + v88;
    if ( __OFADD__(v87, v88) )
    {
LABEL_81:
      raiseOverflow();
      goto LABEL_87;
    }
    v98 = v38;
    v82 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v106 = v87;
    v81 = 129i64;
    while ( (__int64)v106 < v98 )
    {
      v82 = "D:\\TuringComplete_Phu\\model\\scores.nim";
      v99 = v106;
      v81 = 578i64;
      if ( v106 > 0x270F )
      {
        raiseIndexError2(v99, 9999i64);
        goto LABEL_87;
      }
      v20 = (__int64 *)((char *)&component_cost_buffer__modelZscores_u12 + 16 * v99);
      v21 = *v20;
      v22 = v20[1];
      v36 = v21;
      v37 = v22;
      v81 = 579i64;
      v105 = 0;
      if ( (v84 & 7) != 2 )
      {
        dollar___modelZsave95mongerZcommon_u3503(v91, (unsigned __int8)v84);
        v30 = TM__cWnRfAoMBYzrX9aW9aZjMzkg_40;
        v31 = &TM__cWnRfAoMBYzrX9aW9aZjMzkg_39;
        v28 = v91[0];
        v29 = v91[1];
        raiseFieldErrorStr(&v30, &v28);
        goto LABEL_87;
      }
      v105 = v36 <= v85;
      if ( v36 <= v85 )
      {
        if ( (v84 & 7) != 2 )
        {
          dollar___modelZsave95mongerZcommon_u3503(v92, (unsigned __int8)v84);
          v30 = TM__cWnRfAoMBYzrX9aW9aZjMzkg_41;
          v31 = &TM__cWnRfAoMBYzrX9aW9aZjMzkg_39;
          v28 = v92[0];
          v29 = v92[1];
          raiseFieldErrorStr(&v30, &v28);
          goto LABEL_87;
        }
        v105 = v37 <= v86;
      }
      if ( v105 )
      {
        v81 = 581i64;
        v33 = get_gate_cost__modelZscores_u2304((unsigned __int8 *)a2, v36);
        if ( !*v104 )
        {
          v81 = 582i64;
          v34 = get_delay_cost__modelZscores_u2316((unsigned __int8 *)a2, v37);
          if ( !*v104 )
          {
            v89 = v33;
            v90 = v34;
          }
        }
        goto LABEL_87;
      }
      v81 = 131i64;
      v82 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v35 = v106 + 1;
      if ( __OFADD__(1i64, v106) )
        goto LABEL_81;
      v106 = v35;
    }
    v81 = 585i64;
    v82 = "D:\\TuringComplete_Phu\\model\\scores.nim";
    if ( v87 > 0x270F )
      goto LABEL_20;
    v23 = (__int64 *)((char *)&component_cost_buffer__modelZscores_u12 + 16 * v87);
    v24 = *v23;
    v25 = v23[1];
    v41 = v24;
    v42 = v25;
    v81 = 587i64;
    v39 = get_gate_cost__modelZscores_u2304((unsigned __int8 *)a2, v24);
    if ( !*v104 )
    {
      v81 = 588i64;
      v40 = get_delay_cost__modelZscores_u2316((unsigned __int8 *)a2, v42);
      if ( !*v104 )
      {
        v89 = v39;
        v90 = v40;
      }
    }
  }
  else
  {
    if ( (unsigned __int8)v84 > 2u )
      goto LABEL_87;
    if ( (_BYTE)v84 )
    {
      if ( (unsigned __int8)v84 != 1 )
        goto LABEL_87;
      v81 = 556i64;
      v55 = v87 + v88;
      if ( __OFADD__(v87, v88) )
        goto LABEL_81;
      v54 = v55 - 1;
      if ( __OFSUB__(v55, 1i64) )
        goto LABEL_81;
      if ( v54 > 0x270F )
      {
        raiseIndexError2(v54, 9999i64);
        goto LABEL_87;
      }
      v14 = (__int64 *)((char *)&component_cost_buffer__modelZscores_u12 + 16 * v54);
      v15 = *v14;
      v16 = v14[1];
      v56 = v15;
      v57 = v16;
      v81 = 558i64;
      v52 = get_gate_cost__modelZscores_u2304((unsigned __int8 *)a2, v15);
      if ( !*v104 )
      {
        v81 = 559i64;
        v53 = get_delay_cost__modelZscores_u2316((unsigned __int8 *)a2, v57);
        if ( !*v104 )
        {
          v97 = 0i64;
          v96 = 0i64;
          v81 = 562i64;
          v82 = "D:\\TuringComplete_Phu\\model\\scores.nim";
          v51 = v87 + v88;
          if ( __OFADD__(v87, v88) )
            goto LABEL_81;
          v50 = v51 - 2;
          if ( __OFSUB__(v51, 2i64) )
            goto LABEL_81;
          v96 = v50;
          v82 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v107 = v50;
          v81 = 34i64;
          while ( (__int64)v107 >= (__int64)v87 )
          {
            v82 = "D:\\TuringComplete_Phu\\model\\scores.nim";
            v97 = v107;
            v81 = 564i64;
            if ( v107 > 0x270F )
            {
              raiseIndexError2(v97, 9999i64);
              goto LABEL_87;
            }
            v17 = (__int64 *)((char *)&component_cost_buffer__modelZscores_u12 + 16 * v97);
            v18 = *v17;
            v19 = v17[1];
            v48 = v18;
            v49 = v19;
            v81 = 566i64;
            v44 = get_gate_cost__modelZscores_u2304((unsigned __int8 *)a2, v18);
            if ( *v104 )
              goto LABEL_87;
            v81 = 567i64;
            v45 = get_delay_cost__modelZscores_u2316((unsigned __int8 *)a2, v49);
            if ( *v104 )
              goto LABEL_87;
            v46 = v44;
            v47 = v45;
            v81 = 569i64;
            if ( v53 < v45 )
            {
              v81 = 570i64;
              v89 = v52;
              v90 = v53;
              goto LABEL_87;
            }
            v81 = 573i64;
            if ( v47 != v53 )
            {
              v30 = TM__cWnRfAoMBYzrX9aW9aZjMzkg_36;
              v31 = &TM__cWnRfAoMBYzrX9aW9aZjMzkg_35;
              failedAssertImpl__stdZassertions_u234(&v30);
              if ( *v104 )
                goto LABEL_87;
            }
            v52 = v46;
            v53 = v47;
            v81 = 39i64;
            v82 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
            v43 = v107 - 1;
            if ( __OFSUB__(v107, 1i64) )
              goto LABEL_37;
            v107 = v43;
          }
          v82 = "D:\\TuringComplete_Phu\\model\\scores.nim";
          v81 = 575i64;
          v89 = v52;
          v90 = v53;
        }
      }
    }
    else
    {
      v81 = 536i64;
      if ( v87 > 0x270F )
      {
LABEL_20:
        raiseIndexError2(v87, 9999i64);
        goto LABEL_87;
      }
      v8 = (__int64 *)((char *)&component_cost_buffer__modelZscores_u12 + 16 * v87);
      v9 = *v8;
      v10 = v8[1];
      v69 = v9;
      v70 = v10;
      v81 = 538i64;
      v67 = get_gate_cost__modelZscores_u2304((unsigned __int8 *)a2, v9);
      if ( !*v104 )
      {
        v81 = 539i64;
        v68 = get_delay_cost__modelZscores_u2316((unsigned __int8 *)a2, v70);
        if ( !*v104 )
        {
          v95 = 0i64;
          v94 = 0i64;
          v93 = 0i64;
          v81 = 541i64;
          v82 = "D:\\TuringComplete_Phu\\model\\scores.nim";
          v66 = v87 + 1;
          if ( __OFADD__(1i64, v87) )
            goto LABEL_81;
          v94 = v66;
          v81 = 541i64;
          v82 = "D:\\TuringComplete_Phu\\model\\scores.nim";
          v65 = v87 + v88;
          if ( __OFADD__(v87, v88) )
            goto LABEL_81;
          v93 = v65;
          v82 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v108 = v94;
          v81 = 129i64;
          while ( (__int64)v108 < v93 )
          {
            v82 = "D:\\TuringComplete_Phu\\model\\scores.nim";
            v95 = v108;
            v81 = 542i64;
            if ( v108 > 0x270F )
            {
              raiseIndexError2(v95, 9999i64);
              goto LABEL_87;
            }
            v11 = (__int64 *)((char *)&component_cost_buffer__modelZscores_u12 + 16 * v95);
            v12 = *v11;
            v13 = v11[1];
            v63 = v12;
            v64 = v13;
            v81 = 544i64;
            v59 = get_gate_cost__modelZscores_u2304((unsigned __int8 *)a2, v12);
            if ( *v104 )
              goto LABEL_87;
            v81 = 545i64;
            v60 = get_delay_cost__modelZscores_u2316((unsigned __int8 *)a2, v64);
            if ( *v104 )
              goto LABEL_87;
            v61 = v59;
            v62 = v60;
            v81 = 547i64;
            if ( v67 < v59 )
            {
              v81 = 548i64;
              v89 = v67;
              v90 = v68;
              goto LABEL_87;
            }
            v81 = 551i64;
            if ( v61 != v67 )
            {
              v30 = TM__cWnRfAoMBYzrX9aW9aZjMzkg_29;
              v31 = &TM__cWnRfAoMBYzrX9aW9aZjMzkg_28;
              failedAssertImpl__stdZassertions_u234(&v30);
              if ( *v104 )
                goto LABEL_87;
            }
            v67 = v61;
            v68 = v62;
            v81 = 131i64;
            v82 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
            v58 = v108 + 1;
            if ( __OFADD__(1i64, v108) )
            {
LABEL_37:
              raiseOverflow();
              goto LABEL_87;
            }
            v108 = v58;
          }
          v82 = "D:\\TuringComplete_Phu\\model\\scores.nim";
          v81 = 553i64;
          v89 = v67;
          v90 = v68;
        }
      }
    }
  }
LABEL_87:
  popFrame_74();
  v26 = v90;
  *a1 = v89;
  a1[1] = v26;
  return a1;
}
