_QWORD *__fastcall get_output_z_value__modelZsimulationZcode95gen_u4011(_QWORD *a1, __int64 a2, __int64 a3, _QWORD *a4)
{
  _QWORD *v4; // rcx
  __int64 v5; // rdx
  __int64 v6; // rdx
  __int64 v7; // rdx
  void *v8; // rdx
  __int64 v10; // [rsp+0h] [rbp-80h] BYREF
  __int64 v11[2]; // [rsp+20h] [rbp-60h] BYREF
  __int64 v12; // [rsp+30h] [rbp-50h] BYREF
  __int64 v13; // [rsp+38h] [rbp-48h]
  __int64 v14; // [rsp+40h] [rbp-40h]
  __int64 v15; // [rsp+50h] [rbp-30h] BYREF
  __int64 v16; // [rsp+58h] [rbp-28h]
  __int64 v17; // [rsp+60h] [rbp-20h]
  const char *v18; // [rsp+78h] [rbp-8h]
  __int64 v19; // [rsp+80h] [rbp+0h]
  const char *v20; // [rsp+88h] [rbp+8h]
  __int16 v21; // [rsp+90h] [rbp+10h]
  void (__fastcall *v22)(__int64 *, __int64 *); // [rsp+A0h] [rbp+20h] BYREF
  _QWORD *v23; // [rsp+A8h] [rbp+28h]
  __int64 v24; // [rsp+B0h] [rbp+30h]
  __int64 v25; // [rsp+B8h] [rbp+38h]
  __int64 v26; // [rsp+C0h] [rbp+40h]
  __int64 v27; // [rsp+D0h] [rbp+50h] BYREF
  void *v28; // [rsp+D8h] [rbp+58h]
  char v29; // [rsp+EEh] [rbp+6Eh]
  char v30; // [rsp+EFh] [rbp+6Fh]
  _QWORD *v31; // [rsp+F0h] [rbp+70h]
  _BYTE *v32; // [rsp+F8h] [rbp+78h]

  v18 = "get_output_z_value";
  v20 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v19 = 0i64;
  v21 = 0;
  nimFrame_88(&v10 + 14);
  v32 = (_BYTE *)nimErrorFlag_86();
  v27 = 0i64;
  v28 = 0i64;
  v31 = a4;
  v19 = 398i64;
  v20 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  if ( a3 >= 0 && a3 < *(_QWORD *)(a2 + 48) )
  {
    v4 = (_QWORD *)(80 * a3 + *(_QWORD *)(a2 + 56));
    v5 = v4[3];
    v24 = v4[2];
    v25 = v5;
    v26 = v4[4];
    v19 = 399i64;
    v30 = 0;
    v6 = v31[8];
    v15 = v31[7];
    v16 = v6;
    v17 = v31[9];
    v12 = v24;
    v13 = v25;
    v14 = v26;
    v30 = contains__modelZsimulationZcode95gen_u3866(&v15, &v12);
    if ( !*v32 )
    {
      if ( v30 )
      {
        v19 = 403i64;
        nimZeroMem_66(&v22, 16i64);
        v22 = (void (__fastcall *)(__int64 *, __int64 *))get_output_z_value__modelZsimulationZcode95gen_u3951;
        v23 = v31;
        v12 = v24;
        v13 = v25;
        v14 = v26;
        if ( v31 )
        {
          ((void (__fastcall *)(__int64 *, __int64 *, _QWORD *))v22)(&v27, &v12, v23);
        }
        else
        {
          v22(v11, &v12);
          v27 = v11[0];
          v28 = (void *)v11[1];
        }
      }
      else
      {
        v19 = 400i64;
        v29 = 0;
        v7 = v31[5];
        v12 = v31[4];
        v13 = v7;
        v14 = v31[6];
        v15 = v24;
        v16 = v25;
        v17 = v26;
        v29 = contains__modelZsimulationZcode95gen_u3866(&v12, &v15);
        if ( !*v32 )
        {
          if ( v29 )
          {
            v19 = 402i64;
            v27 = 5i64;
            v28 = &TM__THWBxVSaWN2Zh7OMooFH0w_2021;
          }
          else
          {
            v19 = 401i64;
            v27 = 4i64;
            v28 = &TM__THWBxVSaWN2Zh7OMooFH0w_2019;
          }
        }
      }
    }
  }
  else
  {
    raiseIndexError2(a3, *(_QWORD *)(a2 + 48) - 1i64);
  }
  popFrame_88();
  v8 = v28;
  *a1 = v27;
  a1[1] = v8;
  return a1;
}
