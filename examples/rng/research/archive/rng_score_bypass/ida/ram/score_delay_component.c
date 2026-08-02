__int64 __fastcall get_delay_cost__modelZscores_u2316(unsigned __int8 *a1, __int64 a2)
{
  int v2; // eax
  __int64 v3; // rax
  char v4; // dl
  bool v5; // of
  __int64 v6; // rax
  char v8[312]; // [rsp+20h] [rbp-60h] BYREF
  __int64 v9; // [rsp+158h] [rbp+D8h]
  __int64 v10; // [rsp+5C8h] [rbp+548h] BYREF
  __int64 v11; // [rsp+5D0h] [rbp+550h]
  __int64 v12; // [rsp+5D8h] [rbp+558h]
  char v13[8]; // [rsp+5E0h] [rbp+560h] BYREF
  const char *v14; // [rsp+5E8h] [rbp+568h]
  __int64 v15; // [rsp+5F0h] [rbp+570h]
  const char *v16; // [rsp+5F8h] [rbp+578h]
  __int16 v17; // [rsp+600h] [rbp+580h]
  char v18; // [rsp+61Fh] [rbp+59Fh]
  __int64 v19; // [rsp+620h] [rbp+5A0h]
  double v20; // [rsp+628h] [rbp+5A8h]
  double v21; // [rsp+630h] [rbp+5B0h]
  double X; // [rsp+638h] [rbp+5B8h]
  _BYTE *v23; // [rsp+640h] [rbp+5C0h]
  __int64 delay_cost__modelZscores_u2270; // [rsp+648h] [rbp+5C8h]

  v14 = "get_delay_cost";
  v16 = "D:\\TuringComplete_Phu\\model\\scores.nim";
  v15 = 0i64;
  v17 = 0;
  nimFrame_74(v13);
  v23 = (_BYTE *)nimErrorFlag_72();
  delay_cost__modelZscores_u2270 = 0i64;
  v15 = 495i64;
  v2 = *a1;
  if ( v2 == 118 )
  {
    v15 = 504i64;
    if ( *((__int64 *)a1 + 21) > 0 )
    {
      if ( *(_QWORD *)(*((_QWORD *)a1 + 22) + 8i64) )
      {
        v15 = 508i64;
        if ( *((__int64 *)a1 + 21) <= 1 )
        {
          raiseIndexError2(1i64, *((_QWORD *)a1 + 21) - 1i64);
          goto LABEL_36;
        }
        if ( *(__int64 *)(*((_QWORD *)a1 + 22) + 16i64) < 0 )
        {
          raiseRangeErrorNoArgs();
          goto LABEL_36;
        }
        v3 = *(_QWORD *)(*((_QWORD *)a1 + 22) + 16i64);
        v4 = 0;
        v5 = __OFADD__(1i64, v3);
        v6 = v3 + 1;
        if ( v5 )
          v4 = 1;
        v11 = v6;
        if ( (v4 & 1) == 0 )
        {
          if ( !v11 )
          {
            raiseDivByZero();
            goto LABEL_36;
          }
          if ( !(unsigned __int8)nimDivInt_1(512i64, v11, &v10) )
          {
            delay_cost__modelZscores_u2270 = v10;
            goto LABEL_36;
          }
        }
      }
      else
      {
        v15 = 505i64;
        X = 0.0;
        X = log2((double)(int)*((_QWORD *)a1 + 39));
        v21 = 0.0;
        v21 = log2(X);
        v20 = 0.0;
        v20 = ceil(v21);
        v19 = (unsigned int)(int)v20;
        v15 = 506i64;
        v12 = v19 + 6;
        if ( !__OFADD__(6i64, v19) )
        {
          delay_cost__modelZscores_u2270 = v12;
          goto LABEL_36;
        }
      }
      raiseOverflow();
      goto LABEL_36;
    }
    raiseIndexError2(0i64, *((_QWORD *)a1 + 21) - 1i64);
  }
  else
  {
    if ( *a1 > 0x76u )
      goto LABEL_35;
    if ( v2 == 79 )
    {
      v16 = "D:\\TuringComplete_Phu\\model\\scores.nim";
      v15 = 500i64;
      delay_cost__modelZscores_u2270 = *((_QWORD *)a1 + 38);
      goto LABEL_36;
    }
    if ( *a1 > 0x4Fu )
    {
LABEL_35:
      v15 = 510i64;
      delay_cost__modelZscores_u2270 = get_delay_cost__modelZscores_u2270(*a1, *((_QWORD *)a1 + 29), a2);
      goto LABEL_36;
    }
    if ( v2 == 78 )
    {
      v15 = 497i64;
      v18 = 0;
      v18 = in_custom_prototypes__modelZboardZcustom95prototype95list_u9(*((_QWORD *)a1 + 49));
      if ( !*v23 && v18 == 1 )
      {
        nimZeroMem_54(v8, 1448i64);
        v15 = 498i64;
        get_custom_prototype__modelZboardZcustom95prototype95list_u451(*((_QWORD *)a1 + 49), v8);
        if ( !*v23 )
        {
          delay_cost__modelZscores_u2270 = v9;
          v15 = 170i64;
          v16 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        }
        eqdestroy___modelZboardZprototype95list_u3239(v8);
      }
    }
    else
    {
      if ( v2 != 54 && v2 != 56 )
        goto LABEL_35;
      v15 = 502i64;
      delay_cost__modelZscores_u2270 = *((_QWORD *)a1 + 36);
    }
  }
LABEL_36:
  popFrame_74();
  return delay_cost__modelZscores_u2270;
}
