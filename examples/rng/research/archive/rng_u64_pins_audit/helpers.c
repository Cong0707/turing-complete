/* rotate_point: rotate__modelZsave95mongerZcommon_u4629 @ 0x0000000140186c29-0x0000000140186e35 */

__int64 __fastcall rotate__modelZsave95mongerZcommon_u4629(unsigned int a1, unsigned __int8 a2)
{
  __int64 v3[2]; // [rsp+20h] [rbp-60h] BYREF
  unsigned int v4; // [rsp+34h] [rbp-4Ch]
  unsigned int v5; // [rsp+38h] [rbp-48h]
  unsigned int v6; // [rsp+3Ch] [rbp-44h]
  char v7[8]; // [rsp+40h] [rbp-40h] BYREF
  const char *v8; // [rsp+48h] [rbp-38h]
  __int64 v9; // [rsp+50h] [rbp-30h]
  const char *v10; // [rsp+58h] [rbp-28h]
  __int16 v11; // [rsp+60h] [rbp-20h]
  unsigned int v12; // [rsp+70h] [rbp-10h] BYREF
  __int16 v13; // [rsp+74h] [rbp-Ch]
  __int16 v14; // [rsp+76h] [rbp-Ah]
  __int64 v15; // [rsp+78h] [rbp-8h]

  v8 = "rotate";
  v10 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
  v9 = 0i64;
  v11 = 0;
  nimFrame_42(v7);
  v15 = nimErrorFlag_40();
  nimZeroMem_26(&v12, 4i64);
  v9 = 715i64;
  if ( a2 == 3 )
  {
    v9 = 723i64;
    v14 = HIWORD(a1);
    LOWORD(v4) = HIWORD(a1);
    if ( (_WORD)a1 != 0x8000 )
    {
      HIWORD(v4) = -(__int16)a1;
      v12 = v4;
      goto LABEL_17;
    }
    goto LABEL_14;
  }
  if ( a2 > 3u )
    goto LABEL_16;
  if ( a2 == 2 )
  {
    v9 = 721i64;
    if ( (_WORD)a1 != 0x8000 )
    {
      LOWORD(v5) = -(__int16)a1;
      if ( HIWORD(a1) != 0x8000 )
      {
        HIWORD(v5) = -HIWORD(a1);
        v12 = v5;
        goto LABEL_17;
      }
    }
    goto LABEL_14;
  }
  if ( a2 > 2u )
  {
LABEL_16:
    v9 = 725i64;
    v3[0] = TM__AZJHBAzoQYZ8EayTGp7UeA_330;
    v3[1] = (__int64)&TM__AZJHBAzoQYZ8EayTGp7UeA_329;
    failedAssertImpl__stdZassertions_u234(v3);
    goto LABEL_17;
  }
  if ( a2 )
  {
    v13 = 0;
    v9 = 719i64;
    if ( HIWORD(a1) != 0x8000 )
    {
      LOWORD(v6) = -HIWORD(a1);
      v13 = a1;
      HIWORD(v6) = a1;
      v12 = v6;
      goto LABEL_17;
    }
LABEL_14:
    raiseOverflow();
    goto LABEL_17;
  }
  v9 = 717i64;
  v12 = a1;
LABEL_17:
  popFrame_42();
  return v12;
}


/* rotate_then_translate: rotate_then_translate__modelZsave95mongerZcommon_u4638 @ 0x000000014018b5a7-0x000000014018b89f */

