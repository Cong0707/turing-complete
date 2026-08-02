__int64 __fastcall import_costs__modelZscores_u2127(unsigned __int8 a1, __int64 *a2)
{
  __int64 v2; // rax
  char v3; // dl
  bool v4; // of
  __int64 v5; // rax
  __int64 v6; // r8
  __int64 *v7; // rdx
  __int64 v8; // rax
  __int64 v9; // rdx
  __int64 v10; // rax
  char v11; // dl
  __int64 v12; // rax
  void *v13; // rdx
  __int64 v15; // [rsp+0h] [rbp-80h] BYREF
  __int64 v16; // [rsp+20h] [rbp-60h] BYREF
  void *v17; // [rsp+28h] [rbp-58h]
  __int64 v18; // [rsp+30h] [rbp-50h]
  __int64 v19; // [rsp+38h] [rbp-48h]
  unsigned __int64 v20; // [rsp+40h] [rbp-40h]
  __int64 v21; // [rsp+48h] [rbp-38h]
  unsigned __int64 v22; // [rsp+50h] [rbp-30h]
  __int64 v23; // [rsp+58h] [rbp-28h]
  const char *v24; // [rsp+68h] [rbp-18h]
  __int64 v25; // [rsp+70h] [rbp-10h]
  const char *v26; // [rsp+78h] [rbp-8h]
  __int16 v27; // [rsp+80h] [rbp+0h]
  __int64 v28; // [rsp+98h] [rbp+18h]
  __int64 v29[3]; // [rsp+A0h] [rbp+20h] BYREF
  __int64 v30; // [rsp+B8h] [rbp+38h]
  __int64 v31; // [rsp+C0h] [rbp+40h]
  __int64 v32; // [rsp+C8h] [rbp+48h]
  __int64 *v33; // [rsp+D0h] [rbp+50h]
  char v34; // [rsp+DEh] [rbp+5Eh]
  unsigned __int8 v35; // [rsp+DFh] [rbp+5Fh]
  __int64 v36; // [rsp+E0h] [rbp+60h]
  unsigned __int64 v37; // [rsp+E8h] [rbp+68h]
  _BYTE *v38; // [rsp+F0h] [rbp+70h]
  __int64 v39; // [rsp+F8h] [rbp+78h]
  __int64 v40; // [rsp+100h] [rbp+80h]
  __int64 v41; // [rsp+108h] [rbp+88h]

  v24 = "import_costs";
  v26 = "D:\\TuringComplete_Phu\\model\\scores.nim";
  v25 = 0i64;
  v27 = 0;
  nimFrame_74(&v15 + 12);
  v38 = (_BYTE *)nimErrorFlag_72();
  v25 = 310i64;
  if ( ((TM__cWnRfAoMBYzrX9aW9aZjMzkg_47[a1 >> 3] >> (a1 & 7)) & 1) != 0 )
  {
    v25 = 311i64;
  }
  else
  {
    v25 = 314i64;
    nimZeroMem_54(v29, 16i64);
    v16 = v29[0];
    v17 = (void *)v29[1];
    insert_cost__modelZscores_u49(a1, &v16);
    if ( !*v38 )
    {
      v37 = 0i64;
      v36 = 0i64;
      v25 = 317i64;
      v26 = "D:\\TuringComplete_Phu\\model\\scores.nim";
      v2 = *((_QWORD *)&component_costs__modelZscores_u10 + 2 * a1);
      v3 = 0;
      v4 = __OFADD__(1i64, v2);
      v5 = v2 + 1;
      if ( v4 )
        v3 = 1;
      v23 = v5;
      if ( (v3 & 1) != 0 )
        goto LABEL_16;
      v36 = v23;
      v26 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v41 = v23;
      v25 = 129i64;
      while ( v41 < component_cost_buffer_len__modelZscores_u11 )
      {
        v26 = "D:\\TuringComplete_Phu\\model\\scores.nim";
        v37 = v41;
        v25 = 318i64;
        v22 = v41 - 1;
        if ( __OFSUB__(v41, 1i64) )
          goto LABEL_16;
        if ( v22 > 0x270F )
        {
          raiseIndexError2(v22, 9999i64);
          return popFrame_74();
        }
        if ( v37 > 0x270F )
        {
          raiseIndexError2(v37, 9999i64);
          return popFrame_74();
        }
        v6 = 16 * v22;
        v7 = (__int64 *)((char *)&component_cost_buffer__modelZscores_u12 + 16 * v37);
        v8 = *v7;
        v9 = v7[1];
        *(_QWORD *)((char *)&component_cost_buffer__modelZscores_u12 + v6) = v8;
        *(_QWORD *)((char *)&component_cost_buffer__modelZscores_u12 + v6 + 8) = v9;
        v25 = 131i64;
        v26 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
        v21 = v41 + 1;
        if ( __OFADD__(1i64, v41) )
          goto LABEL_16;
        v41 = v21;
      }
      v25 = 319i64;
      v26 = "D:\\TuringComplete_Phu\\model\\scores.nim";
      v28 = component_cost_buffer_len__modelZscores_u11 - 1;
      if ( __OFSUB__(component_cost_buffer_len__modelZscores_u11, 1i64)
        || (component_cost_buffer_len__modelZscores_u11 = v28,
            v35 = 0,
            v34 = 0,
            v25 = 320i64,
            v26 = "D:\\TuringComplete_Phu\\model\\scores.nim",
            v20 = a1 + 1i64,
            v20 >= 0x7D) )
      {
LABEL_16:
        raiseOverflow();
      }
      else
      {
        v34 = v20;
        v26 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
        v40 = (unsigned __int8)v20;
        v25 = 97i64;
        while ( v40 <= 124 )
        {
          v26 = "D:\\TuringComplete_Phu\\model\\scores.nim";
          v35 = v40;
          v25 = 321i64;
          v10 = *((_QWORD *)&component_costs__modelZscores_u10 + 2 * (unsigned __int8)v40);
          v11 = 0;
          v4 = __OFSUB__(v10, 1i64);
          v12 = v10 - 1;
          if ( v4 )
            v11 = 1;
          v19 = v12;
          if ( (v11 & 1) != 0 )
            goto LABEL_16;
          *((_QWORD *)&component_costs__modelZscores_u10 + 2 * v35) = v19;
          v25 = 102i64;
          v26 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v18 = v40 + 1;
          if ( __OFADD__(1i64, v40) )
            goto LABEL_16;
          v40 = v18;
        }
        qword_1467664A8[2 * a1] = 0i64;
        v33 = 0i64;
        v26 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v39 = 0i64;
        v25 = 259i64;
        v32 = *a2;
        v31 = v32;
        v25 = 260i64;
        while ( v39 < v31 )
        {
          v25 = 324i64;
          v26 = "D:\\TuringComplete_Phu\\model\\scores.nim";
          if ( v39 < 0 || v39 >= *a2 )
          {
            raiseIndexError2(v39, *a2 - 1);
            return popFrame_74();
          }
          v33 = (__int64 *)(a2[1] + 16 * v39 + 8);
          v25 = 325i64;
          v13 = (void *)v33[1];
          v16 = *v33;
          v17 = v13;
          insert_cost__modelZscores_u49(a1, &v16);
          if ( !*v38 )
          {
            v25 = 326i64;
            stareq___pureZtimes_u3584_1(v33, 8i64);
            v26 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v39;
            v25 = 263i64;
            v30 = *a2;
            if ( v30 == v31 )
              continue;
            v16 = TM__cWnRfAoMBYzrX9aW9aZjMzkg_108;
            v17 = &TM__cWnRfAoMBYzrX9aW9aZjMzkg_107;
            failedAssertImpl__stdZassertions_u234(&v16);
            if ( !*v38 )
              continue;
          }
          return popFrame_74();
        }
        v25 = 328i64;
        v26 = "D:\\TuringComplete_Phu\\model\\scores.nim";
        switch ( a1 )
        {
          case 4u:
            v25 = 332i64;
            import_costs__modelZscores_u2127(20i64, a2);
            break;
          case 7u:
            v25 = 330i64;
            import_costs__modelZscores_u2127(19i64, a2);
            break;
          case 9u:
            v25 = 334i64;
            import_costs__modelZscores_u2127(22i64, a2);
            break;
          case 0xAu:
            v25 = 336i64;
            import_costs__modelZscores_u2127(23i64, a2);
            break;
          case 0xBu:
            v25 = 338i64;
            import_costs__modelZscores_u2127(24i64, a2);
            break;
          case 0x27u:
            v25 = 340i64;
            import_costs__modelZscores_u2127(50i64, a2);
            break;
          case 0x37u:
            v25 = 342i64;
            import_costs__modelZscores_u2127(119i64, a2);
            break;
          default:
            return popFrame_74();
        }
      }
    }
  }
  return popFrame_74();
}
