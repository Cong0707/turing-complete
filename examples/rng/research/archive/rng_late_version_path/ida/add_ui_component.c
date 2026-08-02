// address: 0x1405da5f4-0x1405db105
// name: add_component__presenterZutilitiesZhelper95functions_u5957
__int64 __fastcall add_component__presenterZutilitiesZhelper95functions_u5957(__int64 a1, unsigned __int8 *a2)
{
  int v2; // r8d
  __int64 v3; // r11
  int v4; // ecx
  char v5; // r11
  __int64 v6; // r9
  char v7; // r8
  unsigned __int8 v8; // cl
  __int64 v9; // rdx
  __int64 v10; // rdx
  __int64 v12[2]; // [rsp+A0h] [rbp+20h] BYREF
  __int64 v13; // [rsp+B0h] [rbp+30h] BYREF
  __int64 v14; // [rsp+B8h] [rbp+38h]
  __int64 v15[4]; // [rsp+C0h] [rbp+40h] BYREF
  __int64 v16[4]; // [rsp+E0h] [rbp+60h] BYREF
  __int64 v17[4]; // [rsp+100h] [rbp+80h] BYREF
  __int64 v18; // [rsp+120h] [rbp+A0h] BYREF
  __int64 v19; // [rsp+128h] [rbp+A8h]
  __int64 v20; // [rsp+130h] [rbp+B0h] BYREF
  __int64 v21; // [rsp+138h] [rbp+B8h]
  __int64 v22; // [rsp+140h] [rbp+C0h] BYREF
  __int64 v23; // [rsp+148h] [rbp+C8h]
  __int64 v24; // [rsp+150h] [rbp+D0h]
  char v25[8]; // [rsp+160h] [rbp+E0h] BYREF
  const char *v26; // [rsp+168h] [rbp+E8h]
  __int64 v27; // [rsp+170h] [rbp+F0h]
  const char *v28; // [rsp+178h] [rbp+F8h]
  __int16 v29; // [rsp+180h] [rbp+100h]
  __int64 v30; // [rsp+190h] [rbp+110h]
  __int64 v31; // [rsp+198h] [rbp+118h]
  __int64 v32[4]; // [rsp+1A0h] [rbp+120h] BYREF
  __int64 clamped_word_size__modelZboardZprototype95list_u4458; // [rsp+1C0h] [rbp+140h]
  __int64 v34; // [rsp+1C8h] [rbp+148h]
  __int64 v35[4]; // [rsp+1D0h] [rbp+150h] BYREF
  __int64 v36; // [rsp+1F0h] [rbp+170h]
  __int64 v37; // [rsp+1F8h] [rbp+178h]
  __int64 v38; // [rsp+200h] [rbp+180h] BYREF
  __int64 v39; // [rsp+208h] [rbp+188h]
  __int64 v40; // [rsp+210h] [rbp+190h] BYREF
  __int64 v41; // [rsp+218h] [rbp+198h]
  __int64 v42; // [rsp+220h] [rbp+1A0h] BYREF
  __int64 v43; // [rsp+228h] [rbp+1A8h]
  __int64 v44; // [rsp+230h] [rbp+1B0h] BYREF
  __int64 v45; // [rsp+238h] [rbp+1B8h]
  __int64 v46; // [rsp+240h] [rbp+1C0h]
  __int64 v47; // [rsp+250h] [rbp+1D0h] BYREF
  __int64 v48; // [rsp+258h] [rbp+1D8h]
  __int64 v49; // [rsp+260h] [rbp+1E0h]
  __int64 v50; // [rsp+270h] [rbp+1F0h] BYREF
  __int64 v51; // [rsp+278h] [rbp+1F8h]
  __int64 v52; // [rsp+280h] [rbp+200h]
  __int64 v53; // [rsp+290h] [rbp+210h]
  char can_place_component__modelZboardZboard_u9929; // [rsp+29Fh] [rbp+21Fh]
  _BYTE *v55; // [rsp+2A0h] [rbp+220h]
  unsigned __int8 v56; // [rsp+2AFh] [rbp+22Fh]

  v26 = "add_component";
  v28 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
  v27 = 0i64;
  v29 = 0;
  nimFrame_149(v25);
  v55 = (_BYTE *)nimErrorFlag_144();
  v56 = 0;
  nimZeroMem_121(&v50, 24i64);
  nimZeroMem_121(&v47, 24i64);
  nimZeroMem_121(&v44, 24i64);
  v42 = 0i64;
  v43 = 0i64;
  v40 = 0i64;
  v41 = 0i64;
  v38 = 0i64;
  v39 = 0i64;
  v36 = 0i64;
  v37 = 0i64;
  v27 = 352i64;
  v28 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  initHashSet__modelZboardZboard_u9946(&v22, 64i64);
  v50 = v22;
  v51 = v23;
  v52 = v24;
  if ( *v55 )
    goto LABEL_13;
  v27 = 829i64;
  v28 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
  can_place_component__modelZboardZboard_u9929 = 0;
  v2 = a2[6];
  v3 = *((_QWORD *)a2 + 49);
  v4 = *a2;
  v22 = v50;
  v23 = v51;
  v24 = v52;
  can_place_component__modelZboardZboard_u9929 = board_can_place_component__modelZboardZboard_u9929(
                                                   (int)a1 + 152,
                                                   v4,
                                                   v3,
                                                   0,
                                                   *(_DWORD *)(a2 + 2),
                                                   v2,
                                                   0,
                                                   (__int64)&v22);
  if ( *v55 )
  {
LABEL_13:
    v27 = 982i64;
    v28 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    v20 = v36;
    v21 = v37;
    eqdestroy___modelZsave95mongerZcommon_u5612(&v20);
    v27 = 934i64;
    v28 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v20 = v38;
    v21 = v39;
    eqdestroy___modelZboardZboard_u17903(&v20);
    v27 = 34i64;
    v28 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    v20 = v40;
    v21 = v41;
    eqdestroy___modelZsave95mongerZversionsZv0_u296(&v20);
    v27 = 119i64;
    v28 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
    v20 = v42;
    v21 = v43;
    eqdestroy___modelZsave95mongerZserialize_u455(&v20);
    v27 = 123i64;
    v28 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
    eqdestroy___modelZsave95mongerZsave95monger_u874(&v44);
    v27 = 131i64;
    eqdestroy___modelZsave95mongerZsave95monger_u895(&v47);
    v27 = 250i64;
    v28 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    eqdestroy___modelZboardZboard_u9871(&v50);
    goto LABEL_14;
  }
  if ( can_place_component__modelZboardZboard_u9929 )
  {
    v27 = 835i64;
    v28 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
    nimZeroMem_121(v35, 24i64);
    v27 = 841i64;
    v34 = new_permanent_id__modelZsave95mongerZcommon_u3402();
    if ( !*v55 )
    {
      v27 = 845i64;
      clamped_word_size__modelZboardZprototype95list_u4458 = get_clamped_word_size__modelZboardZprototype95list_u4458(
                                                               *a2,
                                                               *refptr_current_word_size__modelZmodel95types_u728,
                                                               0);
      if ( !*v55 )
      {
        nimZeroMem_121(v32, 24i64);
        LOBYTE(v32[0]) = 0;
        v27 = 1062i64;
        v28 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
        initTable__modelZboardZboard_u21145(&v22, 32i64);
        v47 = v22;
        v48 = v23;
        v49 = v24;
        if ( !*v55 )
        {
          v27 = 1065i64;
          initTable__modelZboardZboard_u21177(&v22, 32i64);
          v44 = v22;
          v45 = v23;
          v46 = v24;
          if ( !*v55 )
          {
            v27 = 1066i64;
            newSeq__modelZisa95specZexpressions_u2408(&v42, 0i64);
            v27 = 1068i64;
            newSeq__modelZboardZboard_u21234(&v40, 0i64);
            v27 = 835i64;
            v28 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
            v5 = a2[472];
            v6 = *((_QWORD *)a2 + 49);
            v7 = a2[6];
            v8 = *a2;
            v22 = v35[0];
            v23 = v35[1];
            v24 = v35[2];
            v9 = *((_QWORD *)a2 + 25);
            v20 = *((_QWORD *)a2 + 24);
            v21 = v9;
            v10 = *((_QWORD *)a2 + 27);
            v18 = *((_QWORD *)a2 + 26);
            v19 = v10;
            v17[0] = v32[0];
            v17[1] = v32[1];
            v17[2] = v32[2];
            v16[0] = v47;
            v16[1] = v48;
            v16[2] = v49;
            v15[0] = v44;
            v15[1] = v45;
            v15[2] = v46;
            v13 = v42;
            v14 = v43;
            v12[0] = v40;
            v12[1] = v41;
            v53 = board_add_component__modelZboardZboard_u21118(
                    a1 + 152,
                    v8,
                    &v22,
                    *(_DWORD *)(a2 + 2),
                    v7,
                    v34,
                    &v20,
                    &v18,
                    v6,
                    clamped_word_size__modelZboardZprototype95list_u4458,
                    v5,
                    v17,
                    v16,
                    0i64,
                    v15,
                    &v13,
                    0,
                    v12,
                    0);
            if ( !*v55 )
            {
              v27 = 850i64;
              v36 = 1i64;
              v37 = newSeqPayload(1i64, 8i64, 8i64);
              *(_QWORD *)(v37 + 8) = v53;
              v31 = 0i64;
              v30 = 0i64;
              v31 = newSeqPayload(0i64, 8i64, 8i64);
              v18 = v36;
              v19 = v37;
              v13 = v30;
              v14 = v31;
              board_commit_change__modelZboardZboard_u18603(&v20, a1 + 152, &v18, &v13);
              v38 = v20;
              v39 = v21;
              if ( !*v55 )
              {
                v27 = 851i64;
                add_undo_changes__modelZboardZboard_u17728(&v38);
                if ( !*v55 )
                  v56 = 1;
              }
            }
          }
        }
      }
    }
    goto LABEL_13;
  }
  v56 = 0;
  v27 = 982i64;
  v28 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
  v20 = v36;
  v21 = v37;
  eqdestroy___modelZsave95mongerZcommon_u5612(&v20);
  v27 = 934i64;
  v28 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  v20 = v38;
  v21 = v39;
  eqdestroy___modelZboardZboard_u17903(&v20);
  v27 = 34i64;
  v28 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
  v20 = v40;
  v21 = v41;
  eqdestroy___modelZsave95mongerZversionsZv0_u296(&v20);
  v27 = 119i64;
  v28 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
  v20 = v42;
  v21 = v43;
  eqdestroy___modelZsave95mongerZserialize_u455(&v20);
  v27 = 123i64;
  v28 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
  eqdestroy___modelZsave95mongerZsave95monger_u874(&v44);
  v27 = 131i64;
  eqdestroy___modelZsave95mongerZsave95monger_u895(&v47);
  v27 = 250i64;
  v28 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  eqdestroy___modelZboardZboard_u9871(&v50);
LABEL_14:
  popFrame_149();
  return v56;
}
