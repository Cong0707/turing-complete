__int64 __fastcall connect__modelZsimulationZpreorder_u19843(__int64 *a1, _QWORD *a2)
{
  __int64 v2; // rbx
  __int64 v3; // rdx
  __int64 v4; // rdx
  __int64 v5; // r9
  __int64 v6; // rcx
  __int64 v8; // [rsp+0h] [rbp-E0h] BYREF
  __int64 v9; // [rsp+20h] [rbp-C0h] BYREF
  __int64 v10; // [rsp+28h] [rbp-B8h]
  __int64 v11; // [rsp+30h] [rbp-B0h] BYREF
  __int64 v12; // [rsp+38h] [rbp-A8h]
  __int64 v13; // [rsp+40h] [rbp-A0h]
  __int64 v14; // [rsp+50h] [rbp-90h]
  __int64 v15; // [rsp+58h] [rbp-88h]
  __int64 v16; // [rsp+60h] [rbp-80h]
  __int64 v17; // [rsp+68h] [rbp-78h]
  __int64 v18; // [rsp+70h] [rbp-70h]
  const char *v19; // [rsp+88h] [rbp-58h]
  __int64 v20; // [rsp+90h] [rbp-50h]
  const char *v21; // [rsp+98h] [rbp-48h]
  __int16 v22; // [rsp+A0h] [rbp-40h]
  char v23; // [rsp+B7h] [rbp-29h]
  __int64 v24; // [rsp+B8h] [rbp-28h]
  __int64 *v25; // [rsp+C0h] [rbp-20h]
  char v26; // [rsp+CFh] [rbp-11h]
  _QWORD *v27; // [rsp+D0h] [rbp-10h]
  _BYTE *v28; // [rsp+D8h] [rbp-8h]

  v2 = a1[1];
  v14 = *a1;
  v15 = v2;
  v19 = "connect";
  v21 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v20 = 0i64;
  v22 = 0;
  nimFrame_80(&v8 + 16);
  v28 = (_BYTE *)nimErrorFlag_78();
  v27 = a2;
  v20 = 733i64;
  v21 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v26 = 0;
  v3 = a2[18];
  v11 = a2[17];
  v12 = v3;
  v13 = a2[19];
  v9 = v14;
  v10 = v15;
  v26 = contains__modelZsimulationZpreorder_u2519(&v11, &v9);
  if ( !*v28 && v26 == 1 )
  {
    v20 = 734i64;
    v25 = 0i64;
    v9 = v14;
    v10 = v15;
    v25 = (__int64 *)X5BX5D___modelZsimulationZpreorder_u19952(v27 + 17, &v9);
    if ( !*v28 )
    {
      v4 = v25[1];
      v16 = *v25;
      v17 = v4;
      v18 = v25[2];
      v24 = v16;
      v20 = 737i64;
      if ( (_BYTE)v18 || (v20 = 738i64, incl__modelZboardZboard_u11061(v27 + 20, v24), !*v28) )
      {
        v20 = 740i64;
        v23 = 0;
        v5 = v27[26];
        if ( v27[27] )
          v6 = v27[27] + 8i64;
        else
          v6 = 0i64;
        v11 = v16;
        v12 = v17;
        v13 = v18;
        v23 = contains__modelZsimulationZpreorder_u20066(v6, v5, &v11);
        if ( !v23 )
        {
          v20 = 741i64;
          v11 = v16;
          v12 = v17;
          v13 = v18;
          add__modelZsimulationZpreorder_u20106(v27 + 26, &v11);
        }
      }
    }
  }
  return popFrame_80();
}