_QWORD *__fastcall rotate_then_translate__modelZsave95mongerZcommon_u4638(
        _QWORD *a1,
        __int64 *a2,
        unsigned __int8 a3,
        unsigned int a4)
{
  __int64 v5; // rdx
  __int64 v6; // rdx
  __int64 v8; // [rsp+0h] [rbp-E0h] BYREF
  __int64 v9[2]; // [rsp+20h] [rbp-C0h] BYREF
  __int64 v10[6]; // [rsp+30h] [rbp-B0h] BYREF
  __int64 v11; // [rsp+60h] [rbp-80h]
  const char *v12; // [rsp+68h] [rbp-78h]
  __int16 v13; // [rsp+70h] [rbp-70h]
  int v14; // [rsp+80h] [rbp-60h] BYREF
  unsigned int v15; // [rsp+84h] [rbp-5Ch]
  int v16; // [rsp+88h] [rbp-58h] BYREF
  unsigned int v17; // [rsp+8Ch] [rbp-54h]
  __int64 v18; // [rsp+90h] [rbp-50h] BYREF
  __int64 v19; // [rsp+98h] [rbp-48h]
  __int64 v20; // [rsp+A0h] [rbp-40h]
  __int64 v21; // [rsp+B0h] [rbp-30h]
  __int64 v22; // [rsp+B8h] [rbp-28h]
  __int64 v23; // [rsp+C0h] [rbp-20h]
  _BYTE *v24; // [rsp+C8h] [rbp-18h]
  _BYTE *v25; // [rsp+D0h] [rbp-10h]
  __int64 v26; // [rsp+D8h] [rbp-8h]

  v10[5] = (__int64)"rotate_then_translate";
  v12 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
  v11 = 0i64;
  v13 = 0;
  nimFrame_42(&v8 + 10);
  v25 = (_BYTE *)nimErrorFlag_40();
  nimZeroMem_26(&v18, 24i64);
  v11 = 546i64;
  v12 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
  v5 = a2[1];
  v10[0] = *a2;
  v10[1] = v5;
  v10[2] = a2[2];
  eqcopy___modelZsave95mongerZcommon_u4090(&v18, v10);
  v11 = 729i64;
  v17 = rotate__modelZsave95mongerZcommon_u4629(v18, a3);
  if ( !*v25 )
  {
    nimZeroMem_26(&v16, 4i64);
    v16 = plus___modelZsave95mongerZcommon_u4308(v17, a4);
    if ( !*v25 )
    {
      LODWORD(v18) = v16;
      v11 = 730i64;
      v15 = rotate__modelZsave95mongerZcommon_u4629(HIDWORD(v18), a3);
      if ( !*v25 )
      {
        nimZeroMem_26(&v14, 4i64);
        v14 = plus___modelZsave95mongerZcommon_u4308(v15, a4);
        if ( !*v25 )
        {
          HIDWORD(v18) = v14;
          v24 = 0i64;
          v12 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          v26 = 0i64;
          v23 = v19;
          v22 = v19;
          v11 = 260i64;
          while ( v26 < v22 )
          {
            v11 = 731i64;
            v12 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
            if ( v26 < 0 || v26 >= v19 )
            {
              raiseIndexError2(v26, v19 - 1);
              break;
            }
            v24 = (_BYTE *)(v20 + 4 * v26 + 8);
            v11 = 732i64;
            *v24 = (*v24 + 2 * a3) & 7;
            v12 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v26;
            v11 = 263i64;
            v21 = v19;
            if ( v19 != v22 )
            {
              v9[0] = TM__AZJHBAzoQYZ8EayTGp7UeA_426;
              v9[1] = (__int64)&TM__AZJHBAzoQYZ8EayTGp7UeA_282;
              failedAssertImpl__stdZassertions_u234(v9);
              if ( *v25 )
                break;
            }
          }
        }
      }
    }
  }
  popFrame_42();
  v6 = v19;
  *a1 = v18;
  a1[1] = v6;
  a1[2] = v20;
  return a1;
}


/* get_output_word_size: get_output_word_size__modelZboardZprototype95list_u4333 @ 0x00000001402367c6-0x0000000140236b33 */

