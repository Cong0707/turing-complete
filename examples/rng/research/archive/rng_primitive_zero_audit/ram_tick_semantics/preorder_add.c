__int64 __fastcall add__modelZsimulationZpreorder_u21027(__int64 *a1, __int64 *a2)
{
  __int64 result; // rax
  __int64 v3; // rcx
  __int64 v4; // [rsp+30h] [rbp-50h]
  __int64 v5; // [rsp+38h] [rbp-48h]
  __int64 v7; // [rsp+68h] [rbp-18h]
  bool v8; // [rsp+7Fh] [rbp-1h]

  v4 = *a2;
  v5 = a2[1];
  v7 = *a1;
  v8 = a1[1] == 0;
  if ( a1[1] )
  {
    if ( __OFADD__(1i64, v7) )
      return raiseOverflow();
    v8 = (__int64)(*(_QWORD *)a1[1] & 0xBFFFFFFFFFFFFFFFui64) < v7 + 1;
  }
  if ( v8 )
    a1[1] = prepareSeqAddUninit(v7, a1[1], 1, 16, 8i64);
  if ( __OFADD__(1i64, v7) )
    return raiseOverflow();
  *a1 = v7 + 1;
  v3 = a1[1] + 16 * v7;
  result = v4;
  *(_QWORD *)(v3 + 8) = v4;
  *(_QWORD *)(v3 + 16) = v5;
  return result;
}
