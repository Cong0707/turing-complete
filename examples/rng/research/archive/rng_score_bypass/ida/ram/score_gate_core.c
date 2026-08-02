__int64 __fastcall get_gate_cost__modelZscores_u2232(unsigned __int8 a1, signed __int64 a2, __int64 a3)
{
  __int64 v3; // rdx
  __int64 v5; // [rsp+20h] [rbp-60h] BYREF
  void *v6; // [rsp+28h] [rbp-58h]
  unsigned __int64 v7; // [rsp+38h] [rbp-48h]
  unsigned __int64 v8; // [rsp+40h] [rbp-40h]
  __int64 v9; // [rsp+48h] [rbp-38h]
  __int64 v10; // [rsp+50h] [rbp-30h]
  __int64 v11; // [rsp+58h] [rbp-28h]
  unsigned __int64 v12; // [rsp+60h] [rbp-20h]
  unsigned __int64 v13; // [rsp+68h] [rbp-18h]
  unsigned __int64 v14; // [rsp+70h] [rbp-10h]
  unsigned __int64 v15; // [rsp+78h] [rbp-8h]
  _QWORD v16[2]; // [rsp+80h] [rbp+0h] BYREF
  __int64 v17; // [rsp+90h] [rbp+10h]
  const char *v18; // [rsp+98h] [rbp+18h]
  __int16 v19; // [rsp+A0h] [rbp+20h]
  signed __int64 v20; // [rsp+B8h] [rbp+38h]
  double v21; // [rsp+C0h] [rbp+40h]
  double v22; // [rsp+C8h] [rbp+48h]
  double v23; // [rsp+D0h] [rbp+50h]
  double v24; // [rsp+D8h] [rbp+58h]
  double v25; // [rsp+E0h] [rbp+60h]
  double v26; // [rsp+E8h] [rbp+68h]
  double v27; // [rsp+F0h] [rbp+70h]
  double v28; // [rsp+F8h] [rbp+78h]
  double v29; // [rsp+100h] [rbp+80h]
  double v30; // [rsp+108h] [rbp+88h]
  double v31; // [rsp+110h] [rbp+90h]
  double v32; // [rsp+118h] [rbp+98h]
  double v33; // [rsp+120h] [rbp+A0h]
  double v34; // [rsp+128h] [rbp+A8h]
  double v35; // [rsp+130h] [rbp+B0h]
  double v36; // [rsp+138h] [rbp+B8h]
  double v37; // [rsp+140h] [rbp+C0h]
  double v38; // [rsp+148h] [rbp+C8h]
  char v39; // [rsp+157h] [rbp+D7h]
  _BYTE *v40; // [rsp+158h] [rbp+D8h]
  double v41; // [rsp+160h] [rbp+E0h]
  __int64 v42; // [rsp+168h] [rbp+E8h]

  v16[1] = "get_gate_cost";
  v18 = "D:\\TuringComplete_Phu\\model\\scores.nim";
  v17 = 0i64;
  v19 = 0;
  nimFrame_74(v16);
  v40 = (_BYTE *)nimErrorFlag_72();
  v42 = 0i64;
  v20 = a2;
  v17 = 378i64;
  v39 = 0;
  v39 = eqeq___modelZmodel95types_u853(a2, *(_QWORD *)refptr_AUTO_SIZE__modelZmodel95types_u54);
  if ( v39 != 1 || (v17 = 379i64, v20 = bits__modelZsave95mongerZcommon_u192(8i64), !*v40) )
  {
    v17 = 381i64;
    if ( a1 > 0x11u
      && (a1 <= 0x27u || a1 > 0x29u)
      && (a1 <= 0x2Au || a1 > 0x30u)
      && (a1 <= 0x32u || a1 > 0x35u)
      && (a1 <= 0x39u || a1 > 0x67u)
      && (a1 <= 0x68u || a1 > 0x6Bu)
      && (a1 <= 0x6Cu || a1 > 0x75u)
      && (a1 <= 0x77u || a1 > 0x7Cu) )
    {
      v17 = 384i64;
      switch ( a1 )
      {
        case 0x12u:
        case 0x13u:
        case 0x14u:
        case 0x15u:
        case 0x16u:
        case 0x17u:
        case 0x18u:
        case 0x1Au:
        case 0x27u:
        case 0x2Au:
        case 0x32u:
          v17 = 388i64;
          if ( a3 % 8 > 3 )
          {
            v17 = 391i64;
            v13 = a3 / 8 + 1;
            if ( __OFADD__(1i64, a3 / 8) )
              goto LABEL_42;
            v12 = v13 * v20;
            if ( !is_mul_ok(v13, v20) )
              goto LABEL_42;
            v11 = a3 % 8 - 8;
            if ( __OFSUB__(a3 % 8, 8i64) )
              goto LABEL_42;
            v10 = v12 + v11;
            if ( __OFADD__(v12, v11) )
              goto LABEL_42;
            v42 = v10;
          }
          else
          {
            v17 = 389i64;
            v15 = a3 / 8 * v20;
            if ( !is_mul_ok(a3 / 8, v20) )
              goto LABEL_42;
            v14 = v15 + a3 % 8;
            if ( __OFADD__(v15, a3 % 8) )
              goto LABEL_42;
            v42 = v14;
          }
          break;
        case 0x19u:
          v17 = 405i64;
          v8 = 2 * v20;
          if ( !is_mul_ok(2ui64, v20) )
            goto LABEL_42;
          v42 = v8;
          break;
        case 0x1Bu:
        case 0x1Cu:
        case 0x1Du:
        case 0x26u:
        case 0x68u:
          v23 = 0.0;
          v22 = 0.0;
          v17 = 399i64;
          if ( v20 <= 8 )
          {
            v17 = 402i64;
            v22 = (double)(int)a3 / 8.0;
            v41 = v22;
          }
          else
          {
            v17 = 400i64;
            v23 = (double)(int)a3 / 7.0;
            v41 = v23;
          }
          v17 = 403i64;
          v21 = 0.0;
          v21 = ceil(((double)(int)v20 - 8.0) * v41);
          v3 = (unsigned int)(int)v21;
          v9 = v3 + a3;
          if ( __OFADD__(v3, a3) )
            goto LABEL_42;
          v42 = v9;
          break;
        case 0x1Eu:
        case 0x31u:
        case 0x39u:
          v25 = (double)(int)a3 / 8.0;
          v17 = 395i64;
          v24 = 0.0;
          v24 = ceil((double)(int)v20 * v25);
          v42 = (unsigned int)(int)v24;
          break;
        case 0x1Fu:
        case 0x20u:
        case 0x6Cu:
          v17 = 420i64;
          if ( v20 <= 8 )
          {
            v28 = (double)(int)v20;
            v27 = (double)(int)a3 / 8.0;
            v17 = 427i64;
            v26 = 0.0;
            v26 = ceil(v27 * (double)(int)v20);
            v42 = (unsigned int)(int)v26;
          }
          else
          {
            v31 = (double)(int)v20 * (double)(int)v20;
            v30 = (double)(int)a3 / 64.0;
            v17 = 423i64;
            v29 = 0.0;
            v29 = ceil(v30 * v31);
            v42 = (unsigned int)(int)v29;
          }
          break;
        case 0x21u:
        case 0x22u:
        case 0x23u:
        case 0x24u:
        case 0x25u:
          v17 = 410i64;
          if ( v20 <= 8 )
          {
            v34 = (double)(int)v20;
            v33 = (double)(int)a3 / 8.0;
            v17 = 417i64;
            v32 = 0.0;
            v32 = ceil(v33 * (double)(int)v20);
            v42 = (unsigned int)(int)v32;
          }
          else
          {
            v17 = 411i64;
            v38 = 0.0;
            v38 = log2((double)(int)v20);
            v37 = (double)(int)v20 * v38;
            v36 = (double)(int)a3 / 24.0;
            v17 = 413i64;
            v35 = 0.0;
            v35 = ceil(v36 * v37);
            v42 = (unsigned int)(int)v35;
          }
          break;
        case 0x36u:
        case 0x38u:
          v17 = 429i64;
          v42 = 0i64;
          break;
        case 0x37u:
        case 0x77u:
          v17 = 407i64;
          v7 = 5 * v20;
          if ( is_mul_ok(5ui64, v20) )
            v42 = v7;
          else
LABEL_42:
            raiseOverflow();
          break;
        case 0x76u:
          v17 = 431i64;
          v5 = TM__cWnRfAoMBYzrX9aW9aZjMzkg_15;
          v6 = &TM__cWnRfAoMBYzrX9aW9aZjMzkg_14;
          failedAssertImpl__stdZassertions_u234(&v5);
          break;
        default:
          v17 = 433i64;
          v5 = TM__cWnRfAoMBYzrX9aW9aZjMzkg_17;
          v6 = &TM__cWnRfAoMBYzrX9aW9aZjMzkg_16;
          failedAssertImpl__stdZassertions_u234(&v5);
          break;
      }
    }
    else
    {
      v17 = 382i64;
      v42 = a3;
    }
  }
  popFrame_74();
  return v42;
}
