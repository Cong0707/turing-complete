__int64 __fastcall find_top_port__modelZsimulationZpreorder_u18852(__int64 a1, __int64 a2, __int64 a3)
{
  __int64 v3; // rcx
  __int64 v4; // rax
  __int64 v6[2]; // [rsp+30h] [rbp-50h] BYREF
  __int64 v7; // [rsp+40h] [rbp-40h] BYREF
  __int64 v8; // [rsp+48h] [rbp-38h]
  char v9[560]; // [rsp+50h] [rbp-30h] BYREF
  __int64 v10; // [rsp+280h] [rbp+200h]
  __int64 v11; // [rsp+288h] [rbp+208h]
  __int64 (__fastcall *v12)(__int64, __int64, __int64 *, __int64 *, _QWORD *); // [rsp+290h] [rbp+210h] BYREF
  _QWORD *v13; // [rsp+298h] [rbp+218h]
  __int64 (__fastcall *v14)(); // [rsp+2A0h] [rbp+220h] BYREF
  _QWORD *v15; // [rsp+2A8h] [rbp+228h]
  __int64 (__fastcall *v16)(); // [rsp+2B0h] [rbp+230h] BYREF
  _QWORD *v17; // [rsp+2B8h] [rbp+238h]
  unsigned int v18; // [rsp+2CCh] [rbp+24Ch]
  __int64 v19; // [rsp+2D0h] [rbp+250h]
  __int64 v20; // [rsp+2D8h] [rbp+258h]
  char v21[8]; // [rsp+2E0h] [rbp+260h] BYREF
  const char *v22; // [rsp+2E8h] [rbp+268h]
  __int64 v23; // [rsp+2F0h] [rbp+270h]
  const char *v24; // [rsp+2F8h] [rbp+278h]
  __int16 v25; // [rsp+300h] [rbp+280h]
  char v26[560]; // [rsp+310h] [rbp+290h] BYREF
  __int64 v27; // [rsp+540h] [rbp+4C0h]
  __int64 v28; // [rsp+548h] [rbp+4C8h]
  _QWORD *v29; // [rsp+550h] [rbp+4D0h]
  _BYTE *v30; // [rsp+558h] [rbp+4D8h]

  v22 = "find_top_port";
  v24 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v23 = 0i64;
  v25 = 0;
  nimFrame_80(v21);
  v30 = (_BYTE *)nimErrorFlag_78();
  v29 = (_QWORD *)a3;
  nimZeroMem_60(v26, 560i64);
  v23 = 647i64;
  if ( a1 < 0 || a1 >= v29[12] )
  {
LABEL_3:
    raiseIndexError2(a1, v29[12] - 1i64);
    return popFrame_80();
  }
  qmemcpy(v26, (const void *)(560 * a1 + v29[13] + 8), sizeof(v26));
  v23 = 649i64;
  if ( v26[272] == 1 )
  {
    v23 = 34i64;
    v24 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    if ( a1 >= 0 && a1 < v29[12] )
    {
      v20 = 0i64;
      v19 = 0i64;
      v20 = newSeqPayload(0i64, 48i64, 8i64);
      v3 = v29[13] + 560 * a1 + 240 + 8;
      v7 = v19;
      v8 = v20;
      eqsink___modelZsave95mongerZversionsZv0_u305(v3, &v7);
      v23 = 651i64;
      v24 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      return popFrame_80();
    }
    goto LABEL_3;
  }
  v23 = 653i64;
  if ( v26[0] == 54 || v26[0] == 56 )
  {
    v28 = 0i64;
    nimZeroMem_60(v9, 560i64);
    v23 = 654i64;
    v28 = a1;
    add__modelZsave95mongerZcommon_u5717(a2, a1);
    v23 = 656i64;
    v18 = p__modelZmodel95types_u1460(13i64, 0xFFFFFFFFi64);
    if ( !*v30 )
    {
      v23 = 658i64;
      nimZeroMem_60(&v16, 16i64);
      v16 = get_component_at_offset__modelZsimulationZpreorder_u16736;
      v17 = v29;
      v4 = v29
         ? ((__int64 (__fastcall *)(char *, _QWORD, _QWORD *))v16)(v26, v18, v17)
         : ((__int64 (__fastcall *)(char *, _QWORD))v16)(v26, v18);
      v27 = v4;
      if ( !*v30 )
      {
        v23 = 659i64;
        if ( v27 >= 0 && v27 < v29[12] )
        {
          qmemcpy(v9, (const void *)(560 * v27 + v29[13] + 8), sizeof(v9));
          v23 = 661i64;
          if ( v9[0] == 54 || v9[0] == 56 )
          {
            v23 = 662i64;
            nimZeroMem_60(&v14, 16i64);
            v14 = find_top_port__modelZsimulationZpreorder_u18852;
            v15 = v29;
            if ( v29 )
              ((void (__fastcall *)(__int64, __int64, _QWORD *))v14)(v27, a2, v15);
            else
              ((void (__fastcall *)(__int64, __int64))v14)(v27, a2);
          }
          else
          {
            v23 = 664i64;
            nimZeroMem_60(&v12, 16i64);
            v12 = connect_to_ram__modelZsimulationZpreorder_u16965;
            v13 = v29;
            v11 = 0i64;
            v10 = 0i64;
            v11 = newSeqPayload(0i64, 16i64, 8i64);
            v7 = v10;
            v8 = v11;
            v6[0] = NO_POINT__modelZsimulationZpreorder_u16964;
            v6[1] = 2147516416i64;
            if ( v13 )
              v12(a1, 0i64, &v7, v6, v13);
            else
              ((void (__fastcall *)(__int64, _QWORD, __int64 *, __int64 *))v12)(a1, 0i64, &v7, v6);
          }
        }
        else
        {
          raiseIndexError2(v27, v29[12] - 1i64);
        }
      }
    }
  }
  return popFrame_80();
}
