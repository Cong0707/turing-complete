// address: 0x1401c05e5-0x1401c0d61
// name: parse_state__modelZsave95mongerZsave95monger_u73
__int64 __fastcall parse_state__modelZsave95mongerZsave95monger_u73(
        __int64 *a1,
        unsigned __int8 a2,
        unsigned __int8 a3,
        __int64 a4)
{
  __int64 v4; // rbx
  _QWORD *v5; // rax
  _QWORD *v6; // rax
  _QWORD *v7; // rax
  __int64 v9; // [rsp+0h] [rbp-90h] BYREF
  __int64 v10; // [rsp+20h] [rbp-70h] BYREF
  __int64 v11; // [rsp+28h] [rbp-68h]
  __int64 v12; // [rsp+30h] [rbp-60h]
  __int64 v13; // [rsp+38h] [rbp-58h]
  const char *v14; // [rsp+48h] [rbp-48h]
  __int64 v15; // [rsp+50h] [rbp-40h]
  const char *v16; // [rsp+58h] [rbp-38h]
  __int16 v17; // [rsp+60h] [rbp-30h]
  __int64 v18; // [rsp+78h] [rbp-18h]
  __int64 v19; // [rsp+80h] [rbp-10h]
  _BYTE *v20; // [rsp+88h] [rbp-8h]

  v4 = a1[1];
  v12 = *a1;
  v13 = v4;
  v14 = "parse_state";
  v16 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
  v15 = 0i64;
  v17 = 0;
  nimFrame_59(&v9 + 8);
  v20 = (_BYTE *)nimErrorFlag_57();
  nimZeroMem_43(a4, 1224i64);
  v16 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
  *(_QWORD *)(a4 + 112) = 99999i64;
  *(_QWORD *)(a4 + 120) = 99999i64;
  *(_BYTE *)(a4 + 128) = 1;
  v15 = 55i64;
  v19 = v12;
  if ( v12 )
  {
    v15 = 56i64;
    if ( v12 > 0 )
    {
      *(_BYTE *)(a4 + 1) = *(_BYTE *)(v13 + 8);
      v15 = 59i64;
      switch ( *(_BYTE *)(a4 + 1) )
      {
        case 0:
          v15 = 60i64;
          v10 = v12;
          v11 = v13;
          ((void (__fastcall *)(__int64 *, _QWORD, _QWORD, __int64))parse__modelZsave95mongerZversionsZv0_u1067)(
            &v10,
            a2,
            a3,
            a4);
          if ( !*v20 )
            goto LABEL_36;
          goto LABEL_37;
        case 1:
          v15 = 61i64;
          v10 = v12;
          v11 = v13;
          ((void (__fastcall *)(__int64 *, _QWORD, _QWORD, __int64))parse__modelZsave95mongerZversionsZv1_u124)(
            &v10,
            a2,
            a3,
            a4);
          if ( *v20 )
            goto LABEL_37;
          goto LABEL_36;
        case 2:
          v15 = 62i64;
          v10 = v12;
          v11 = v13;
          ((void (__fastcall *)(__int64 *, _QWORD, _QWORD, __int64))parse__modelZsave95mongerZversionsZv2_u111)(
            &v10,
            a2,
            a3,
            a4);
          if ( *v20 )
            goto LABEL_37;
          goto LABEL_36;
        case 3:
          v15 = 63i64;
          v10 = v12;
          v11 = v13;
          ((void (__fastcall *)(__int64 *, _QWORD, _QWORD, __int64))parse__modelZsave95mongerZversionsZv3_u91)(
            &v10,
            a2,
            a3,
            a4);
          if ( *v20 )
            goto LABEL_37;
          goto LABEL_36;
        case 4:
          v15 = 64i64;
          v10 = v12;
          v11 = v13;
          ((void (__fastcall *)(__int64 *, _QWORD, _QWORD, __int64))parse__modelZsave95mongerZversionsZv4_u91)(
            &v10,
            a2,
            a3,
            a4);
          if ( *v20 )
            goto LABEL_37;
          goto LABEL_36;
        case 5:
          v15 = 65i64;
          v10 = v12;
          v11 = v13;
          ((void (__fastcall *)(__int64 *, _QWORD, _QWORD, __int64))parse__modelZsave95mongerZversionsZv5_u91)(
            &v10,
            a2,
            a3,
            a4);
          if ( *v20 )
            goto LABEL_37;
          goto LABEL_36;
        case 6:
          v15 = 66i64;
          v10 = v12;
          v11 = v13;
          ((void (__fastcall *)(__int64 *, _QWORD, _QWORD, __int64))parse__modelZsave95mongerZversionsZv6_u94)(
            &v10,
            a2,
            a3,
            a4);
          if ( *v20 )
            goto LABEL_37;
          goto LABEL_36;
        case 7:
          v15 = 67i64;
          v10 = v12;
          v11 = v13;
          ((void (__fastcall *)(__int64 *, _QWORD, _QWORD, __int64))parse__modelZsave95mongerZversionsZv7_u2928)(
            &v10,
            a2,
            a3,
            a4);
          if ( *v20 )
            goto LABEL_37;
          goto LABEL_36;
        case 8:
          v15 = 68i64;
          v10 = v12;
          v11 = v13;
          ((void (__fastcall *)(__int64 *, _QWORD, _QWORD, __int64))parse__modelZsave95mongerZversionsZv8_u338)(
            &v10,
            a2,
            a3,
            a4);
          if ( *v20 )
            goto LABEL_37;
          goto LABEL_36;
        case 9:
          v15 = 69i64;
          v10 = v12;
          v11 = v13;
          ((void (__fastcall *)(__int64 *, _QWORD, _QWORD, __int64))parse__modelZsave95mongerZversionsZv9_u338)(
            &v10,
            a2,
            a3,
            a4);
          if ( *v20 )
            goto LABEL_37;
          goto LABEL_36;
        case 0xA:
          v15 = 70i64;
          v10 = v12;
          v11 = v13;
          ((void (__fastcall *)(__int64 *, _QWORD, _QWORD, __int64))parse__modelZsave95mongerZversionsZv10_u338)(
            &v10,
            a2,
            a3,
            a4);
          if ( *v20 )
            goto LABEL_37;
          goto LABEL_36;
        case 0xB:
          v15 = 71i64;
          v10 = v12;
          v11 = v13;
          ((void (__fastcall *)(__int64 *, _QWORD, _QWORD, __int64))parse__modelZsave95mongerZversionsZv11_u338)(
            &v10,
            a2,
            a3,
            a4);
          if ( *v20 )
            goto LABEL_37;
          goto LABEL_36;
        case 0xC:
          v15 = 72i64;
          v10 = v12;
          v11 = v13;
          ((void (__fastcall *)(__int64 *, _QWORD, _QWORD, __int64))parse__modelZsave95mongerZversionsZv12_u362)(
            &v10,
            a2,
            a3,
            a4);
          if ( *v20 )
            goto LABEL_37;
          goto LABEL_36;
        case 0xD:
          v15 = 73i64;
          v10 = v12;
          v11 = v13;
          ((void (__fastcall *)(__int64 *, _QWORD, _QWORD, __int64))parse__modelZsave95mongerZversionsZv13_u323)(
            &v10,
            a2,
            a3,
            a4);
          if ( *v20 )
            goto LABEL_37;
          goto LABEL_36;
        case 0xE:
          v15 = 74i64;
          v10 = v12;
          v11 = v13;
          ((void (__fastcall *)(__int64 *, _QWORD, _QWORD, __int64))parse__modelZsave95mongerZversionsZv14_u345)(
            &v10,
            a2,
            a3,
            a4);
          if ( *v20 )
            goto LABEL_37;
          goto LABEL_36;
        case 0xF:
          v15 = 75i64;
          v10 = v12;
          v11 = v13;
          parse__modelZsave95mongerZversionsZv15_u321(&v10, a2, a3, a4);
          if ( !*v20 )
            goto LABEL_36;
          goto LABEL_37;
        default:
LABEL_36:
          if ( *v20 )
          {
LABEL_37:
            v5 = (_QWORD *)nimBorrowCurrentException_0();
            if ( (unsigned __int8)isObjDisplayCheck_1(*v5, 2i64, 1721001728i64)
              || (v6 = (_QWORD *)nimBorrowCurrentException_0(),
                  (unsigned __int8)isObjDisplayCheck_1(*v6, 3i64, 1284213504i64))
              || (v7 = (_QWORD *)nimBorrowCurrentException_0(),
                  (unsigned __int8)isObjDisplayCheck_1(*v7, 3i64, 1425264640i64)) )
            {
              *v20 = 0;
              popCurrentException_1();
            }
          }
          if ( !*v20 )
            goto LABEL_42;
          return popFrame_59();
      }
    }
    raiseIndexError2(0i64, v12 - 1);
  }
  else
  {
LABEL_42:
    v15 = 79i64;
    if ( !*(_QWORD *)(a4 + 136) )
    {
      v15 = 80i64;
      *(_QWORD *)(a4 + 136) = 10000000i64;
    }
    v15 = 82i64;
    while ( !*(_QWORD *)(a4 + 80) )
    {
      v15 = 83i64;
      v18 = 0i64;
      v18 = rand__pureZrandom_u143(0x7FFFFFFFFFFFFFFFi64);
      if ( *v20 )
        break;
      *(_QWORD *)(a4 + 80) = v18;
    }
  }
  return popFrame_59();
}
