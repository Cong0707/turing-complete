__int64 __fastcall get_delay_cost__modelZscores_u2270(unsigned __int8 a1, __int64 a2, __int64 a3)
{
  __int64 v3; // rax
  __int64 v4; // rax
  __int64 v5; // rdx
  __int64 v6; // rax
  __int64 v8; // [rsp+20h] [rbp-C0h] BYREF
  void *v9; // [rsp+28h] [rbp-B8h]
  __int64 v10; // [rsp+38h] [rbp-A8h]
  char v11[8]; // [rsp+40h] [rbp-A0h] BYREF
  const char *v12; // [rsp+48h] [rbp-98h]
  __int64 v13; // [rsp+50h] [rbp-90h]
  const char *v14; // [rsp+58h] [rbp-88h]
  __int16 v15; // [rsp+60h] [rbp-80h]
  __int64 v16; // [rsp+70h] [rbp-70h]
  double v17; // [rsp+78h] [rbp-68h]
  double X; // [rsp+80h] [rbp-60h]
  __int64 v19; // [rsp+88h] [rbp-58h]
  double v20; // [rsp+90h] [rbp-50h]
  double v21; // [rsp+98h] [rbp-48h]
  __int64 v22; // [rsp+A0h] [rbp-40h]
  __int64 v23; // [rsp+A8h] [rbp-38h]
  double v24; // [rsp+B0h] [rbp-30h]
  double v25; // [rsp+B8h] [rbp-28h]
  double v26; // [rsp+C0h] [rbp-20h]
  _BYTE *v27; // [rsp+C8h] [rbp-18h]
  __int64 v28; // [rsp+D0h] [rbp-10h]
  char v29; // [rsp+DFh] [rbp-1h]

  v12 = "get_delay_cost";
  v14 = "D:\\TuringComplete_Phu\\model\\scores.nim";
  v13 = 0i64;
  v15 = 0;
  nimFrame_74(v11);
  v27 = (_BYTE *)nimErrorFlag_72();
  v28 = 0i64;
  v16 = a2;
  v13 = 437i64;
  v29 = 0;
  v29 = eqeq___modelZmodel95types_u853(a2, *(_QWORD *)refptr_AUTO_SIZE__modelZmodel95types_u54);
  if ( !v29 )
    v29 = a2 <= 0;
  if ( v29 == 1 )
  {
    v13 = 438i64;
    v16 = bits__modelZsave95mongerZcommon_u192(8i64);
    if ( *v27 )
      goto LABEL_58;
  }
  v13 = 440i64;
  if ( a1 <= 0x11u
    || a1 > 0x27u && a1 <= 0x29u
    || a1 > 0x2Au && a1 <= 0x30u
    || a1 > 0x32u && a1 <= 0x35u
    || a1 > 0x39u && a1 <= 0x67u
    || a1 > 0x68u && a1 <= 0x6Bu
    || a1 > 0x6Cu && a1 <= 0x75u
    || a1 > 0x77u && a1 <= 0x7Cu )
  {
    v13 = 441i64;
    v28 = a3;
    goto LABEL_58;
  }
  v13 = 443i64;
  if ( a1 == 119 )
    goto LABEL_42;
  if ( a1 > 0x77u )
    goto LABEL_57;
  if ( a1 == 118 )
    goto LABEL_56;
  if ( a1 > 0x76u )
    goto LABEL_57;
  if ( a1 == 108 )
    goto LABEL_51;
  if ( a1 > 0x6Cu )
    goto LABEL_57;
  if ( a1 == 104 )
    goto LABEL_51;
  if ( a1 > 0x68u )
    goto LABEL_57;
  if ( a1 == 57 )
    goto LABEL_51;
  if ( a1 > 0x39u )
  {
LABEL_57:
    v13 = 469i64;
    v8 = TM__cWnRfAoMBYzrX9aW9aZjMzkg_25;
    v9 = &TM__cWnRfAoMBYzrX9aW9aZjMzkg_24;
    failedAssertImpl__stdZassertions_u234(&v8);
    goto LABEL_58;
  }
  if ( a1 >= 0x26u )
  {
    v3 = 1i64 << a1;
    if ( ((1i64 << a1) & 0x84048000000000i64) != 0 )
      goto LABEL_42;
    if ( (v3 & 0x140000000000000i64) == 0 )
    {
      if ( (v3 & 0x2004000000000i64) == 0 )
        goto LABEL_57;
      goto LABEL_51;
    }
LABEL_56:
    v13 = 467i64;
    v8 = TM__cWnRfAoMBYzrX9aW9aZjMzkg_23;
    v9 = &TM__cWnRfAoMBYzrX9aW9aZjMzkg_22;
    failedAssertImpl__stdZassertions_u234(&v8);
    goto LABEL_58;
  }
  if ( a1 >= 0x21u )
  {
    v13 = 452i64;
    v26 = log2((double)(int)v16);
    v25 = (double)(int)a3 / 3.0;
    v13 = 454i64;
    v24 = 0.0;
    v24 = ceil(v25 * v26);
    v23 = (unsigned int)(int)v24;
    v13 = 455i64;
    v4 = a3;
    if ( a3 > 4 )
      v4 = 4i64;
    if ( v23 >= v4 )
      v4 = v23;
    v28 = v4;
    goto LABEL_58;
  }
  if ( a1 >= 0x1Bu )
  {
LABEL_51:
    v22 = v16;
    v21 = (double)(int)a3 / 8.0;
    v13 = 464i64;
    v20 = 0.0;
    v20 = ceil((double)(int)v16 * v21);
    v19 = (unsigned int)(int)v20;
    v13 = 465i64;
    v6 = a3;
    if ( a3 > 4 )
      v6 = 4i64;
    if ( v19 >= v6 )
      v6 = v19;
    v28 = v6;
    goto LABEL_58;
  }
  if ( a1 <= 0x19u )
  {
    if ( a1 < 0x12u )
      goto LABEL_57;
LABEL_42:
    v13 = 449i64;
    v28 = a3;
    goto LABEL_58;
  }
  v13 = 458i64;
  X = 0.0;
  X = log2((double)(int)v16 / 8.0);
  v17 = 0.0;
  v17 = ceil(X);
  v5 = (unsigned int)(int)v17;
  v10 = v5 + a3;
  if ( __OFADD__(v5, a3) )
    raiseOverflow();
  else
    v28 = v10;
LABEL_58:
  popFrame_74();
  return v28;
}
