// address: 0x14061f93e-0x14061fc6c
// name: deserialize_package__modelZpk95save95mongerZpk95save95monger_u12
__int64 __fastcall deserialize_package__modelZpk95save95mongerZpk95save95monger_u12(
        __int64 *a1,
        __int64 *a2,
        __int64 *a3,
        __int64 *a4,
        __int64 *a5,
        unsigned __int8 a6,
        _BYTE *a7)
{
  __int64 v7; // rbx
  __int64 v8; // rax
  __int64 v9; // rdx
  __int64 v10; // rdx
  __int64 v11; // rdx
  __int64 v12; // rdx
  _QWORD *v13; // rax
  __int64 v15[2]; // [rsp+40h] [rbp-40h] BYREF
  __int64 v16[2]; // [rsp+50h] [rbp-30h] BYREF
  __int64 v17[2]; // [rsp+60h] [rbp-20h] BYREF
  __int64 v18[2]; // [rsp+70h] [rbp-10h] BYREF
  __int64 v19[3]; // [rsp+80h] [rbp+0h] BYREF
  unsigned __int8 v20; // [rsp+9Ch] [rbp+1Ch]
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
  char v31[8]; // [rsp+F0h] [rbp+70h] BYREF
  const char *v32; // [rsp+F8h] [rbp+78h]
  __int64 v33; // [rsp+100h] [rbp+80h]
  const char *v34; // [rsp+108h] [rbp+88h]
  __int16 v35; // [rsp+110h] [rbp+90h]
  char v36; // [rsp+12Fh] [rbp+AFh]
  __int64 v37; // [rsp+130h] [rbp+B0h]
  _BYTE *v38; // [rsp+138h] [rbp+B8h]

  v7 = a1[1];
  v29 = *a1;
  v30 = v7;
  v8 = *a2;
  v9 = a2[1];
  v27 = v8;
  v28 = v9;
  v10 = a3[1];
  v25 = *a3;
  v26 = v10;
  v11 = a4[1];
  v23 = *a4;
  v24 = v11;
  v12 = a5[1];
  v21 = *a5;
  v22 = v12;
  v20 = a6;
  v32 = "deserialize_package";
  v34 = "D:\\TuringComplete_Phu\\model\\pk_save_monger\\pk_save_monger.nim";
  v33 = 0i64;
  v35 = 0;
  nimFrame_158(v31);
  v38 = (_BYTE *)nimErrorFlag_153();
  nimZeroMem_129(a7, 64i64);
  v33 = 33i64;
  v34 = "D:\\TuringComplete_Phu\\model\\pk_save_monger\\pk_save_monger.nim";
  v37 = v29;
  if ( v29 > 0 )
  {
    v33 = 37i64;
    v36 = *(_BYTE *)(v30 + 8);
    v33 = 38i64;
    if ( v36 )
    {
      v33 = 45i64;
      nimZeroMem_129(a7, 64i64);
      *a7 = 3;
    }
    else
    {
      v33 = 40i64;
      v19[0] = v29;
      v19[1] = v30;
      v18[0] = v27;
      v18[1] = v28;
      v17[0] = v25;
      v17[1] = v26;
      v16[0] = v23;
      v16[1] = v24;
      v15[0] = v21;
      v15[1] = v22;
      deserialize__modelZpk95save95mongerZpk95versionsZv0_u52(
        (unsigned int)v19,
        (unsigned int)v18,
        (unsigned int)v17,
        (unsigned int)v16,
        (__int64)v15,
        v20,
        (__int64)a7);
      if ( *v38 )
      {
        v13 = (_QWORD *)nimBorrowCurrentException_9();
        if ( (unsigned __int8)isObjDisplayCheck_11(*v13, 3i64, 1284213504i64) )
        {
          *v38 = 0;
          v33 = 47i64;
          nimZeroMem_129(a7, 64i64);
          *a7 = 4;
          popCurrentException_14();
        }
      }
    }
  }
  else
  {
    v33 = 34i64;
    nimZeroMem_129(a7, 64i64);
    *a7 = 2;
  }
  return popFrame_158();
}
