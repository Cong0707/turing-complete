__int64 __fastcall insert_cost__modelZscores_u49(unsigned __int8 a1, __int64 *a2)
{
  __int64 v2; // rax
  __int64 v3; // rdx
  __int64 v4; // rdx
  __int64 v5; // r8
  __int64 *v6; // rdx
  __int64 v7; // rax
  __int64 v8; // rdx
  __int64 v9; // rax
  char v10; // dl
  bool v11; // of
  __int64 v12; // rax
  __int64 v13; // rdx
  __int64 v14; // r8
  __int64 *v15; // rdx
  __int64 v16; // rax
  __int64 v17; // rdx
  __int64 v18; // rdx
  __int64 v19; // r8
  void *v20; // rdx
  __int64 v21; // rax
  char v22; // dl
  __int64 v23; // rax
  __int64 v25; // [rsp+20h] [rbp-60h] BYREF
  void *v26; // [rsp+28h] [rbp-58h]
  __int64 v27; // [rsp+30h] [rbp-50h]
  void *v28; // [rsp+38h] [rbp-48h]
  __int64 v29; // [rsp+48h] [rbp-38h]
  __int64 v30; // [rsp+50h] [rbp-30h]
  unsigned __int64 v31; // [rsp+58h] [rbp-28h]
  __int64 v32; // [rsp+60h] [rbp-20h]
  unsigned __int64 v33; // [rsp+68h] [rbp-18h]
  __int64 v34; // [rsp+70h] [rbp-10h]
  __int64 v35; // [rsp+78h] [rbp-8h]
  __int64 v36; // [rsp+80h] [rbp+0h]
  __int64 v37; // [rsp+88h] [rbp+8h]
  unsigned __int64 v38; // [rsp+90h] [rbp+10h]
  __int64 v39; // [rsp+98h] [rbp+18h]
  __int64 v40; // [rsp+A0h] [rbp+20h]
  unsigned __int64 v41; // [rsp+A8h] [rbp+28h]
  __int64 v42; // [rsp+B0h] [rbp+30h]
  unsigned __int64 v43; // [rsp+B8h] [rbp+38h]
  __int64 v44; // [rsp+C0h] [rbp+40h]
  __int64 v45; // [rsp+C8h] [rbp+48h]
  __int64 v46; // [rsp+D0h] [rbp+50h]
  __int64 v47; // [rsp+D8h] [rbp+58h]
  char v48[8]; // [rsp+E0h] [rbp+60h] BYREF
  const char *v49; // [rsp+E8h] [rbp+68h]
  __int64 v50; // [rsp+F0h] [rbp+70h]
  const char *v51; // [rsp+F8h] [rbp+78h]
  __int16 v52; // [rsp+100h] [rbp+80h]
  char v53; // [rsp+116h] [rbp+96h]
  unsigned __int8 v54; // [rsp+117h] [rbp+97h]
  __int64 v55; // [rsp+118h] [rbp+98h]
  __int64 v56; // [rsp+120h] [rbp+A0h]
  unsigned __int64 v57; // [rsp+128h] [rbp+A8h]
  char v58; // [rsp+136h] [rbp+B6h]
  unsigned __int8 v59; // [rsp+137h] [rbp+B7h]
  __int64 v60; // [rsp+138h] [rbp+B8h]
  unsigned __int64 v61; // [rsp+140h] [rbp+C0h]
  __int64 v62; // [rsp+148h] [rbp+C8h]
  __int64 v63; // [rsp+150h] [rbp+D0h]
  __int64 inserted; // [rsp+158h] [rbp+D8h]
  __int64 v65; // [rsp+160h] [rbp+E0h]
  _BYTE *v66; // [rsp+168h] [rbp+E8h]
  __int64 v67; // [rsp+170h] [rbp+F0h]
  __int64 v68; // [rsp+178h] [rbp+F8h]
  __int64 v69; // [rsp+180h] [rbp+100h]
  __int64 v70; // [rsp+188h] [rbp+108h]

  v2 = *a2;
  v3 = a2[1];
  v27 = v2;
  v28 = (void *)v3;
  v49 = "insert_cost";
  v51 = "D:\\TuringComplete_Phu\\model\\scores.nim";
  v50 = 0i64;
  v52 = 0;
  nimFrame_74(v48);
  v66 = (_BYTE *)nimErrorFlag_72();
  v50 = 68i64;
  v65 = qword_1467664A8[2 * a1];
  v50 = 69i64;
  v25 = v27;
  v26 = v28;
  inserted = insert_cost__modelZscores_u13((unsigned __int64 *)&component_costs__modelZscores_u10 + 2 * a1, &v25);
  if ( !*v66 )
  {
    v50 = 70i64;
    v63 = qword_1467664A8[2 * a1];
    v50 = 72i64;
    if ( inserted == -1 )
      goto LABEL_7;
    v50 = 73i64;
    v47 = v65 + 1;
    if ( __OFADD__(1i64, v65) )
    {
LABEL_49:
      raiseOverflow();
      return popFrame_74();
    }
    if ( v63 == v47
      || (v25 = TM__cWnRfAoMBYzrX9aW9aZjMzkg_74,
          v26 = &TM__cWnRfAoMBYzrX9aW9aZjMzkg_73,
          failedAssertImpl__stdZassertions_u234(&v25),
          !*v66) )
    {
LABEL_7:
      v50 = 76i64;
      if ( v63 >= v65 )
      {
        v50 = 84i64;
        v51 = "D:\\TuringComplete_Phu\\model\\scores.nim";
        if ( v65 < v63 )
        {
          v50 = 85i64;
          v36 = v63 - 1;
          if ( __OFSUB__(v63, 1i64) )
            goto LABEL_49;
          if ( v65 == v36
            || (v25 = TM__cWnRfAoMBYzrX9aW9aZjMzkg_85,
                v26 = &TM__cWnRfAoMBYzrX9aW9aZjMzkg_84,
                failedAssertImpl__stdZassertions_u234(&v25),
                !*v66) )
          {
            v50 = 87i64;
            if ( inserted != -1
              || (v25 = TM__cWnRfAoMBYzrX9aW9aZjMzkg_87,
                  v26 = &TM__cWnRfAoMBYzrX9aW9aZjMzkg_86,
                  failedAssertImpl__stdZassertions_u234(&v25),
                  !*v66) )
            {
              v57 = 0i64;
              v56 = 0i64;
              v55 = 0i64;
              v50 = 90i64;
              v51 = "D:\\TuringComplete_Phu\\model\\scores.nim";
              v35 = component_cost_buffer_len__modelZscores_u11 - 1;
              if ( __OFSUB__(component_cost_buffer_len__modelZscores_u11, 1i64) )
                goto LABEL_49;
              v56 = v35;
              v50 = 90i64;
              v51 = "D:\\TuringComplete_Phu\\model\\scores.nim";
              v13 = *((_QWORD *)&component_costs__modelZscores_u10 + 2 * a1);
              v34 = v13 + inserted;
              if ( __OFADD__(v13, inserted) )
                goto LABEL_49;
              v55 = v34;
              v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
              v68 = v56;
              v50 = 34i64;
              while ( v55 <= v68 )
              {
                v51 = "D:\\TuringComplete_Phu\\model\\scores.nim";
                v57 = v68;
                v50 = 92i64;
                v33 = v68 + 1;
                if ( __OFADD__(1i64, v68) )
                  goto LABEL_49;
                if ( v33 > 0x270F )
                {
                  raiseIndexError2(v33, 9999i64);
                  return popFrame_74();
                }
                if ( v57 > 0x270F )
                {
                  raiseIndexError2(v57, 9999i64);
                  return popFrame_74();
                }
                v14 = 16 * v33;
                v15 = (__int64 *)((char *)&component_cost_buffer__modelZscores_u12 + 16 * v57);
                v16 = *v15;
                v17 = v15[1];
                *(_QWORD *)((char *)&component_cost_buffer__modelZscores_u12 + v14) = v16;
                *(_QWORD *)((char *)&component_cost_buffer__modelZscores_u12 + v14 + 8) = v17;
                v50 = 39i64;
                v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                v32 = v68 - 1;
                if ( __OFSUB__(v68, 1i64) )
                  goto LABEL_49;
                v68 = v32;
              }
              v50 = 93i64;
              v51 = "D:\\TuringComplete_Phu\\model\\scores.nim";
              v18 = *((_QWORD *)&component_costs__modelZscores_u10 + 2 * a1);
              v38 = v18 + inserted;
              if ( __OFADD__(v18, inserted) )
                goto LABEL_49;
              if ( v38 > 0x270F )
              {
                raiseIndexError2(v38, 9999i64);
                return popFrame_74();
              }
              v19 = 16 * v38;
              v20 = v28;
              *(_QWORD *)((char *)&component_cost_buffer__modelZscores_u12 + v19) = v27;
              *(_QWORD *)((char *)&component_cost_buffer__modelZscores_u12 + v19 + 8) = v20;
              v50 = 94i64;
              v37 = component_cost_buffer_len__modelZscores_u11 + 1;
              if ( __OFADD__(1i64, component_cost_buffer_len__modelZscores_u11) )
                goto LABEL_49;
              component_cost_buffer_len__modelZscores_u11 = v37;
              v54 = 0;
              v53 = 0;
              v50 = 95i64;
              v51 = "D:\\TuringComplete_Phu\\model\\scores.nim";
              v31 = a1 + 1i64;
              if ( v31 >= 0x7D )
                goto LABEL_49;
              v53 = v31;
              v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
              v67 = (unsigned __int8)v31;
              v50 = 97i64;
              while ( v67 <= 124 )
              {
                v51 = "D:\\TuringComplete_Phu\\model\\scores.nim";
                v54 = v67;
                v50 = 96i64;
                v21 = *((_QWORD *)&component_costs__modelZscores_u10 + 2 * (unsigned __int8)v67);
                v22 = 0;
                v11 = __OFADD__(1i64, v21);
                v23 = v21 + 1;
                if ( v11 )
                  v22 = 1;
                v30 = v23;
                if ( (v22 & 1) != 0 )
                  goto LABEL_49;
                *((_QWORD *)&component_costs__modelZscores_u10 + 2 * v54) = v30;
                v50 = 102i64;
                v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                v29 = v67 + 1;
                if ( __OFADD__(1i64, v67) )
                  goto LABEL_49;
                v67 = v29;
              }
            }
          }
        }
      }
      else
      {
        v50 = 77i64;
        v46 = v65 - v63;
        if ( __OFSUB__(v65, v63) )
          goto LABEL_49;
        v62 = v46;
        v61 = 0i64;
        v60 = 0i64;
        v50 = 78i64;
        v51 = "D:\\TuringComplete_Phu\\model\\scores.nim";
        v4 = *((_QWORD *)&component_costs__modelZscores_u10 + 2 * a1);
        v44 = v4 + v65;
        if ( __OFADD__(v4, v65) )
          goto LABEL_49;
        v60 = v44;
        v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
        v70 = v44;
        v50 = 129i64;
        while ( v70 < component_cost_buffer_len__modelZscores_u11 )
        {
          v51 = "D:\\TuringComplete_Phu\\model\\scores.nim";
          v61 = v70;
          v50 = 80i64;
          v43 = v70 - v62;
          if ( __OFSUB__(v70, v62) )
            goto LABEL_49;
          if ( v43 > 0x270F )
          {
            raiseIndexError2(v43, 9999i64);
            return popFrame_74();
          }
          if ( v61 > 0x270F )
          {
            raiseIndexError2(v61, 9999i64);
            return popFrame_74();
          }
          v5 = 16 * v43;
          v6 = (__int64 *)((char *)&component_cost_buffer__modelZscores_u12 + 16 * v61);
          v7 = *v6;
          v8 = v6[1];
          *(_QWORD *)((char *)&component_cost_buffer__modelZscores_u12 + v5) = v7;
          *(_QWORD *)((char *)&component_cost_buffer__modelZscores_u12 + v5 + 8) = v8;
          v50 = 131i64;
          v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v42 = v70 + 1;
          if ( __OFADD__(1i64, v70) )
            goto LABEL_49;
          v70 = v42;
        }
        v50 = 81i64;
        v51 = "D:\\TuringComplete_Phu\\model\\scores.nim";
        v45 = component_cost_buffer_len__modelZscores_u11 - v62;
        if ( __OFSUB__(component_cost_buffer_len__modelZscores_u11, v62) )
          goto LABEL_49;
        component_cost_buffer_len__modelZscores_u11 = v45;
        v59 = 0;
        v58 = 0;
        v50 = 82i64;
        v51 = "D:\\TuringComplete_Phu\\model\\scores.nim";
        v41 = a1 + 1i64;
        if ( v41 >= 0x7D )
          goto LABEL_49;
        v58 = v41;
        v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
        v69 = (unsigned __int8)v41;
        v50 = 97i64;
        while ( v69 <= 124 )
        {
          v51 = "D:\\TuringComplete_Phu\\model\\scores.nim";
          v59 = v69;
          v50 = 83i64;
          v9 = *((_QWORD *)&component_costs__modelZscores_u10 + 2 * (unsigned __int8)v69);
          v10 = 0;
          v11 = __OFSUB__(v9, v62);
          v12 = v9 - v62;
          if ( v11 )
            v10 = 1;
          v40 = v12;
          if ( (v10 & 1) != 0 )
            goto LABEL_49;
          *((_QWORD *)&component_costs__modelZscores_u10 + 2 * v59) = v40;
          v50 = 102i64;
          v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v39 = v69 + 1;
          if ( __OFADD__(1i64, v69) )
            goto LABEL_49;
          v69 = v39;
        }
      }
    }
  }
  return popFrame_74();
}
