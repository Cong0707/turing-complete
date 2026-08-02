__int64 __fastcall preorder__modelZsimulationZcompile95thread_u4293(__int64 a1, __int64 *a2, char a3)
{
  __int64 v3; // rax
  __int64 v4; // rdx
  __int64 v5; // rdx
  void *v6; // rdx
  void *v7; // rdx
  bool v8; // al
  void *v9; // rdx
  __int64 *address; // rax
  void *v11; // rdx
  void *v12; // rdx
  void *v13; // rdx
  void *v14; // rdx
  void *v15; // rdx
  __int64 v17; // [rsp+40h] [rbp-40h] BYREF
  _QWORD *v18; // [rsp+48h] [rbp-38h]
  __int64 v19[4]; // [rsp+50h] [rbp-30h] BYREF
  __int64 v20; // [rsp+70h] [rbp-10h] BYREF
  void *v21; // [rsp+78h] [rbp-8h]
  __int64 v22; // [rsp+80h] [rbp+0h]
  _QWORD *v23; // [rsp+88h] [rbp+8h]
  char v24[112]; // [rsp+90h] [rbp+10h] BYREF
  char v25[192]; // [rsp+100h] [rbp+80h] BYREF
  __int64 v26; // [rsp+1C0h] [rbp+140h]
  void *v27; // [rsp+1C8h] [rbp+148h]
  __int64 v28; // [rsp+330h] [rbp+2B0h] BYREF
  __int64 v29; // [rsp+338h] [rbp+2B8h]
  __int64 v30; // [rsp+340h] [rbp+2C0h] BYREF
  _QWORD *v31; // [rsp+348h] [rbp+2C8h]
  __int64 v32; // [rsp+350h] [rbp+2D0h] BYREF
  _QWORD *v33; // [rsp+358h] [rbp+2D8h]
  __int64 v34; // [rsp+360h] [rbp+2E0h] BYREF
  _QWORD *v35; // [rsp+368h] [rbp+2E8h]
  __int64 v36; // [rsp+370h] [rbp+2F0h]
  _QWORD *v37; // [rsp+378h] [rbp+2F8h]
  __int64 v38; // [rsp+380h] [rbp+300h]
  _QWORD *v39; // [rsp+388h] [rbp+308h]
  __int64 v40; // [rsp+390h] [rbp+310h] BYREF
  _QWORD *v41; // [rsp+398h] [rbp+318h]
  __int64 v42; // [rsp+3A0h] [rbp+320h] BYREF
  _QWORD *v43; // [rsp+3A8h] [rbp+328h]
  __int64 v44; // [rsp+3B8h] [rbp+338h] BYREF
  char v45[8]; // [rsp+3C0h] [rbp+340h] BYREF
  const char *v46; // [rsp+3C8h] [rbp+348h]
  __int64 v47; // [rsp+3D0h] [rbp+350h]
  const char *v48; // [rsp+3D8h] [rbp+358h]
  __int16 v49; // [rsp+3E0h] [rbp+360h]
  char v50[720]; // [rsp+6C0h] [rbp+640h] BYREF
  __int64 v51; // [rsp+990h] [rbp+910h] BYREF
  _QWORD *v52; // [rsp+998h] [rbp+918h]
  __int64 *v53; // [rsp+9A8h] [rbp+928h]
  __int64 *v54; // [rsp+9B0h] [rbp+930h]
  __int64 v55; // [rsp+9B8h] [rbp+938h]
  __int64 v56; // [rsp+9C0h] [rbp+940h]
  __int64 v57; // [rsp+9C8h] [rbp+948h]
  __int64 v58; // [rsp+9D0h] [rbp+950h]
  __int64 v59; // [rsp+9D8h] [rbp+958h]
  __int64 v60; // [rsp+9E0h] [rbp+960h]
  __int64 v61; // [rsp+9E8h] [rbp+968h]
  __int64 v62; // [rsp+9F0h] [rbp+970h]
  _QWORD *v63; // [rsp+9F8h] [rbp+978h]
  char *v64; // [rsp+A00h] [rbp+980h]
  char v65; // [rsp+A0Fh] [rbp+98Fh]
  unsigned __int64 v66; // [rsp+A10h] [rbp+990h]
  char v67; // [rsp+A1Fh] [rbp+99Fh]
  __int64 v68; // [rsp+A20h] [rbp+9A0h]
  __int64 v69; // [rsp+A28h] [rbp+9A8h]
  __int64 v70; // [rsp+A30h] [rbp+9B0h]
  __int64 v71; // [rsp+A38h] [rbp+9B8h]
  __int64 v72; // [rsp+A40h] [rbp+9C0h]
  __int64 v73; // [rsp+A48h] [rbp+9C8h]
  __int64 v74; // [rsp+A50h] [rbp+9D0h]
  _BYTE *v75; // [rsp+A58h] [rbp+9D8h]
  bool v76; // [rsp+A67h] [rbp+9E7h]
  __int64 v77; // [rsp+A68h] [rbp+9E8h]
  char v78; // [rsp+A77h] [rbp+9F7h]
  unsigned __int64 v79; // [rsp+A78h] [rbp+9F8h]
  __int64 v80; // [rsp+A80h] [rbp+A00h]
  __int64 v81; // [rsp+A88h] [rbp+A08h]

  v3 = *a2;
  v4 = a2[1];
  v22 = v3;
  v23 = (_QWORD *)v4;
  v46 = "preorder";
  v48 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
  v47 = 0i64;
  v49 = 0;
  nimFrame_89(v45);
  v75 = (_BYTE *)nimErrorFlag_87();
  v51 = 0i64;
  v52 = 0i64;
  nimZeroMem_67(v50, 720i64);
  nimZeroMem_67(v24, 104i64);
  nimZeroMem_67(&v44, 8i64);
  nimZeroMem_67(v25, 104i64);
  v74 = 0i64;
  v48 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v81 = 0i64;
  v47 = 183i64;
  v73 = *(_QWORD *)(a1 + 184);
  v72 = v73;
  v47 = 184i64;
  while ( v81 < v72 )
  {
    v74 = v81;
    v47 = 185i64;
    v48 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    if ( v81 < 0 || v81 >= *(_QWORD *)(a1 + 184) )
    {
      raiseIndexError2(v81, *(_QWORD *)(a1 + 184) - 1i64);
      goto LABEL_117;
    }
    eqcopy___modelZsave95mongerZcommon_u3692(v25, *(_QWORD *)(a1 + 192) + 104 * v81 + 8);
    v44 = v74;
    v47 = 185i64;
    v48 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    eqsink___modelZsave95mongerZcommon_u3698(v24, v25);
    eqwasMoved___modelZsave95mongerZcommon_u3686(v25);
    v47 = 492i64;
    v48 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
    set_wire_runtime_kind__modelZsave95mongerZcommon_u4222(a1 + 152, v44, 0i64);
    if ( !*v75 )
    {
      v48 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      ++v81;
      v47 = 187i64;
      v71 = *(_QWORD *)(a1 + 184);
      if ( v71 == v72 )
        continue;
      v20 = TM__nTvHpEr8JHyxC5V4m579axA_81;
      v21 = &TM__nTvHpEr8JHyxC5V4m579axA_80;
      failedAssertImpl__stdZassertions_u234(&v20);
      if ( !*v75 )
        continue;
    }
    goto LABEL_117;
  }
  v47 = 185i64;
  eqdestroy___modelZsave95mongerZcommon_u3689(v25);
  eqdestroy___modelZsave95mongerZcommon_u3689(v24);
  v47 = 494i64;
  v48 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
  *(_BYTE *)(a1 + 144) = 0;
  nimZeroMem_67(v25, 560i64);
  v70 = 0i64;
  v48 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v80 = 0i64;
  v47 = 183i64;
  v69 = *(_QWORD *)(a1 + 152);
  v68 = v69;
  v47 = 184i64;
  while ( v80 < v68 )
  {
    v70 = v80;
    v47 = 34i64;
    v48 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    if ( v80 < 0 || v80 >= *(_QWORD *)(a1 + 152) )
    {
      raiseIndexError2(v80, *(_QWORD *)(a1 + 152) - 1i64);
      break;
    }
    eqcopy___modelZsave95mongerZversionsZv0_u148(v25, *(_QWORD *)(a1 + 160) + 560 * v80 + 8);
    v47 = 497i64;
    v48 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
    if ( v25[0] == 59 || v25[0] == 41 )
    {
      v47 = 498i64;
      v67 = 0;
      v20 = v26;
      v21 = v27;
      v67 = is_complete__modelZcampaigns_u16328(&v20);
      if ( *v75 )
        break;
      if ( v67 != 1 )
      {
        v47 = 501i64;
        if ( v70 < 0 || v70 >= *(_QWORD *)(a1 + 152) )
        {
LABEL_100:
          raiseIndexError2(v70, *(_QWORD *)(a1 + 152) - 1i64);
          break;
        }
        if ( *(__int64 *)(*(_QWORD *)(a1 + 160) + 560 * v70 + 176) <= 0 )
        {
LABEL_24:
          raiseIndexError2(0i64, *(_QWORD *)(*(_QWORD *)(a1 + 160) + 560 * v70 + 176) - 1i64);
          break;
        }
        *(_QWORD *)(*(_QWORD *)(*(_QWORD *)(a1 + 160) + 560 * v70 + 184) + 8i64) = 0i64;
      }
      else
      {
        v47 = 499i64;
        if ( v70 < 0 || v70 >= *(_QWORD *)(a1 + 152) )
          goto LABEL_100;
        if ( *(__int64 *)(*(_QWORD *)(a1 + 160) + 560 * v70 + 176) <= 0 )
          goto LABEL_24;
        *(_QWORD *)(*(_QWORD *)(*(_QWORD *)(a1 + 160) + 560 * v70 + 184) + 8i64) = 1i64;
      }
      v47 = 502i64;
      if ( v25[0] == 41 )
      {
        v42 = 0i64;
        v43 = 0i64;
        v40 = 0i64;
        v41 = 0i64;
        v38 = 0i64;
        v39 = 0i64;
        v36 = 0i64;
        v37 = 0i64;
        v79 = -1i64;
        v47 = 505i64;
        dollar___systemZdollars_u14(&v40, v70);
        if ( *v75 )
          goto LABEL_69;
        v20 = v40;
        v21 = v41;
        get_level_local__modelZboardZschematics_u13832(&v42, &v20);
        if ( *v75 )
          goto LABEL_69;
        v47 = 506i64;
        if ( v42 )
        {
          v47 = 509i64;
          v66 = 0i64;
          v20 = v42;
          v21 = v43;
          v66 = nsuParseUInt(&v20);
          if ( *v75 || (v79 = v66, *v75) )
          {
            *v75 = 0;
            v47 = 510i64;
            raiseDefect();
            popCurrentException_9();
          }
          if ( *v75 )
            goto LABEL_69;
        }
        v47 = 512i64;
        v65 = 0;
        v65 = is_score_unlocked__modelZboardZschematics_u1782();
        if ( *v75 )
          goto LABEL_69;
        if ( v65 == 1 )
        {
          v47 = 513i64;
          v78 = 0;
          v5 = *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 1);
          v19[0] = *(_QWORD *)refptr_level_progress__modelZmodel95types_u825;
          v19[1] = v5;
          v19[2] = *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 2);
          v20 = v26;
          v21 = v27;
          v78 = contains__modelZcampaigns_u16380(v19, &v20);
          if ( *v75 )
            goto LABEL_69;
          if ( v78 == 1 )
          {
            v64 = 0i64;
            v20 = v26;
            v21 = v27;
            v64 = (char *)X5BX5D___modelZcampaigns_u16467(refptr_level_progress__modelZmodel95types_u825, &v20);
            if ( !*v75 )
            {
              v78 = *v64;
              goto LABEL_45;
            }
LABEL_69:
            v47 = 394i64;
            v48 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v37 && (*v37 & 0x4000000000000000i64) == 0 )
              deallocShared(v37);
            if ( v39 && (*v39 & 0x4000000000000000i64) == 0 )
              deallocShared(v39);
            if ( v41 && (*v41 & 0x4000000000000000i64) == 0 )
              deallocShared(v41);
            if ( v43 && (*v43 & 0x4000000000000000i64) == 0 )
              deallocShared(v43);
            if ( *v75 )
              break;
            goto LABEL_82;
          }
LABEL_45:
          if ( v78 == 1 )
          {
            v63 = 0i64;
            v30 = 0i64;
            v31 = 0i64;
            v47 = 514i64;
            v48 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
            v62 = 0i64;
            v20 = v26;
            v21 = v27;
            v62 = X5BX5D___modelZcampaigns_u16467(refptr_level_progress__modelZmodel95types_u825, &v20);
            if ( !*v75 )
            {
              v47 = 636i64;
              v48 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
              v6 = *(void **)(v62 + 56);
              v20 = *(_QWORD *)(v62 + 48);
              v21 = v6;
              eqcopy___modelZmodel95types_u4147(&v30, &v20);
              v48 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              v77 = 0i64;
              v61 = v30;
              v60 = v30;
              v47 = 251i64;
              while ( v77 < v60 )
              {
                v47 = 514i64;
                v48 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
                if ( v77 < 0 || v77 >= v30 )
                {
                  raiseIndexError2(v77, v30 - 1);
                  break;
                }
                v63 = &v31[3 * v77 + 1];
                v47 = 515i64;
                if ( v79 > v31[3 * v77 + 2] )
                {
                  v47 = 516i64;
                  v79 = v63[1];
                }
                v48 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                ++v77;
                v47 = 254i64;
                v59 = v30;
                if ( v30 != v60 )
                {
                  v20 = TM__nTvHpEr8JHyxC5V4m579axA_83;
                  v21 = &TM__nTvHpEr8JHyxC5V4m579axA_82;
                  failedAssertImpl__stdZassertions_u234(&v20);
                  if ( *v75 )
                    break;
                }
              }
            }
            v47 = 636i64;
            v48 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
            v20 = v30;
            v21 = v31;
            eqdestroy___modelZmodel95types_u4144(&v20);
            if ( *v75 )
              goto LABEL_69;
          }
        }
        v47 = 518i64;
        v48 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
        if ( v70 >= 0 && v70 < *(_QWORD *)(a1 + 152) )
        {
          if ( *(__int64 *)(*(_QWORD *)(a1 + 160) + 560 * v70 + 176) > 1 )
          {
            *(_QWORD *)(*(_QWORD *)(*(_QWORD *)(a1 + 160) + 560 * v70 + 184) + 16i64) = v79;
            v47 = 520i64;
            v34 = 0i64;
            v35 = 0i64;
            dollar___systemZdollars_u14(&v34, v70);
            if ( *v75 )
            {
              v20 = v34;
              v21 = v35;
              eqdestroy___system_u281_35(&v20);
            }
            else
            {
              v38 = v34;
              v39 = v35;
              v32 = 0i64;
              v33 = 0i64;
              dollar___systemZdollars_u59(&v32, v79);
              if ( *v75 )
              {
                v20 = v32;
                v21 = v33;
                eqdestroy___system_u281_35(&v20);
              }
              else
              {
                v36 = v32;
                v37 = v33;
                v20 = v38;
                v21 = v39;
                v17 = v32;
                v18 = v33;
                store_level_local__modelZboardZschematics_u13501(&v20, &v17);
              }
            }
          }
          else
          {
            raiseIndexError2(1i64, *(_QWORD *)(*(_QWORD *)(a1 + 160) + 560 * v70 + 176) - 1i64);
          }
        }
        else
        {
          raiseIndexError2(v70, *(_QWORD *)(a1 + 152) - 1i64);
        }
        goto LABEL_69;
      }
    }
