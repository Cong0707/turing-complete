__int64 __fastcall input_size__modelZsimulationZpreorder_u2007(__int64 a1, _QWORD *a2)
{
  char v3[8]; // [rsp+20h] [rbp-40h] BYREF
  const char *v4; // [rsp+28h] [rbp-38h]
  __int64 v5; // [rsp+30h] [rbp-30h]
  const char *v6; // [rsp+38h] [rbp-28h]
  __int16 v7; // [rsp+40h] [rbp-20h]
  __int64 v8; // [rsp+50h] [rbp-10h]
  _QWORD *v9; // [rsp+58h] [rbp-8h]

  v4 = "input_size";
  v6 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v5 = 0i64;
  v7 = 0;
  nimFrame_80(v3);
  v9 = a2;
  v6 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v5 = 77i64;
  if ( (__int64)a2[5] >= 0 && v9[5] < v9[3] )
  {
    if ( a1 >= 0 && a1 < *(_QWORD *)(v9[4] + 16i64 * v9[5] + 8) )
    {
      if ( *(__int64 *)(*(_QWORD *)(v9[4] + 16i64 * v9[5] + 16) + 8 * a1 + 8) >= 0
        && *(_QWORD *)(*(_QWORD *)(v9[4] + 16i64 * v9[5] + 16) + 8 * a1 + 8) < v9[1] )
      {
        v8 = *(_QWORD *)(v9[2] + (*(_QWORD *)(*(_QWORD *)(v9[4] + 16i64 * v9[5] + 16) + 8 * a1 + 8) << 6) + 48i64);
      }
      else
      {
        raiseIndexError2(*(_QWORD *)(*(_QWORD *)(v9[4] + 16i64 * v9[5] + 16) + 8 * a1 + 8), v9[1] - 1i64);
      }
    }
    else
    {
      raiseIndexError2(a1, *(_QWORD *)(v9[4] + 16i64 * v9[5] + 8) - 1i64);
    }
  }
  else
  {
    raiseIndexError2(v9[5], v9[3] - 1i64);
  }
  popFrame_80();
  return v8;
}
