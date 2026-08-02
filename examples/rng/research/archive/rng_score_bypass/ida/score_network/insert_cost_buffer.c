__int64 __fastcall insert_cost__modelZscores_u13(unsigned __int64 *a1, __int64 *a2)
{
  unsigned __int64 v2; // rax
  char v3; // cl
  bool v4; // of
  __int64 v5; // rax
  char v6; // dl
  unsigned __int64 v7; // rax
  char v8; // cl
  unsigned __int64 v9; // rax
  unsigned __int64 v10; // rax
  char v11; // dl
  unsigned __int64 v12; // rax
  unsigned __int64 v13; // rax
  char v14; // dl
  __int64 v15; // rax
  __int64 v16; // r8
  unsigned __int64 v17; // rax
  char v18; // cl
  __int64 v19; // rax
  unsigned __int64 v20; // rax
  char v21; // cl
  __int64 v22; // rax
  __int64 v23; // r8
  __int64 *v24; // rdx
  __int64 v25; // rax
  __int64 v26; // rdx
  unsigned __int64 v27; // rax
  char v28; // cl
  unsigned __int64 v29; // rax
  unsigned __int64 v30; // rax
  char v31; // cl
  unsigned __int64 v32; // rax
  unsigned __int64 v33; // rax
  char v34; // cl
  unsigned __int64 v35; // rax
  unsigned __int64 v36; // rax
  char v37; // dl
  __int64 v38; // rax
  bool v39; // cl
  __int64 v41; // [rsp+20h] [rbp-60h]
  __int64 v42; // [rsp+28h] [rbp-58h]
  unsigned __int64 v43; // [rsp+38h] [rbp-48h]
  __int64 v44; // [rsp+40h] [rbp-40h]
  __int64 v45; // [rsp+48h] [rbp-38h]
  unsigned __int64 v46; // [rsp+68h] [rbp-18h]
  unsigned __int64 v47; // [rsp+70h] [rbp-10h]
  unsigned __int64 v48; // [rsp+98h] [rbp+18h]
  unsigned __int64 v49; // [rsp+A0h] [rbp+20h]
  unsigned __int64 v50; // [rsp+C0h] [rbp+40h]
  char v51[8]; // [rsp+E0h] [rbp+60h] BYREF
  const char *v52; // [rsp+E8h] [rbp+68h]
  __int64 v53; // [rsp+F0h] [rbp+70h]
  const char *v54; // [rsp+F8h] [rbp+78h]
  __int16 v55; // [rsp+100h] [rbp+80h]
  unsigned __int64 v56; // [rsp+118h] [rbp+98h]
  __int64 v57; // [rsp+120h] [rbp+A0h]
  __int64 v58; // [rsp+128h] [rbp+A8h]
  unsigned __int64 v59; // [rsp+130h] [rbp+B0h]
  __int64 v60; // [rsp+138h] [rbp+B8h]
  unsigned __int64 v61; // [rsp+140h] [rbp+C0h]
  unsigned __int64 v62; // [rsp+148h] [rbp+C8h]
  __int64 v63; // [rsp+150h] [rbp+D0h]
  unsigned __int64 v64; // [rsp+158h] [rbp+D8h]
  __int64 v65; // [rsp+160h] [rbp+E0h]
  unsigned __int64 v66; // [rsp+168h] [rbp+E8h]
  bool v67; // [rsp+177h] [rbp+F7h]
  unsigned __int64 v68; // [rsp+178h] [rbp+F8h]
  unsigned __int64 v69; // [rsp+180h] [rbp+100h]
  unsigned __int64 v70; // [rsp+188h] [rbp+108h]

  v41 = *a2;
  v42 = a2[1];
  v52 = "insert_cost";
  v54 = "D:\\TuringComplete_Phu\\model\\scores.nim";
  v53 = 0i64;
  v55 = 0;
  nimFrame_74(v51);
  v70 = 0i64;
  v69 = -1i64;
  v64 = 0i64;
  v63 = 0i64;
  v53 = 18i64;
  v54 = "D:\\TuringComplete_Phu\\model\\scores.nim";
  v2 = a1[1];
  v3 = 0;
  v4 = __OFADD__(*a1, v2);
  v5 = *a1 + v2;
  if ( v4 )
    v3 = 1;
  if ( (v3 & 1) != 0 )
    goto LABEL_77;
  v63 = v5;
  v53 = 128i64;
  v54 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
  v68 = *a1;
  v53 = 129i64;
  while ( (__int64)v68 < v63 )
  {
    v54 = "D:\\TuringComplete_Phu\\model\\scores.nim";
    v64 = v68;
    v53 = 19i64;
    if ( v68 > 0x270F )
    {
      raiseIndexError2(v64, 9999i64);
      goto LABEL_98;
    }
    if ( *((_QWORD *)&component_cost_buffer__modelZscores_u12 + 2 * v64) >= v41 )
    {
      v69 = v64;
      v53 = 23i64;
      break;
    }
    v53 = 131i64;
    v54 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v6 = 0;
    if ( __OFADD__(1i64, v68) )
      v6 = 1;
    if ( (v6 & 1) != 0 )
      goto LABEL_77;
    ++v68;
  }
  v53 = 25i64;
  v54 = "D:\\TuringComplete_Phu\\model\\scores.nim";
  if ( v69 == -1i64 )
  {
    v53 = 27i64;
    v67 = 0;
    v67 = a1[1] == 0;
    if ( !v67 )
    {
      v53 = 29i64;
      v7 = a1[1];
      v8 = 0;
      v4 = __OFADD__(*a1, v7);
      v9 = *a1 + v7;
      if ( v4 )
        v8 = 1;
      if ( (v8 & 1) != 0 )
        goto LABEL_77;
      v50 = v9 - 1;
      if ( __OFSUB__(v9, 1i64) )
        goto LABEL_77;
      if ( v50 > 0x270F )
      {
        raiseIndexError2(v50, 9999i64);
        goto LABEL_98;
      }
      v67 = v42 < qword_146766C88[2 * v50];
    }
    if ( !v67 )
    {
      v53 = 32i64;
      v70 = -1i64;
    }
    else
    {
      v53 = 30i64;
      v10 = a1[1];
      v11 = 0;
      v4 = __OFADD__(1i64, v10);
      v12 = v10 + 1;
      if ( v4 )
        v11 = 1;
      if ( (v11 & 1) != 0 )
        goto LABEL_77;
      a1[1] = v12;
      v53 = 31i64;
      v13 = a1[1];
      v14 = 0;
      v4 = __OFSUB__(v13, 1i64);
      v15 = v13 - 1;
      if ( v4 )
        v14 = 1;
      if ( (v14 & 1) != 0 )
      {
LABEL_77:
        raiseOverflow();
        goto LABEL_98;
      }
      v70 = v15;
    }
  }
  else
  {
    v53 = 35i64;
    if ( v69 <= 0x270F )
    {
      if ( v42 > qword_146766C88[2 * v69] )
      {
        v53 = 57i64;
        if ( v41 == *((_QWORD *)&component_cost_buffer__modelZscores_u12 + 2 * v69) )
        {
          v53 = 59i64;
          v70 = -1i64;
          goto LABEL_98;
        }
        v53 = 64i64;
        v36 = a1[1];
        v37 = 0;
        v4 = __OFADD__(1i64, v36);
        v38 = v36 + 1;
        if ( v4 )
          v37 = 1;
        v57 = v38;
        if ( (v37 & 1) == 0 )
        {
          a1[1] = v57;
          v53 = 65i64;
          v39 = __OFSUB__(v69, *a1);
          v56 = v69 - *a1;
          if ( !v39 )
          {
            v70 = v56;
            goto LABEL_98;
          }
        }
      }
      else
      {
        v16 = 16 * v69;
        *(_QWORD *)((char *)&component_cost_buffer__modelZscores_u12 + v16) = v41;
        *(_QWORD *)((char *)&component_cost_buffer__modelZscores_u12 + v16 + 8) = v42;
        v62 = 0i64;
        v61 = 0i64;
        v60 = 0i64;
        v53 = 39i64;
        v54 = "D:\\TuringComplete_Phu\\model\\scores.nim";
        if ( !__OFADD__(1i64, v69) )
        {
          v61 = v69 + 1;
          v53 = 39i64;
          v54 = "D:\\TuringComplete_Phu\\model\\scores.nim";
          v17 = a1[1];
          v18 = 0;
          v4 = __OFADD__(*a1, v17);
          v19 = *a1 + v17;
          if ( v4 )
            v18 = 1;
          if ( (v18 & 1) == 0 )
          {
            v60 = v19;
            v54 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
            v66 = v61;
            v53 = 129i64;
            while ( (__int64)v66 < v60 )
            {
              v54 = "D:\\TuringComplete_Phu\\model\\scores.nim";
              v62 = v66;
              v53 = 40i64;
              if ( v66 > 0x270F )
              {
                raiseIndexError2(v62, 9999i64);
                goto LABEL_98;
              }
              if ( qword_146766C88[2 * v62] < v42 )
              {
                v53 = 42i64;
                if ( __OFADD__(1i64, v69) )
                  goto LABEL_77;
                if ( v62 == v69 + 1 )
                {
                  v53 = 43i64;
                  v70 = -1i64;
                  goto LABEL_98;
                }
                v59 = 0i64;
                v58 = 0i64;
                v53 = 46i64;
                v54 = "D:\\TuringComplete_Phu\\model\\scores.nim";
                v20 = a1[1];
                v21 = 0;
                v4 = __OFADD__(*a1, v20);
                v22 = *a1 + v20;
                if ( v4 )
                  v21 = 1;
                if ( (v21 & 1) == 0 )
                {
                  v58 = v22;
                  v54 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                  v65 = v62;
                  v53 = 129i64;
                  while ( v65 < v58 )
                  {
                    v54 = "D:\\TuringComplete_Phu\\model\\scores.nim";
                    v59 = v65;
                    v53 = 47i64;
                    v45 = v65 - v62;
                    if ( __OFSUB__(v65, v62) )
                      goto LABEL_77;
                    v44 = v45 + v69;
                    if ( __OFADD__(v45, v69) )
                      goto LABEL_77;
                    v43 = v44 + 1;
                    if ( __OFADD__(1i64, v44) )
                      goto LABEL_77;
                    if ( v43 > 0x270F )
                    {
                      raiseIndexError2(v43, 9999i64);
                      goto LABEL_98;
                    }
                    v53 = 48i64;
                    if ( v59 > 0x270F )
                    {
                      raiseIndexError2(v59, 9999i64);
                      goto LABEL_98;
                    }
                    v23 = 16 * v43;
                    v24 = (__int64 *)((char *)&component_cost_buffer__modelZscores_u12 + 16 * v59);
                    v25 = *v24;
                    v26 = v24[1];
                    *(_QWORD *)((char *)&component_cost_buffer__modelZscores_u12 + v23) = v25;
                    *(_QWORD *)((char *)&component_cost_buffer__modelZscores_u12 + v23 + 8) = v26;
                    v53 = 131i64;
                    v54 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                    if ( __OFADD__(1i64, v65) )
                      goto LABEL_77;
                    ++v65;
                  }
                  v53 = 49i64;
                  v54 = "D:\\TuringComplete_Phu\\model\\scores.nim";
                  v47 = v62 - v69;
                  if ( !__OFSUB__(v62, v69) )
                  {
                    v46 = v47 - 1;
                    if ( !__OFSUB__(v47, 1i64) )
                    {
                      v27 = a1[1];
                      v28 = 0;
                      v4 = __OFSUB__(v27, v46);
                      v29 = v27 - v46;
                      if ( v4 )
                        v28 = 1;
                      if ( (v28 & 1) == 0 )
                      {
                        a1[1] = v29;
                        v53 = 50i64;
                        v70 = -1i64;
                        goto LABEL_98;
                      }
                    }
                  }
                }
                goto LABEL_77;
              }
              v53 = 131i64;
              v54 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
              if ( __OFADD__(1i64, v66) )
                goto LABEL_77;
              ++v66;
            }
            v53 = 52i64;
            v54 = "D:\\TuringComplete_Phu\\model\\scores.nim";
            v30 = a1[1];
            v31 = 0;
            v4 = __OFADD__(*a1, v30);
            v32 = *a1 + v30;
            if ( v4 )
              v31 = 1;
            if ( (v31 & 1) == 0 )
            {
              v49 = v32 - v69;
              if ( !__OFSUB__(v32, v69) )
              {
                v48 = v49 - 1;
                if ( !__OFSUB__(v49, 1i64) )
                {
                  v33 = a1[1];
                  v34 = 0;
                  v4 = __OFSUB__(v33, v48);
                  v35 = v33 - v48;
                  if ( v4 )
                    v34 = 1;
                  if ( (v34 & 1) == 0 )
                  {
                    a1[1] = v35;
                    v53 = 53i64;
                    v70 = -1i64;
                    goto LABEL_98;
                  }
                }
              }
            }
          }
        }
      }
      goto LABEL_77;
    }
    raiseIndexError2(v69, 9999i64);
  }
LABEL_98:
  popFrame_74();
  return v70;
}