LABEL_82:
    v47 = 522i64;
    v48 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
    v76 = 0;
    v58 = 0i64;
    v7 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
    v20 = *refptr_loaded_level__modelZmodel95types_u830;
    v21 = v7;
    v58 = X5BX5D___modelZboardZboard_u17368(refptr_campaign__modelZmodel95types_u817, &v20);
    if ( *v75 )
      break;
    v8 = *(_BYTE *)(v58 + 64) == 3 || *(_BYTE *)(v58 + 64) == 5;
    v76 = v8;
    if ( v8 )
    {
      v47 = 523i64;
      v76 = v25[0] == 62;
    }
    if ( v76 )
    {
      v47 = 524i64;
      v57 = 0i64;
      v9 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
      v20 = *refptr_loaded_level__modelZmodel95types_u830;
      v21 = v9;
      v57 = X5BX5D___modelZboardZboard_u17368(refptr_campaign__modelZmodel95types_u817, &v20);
      if ( *v75 )
        break;
      v29 = *(_QWORD *)(v57 + 512);
      v47 = 526i64;
      if ( v29 )
      {
        v47 = 529i64;
        if ( v70 < 0 || v70 >= *(_QWORD *)(a1 + 152) )
          goto LABEL_100;
        *(_QWORD *)(*(_QWORD *)(a1 + 160) + 560 * v70 + 232) = v29;
      }
      else
      {
        v47 = 527i64;
        if ( v70 < 0 || v70 >= *(_QWORD *)(a1 + 152) )
          goto LABEL_100;
        nimZeroMem_67(&v28, 8i64);
        v28 = bits__modelZsave95mongerZcommon_u192(8i64);
        if ( *v75 )
          break;
        *(_QWORD *)(*(_QWORD *)(a1 + 160) + 560 * v70 + 232) = v28;
      }
    }
    v48 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v80;
    v47 = 187i64;
    v56 = *(_QWORD *)(a1 + 152);
    if ( v56 != v68 )
    {
      v20 = TM__nTvHpEr8JHyxC5V4m579axA_84;
      v21 = &TM__nTvHpEr8JHyxC5V4m579axA_80;
      failedAssertImpl__stdZassertions_u234(&v20);
      if ( *v75 )
        break;
    }
  }
  v47 = 34i64;
  v48 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
  eqdestroy___modelZsave95mongerZversionsZv0_u145(v25);
  if ( !*v75 )
  {
    v47 = 1699i64;
    v48 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    address = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_level_path__modelZmodel95types_u78);
    v11 = (void *)address[1];
    v20 = *address;
    v21 = v11;
    eqcopy___system_u2661(&v51, &v20);
    v47 = 532i64;
    v48 = "D:\\TuringComplete_Phu\\model\\simulation\\compile_thread.nim";
    v55 = 0i64;
    v12 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
    v20 = *refptr_loaded_level__modelZmodel95types_u830;
    v21 = v12;
    v55 = X5BX5D___modelZboardZboard_u17368(refptr_campaign__modelZmodel95types_u817, &v20);
    if ( !*v75 )
    {
      if ( *(_BYTE *)(v55 + 64) == 3 )
      {
        v47 = 533i64;
        prepareAdd(&v51, *(_QWORD *)refptr_loaded_architecture__modelZmodel95types_u831);
        v13 = (void *)*((_QWORD *)refptr_loaded_architecture__modelZmodel95types_u831 + 1);
        v20 = *(_QWORD *)refptr_loaded_architecture__modelZmodel95types_u831;
        v21 = v13;
        appendString_30(&v51, &v20);
      }
      v47 = 536i64;
      if ( a3 == 1 )
      {
        v47 = 538i64;
        v54 = 0i64;
        v14 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
        v20 = *refptr_loaded_level__modelZmodel95types_u830;
        v21 = v14;
        v54 = (__int64 *)X5BX5D___modelZboardZboard_u17368(refptr_campaign__modelZmodel95types_u817, &v20);
        if ( *v75 )
          goto LABEL_117;
        v47 = 537i64;
        v20 = v51;
        v21 = v52;
        v17 = v22;
        v18 = v23;
        get_preorder_input__modelZsimulationZpreorder_u5002((_QWORD *)a1, v54, &v20, &v17, 0, 0, 0, (__int64)v50);
        if ( *v75 )
          goto LABEL_117;
LABEL_116:
        v47 = 545i64;
        compile_thread_send__modelZsimulationZcompile95thread_u3720(a1 + 152, v50);
        goto LABEL_117;
      }
      v47 = 542i64;
      v53 = 0i64;
      v15 = (void *)refptr_loaded_level__modelZmodel95types_u830[1];
      v20 = *refptr_loaded_level__modelZmodel95types_u830;
      v21 = v15;
      v53 = (__int64 *)X5BX5D___modelZboardZboard_u17368(refptr_campaign__modelZmodel95types_u817, &v20);
      if ( !*v75 )
      {
        v47 = 541i64;
        v20 = v51;
        v21 = v52;
        v17 = v22;
        v18 = v23;
        get_preorder_input__modelZsimulationZpreorder_u5002((_QWORD *)a1, v53, &v20, &v17, 0, 0, 0, (__int64)v50);
        if ( !*v75 )
          goto LABEL_116;
      }
    }
  }
LABEL_117:
  v47 = 326i64;
  v48 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  eqdestroy___modelZsimulationZpreorder_u8400(v50);
  v47 = 394i64;
  v48 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v52 && (*v52 & 0x4000000000000000i64) == 0 )
    deallocShared(v52);
  return popFrame_89();
}
