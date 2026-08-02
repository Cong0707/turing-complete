__int64 __fastcall get_level_score__modelZscores_u2620(signed __int64 a1, unsigned __int64 a2, __int64 a3)
{
  __int64 v3; // rax
  char v4; // cl
  unsigned __int64 v5; // rax
  unsigned __int64 v6; // kr00_8
  char v8[8]; // [rsp+20h] [rbp-50h] BYREF
  const char *v9; // [rsp+28h] [rbp-48h]
  __int64 v10; // [rsp+30h] [rbp-40h]
  const char *v11; // [rsp+38h] [rbp-38h]
  __int16 v12; // [rsp+40h] [rbp-30h]
  unsigned __int64 v13; // [rsp+50h] [rbp-20h]
  unsigned __int64 v14; // [rsp+58h] [rbp-18h]
  _BYTE *v15; // [rsp+60h] [rbp-10h]
  unsigned __int64 v16; // [rsp+68h] [rbp-8h]

  v9 = "get_level_score";
  v11 = "D:\\TuringComplete_Phu\\model\\scores.nim";
  v10 = 0i64;
  v12 = 0;
  nimFrame_74(v8);
  v15 = (_BYTE *)nimErrorFlag_72();
  v16 = 0i64;
  v10 = 613i64;
  if ( a1 >= 0 )
  {
    v10 = 617i64;
    v14 = a2 * a1;
    if ( !is_mul_ok(a2, a1) )
      goto LABEL_4;
    v3 = a3;
    if ( a3 <= 0 )
      v3 = 1i64;
    v4 = 0;
    v6 = v3;
    v5 = v14 * v3;
    if ( !is_mul_ok(v14, v6) )
      v4 = 1;
    v13 = v5;
    if ( (v4 & 1) != 0 )
    {
LABEL_4:
      raiseOverflow();
      *v15 = 0;
      v10 = 619i64;
      raiseDefect();
      v10 = 619i64;
      v16 = 0x7FFFFFFFFFFFFFFFi64;
      popCurrentException_2();
    }
    else
    {
      v16 = v13;
    }
  }
  else
  {
    v10 = 614i64;
    v16 = 0x7FFFFFFFFFFFFFFFi64;
  }
  popFrame_74();
  return v16;
}
