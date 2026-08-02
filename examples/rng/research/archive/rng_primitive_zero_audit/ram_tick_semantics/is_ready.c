__int64 __fastcall is_ready__modelZsimulationZpreorder_u20904(__int64 a1, _QWORD *a2)
{
  __int64 v2; // rax
  _QWORD *v3; // rax
  __int64 v4; // rbx
  __int64 v5; // rbx
  __int64 v6; // rbx
  __int64 v7; // rbx
  __int64 v8; // rdx
  __int64 v10[2]; // [rsp+20h] [rbp-60h] BYREF
  __int64 v11[10]; // [rsp+30h] [rbp-50h] BYREF
  _QWORD v12[2]; // [rsp+80h] [rbp+0h] BYREF
  __int64 v13; // [rsp+90h] [rbp+10h]
  const char *v14; // [rsp+98h] [rbp+18h]
  __int16 v15; // [rsp+A0h] [rbp+20h]
  __int64 v16[72]; // [rsp+B0h] [rbp+30h] BYREF
  bool v17; // [rsp+2F7h] [rbp+277h]
  __int64 v18; // [rsp+2F8h] [rbp+278h]
  __int64 v19; // [rsp+300h] [rbp+280h]
  __int64 v20; // [rsp+308h] [rbp+288h]
  __int64 v21; // [rsp+310h] [rbp+290h]
  char v22; // [rsp+31Fh] [rbp+29Fh]
  _QWORD *v23; // [rsp+320h] [rbp+2A0h]
  _BYTE *v24; // [rsp+328h] [rbp+2A8h]
  __int64 v25; // [rsp+330h] [rbp+2B0h]
  unsigned __int8 v26; // [rsp+33Fh] [rbp+2BFh]

  v12[1] = "is_ready";
  v14 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v13 = 0i64;
  v15 = 0;
  nimFrame_80(v12);
  v24 = (_BYTE *)nimErrorFlag_78();
  v26 = 0;
  v23 = a2;
  nimZeroMem_60(v16, 560i64);
  v13 = 812i64;
  v14 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  if ( a1 >= 0 && a1 < v23[12] )
  {
    qmemcpy(v16, (const void *)(560 * a1 + v23[13] + 8), 0x230ui64);
    v13 = 814i64;
    if ( LOBYTE(v16[0]) == 78 )
    {
      v13 = 815i64;
      v26 = 1;
    }
    else
    {
      v13 = 817i64;
      if ( LOBYTE(v16[4]) != 1
        || ((v13 = 818i64, v22 = 0, !v23[32]) ? (v2 = 0i64) : (v2 = v23[32] + 8i64),
            (v22 = contains__modelZtranslations_u2303_5(v2, v23[31], v16[5])) != 0) )
      {
        v21 = 0i64;
        nimZeroMem_60(v11, 80i64);
        v14 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v25 = 0i64;
        v20 = v16[6];
        v19 = v16[6];
        v13 = 184i64;
        while ( v25 < v19 )
        {
          v13 = 821i64;
          v14 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          v21 = v25;
          if ( v25 < 0 || v25 >= v16[6] )
          {
            raiseIndexError2(v25, v16[6] - 1);
            goto LABEL_35;
          }
          v3 = (_QWORD *)(v16[7] + 80 * v25);
          v4 = v3[2];
          v11[0] = v3[1];
          v11[1] = v4;
          v5 = v3[4];
          v11[2] = v3[3];
          v11[3] = v5;
          v6 = v3[6];
          v11[4] = v3[5];
          v11[5] = v6;
          v7 = v3[8];
          v11[6] = v3[7];
          v11[7] = v7;
          v8 = v3[10];
          v11[8] = v3[9];
          v11[9] = v8;
          v13 = 822i64;
          if ( a1 < 0 || a1 >= v23[33] )
          {
            raiseIndexError2(a1, v23[33] - 1i64);
            goto LABEL_35;
          }
          if ( v21 < 0 || v21 >= *(_QWORD *)(v23[34] + 16 * a1 + 8) )
          {
            raiseIndexError2(v21, *(_QWORD *)(v23[34] + 16 * a1 + 8) - 1i64);
            goto LABEL_35;
          }
          v18 = *(_QWORD *)(*(_QWORD *)(v23[34] + 16 * a1 + 16) + 8 * v21 + 8);
          v13 = 823i64;
          if ( v18 < 0 || v18 >= v23[35] )
          {
            raiseIndexError2(v18, v23[35] - 1i64);
            goto LABEL_35;
          }
          if ( v18 >= v23[37] )
          {
            raiseIndexError2(v18, v23[37] - 1i64);
            goto LABEL_35;
          }
          v17 = *(_QWORD *)(v23[36] + 8 * v18 + 8) < *(__int16 *)(v23[38] + (v18 << 6) + 24);
          v13 = 825i64;
          if ( v17 )
          {
            v13 = 826i64;
            v26 = 0;
            goto LABEL_35;
          }
          v14 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          ++v25;
          v13 = 187i64;
          v16[71] = v16[6];
          if ( v16[6] != v19 )
          {
            v10[0] = TM__8dO79bDlK9csFzRs49cEE7wlw_59;
            v10[1] = (__int64)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
            failedAssertImpl__stdZassertions_u234(v10);
            if ( *v24 )
              goto LABEL_35;
          }
        }
        v14 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        v13 = 828i64;
        v26 = 1;
      }
      else
      {
        v13 = 819i64;
        v26 = 0;
      }
    }
  }
  else
  {
    raiseIndexError2(a1, v23[12] - 1i64);
  }
LABEL_35:
  popFrame_80();
  return v26;
}
