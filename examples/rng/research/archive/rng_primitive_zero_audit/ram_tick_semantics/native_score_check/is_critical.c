__int64 __fastcall is_critical__modelZsimulationZpreorder_u2464(__int64 *a1, __int64 *a2, __int64 a3, _QWORD *a4)
{
  __int64 v5; // rax
  __int64 v6; // rdx
  __int64 v7; // rdx
  __int64 v8; // r8
  __int64 v9; // rdx
  __int64 v10; // rcx
  __int64 v11; // rdx
  __int64 v13; // [rsp+0h] [rbp-F0h] BYREF
  __int64 v14; // [rsp+20h] [rbp-D0h] BYREF
  void *v15; // [rsp+28h] [rbp-C8h]
  __int64 v16; // [rsp+30h] [rbp-C0h] BYREF
  __int64 v17; // [rsp+38h] [rbp-B8h]
  __int64 v18; // [rsp+40h] [rbp-B0h]
  __int64 v19; // [rsp+50h] [rbp-A0h]
  void *v20; // [rsp+58h] [rbp-98h]
  const char *v21; // [rsp+68h] [rbp-88h]
  __int64 v22; // [rsp+70h] [rbp-80h]
  const char *v23; // [rsp+78h] [rbp-78h]
  __int16 v24; // [rsp+80h] [rbp-70h]
  __int64 v25; // [rsp+98h] [rbp-58h]
  char v26; // [rsp+A7h] [rbp-49h]
  __int64 v27; // [rsp+A8h] [rbp-48h]
  __int64 v28; // [rsp+B0h] [rbp-40h]
  __int64 *v29; // [rsp+B8h] [rbp-38h]
  __int64 *v30; // [rsp+C0h] [rbp-30h]
  __int64 *v31; // [rsp+C8h] [rbp-28h]
  _QWORD *v32; // [rsp+D0h] [rbp-20h]
  _BYTE *v33; // [rsp+D8h] [rbp-18h]
  __int64 v34; // [rsp+E0h] [rbp-10h]
  char v35; // [rsp+EEh] [rbp-2h]
  unsigned __int8 v36; // [rsp+EFh] [rbp-1h]

  v5 = *a2;
  v6 = a2[1];
  v19 = v5;
  v20 = (void *)v6;
  v21 = "is_critical";
  v23 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v22 = 0i64;
  v24 = 0;
  nimFrame_80(&v13 + 12);
  v33 = (_BYTE *)nimErrorFlag_78();
  v36 = 0;
  v32 = a4;
  v22 = 228i64;
  v23 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v35 = 0;
  v7 = a4[2];
  v16 = a4[1];
  v17 = v7;
  v18 = a4[3];
  v14 = v19;
  v15 = v20;
  v35 = contains__modelZsimulationZpreorder_u2519(&v16, &v14);
  if ( !*v33 )
  {
    if ( v35 != 1 )
      goto LABEL_25;
    v31 = 0i64;
    v14 = v19;
    v15 = v20;
    v31 = (__int64 *)X5BX5D___modelZsimulationZpreorder_u2983(v32 + 1, &v14);
    if ( !*v33 )
    {
      v8 = *v31;
      v9 = v32[5];
      v16 = v32[4];
      v17 = v9;
      v18 = v32[6];
      v35 = contains__modelZboardZboard_u12534(&v16, v8);
      if ( !*v33 )
      {
LABEL_25:
        if ( v35 != 1 )
        {
          v30 = 0i64;
          v29 = 0i64;
          v22 = 231i64;
          v23 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          v14 = v19;
          v15 = v20;
          v29 = (__int64 *)X5BX5D___modelZsimulationZpreorder_u3293(v32 + 7, &v14);
          if ( !*v33 )
          {
            v23 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            v34 = 0i64;
            v22 = 250i64;
            v28 = *v29;
            v27 = v28;
            v22 = 251i64;
            while ( v34 < v27 )
            {
              v22 = 231i64;
              v23 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
              if ( v34 < 0 || v34 >= *v29 )
              {
                raiseIndexError2(v34, *v29 - 1);
                break;
              }
              v30 = (__int64 *)(v29[1] + 8 * v34 + 8);
              v22 = 232i64;
              if ( a3 == *v30 )
              {
                v22 = 233i64;
              }
              else
              {
                v22 = 234i64;
                v26 = 0;
                v10 = *v30;
                v11 = a1[1];
                v16 = *a1;
                v17 = v11;
                v18 = a1[2];
                v26 = contains__modelZboardZboard_u12534(&v16, v10);
                if ( *v33 )
                  break;
                if ( v26 == 1 )
                {
                  v22 = 235i64;
                  v36 = 1;
                  break;
                }
              }
              v23 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v34;
              v22 = 254i64;
              v25 = *v29;
              if ( v25 != v27 )
              {
                v14 = TM__8dO79bDlK9csFzRs49cEE7wlw_195;
                v15 = &TM__8dO79bDlK9csFzRs49cEE7wlw_20;
                failedAssertImpl__stdZassertions_u234(&v14);
                if ( *v33 )
                  break;
              }
            }
          }
        }
        else
        {
          v22 = 229i64;
          v36 = 1;
        }
      }
    }
  }
  popFrame_80();
  return v36;
}
