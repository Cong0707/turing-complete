__int64 __fastcall add_wire_pins__modelZsimulationZpreorder_u8791(__int64 a1, __int64 *a2, __int64 *a3, _QWORD *a4)
{
  __int64 v4; // rax
  __int64 v5; // rdx
  __int64 v6; // rdx
  __int64 v7; // rdx
  __int64 v8; // rdx
  __int64 v10; // [rsp+20h] [rbp-60h] BYREF
  __int64 v11; // [rsp+28h] [rbp-58h]
  __int64 v12; // [rsp+30h] [rbp-50h]
  __int64 v13; // [rsp+40h] [rbp-40h] BYREF
  __int64 v14; // [rsp+48h] [rbp-38h]
  __int64 v15; // [rsp+50h] [rbp-30h] BYREF
  __int64 v16; // [rsp+58h] [rbp-28h]
  __int64 v17; // [rsp+60h] [rbp-20h]
  __int64 v18; // [rsp+68h] [rbp-18h]
  __int64 v19; // [rsp+70h] [rbp-10h]
  __int64 v20; // [rsp+78h] [rbp-8h]
  __int64 v21; // [rsp+80h] [rbp+0h]
  __int64 v22; // [rsp+88h] [rbp+8h]
  __int64 v23; // [rsp+90h] [rbp+10h]
  __int64 v24; // [rsp+98h] [rbp+18h]
  char v25[8]; // [rsp+A0h] [rbp+20h] BYREF
  const char *v26; // [rsp+A8h] [rbp+28h]
  __int64 v27; // [rsp+B0h] [rbp+30h]
  const char *v28; // [rsp+B8h] [rbp+38h]
  __int16 v29; // [rsp+C0h] [rbp+40h]
  __int64 v30[4]; // [rsp+D0h] [rbp+50h] BYREF
  __int64 v31[2]; // [rsp+F0h] [rbp+70h] BYREF
  __int64 v32[2]; // [rsp+100h] [rbp+80h] BYREF
  __int64 v33; // [rsp+110h] [rbp+90h]
  __int64 v34; // [rsp+118h] [rbp+98h]
  __int64 v35; // [rsp+120h] [rbp+A0h]
  char v36; // [rsp+12Fh] [rbp+AFh]
  __int64 v37; // [rsp+130h] [rbp+B0h]
  __int64 v38; // [rsp+138h] [rbp+B8h]
  __int64 v39; // [rsp+140h] [rbp+C0h]
  char v40; // [rsp+14Eh] [rbp+CEh]
  char v41; // [rsp+14Fh] [rbp+CFh]
  _QWORD *v42; // [rsp+150h] [rbp+D0h]
  _BYTE *v43; // [rsp+158h] [rbp+D8h]

  v4 = *a2;
  v5 = a2[1];
  v19 = v4;
  v20 = v5;
  v6 = a3[1];
  v17 = *a3;
  v18 = v6;
  v26 = "add_wire_pins";
  v28 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v27 = 0i64;
  v29 = 0;
  nimFrame_80(v25);
  v43 = (_BYTE *)nimErrorFlag_78();
  v42 = a4;
  nimZeroMem_60(v32, 16i64);
  nimZeroMem_60(v31, 16i64);
  v27 = 370i64;
  v28 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  if ( a1 >= 0 && a1 < v42[1] )
  {
    v41 = 0;
    v41 = is_tombstone__modelZsave95mongerZcommon_u4884(v42[2] + 104 * a1 + 8);
    if ( !*v43 && v41 != 1 )
    {
      v27 = 71i64;
      v13 = v19;
      v14 = v20;
      eqdup___modelZsimulationZpreorder_u1987(&v15, &v13);
      v32[0] = v15;
      v32[1] = v16;
      v30[0] = v15;
      v30[1] = v16;
      v27 = 71i64;
      v13 = v17;
      v14 = v18;
      eqdup___modelZsimulationZpreorder_u1987(&v15, &v13);
      v31[0] = v15;
      v31[1] = v16;
      v30[2] = v15;
      v30[3] = v16;
      v27 = 371i64;
      X5BX5Deq___modelZsimulationZpreorder_u8831(v42 + 3, a1, v30);
      if ( !*v43 )
      {
        v27 = 373i64;
        v40 = 0;
        v7 = v42[7];
        v10 = v42[6];
        v11 = v7;
        v12 = v42[8];
        v15 = v19;
        v16 = v20;
        v40 = contains__modelZsimulationZpreorder_u9980(&v10, &v15);
        if ( !*v43 )
        {
          if ( v40 )
          {
            v38 = 0i64;
            v27 = 376i64;
            v37 = 0i64;
            v15 = v19;
            v16 = v20;
            v37 = X5BX5D___modelZsimulationZpreorder_u11211(v42 + 6, &v15);
            if ( *v43 )
              return popFrame_80();
            v38 = a1;
            add__modelZsave95mongerZcommon_u5717(v37, a1);
          }
          else
          {
            v39 = 0i64;
            v27 = 374i64;
            v24 = 0i64;
            v23 = 1i64;
            v24 = newSeqPayload(1i64, 8i64, 8i64);
            v39 = a1;
            *(_QWORD *)(v24 + 8) = a1;
            v15 = v19;
            v16 = v20;
            v13 = v23;
            v14 = v24;
            X5BX5Deq___modelZsimulationZpreorder_u10054(v42 + 6, &v15, &v13);
            if ( *v43 )
              return popFrame_80();
          }
          v27 = 378i64;
          v36 = 0;
          v8 = v42[7];
          v10 = v42[6];
          v11 = v8;
          v12 = v42[8];
          v15 = v17;
          v16 = v18;
          v36 = contains__modelZsimulationZpreorder_u9980(&v10, &v15);
          if ( !*v43 )
          {
            if ( v36 )
            {
              v34 = 0i64;
              v27 = 381i64;
              v33 = 0i64;
              v15 = v17;
              v16 = v18;
              v33 = X5BX5D___modelZsimulationZpreorder_u11211(v42 + 6, &v15);
              if ( !*v43 )
              {
                v34 = a1;
                add__modelZsave95mongerZcommon_u5717(v33, a1);
              }
            }
            else
            {
              v35 = 0i64;
              v27 = 379i64;
              v22 = 0i64;
              v21 = 1i64;
              v22 = newSeqPayload(1i64, 8i64, 8i64);
              v35 = a1;
              *(_QWORD *)(v22 + 8) = a1;
              v15 = v17;
              v16 = v18;
              v13 = v21;
              v14 = v22;
              X5BX5Deq___modelZsimulationZpreorder_u10054(v42 + 6, &v15, &v13);
            }
          }
        }
      }
    }
  }
  else
  {
    raiseIndexError2(a1, v42[1] - 1i64);
  }
  return popFrame_80();
}