__int64 __fastcall get_output_word_size__modelZboardZprototype95list_u4333(
        unsigned __int8 a1,
        unsigned __int16 a2,
        __int64 a3)
{
  __int64 v4[2]; // [rsp+20h] [rbp-70h] BYREF
  char v5[8]; // [rsp+30h] [rbp-60h] BYREF
  const char *v6; // [rsp+38h] [rbp-58h]
  __int64 v7; // [rsp+40h] [rbp-50h]
  const char *v8; // [rsp+48h] [rbp-48h]
  __int16 v9; // [rsp+50h] [rbp-40h]
  __int64 v10; // [rsp+60h] [rbp-30h]
  __int64 v11; // [rsp+68h] [rbp-28h] BYREF
  char v12; // [rsp+74h] [rbp-1Ch]
  char v13; // [rsp+75h] [rbp-1Bh]
  char v14; // [rsp+76h] [rbp-1Ah]
  char v15; // [rsp+77h] [rbp-19h]
  __int64 v16; // [rsp+78h] [rbp-18h]
  char v17; // [rsp+87h] [rbp-9h]
  _BYTE *v18; // [rsp+88h] [rbp-8h]

  v6 = "get_output_word_size";
  v8 = "D:\\TuringComplete_Phu\\model\\board\\prototype_list.nim";
  v7 = 0i64;
  v9 = 0;
  nimFrame_68(v5);
  v18 = (_BYTE *)nimErrorFlag_66();
  nimZeroMem_49(&v11, 8i64);
  v7 = 2407i64;
  v8 = "D:\\TuringComplete_Phu\\model\\board\\prototype_list.nim";
  if ( a1 != 78
    || (v4[0] = TM__wUqL1Kpuf69c1ieeyVFJbBQ_3413,
        v4[1] = (__int64)&TM__wUqL1Kpuf69c1ieeyVFJbBQ_3412,
        failedAssertImpl__stdZassertions_u234(v4),
        !*v18) )
  {
    v10 = a3;
    v7 = 2410i64;
    v17 = 0;
    v17 = eqeq___modelZmodel95types_u853(a3, *(_QWORD *)refptr_AUTO_SIZE__modelZmodel95types_u54);
    if ( v17 != 1 || (v7 = 2411i64, v10 = bits__modelZsave95mongerZcommon_u192(2i64), !*v18) )
    {
      v7 = 2413i64;
      v16 = 0i64;
      v16 = X5BX5D___modelZboardZprototype95list_u4239(&PROTOTYPES__modelZboardZprototype95list_u3752, a1);
      if ( !*v18 )
      {
        if ( a2 < *(__int64 *)(v16 + 128) )
        {
          v11 = *(_QWORD *)(*(_QWORD *)(v16 + 136) + 56i64 * a2 + 16);
          v7 = 2414i64;
          v15 = 0;
          v15 = eqeq___modelZmodel95types_u853(v11, *(_QWORD *)refptr_VARIABLE_WIDTH__modelZmodel95types_u23);
          if ( v15 != 1 )
          {
            v7 = 2415i64;
            v14 = 0;
            v14 = eqeq___modelZmodel95types_u853(v11, *(_QWORD *)refptr_VARIABLE_WIDTH2__modelZmodel95types_u28);
            if ( v14 != 1 )
            {
              v7 = 2416i64;
              v13 = 0;
              v13 = eqeq___modelZmodel95types_u853(v11, *(_QWORD *)refptr_VARIABLE_WIDTH4__modelZmodel95types_u33);
              if ( v13 != 1 )
              {
                v7 = 2417i64;
                v12 = 0;
                v12 = eqeq___modelZmodel95types_u853(v11, *(_QWORD *)refptr_VARIABLE_WIDTH8__modelZmodel95types_u38);
                if ( v12 == 1 )
                {
                  v7 = 2417i64;
                  v11 = star___modelZsave95mongerZcommon_u213(v10, 8i64);
                }
              }
              else
              {
                v7 = 2416i64;
                v11 = star___modelZsave95mongerZcommon_u213(v10, 4i64);
              }
            }
            else
            {
              v7 = 2415i64;
              v11 = star___modelZsave95mongerZcommon_u213(v10, 2i64);
            }
          }
          else
          {
            v7 = 2414i64;
            v11 = star___modelZsave95mongerZcommon_u213(v10, 1i64);
          }
        }
        else
        {
          raiseIndexError2(a2, *(_QWORD *)(v16 + 128) - 1i64);
        }
      }
    }
  }
  popFrame_68();
  return v11;
}


/* get_clamped_word_size: get_clamped_word_size__modelZboardZprototype95list_u4458 @ 0x0000000140236b33-0x00000001402377d1 */

