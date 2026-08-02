// address: 0x1401c0ff3-0x1401c270c
// name: add_component__modelZsave95mongerZsave95monger_u85
__int64 __fastcall add_component__modelZsave95mongerZsave95monger_u85(__int64 a1, unsigned __int8 *a2)
{
  void *v2; // rdx
  void *v3; // rdx
  void *v4; // rdx
  __int64 v5; // rdx
  __int64 v6; // rdx
  __int64 v7; // rax
  void *v8; // rdx
  void *v9; // rdx
  __int64 v10; // rdx
  __int64 v11; // rdx
  __int64 v12; // rdx
  __int64 v13; // rdx
  __int64 v15; // [rsp+20h] [rbp-60h] BYREF
  __int64 v16; // [rsp+28h] [rbp-58h]
  __int64 v17; // [rsp+30h] [rbp-50h]
  __int64 v18; // [rsp+40h] [rbp-40h] BYREF
  __int64 v19; // [rsp+48h] [rbp-38h]
  __int64 v20; // [rsp+50h] [rbp-30h] BYREF
  void *v21; // [rsp+58h] [rbp-28h]
  __int64 v22; // [rsp+60h] [rbp-20h]
  __int64 v23; // [rsp+68h] [rbp-18h] BYREF
  __int64 v24; // [rsp+70h] [rbp-10h] BYREF
  __int64 v25; // [rsp+78h] [rbp-8h]
  __int64 v26[2]; // [rsp+80h] [rbp+0h] BYREF
  __int64 v27; // [rsp+90h] [rbp+10h] BYREF
  _QWORD *v28; // [rsp+98h] [rbp+18h]
  char v29[8]; // [rsp+A0h] [rbp+20h] BYREF
  const char *v30; // [rsp+A8h] [rbp+28h]
  __int64 v31; // [rsp+B0h] [rbp+30h]
  const char *v32; // [rsp+B8h] [rbp+38h]
  __int16 v33; // [rsp+C0h] [rbp+40h]
  __int64 v34[2]; // [rsp+D0h] [rbp+50h] BYREF
  __int64 v35[3]; // [rsp+E0h] [rbp+60h] BYREF
  __int64 v36; // [rsp+F8h] [rbp+78h]
  __int64 v37; // [rsp+100h] [rbp+80h]
  char v38; // [rsp+10Fh] [rbp+8Fh]
  __int64 v39; // [rsp+110h] [rbp+90h]
  __int64 v40; // [rsp+118h] [rbp+98h]
  __int64 v41; // [rsp+120h] [rbp+A0h]
  __int64 v42; // [rsp+128h] [rbp+A8h]
  __int64 v43; // [rsp+130h] [rbp+B0h]
  __int64 v44; // [rsp+138h] [rbp+B8h]
  char v45; // [rsp+147h] [rbp+C7h]
  __int64 v46; // [rsp+148h] [rbp+C8h]
  __int64 v47; // [rsp+150h] [rbp+D0h]
  __int64 v48; // [rsp+158h] [rbp+D8h]
  __int64 v49; // [rsp+160h] [rbp+E0h]
  __int64 v50; // [rsp+168h] [rbp+E8h]
  __int64 v51; // [rsp+170h] [rbp+F0h]
  __int64 v52; // [rsp+178h] [rbp+F8h]
  __int64 v53; // [rsp+180h] [rbp+100h]
  __int64 v54; // [rsp+188h] [rbp+108h]
  __int64 v55; // [rsp+190h] [rbp+110h]
  _QWORD *v56; // [rsp+198h] [rbp+118h]
  __int64 v57; // [rsp+1A0h] [rbp+120h]
  __int64 v58; // [rsp+1A8h] [rbp+128h]
  __int64 v59; // [rsp+1B0h] [rbp+130h]
  __int64 v60; // [rsp+1B8h] [rbp+138h]
  __int64 *v61; // [rsp+1C0h] [rbp+140h]
  __int64 v62; // [rsp+1C8h] [rbp+148h]
  __int64 value__modelZsave95mongerZcommon_u3399; // [rsp+1D0h] [rbp+150h]
  _BYTE *v64; // [rsp+1D8h] [rbp+158h]
  __int64 v65; // [rsp+1E0h] [rbp+160h]
  __int64 v66; // [rsp+1E8h] [rbp+168h]
  __int64 v67; // [rsp+1F0h] [rbp+170h]
  __int64 v68; // [rsp+1F8h] [rbp+178h]

  v30 = "add_component";
  v32 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
  v31 = 0i64;
  v33 = 0;
  nimFrame_59(v29);
  v64 = (_BYTE *)nimErrorFlag_57();
  v31 = 86i64;
  v32 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
  add_component_kind__modelZsave95mongerZcommon_u5826(a1, *a2);
  if ( !*v64 )
  {
    v31 = 87i64;
    add_point__modelZsave95mongerZcommon_u5785(a1, *(unsigned int *)(a2 + 2));
    if ( !*v64 )
    {
      v31 = 88i64;
      add_u8__modelZsave95mongerZserialize_u343(a1, a2[6]);
      if ( !*v64 )
      {
        v31 = 89i64;
        value__modelZsave95mongerZcommon_u3399 = 0i64;
        value__modelZsave95mongerZcommon_u3399 = get_value__modelZsave95mongerZcommon_u3399(*((_QWORD *)a2 + 1));
        if ( !*v64 )
        {
          add_i64__modelZsave95mongerZserialize_u264(a1, value__modelZsave95mongerZcommon_u3399);
          if ( !*v64 )
          {
            v31 = 90i64;
            v2 = (void *)*((_QWORD *)a2 + 25);
            v20 = *((_QWORD *)a2 + 24);
            v21 = v2;
            add_string__modelZsave95mongerZserialize_u551(a1, &v20);
            if ( !*v64 )
            {
              v31 = 91i64;
              v3 = (void *)*((_QWORD *)a2 + 27);
              v20 = *((_QWORD *)a2 + 26);
              v21 = v3;
              add_string__modelZsave95mongerZserialize_u551(a1, &v20);
              if ( !*v64 )
              {
                v31 = 92i64;
                v62 = *((_QWORD *)a2 + 21);
                add_u16__modelZsave95mongerZserialize_u305(a1, v62);
                if ( !*v64 )
                {
                  v61 = 0i64;
                  v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                  v68 = 0i64;
                  v31 = 250i64;
                  v60 = *((_QWORD *)a2 + 21);
                  v59 = v60;
                  v31 = 251i64;
                  while ( v68 < v59 )
                  {
                    v31 = 93i64;
                    v32 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
                    if ( v68 < 0 || v68 >= *((_QWORD *)a2 + 21) )
                    {
                      raiseIndexError2(v68, *((_QWORD *)a2 + 21) - 1i64);
                      return popFrame_59();
                    }
                    v61 = (__int64 *)(*((_QWORD *)a2 + 22) + 8 * v68 + 8);
                    v31 = 94i64;
                    add_u64__modelZsave95mongerZserialize_u197(a1, *v61);
                    if ( !*v64 )
                    {
                      v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                      ++v68;
                      v31 = 254i64;
                      v58 = *((_QWORD *)a2 + 21);
                      if ( v58 == v59 )
                        continue;
                      v20 = TM__7f55D3VhdE1QIjyhrrkTCw_17;
                      v21 = &TM__7f55D3VhdE1QIjyhrrkTCw_8;
                      failedAssertImpl__stdZassertions_u234(&v20);
                      if ( !*v64 )
                        continue;
                    }
                    return popFrame_59();
                  }
                  v31 = 95i64;
                  v32 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
                  add_bytes__modelZsave95mongerZcommon_u5748(a1, *((_QWORD *)a2 + 46));
                  if ( !*v64 )
                  {
                    v31 = 96i64;
                    add_i16__modelZsave95mongerZserialize_u324(a1, (unsigned int)*((__int16 *)a2 + 92));
                    if ( !*v64 )
                    {
                      v31 = 97i64;
                      add_bits__modelZsave95mongerZcommon_u5741(a1, *((_QWORD *)a2 + 28));
                      if ( !*v64 )
                      {
                        v31 = 98i64;
                        add_bool__modelZsave95mongerZserialize_u190(a1, a2[472]);
                        if ( !*v64 )
                        {
                          v31 = 100i64;
                          if ( a2[480] == 2 )
                          {
                            v31 = 108i64;
                            if ( (a2[480] & 7) != 2i64 )
                            {
                              dollar___modelZsave95mongerZcommon_u3503(v34, a2[480]);
                              v20 = TM__7f55D3VhdE1QIjyhrrkTCw_19;
                              v21 = &TM__7f55D3VhdE1QIjyhrrkTCw_18;
                              v18 = v34[0];
                              v19 = v34[1];
                              raiseFieldErrorStr(&v20, &v18);
                              return popFrame_59();
                            }
                            add_i64__modelZsave95mongerZserialize_u264(a1, *((_QWORD *)a2 + 61));
                            if ( *v64 )
                              return popFrame_59();
                            v31 = 109i64;
                            if ( (a2[480] & 7) != 2i64 )
                            {
                              dollar___modelZsave95mongerZcommon_u3503(v35, a2[480]);
                              v20 = TM__7f55D3VhdE1QIjyhrrkTCw_20;
                              v21 = &TM__7f55D3VhdE1QIjyhrrkTCw_18;
                              v18 = v35[0];
                              v19 = v35[1];
                              raiseFieldErrorStr(&v20, &v18);
                              return popFrame_59();
                            }
                            add_i64__modelZsave95mongerZserialize_u264(a1, *((_QWORD *)a2 + 62));
                            if ( *v64 )
                              return popFrame_59();
                          }
                          else if ( a2[480] <= 2u )
                          {
                            if ( a2[480] )
                            {
                              v31 = 105i64;
                              add_i64__modelZsave95mongerZserialize_u264(a1, 0i64);
                              if ( *v64 )
                                return popFrame_59();
                              v31 = 106i64;
                              add_i64__modelZsave95mongerZserialize_u264(a1, -1i64);
                              if ( *v64 )
                                return popFrame_59();
                            }
                            else
                            {
                              v31 = 102i64;
                              add_i64__modelZsave95mongerZserialize_u264(a1, -1i64);
                              if ( *v64 )
                                return popFrame_59();
                              v31 = 103i64;
                              add_i64__modelZsave95mongerZserialize_u264(a1, 0i64);
                              if ( *v64 )
                                return popFrame_59();
                            }
                          }
                          v31 = 111i64;
                          add_bool__modelZsave95mongerZserialize_u190(a1, a2[376]);
                          if ( !*v64 )
                          {
                            v31 = 112i64;
                            add_init_data__modelZsave95mongerZcommon_u5755(a1, a2[377]);
                            if ( !*v64 )
                            {
                              v31 = 114i64;
                              v57 = *((_QWORD *)a2 + 30);
                              add_u16__modelZsave95mongerZserialize_u305(a1, v57);
                              if ( !*v64 )
                              {
                                v56 = 0i64;
                                v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                                v67 = 0i64;
                                v31 = 250i64;
                                v55 = *((_QWORD *)a2 + 30);
                                v54 = v55;
                                v31 = 251i64;
                                while ( v67 < v54 )
                                {
                                  v31 = 115i64;
                                  v32 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
                                  if ( v67 < 0 || v67 >= *((_QWORD *)a2 + 30) )
                                  {
                                    raiseIndexError2(v67, *((_QWORD *)a2 + 30) - 1i64);
                                    return popFrame_59();
                                  }
                                  v56 = (_QWORD *)(*((_QWORD *)a2 + 31) + 48 * v67 + 8);
                                  v31 = 116i64;
                                  v53 = 0i64;
                                  v53 = get_value__modelZsave95mongerZcommon_u3399(*v56);
                                  if ( !*v64 )
                                  {
                                    add_i64__modelZsave95mongerZserialize_u264(a1, v53);
                                    if ( !*v64 )
                                    {
                                      v31 = 117i64;
                                      v52 = 0i64;
                                      v52 = get_value__modelZsave95mongerZcommon_u3399(v56[1]);
                                      if ( !*v64 )
                                      {
                                        add_i64__modelZsave95mongerZserialize_u264(a1, v52);
                                        if ( !*v64 )
                                        {
                                          v31 = 118i64;
                                          v4 = (void *)v56[3];
                                          v20 = v56[2];
                                          v21 = v4;
                                          add_string__modelZsave95mongerZserialize_u551(a1, &v20);
                                          if ( !*v64 )
                                          {
                                            v31 = 119i64;
                                            add_i64__modelZsave95mongerZserialize_u264(a1, v56[4]);
                                            if ( !*v64 )
                                            {
                                              v31 = 120i64;
                                              add_bits__modelZsave95mongerZcommon_u5741(a1, v56[5]);
                                              if ( !*v64 )
                                              {
                                                v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                                                ++v67;
                                                v31 = 254i64;
                                                v51 = *((_QWORD *)a2 + 30);
                                                if ( v51 == v54 )
                                                  continue;
                                                v20 = TM__7f55D3VhdE1QIjyhrrkTCw_21;
                                                v21 = &TM__7f55D3VhdE1QIjyhrrkTCw_8;
                                                failedAssertImpl__stdZassertions_u234(&v20);
                                                if ( !*v64 )
                                                  continue;
                                              }
                                            }
                                          }
                                        }
                                      }
                                    }
                                  }
                                  return popFrame_59();
                                }
                                v31 = 122i64;
                                v32 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
                                v50 = 0i64;
                                v5 = *((_QWORD *)a2 + 54);
                                v15 = *((_QWORD *)a2 + 53);
                                v16 = v5;
                                v17 = *((_QWORD *)a2 + 55);
                                v50 = len__modelZsave95mongerZsave95monger_u171(&v15);
                                if ( !*v64 )
                                {
                                  add_u16__modelZsave95mongerZserialize_u305(a1, v50);
                                  if ( !*v64 )
                                  {
                                    v27 = 0i64;
                                    v28 = 0i64;
                                    nimZeroMem_43(v26, 16i64);
                                    v31 = 767i64;
                                    v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                                    v6 = *((_QWORD *)a2 + 54);
                                    v15 = *((_QWORD *)a2 + 53);
                                    v16 = v6;
                                    v17 = *((_QWORD *)a2 + 55);
                                    v49 = len__modelZsave95mongerZsave95monger_u171(&v15);
                                    if ( !*v64 )
                                    {
                                      v48 = 0i64;
                                      v47 = 0i64;
                                      v31 = 768i64;
                                      v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                                      v46 = *((_QWORD *)a2 + 53) - 1i64;
                                      v47 = v46;
                                      v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                                      v66 = 0i64;
                                      v31 = 97i64;
                                      while ( v66 <= v47 )
                                      {
                                        v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                                        v48 = v66;
                                        v31 = 769i64;
                                        if ( v66 < 0 || v48 >= *((_QWORD *)a2 + 53) )
                                        {
LABEL_72:
                                          raiseIndexError2(v48, *((_QWORD *)a2 + 53) - 1i64);
                                          return popFrame_59();
                                        }
                                        v45 = 0;
                                        v45 = isFilled__pureZcollectionsZtables_u31_0(*(_QWORD *)(*((_QWORD *)a2 + 54)
                                                                                                + 40 * v48
                                                                                                + 8));
                                        if ( *v64 )
                                          return popFrame_59();
                                        if ( v45 == 1 )
                                        {
                                          v31 = 1699i64;
                                          v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                                          if ( v48 < 0 )
                                            goto LABEL_72;
                                          if ( v48 >= *((_QWORD *)a2 + 53) )
                                            goto LABEL_72;
                                          v7 = *((_QWORD *)a2 + 54) + 40 * v48;
                                          v8 = *(void **)(v7 + 24);
                                          v20 = *(_QWORD *)(v7 + 16);
                                          v21 = v8;
                                          eqcopy___system_u2661(&v27, &v20);
                                          v31 = 170i64;
                                          if ( v48 < 0 || v48 >= *((_QWORD *)a2 + 53) )
                                            goto LABEL_72;
                                          v9 = *(void **)(*((_QWORD *)a2 + 54) + 40 * v48 + 40);
                                          v20 = *(_QWORD *)(*((_QWORD *)a2 + 54) + 40 * v48 + 32);
                                          v21 = v9;
                                          eqcopy___modelZsave95mongerZversionsZv7_u2173(v26, &v20);
                                          v31 = 124i64;
                                          v32 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
                                          v20 = v27;
                                          v21 = v28;
                                          add_string__modelZsave95mongerZserialize_u551(a1, &v20);
                                          if ( *v64 )
                                            return popFrame_59();
                                          v31 = 125i64;
                                          v20 = v26[0];
                                          v21 = (void *)v26[1];
                                          add_string__modelZsave95mongerZserialize_u551(a1, &v20);
                                          if ( *v64 )
                                            return popFrame_59();
                                          v31 = 771i64;
                                          v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                                          v44 = 0i64;
                                          v10 = *((_QWORD *)a2 + 54);
                                          v15 = *((_QWORD *)a2 + 53);
                                          v16 = v10;
                                          v17 = *((_QWORD *)a2 + 55);
                                          v44 = len__modelZsave95mongerZsave95monger_u171(&v15);
                                          if ( *v64 )
                                            return popFrame_59();
                                          if ( v44 != v49 )
                                          {
                                            v20 = TM__7f55D3VhdE1QIjyhrrkTCw_23;
                                            v21 = &TM__7f55D3VhdE1QIjyhrrkTCw_22;
                                            failedAssertImpl__stdZassertions_u234(&v20);
                                            if ( *v64 )
                                              return popFrame_59();
                                          }
                                        }
                                        v31 = 102i64;
                                        v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                                        v25 = v66 + 1;
                                        if ( __OFADD__(1i64, v66) )
                                        {
LABEL_79:
                                          raiseOverflow();
                                          return popFrame_59();
                                        }
                                        v66 = v25;
                                      }
                                      v31 = 170i64;
                                      v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                                      eqdestroy___modelZsave95mongerZversionsZv7_u2170(v26);
                                      v31 = 394i64;
                                      if ( v28 && (*v28 & 0x4000000000000000i64) == 0 )
                                        deallocShared(v28);
                                      v31 = 127i64;
                                      v32 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
                                      if ( *a2 == 78 )
                                      {
                                        v31 = 129i64;
                                        add_i64__modelZsave95mongerZserialize_u264(a1, *((_QWORD *)a2 + 49));
                                        if ( !*v64 )
                                        {
                                          v31 = 130i64;
                                          v43 = 0i64;
                                          v11 = *((_QWORD *)a2 + 51);
                                          v15 = *((_QWORD *)a2 + 50);
                                          v16 = v11;
                                          v17 = *((_QWORD *)a2 + 52);
                                          v43 = len__modelZsave95mongerZsave95monger_u538(&v15);
                                          if ( !*v64 )
                                          {
                                            add_u16__modelZsave95mongerZserialize_u305(a1, v43);
                                            if ( !*v64 )
                                            {
                                              nimZeroMem_43(&v24, 8i64);
                                              nimZeroMem_43(&v23, 8i64);
                                              v31 = 767i64;
                                              v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\coll"
                                                    "ections\\tables.nim";
                                              v12 = *((_QWORD *)a2 + 51);
                                              v15 = *((_QWORD *)a2 + 50);
                                              v16 = v12;
                                              v17 = *((_QWORD *)a2 + 52);
                                              v42 = len__modelZsave95mongerZsave95monger_u538(&v15);
                                              if ( !*v64 )
                                              {
                                                v41 = 0i64;
                                                v40 = 0i64;
                                                v31 = 768i64;
                                                v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\co"
                                                      "llections\\tables.nim";
                                                v39 = *((_QWORD *)a2 + 50) - 1i64;
                                                v40 = v39;
                                                v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                                                v65 = 0i64;
                                                v31 = 97i64;
                                                while ( v65 <= v40 )
                                                {
                                                  v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\"
                                                        "collections\\tables.nim";
                                                  v41 = v65;
                                                  v31 = 769i64;
                                                  if ( v65 < 0 || v41 >= *((_QWORD *)a2 + 50) )
                                                  {
LABEL_105:
                                                    raiseIndexError2(v41, *((_QWORD *)a2 + 50) - 1i64);
                                                    return popFrame_59();
                                                  }
                                                  v38 = 0;
                                                  v38 = isFilled__pureZcollectionsZtables_u31_0(*(_QWORD *)(*((_QWORD *)a2 + 51) + 24 * v41 + 8));
                                                  if ( *v64 )
                                                    return popFrame_59();
                                                  if ( v38 == 1 )
                                                  {
                                                    v31 = 131i64;
                                                    v32 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
                                                    if ( v41 < 0 )
                                                      goto LABEL_105;
                                                    if ( v41 >= *((_QWORD *)a2 + 50) )
                                                      goto LABEL_105;
                                                    v24 = *(_QWORD *)(*((_QWORD *)a2 + 51) + 24 * v41 + 16);
                                                    if ( v41 >= *((_QWORD *)a2 + 50) )
                                                      goto LABEL_105;
                                                    v23 = *(_QWORD *)(*((_QWORD *)a2 + 51) + 24 * v41 + 24);
                                                    v31 = 132i64;
                                                    v37 = 0i64;
                                                    v37 = get_value__modelZsave95mongerZcommon_u3399(v24);
                                                    if ( *v64 )
                                                      return popFrame_59();
                                                    add_i64__modelZsave95mongerZserialize_u264(a1, v37);
                                                    if ( *v64 )
                                                      return popFrame_59();
                                                    v31 = 133i64;
                                                    add_bits__modelZsave95mongerZcommon_u5741(a1, v23);
                                                    if ( *v64 )
                                                      return popFrame_59();
                                                    v31 = 771i64;
                                                    v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure"
                                                          "\\collections\\tables.nim";
                                                    v36 = 0i64;
                                                    v13 = *((_QWORD *)a2 + 51);
                                                    v15 = *((_QWORD *)a2 + 50);
                                                    v16 = v13;
                                                    v17 = *((_QWORD *)a2 + 52);
                                                    v36 = len__modelZsave95mongerZsave95monger_u538(&v15);
                                                    if ( *v64 )
                                                      return popFrame_59();
                                                    if ( v36 != v42 )
                                                    {
                                                      v20 = TM__7f55D3VhdE1QIjyhrrkTCw_25;
                                                      v21 = &TM__7f55D3VhdE1QIjyhrrkTCw_22;
                                                      failedAssertImpl__stdZassertions_u234(&v20);
                                                      if ( *v64 )
                                                        return popFrame_59();
                                                    }
                                                  }
                                                  v31 = 102i64;
                                                  v32 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system"
                                                        "\\iterators_1.nim";
                                                  v22 = v65 + 1;
                                                  if ( __OFADD__(1i64, v65) )
                                                    goto LABEL_79;
                                                  v65 = v22;
                                                }
                                              }
                                            }
                                          }
                                        }
                                      }
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  return popFrame_59();
}
