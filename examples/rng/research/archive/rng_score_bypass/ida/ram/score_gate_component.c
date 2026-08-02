__int64 __fastcall get_gate_cost__modelZscores_u2304(unsigned __int8 *a1, __int64 a2)
{
  int v2; // eax
  bool v3; // dl
  char v5[304]; // [rsp+20h] [rbp-60h] BYREF
  __int64 v6; // [rsp+150h] [rbp+D0h]
  signed __int64 v7; // [rsp+5C8h] [rbp+548h]
  __int64 v8; // [rsp+5D0h] [rbp+550h]
  __int64 v9; // [rsp+5D8h] [rbp+558h]
  char v10[8]; // [rsp+5E0h] [rbp+560h] BYREF
  const char *v11; // [rsp+5E8h] [rbp+568h]
  __int64 v12; // [rsp+5F0h] [rbp+570h]
  const char *v13; // [rsp+5F8h] [rbp+578h]
  __int16 v14; // [rsp+600h] [rbp+580h]
  char v15; // [rsp+61Dh] [rbp+59Dh]
  char v16; // [rsp+61Eh] [rbp+59Eh]
  char v17; // [rsp+61Fh] [rbp+59Fh]
  _BYTE *v18; // [rsp+620h] [rbp+5A0h]
  __int64 gate_cost__modelZscores_u2232; // [rsp+628h] [rbp+5A8h]

  v11 = "get_gate_cost";
  v13 = "D:\\TuringComplete_Phu\\model\\scores.nim";
  v12 = 0i64;
  v14 = 0;
  nimFrame_74(v10);
  v18 = (_BYTE *)nimErrorFlag_72();
  gate_cost__modelZscores_u2232 = 0i64;
  v12 = 472i64;
  if ( a1[32] != 1 )
  {
    v12 = 474i64;
    if ( *a1 == 78 )
    {
      v12 = 476i64;
      v17 = 0;
      v17 = in_custom_prototypes__modelZboardZcustom95prototype95list_u9(*((_QWORD *)a1 + 49));
      if ( !*v18 && v17 == 1 )
      {
        nimZeroMem_54(v5, 1448i64);
        v12 = 477i64;
        get_custom_prototype__modelZboardZcustom95prototype95list_u451(*((_QWORD *)a1 + 49), v5);
        if ( !*v18 )
        {
          gate_cost__modelZscores_u2232 = v6;
          v12 = 170i64;
          v13 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        }
        eqdestroy___modelZboardZprototype95list_u3239(v5);
      }
    }
    else
    {
      v12 = 479i64;
      v13 = "D:\\TuringComplete_Phu\\model\\scores.nim";
      v2 = *a1;
      if ( v2 == 118 )
      {
        v12 = 481i64;
        if ( *((__int64 *)a1 + 21) > 0 )
        {
          if ( *(_QWORD *)(*((_QWORD *)a1 + 22) + 8i64) )
          {
            v12 = 484i64;
            gate_cost__modelZscores_u2232 = *((_QWORD *)a1 + 39);
          }
          else
          {
            v12 = 482i64;
            v3 = !is_mul_ok(0x32ui64, *((_QWORD *)a1 + 39));
            v9 = 50i64 * *((_QWORD *)a1 + 39);
            if ( v3 )
              raiseOverflow();
            else
              gate_cost__modelZscores_u2232 = v9;
          }
        }
        else
        {
          raiseIndexError2(0i64, *((_QWORD *)a1 + 21) - 1i64);
        }
      }
      else if ( *a1 <= 0x76u && (v2 == 54 || v2 == 56) )
      {
        v12 = 486i64;
        gate_cost__modelZscores_u2232 = *((_QWORD *)a1 + 35);
      }
      else
      {
        v12 = 488i64;
        v8 = bits__modelZsave95mongerZcommon_u192(0i64);
        if ( !*v18 )
        {
          v16 = 0;
          v16 = eqeq___modelZmodel95types_u853(*((_QWORD *)a1 + 29), v8);
          if ( v16 != 1 )
          {
            v12 = 492i64;
            gate_cost__modelZscores_u2232 = get_gate_cost__modelZscores_u2232(*a1, *((_QWORD *)a1 + 29), a2);
          }
          else
          {
            v12 = 489i64;
            v15 = 0;
            v15 = eqeq___modelZmodel95types_u853(
                    *((_QWORD *)a1 + 28),
                    *(_QWORD *)refptr_AUTO_SIZE__modelZmodel95types_u54);
            if ( v15 != 1 )
            {
              v12 = 491i64;
              gate_cost__modelZscores_u2232 = get_gate_cost__modelZscores_u2232(*a1, *((_QWORD *)a1 + 28), a2);
            }
            else
            {
              v12 = 490i64;
              v7 = bits__modelZsave95mongerZcommon_u192(8i64);
              if ( !*v18 )
                gate_cost__modelZscores_u2232 = get_gate_cost__modelZscores_u2232(*a1, v7, a2);
            }
          }
        }
      }
    }
  }
  else
  {
    v12 = 473i64;
    gate_cost__modelZscores_u2232 = 0i64;
  }
  popFrame_74();
  return gate_cost__modelZscores_u2232;
}