__int64 __fastcall get_clamped_word_size__modelZboardZprototype95list_u4458(unsigned __int8 a1, __int64 a2, char a3)
{
  __int64 v3; // rax
  __int64 v5; // [rsp+20h] [rbp-60h]
  __int64 v6; // [rsp+28h] [rbp-58h]
  __int64 v7; // [rsp+30h] [rbp-50h]
  __int64 v8; // [rsp+38h] [rbp-48h]
  __int64 v9; // [rsp+40h] [rbp-40h]
  __int64 v10; // [rsp+48h] [rbp-38h]
  __int64 v11; // [rsp+50h] [rbp-30h]
  __int64 v12; // [rsp+58h] [rbp-28h]
  __int64 v13; // [rsp+60h] [rbp-20h]
  __int64 v14; // [rsp+68h] [rbp-18h]
  __int64 v15; // [rsp+70h] [rbp-10h]
  __int64 v16; // [rsp+78h] [rbp-8h]
  __int64 v17; // [rsp+80h] [rbp+0h]
  __int64 v18; // [rsp+88h] [rbp+8h]
  __int64 v19; // [rsp+90h] [rbp+10h]
  __int64 v20; // [rsp+98h] [rbp+18h]
  __int64 v21; // [rsp+A0h] [rbp+20h]
  __int64 v22; // [rsp+A8h] [rbp+28h]
  __int64 v23; // [rsp+B0h] [rbp+30h]
  __int64 v24; // [rsp+B8h] [rbp+38h]
  __int64 v25; // [rsp+C0h] [rbp+40h]
  __int64 v26; // [rsp+C8h] [rbp+48h]
  __int64 v27; // [rsp+D0h] [rbp+50h]
  __int64 v28; // [rsp+D8h] [rbp+58h]
  __int64 v29; // [rsp+E0h] [rbp+60h]
  __int64 v30; // [rsp+E8h] [rbp+68h]
  __int64 v31; // [rsp+F0h] [rbp+70h]
  __int64 v32; // [rsp+F8h] [rbp+78h]
  char v33[8]; // [rsp+100h] [rbp+80h] BYREF
  const char *v34; // [rsp+108h] [rbp+88h]
  __int64 v35; // [rsp+110h] [rbp+90h]
  const char *v36; // [rsp+118h] [rbp+98h]
  __int16 v37; // [rsp+120h] [rbp+A0h]
  __int64 v38; // [rsp+138h] [rbp+B8h] BYREF
  _BYTE *v39; // [rsp+140h] [rbp+C0h]
  char v40; // [rsp+14Fh] [rbp+CFh]
  _BYTE *v41; // [rsp+150h] [rbp+D0h]
  bool v42; // [rsp+15Fh] [rbp+DFh]

  v34 = "get_clamped_word_size";
  v36 = "D:\\TuringComplete_Phu\\model\\board\\prototype_list.nim";
  v35 = 0i64;
  v37 = 0;
  nimFrame_68(v33);
  v41 = (_BYTE *)nimErrorFlag_66();
  nimZeroMem_49(&v38, 8i64);
  v35 = 2431i64;
  v40 = 0;
  v40 = eqeq___modelZmodel95types_u853(a2, *(_QWORD *)refptr_AUTO_SIZE__modelZmodel95types_u54);
  if ( v40 == 1 )
  {
    v35 = 2432i64;
    v42 = 0;
    v39 = 0i64;
    v39 = (_BYTE *)X5BX5D___modelZboardZprototype95list_u4239(&PROTOTYPES__modelZboardZprototype95list_u3752, a1);
    if ( !*v41 )
    {
      v42 = *v39 == 0;
      if ( v42 )
        v42 = a3 == 0;
      if ( !v42 )
      {
        v35 = 2434i64;
        v38 = bits__modelZsave95mongerZcommon_u192(8i64);
      }
      else
      {
        v35 = 2433i64;
        v38 = *(_QWORD *)refptr_AUTO_SIZE__modelZmodel95types_u54;
      }
    }
    goto LABEL_65;
  }
  v35 = 2436i64;
  if ( a1 > 0x76u )
    goto LABEL_61;
  if ( a1 >= 0x5Fu )
  {
    switch ( a1 )
    {
      case '_':
      case '`':
      case 'j':
        goto LABEL_47;
      case 'a':
        v35 = 2448i64;
        v16 = min__modelZsave95mongerZcommon_u221(a2, *(_QWORD *)refptr_MAX_WIRE_WIDTH__modelZmodel95types_u47);
        if ( !*v41 )
        {
          v15 = bits__modelZsave95mongerZcommon_u192(4i64);
          if ( !*v41 )
            v38 = max__modelZsave95mongerZcommon_u225(v16, v15);
        }
        break;
      case 'b':
        v35 = 2450i64;
        v14 = min__modelZsave95mongerZcommon_u221(a2, *(_QWORD *)refptr_MAX_WIRE_WIDTH__modelZmodel95types_u47);
        if ( !*v41 )
        {
          v13 = bits__modelZsave95mongerZcommon_u192(8i64);
          if ( !*v41 )
            v38 = max__modelZsave95mongerZcommon_u225(v14, v13);
        }
        break;
      case 'c':
        v35 = 2442i64;
        v24 = div__modelZsave95mongerZcommon_u217(*(_QWORD *)refptr_MAX_WIRE_WIDTH__modelZmodel95types_u47, 4i64);
        if ( !*v41 )
        {
          v23 = min__modelZsave95mongerZcommon_u221(a2, v24);
          if ( !*v41 )
          {
            v22 = bits__modelZsave95mongerZcommon_u192(1i64);
            if ( !*v41 )
              v38 = max__modelZsave95mongerZcommon_u225(v23, v22);
          }
        }
        break;
      case 'd':
        v35 = 2444i64;
        v21 = div__modelZsave95mongerZcommon_u217(*(_QWORD *)refptr_MAX_WIRE_WIDTH__modelZmodel95types_u47, 8i64);
        if ( !*v41 )
        {
          v20 = min__modelZsave95mongerZcommon_u221(a2, v21);
          if ( !*v41 )
          {
            v19 = bits__modelZsave95mongerZcommon_u192(1i64);
            if ( !*v41 )
              v38 = max__modelZsave95mongerZcommon_u225(v20, v19);
          }
        }
        break;
      case 'e':
        v35 = 2454i64;
        v10 = bits__modelZsave95mongerZcommon_u192(64i64);
        if ( !*v41 )
        {
          v9 = min__modelZsave95mongerZcommon_u221(a2, v10);
          if ( !*v41 )
          {
            v8 = bits__modelZsave95mongerZcommon_u192(1i64);
            if ( !*v41 )
              v38 = max__modelZsave95mongerZcommon_u225(v9, v8);
          }
        }
        break;
      case 'u':
        goto LABEL_54;
      case 'v':
LABEL_20:
        v35 = 2438i64;
        v32 = plus___modelZsave95mongerZcommon_u202(a2, 7i64);
        if ( !*v41 )
        {
          v31 = div__modelZsave95mongerZcommon_u217(v32, 8i64);
          if ( !*v41 )
          {
            v30 = star___modelZsave95mongerZcommon_u213(v31, 8i64);
            if ( !*v41 )
            {
              v29 = min__modelZsave95mongerZcommon_u221(v30, *(_QWORD *)refptr_MAX_WIRE_WIDTH__modelZmodel95types_u47);
              if ( !*v41 )
              {
                v28 = bits__modelZsave95mongerZcommon_u192(2i64);
                if ( !*v41 )
                  v38 = max__modelZsave95mongerZcommon_u225(v29, v28);
              }
            }
          }
        }
        break;
      default:
        goto LABEL_61;
    }
  }
  else if ( a1 > 0x4Du )
  {
    v3 = 1i64 << (a1 - 78);
    if ( (v3 & 0x11009) != 0 )
    {
LABEL_54:
      v35 = 2456i64;
      v38 = a2;
      goto LABEL_65;
    }
    if ( (v3 & 6) == 0 )
    {
      if ( (v3 & 0x4000) != 0 )
      {
        v35 = 2468i64;
        v38 = bits__modelZsave95mongerZcommon_u192(64i64);
        goto LABEL_65;
      }
      goto LABEL_61;
    }
LABEL_47:
    v35 = 2452i64;
    v12 = min__modelZsave95mongerZcommon_u221(a2, *(_QWORD *)refptr_MAX_WIRE_WIDTH__modelZmodel95types_u47);
    if ( !*v41 )
    {
      v11 = bits__modelZsave95mongerZcommon_u192(1i64);
      if ( !*v41 )
        v38 = max__modelZsave95mongerZcommon_u225(v12, v11);
    }
  }
  else
  {
    if ( a1 < 0x12u )
    {
LABEL_61:
      v35 = 2470i64;
      v7 = bits__modelZsave95mongerZcommon_u192(64i64);
      if ( !*v41 )
      {
        v6 = min__modelZsave95mongerZcommon_u221(a2, v7);
        if ( !*v41 )
        {
          v5 = bits__modelZsave95mongerZcommon_u192(2i64);
          if ( !*v41 )
            v38 = max__modelZsave95mongerZcommon_u225(v6, v5);
        }
      }
      goto LABEL_65;
    }
    switch ( a1 )
    {
      case 0x12u:
      case 0x13u:
      case 0x14u:
      case 0x15u:
      case 0x16u:
      case 0x17u:
      case 0x18u:
      case 0x21u:
      case 0x22u:
      case 0x3Au:
      case 0x3Du:
      case 0x45u:
        goto LABEL_47;
      case 0x28u:
        v35 = 2466i64;
        v38 = bits__modelZsave95mongerZcommon_u192(8i64);
        break;
      case 0x2Fu:
        v35 = 2440i64;
        v27 = div__modelZsave95mongerZcommon_u217(*(_QWORD *)refptr_MAX_WIRE_WIDTH__modelZmodel95types_u47, 2i64);
        if ( !*v41 )
        {
          v26 = min__modelZsave95mongerZcommon_u221(a2, v27);
          if ( !*v41 )
          {
            v25 = bits__modelZsave95mongerZcommon_u192(1i64);
            if ( !*v41 )
              v38 = max__modelZsave95mongerZcommon_u225(v26, v25);
          }
        }
        break;
      case 0x30u:
        v35 = 2446i64;
        v18 = min__modelZsave95mongerZcommon_u221(a2, *(_QWORD *)refptr_MAX_WIRE_WIDTH__modelZmodel95types_u47);
        if ( !*v41 )
        {
          v17 = bits__modelZsave95mongerZcommon_u192(2i64);
          if ( !*v41 )
            v38 = max__modelZsave95mongerZcommon_u225(v18, v17);
        }
        break;
      case 0x36u:
      case 0x38u:
        goto LABEL_20;
      case 0x3Cu:
      case 0x44u:
        v35 = 2458i64;
        v38 = bits__modelZsave95mongerZcommon_u192(1i64);
        break;
      case 0x3Fu:
      case 0x49u:
        v35 = 2460i64;
        v38 = bits__modelZsave95mongerZcommon_u192(2i64);
        break;
      case 0x40u:
      case 0x4Au:
      case 0x4Du:
        v35 = 2462i64;
        v38 = bits__modelZsave95mongerZcommon_u192(3i64);
        break;
      case 0x41u:
      case 0x4Bu:
        v35 = 2464i64;
        v38 = bits__modelZsave95mongerZcommon_u192(4i64);
        break;
      default:
        goto LABEL_61;
    }
  }
LABEL_65:
  popFrame_68();
  return v38;
}


