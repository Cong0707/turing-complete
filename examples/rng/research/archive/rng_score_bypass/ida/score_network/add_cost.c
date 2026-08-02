__int64 __fastcall add_cost__modelZscores_u2110(unsigned __int8 a1, __int64 *a2)
{
  __int64 v2; // rax
  __int64 v3; // rdx
  __int64 v5; // [rsp+0h] [rbp-90h] BYREF
  __int64 v6; // [rsp+20h] [rbp-70h] BYREF
  __int64 v7; // [rsp+28h] [rbp-68h]
  __int64 v8; // [rsp+30h] [rbp-60h]
  __int64 v9; // [rsp+38h] [rbp-58h]
  const char *v10; // [rsp+48h] [rbp-48h]
  __int64 v11; // [rsp+50h] [rbp-40h]
  const char *v12; // [rsp+58h] [rbp-38h]
  __int16 v13; // [rsp+60h] [rbp-30h]
  __int64 v14; // [rsp+70h] [rbp-20h] BYREF
  __int64 v15; // [rsp+78h] [rbp-18h]
  _BYTE *v16; // [rsp+88h] [rbp-8h]

  v2 = *a2;
  v3 = a2[1];
  v8 = v2;
  v9 = v3;
  v10 = "add_cost";
  v12 = "D:\\TuringComplete_Phu\\model\\scores.nim";
  v11 = 0i64;
  v13 = 0;
  nimFrame_74(&v5 + 8);
  v16 = (_BYTE *)nimErrorFlag_72();
  v11 = 283i64;
  v12 = "D:\\TuringComplete_Phu\\model\\scores.nim";
  if ( ((TM__cWnRfAoMBYzrX9aW9aZjMzkg_47[a1 >> 3] >> (a1 & 7)) & 1) != 0 )
  {
    v11 = 284i64;
  }
  else
  {
    v11 = 286i64;
    v6 = v8;
    v7 = v9;
    insert_cost__modelZscores_u49(a1, &v6);
    if ( !*v16 )
    {
      v14 = v8;
      v15 = v9;
      v11 = 289i64;
      stareq___pureZtimes_u3584_1(&v14, 8i64);
      v11 = 291i64;
      switch ( a1 )
      {
        case 4u:
          v11 = 295i64;
          v6 = v14;
          v7 = v15;
          insert_cost__modelZscores_u49(0x14u, &v6);
          break;
        case 7u:
          v11 = 293i64;
          v6 = v14;
          v7 = v15;
          insert_cost__modelZscores_u49(0x13u, &v6);
          break;
        case 9u:
          v11 = 297i64;
          v6 = v14;
          v7 = v15;
          insert_cost__modelZscores_u49(0x16u, &v6);
          break;
        case 0xAu:
          v11 = 299i64;
          v6 = v14;
          v7 = v15;
          insert_cost__modelZscores_u49(0x17u, &v6);
          break;
        case 0xBu:
          v11 = 301i64;
          v6 = v14;
          v7 = v15;
          insert_cost__modelZscores_u49(0x18u, &v6);
          break;
        case 0x27u:
          v11 = 303i64;
          v6 = v8;
          v7 = v9;
          insert_cost__modelZscores_u49(0x32u, &v6);
          break;
        case 0x37u:
          v11 = 305i64;
          v6 = v14;
          v7 = v15;
          insert_cost__modelZscores_u49(0x77u, &v6);
          break;
        default:
          return popFrame_74();
      }
    }
  }
  return popFrame_74();
}