/* proto_word_size: proto_word_size__modelZboardZprototype95list_u4422 @ 0x00000001402378b1-0x0000000140237bff */

__int64 __fastcall proto_word_size__modelZboardZprototype95list_u4422(__int64 a1, __int64 a2, __int64 *a3)
{
  __int64 v3; // rdx
  __int64 v4; // rax
  __int64 v6; // [rsp+0h] [rbp-90h] BYREF
  __int64 v7; // [rsp+20h] [rbp-70h]
  __int64 v8; // [rsp+28h] [rbp-68h]
  const char *v9; // [rsp+38h] [rbp-58h]
  __int64 v10; // [rsp+40h] [rbp-50h]
  const char *v11; // [rsp+48h] [rbp-48h]
  __int16 v12; // [rsp+50h] [rbp-40h]
  __int64 v13; // [rsp+68h] [rbp-28h] BYREF
  __int64 v14; // [rsp+70h] [rbp-20h]
  __int64 v15; // [rsp+78h] [rbp-18h]
  char v16; // [rsp+83h] [rbp-Dh]
  char v17; // [rsp+84h] [rbp-Ch]
  char v18; // [rsp+85h] [rbp-Bh]
  char v19; // [rsp+86h] [rbp-Ah]
  char v20; // [rsp+87h] [rbp-9h]
  _BYTE *v21; // [rsp+88h] [rbp-8h]

  v3 = a3[1];
  v7 = *a3;
  v8 = v3;
  v9 = "proto_word_size";
  v11 = "D:\\TuringComplete_Phu\\model\\board\\prototype_list.nim";
  v10 = 0i64;
  v12 = 0;
  nimFrame_68(&v6 + 6);
  v21 = (_BYTE *)nimErrorFlag_66();
  nimZeroMem_49(&v13, 8i64);
  v10 = 2420i64;
  v11 = "D:\\TuringComplete_Phu\\model\\board\\prototype_list.nim";
  v20 = 0;
  v20 = eqeq___modelZmodel95types_u853(*(_QWORD *)(a1 + 8), *(_QWORD *)refptr_VARIABLE_WIDTH__modelZmodel95types_u23);
  if ( v20 != 1 )
  {
    v10 = 2421i64;
    v19 = 0;
    v19 = eqeq___modelZmodel95types_u853(*(_QWORD *)(a1 + 8), *(_QWORD *)refptr_VARIABLE_WIDTH2__modelZmodel95types_u28);
    if ( v19 != 1 )
    {
      v10 = 2422i64;
      v18 = 0;
      v18 = eqeq___modelZmodel95types_u853(
              *(_QWORD *)(a1 + 8),
              *(_QWORD *)refptr_VARIABLE_WIDTH4__modelZmodel95types_u33);
      if ( v18 != 1 )
      {
        v10 = 2423i64;
        v17 = 0;
        v17 = eqeq___modelZmodel95types_u853(
                *(_QWORD *)(a1 + 8),
                *(_QWORD *)refptr_VARIABLE_WIDTH8__modelZmodel95types_u38);
        if ( v17 != 1 )
        {
          v10 = 2424i64;
          v16 = 0;
          v16 = eqeq___modelZmodel95types_u853(
                  *(_QWORD *)(a1 + 8),
                  *(_QWORD *)refptr_VARIABLE_WIDTH_ALT__modelZmodel95types_u43);
          if ( v16 != 1 )
          {
            v10 = 2428i64;
            v13 = *(_QWORD *)(a1 + 8);
          }
          else
          {
            v10 = 2425i64;
            v15 = v7;
            if ( v7 )
            {
              v10 = 2426i64;
              v14 = 0i64;
              if ( v8 )
                v4 = v8 + 8;
              else
                v4 = 0i64;
              v14 = X5BX5D___modelZboardZprototype95list_u4450(v4, v7, 1i64);
              if ( !*v21 )
                v13 = bits__modelZsave95mongerZcommon_u192(v14);
            }
            else
            {
              v10 = 2425i64;
              v13 = a2;
            }
          }
        }
        else
        {
          v10 = 2423i64;
          v13 = star___modelZsave95mongerZcommon_u213(a2, 8i64);
        }
      }
      else
      {
        v10 = 2422i64;
        v13 = star___modelZsave95mongerZcommon_u213(a2, 4i64);
      }
    }
    else
    {
      v10 = 2421i64;
      v13 = star___modelZsave95mongerZcommon_u213(a2, 2i64);
    }
  }
  else
  {
    v10 = 2420i64;
    v13 = star___modelZsave95mongerZcommon_u213(a2, 1i64);
  }
  popFrame_68();
  return v13;
}

