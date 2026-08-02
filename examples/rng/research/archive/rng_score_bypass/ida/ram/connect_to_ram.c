__int64 __fastcall connect_to_ram__modelZsimulationZpreorder_u16965(
        __int64 a1,
        __int64 a2,
        __int64 *a3,
        __int64 *a4,
        _QWORD *a5)
{
  __int64 v5; // rdx
  void *v6; // rdx
  __int64 v7; // rdx
  bool v8; // al
  __int64 v9; // rdx
  __int64 v10; // rax
  _QWORD *v11; // rax
  __int64 v12; // rbx
  __int64 v13; // rbx
  __int64 v14; // rbx
  __int64 v15; // rcx
  __int64 v16; // rcx
  void *v17; // rdx
  __int64 v18; // rcx
  __int64 v20; // [rsp+30h] [rbp-50h] BYREF
  __int64 v21; // [rsp+38h] [rbp-48h]
  __int64 v22; // [rsp+40h] [rbp-40h] BYREF
  void *v23; // [rsp+48h] [rbp-38h]
  __int64 v24; // [rsp+50h] [rbp-30h] BYREF
  __int64 v25; // [rsp+58h] [rbp-28h]
  __int64 v26; // [rsp+60h] [rbp-20h]
  __int64 v27; // [rsp+70h] [rbp-10h]
  void *v28; // [rsp+78h] [rbp-8h]
  __int64 v29; // [rsp+80h] [rbp+0h]
  void *v30; // [rsp+88h] [rbp+8h]
  __int64 v31[3]; // [rsp+90h] [rbp+10h] BYREF
  __int64 v32; // [rsp+A8h] [rbp+28h]
  __int64 v33; // [rsp+B0h] [rbp+30h]
  __int64 v34; // [rsp+B8h] [rbp+38h]
  __int64 v35; // [rsp+C8h] [rbp+48h]
  __int64 v36; // [rsp+D0h] [rbp+50h] BYREF
  char v37; // [rsp+D8h] [rbp+58h]
  __int64 v38; // [rsp+100h] [rbp+80h]
  void *v39; // [rsp+108h] [rbp+88h]
  void (__fastcall *v40)(__int64, __int64, __int64 *, __int64 *); // [rsp+110h] [rbp+90h] BYREF
  _QWORD *v41; // [rsp+118h] [rbp+98h]
  __int64 v42; // [rsp+120h] [rbp+A0h]
  _QWORD *v43; // [rsp+128h] [rbp+A8h]
  __int64 v44; // [rsp+138h] [rbp+B8h] BYREF
  __int64 (__fastcall *v45)(); // [rsp+140h] [rbp+C0h] BYREF
  _QWORD *v46; // [rsp+148h] [rbp+C8h]
  unsigned int v47; // [rsp+150h] [rbp+D0h]
  unsigned int v48; // [rsp+154h] [rbp+D4h]
  unsigned int v49; // [rsp+158h] [rbp+D8h]
  unsigned int v50; // [rsp+15Ch] [rbp+DCh]
  __int64 v51[2]; // [rsp+160h] [rbp+E0h] BYREF
  unsigned int v52; // [rsp+174h] [rbp+F4h]
  unsigned int v53; // [rsp+178h] [rbp+F8h]
  unsigned int v54; // [rsp+17Ch] [rbp+FCh]
  __int64 v55[2]; // [rsp+180h] [rbp+100h] BYREF
  unsigned int v56; // [rsp+194h] [rbp+114h]
  unsigned int v57; // [rsp+198h] [rbp+118h]
  unsigned int v58; // [rsp+19Ch] [rbp+11Ch]
  __int64 (__fastcall *v59)(); // [rsp+1A0h] [rbp+120h] BYREF
  _QWORD *v60; // [rsp+1A8h] [rbp+128h]
  unsigned int v61; // [rsp+1BCh] [rbp+13Ch]
  __int64 v62[2]; // [rsp+1C0h] [rbp+140h] BYREF
  char v63[8]; // [rsp+1D0h] [rbp+150h] BYREF
  const char *v64; // [rsp+1D8h] [rbp+158h]
  __int64 v65; // [rsp+1E0h] [rbp+160h]
  const char *v66; // [rsp+1E8h] [rbp+168h]
  __int16 v67; // [rsp+1F0h] [rbp+170h]
  __int64 (__fastcall *v68)(); // [rsp+200h] [rbp+180h] BYREF
  _QWORD *v69; // [rsp+208h] [rbp+188h]
  unsigned int v70; // [rsp+21Ch] [rbp+19Ch]
  __int64 v71; // [rsp+220h] [rbp+1A0h] BYREF
  __int64 v72; // [rsp+228h] [rbp+1A8h]
  __int64 v73[70]; // [rsp+230h] [rbp+1B0h] BYREF
  __int64 v74; // [rsp+460h] [rbp+3E0h] BYREF
  void *v75; // [rsp+468h] [rbp+3E8h]
  __int64 v76[71]; // [rsp+470h] [rbp+3F0h] BYREF
  __int64 v77; // [rsp+6A8h] [rbp+628h]
  __int64 v78; // [rsp+6B0h] [rbp+630h]
  __int64 v79; // [rsp+6B8h] [rbp+638h]
  __int64 v80; // [rsp+6C0h] [rbp+640h]
  __int64 v81; // [rsp+6C8h] [rbp+648h]
  __int64 v82; // [rsp+6D0h] [rbp+650h]
  __int64 v83; // [rsp+6D8h] [rbp+658h]
  __int64 v84; // [rsp+6E0h] [rbp+660h]
  __int64 v85; // [rsp+6E8h] [rbp+668h]
  char v86; // [rsp+6F6h] [rbp+676h]
  char v87; // [rsp+6F7h] [rbp+677h]
  _QWORD *v88; // [rsp+6F8h] [rbp+678h]
  _BYTE *v89; // [rsp+700h] [rbp+680h]
  __int64 v90; // [rsp+708h] [rbp+688h]
  bool v91; // [rsp+717h] [rbp+697h]
  __int64 v92; // [rsp+718h] [rbp+698h]

  v5 = a3[1];
  v29 = *a3;
  v30 = (void *)v5;
  v6 = (void *)a4[1];
  v27 = *a4;
  v28 = v6;
  v64 = "connect_to_ram";
  v66 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v65 = 0i64;
  v67 = 0;
  nimFrame_80(v63);
  v89 = (_BYTE *)nimErrorFlag_78();
  v88 = a5;
  nimZeroMem_60(v76, 560i64);
  v74 = 0i64;
  v75 = 0i64;
  nimZeroMem_60(v73, 560i64);
  v65 = 588i64;
  if ( a1 < 0 || a1 >= v88[12] )
  {
    raiseIndexError2(a1, v88[12] - 1i64);
LABEL_92:
    v65 = 593i64;
    v66 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
    v22 = v74;
    v23 = v75;
    eqdestroy___modelZsimulationZpreorder_u18715(&v22);
    return popFrame_80();
  }
  qmemcpy(v76, (const void *)(560 * a1 + v88[13] + 8), 0x230ui64);
  v65 = 589i64;
  v87 = 0;
  v7 = *((_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788 + 1);
  v24 = *(_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788;
  v25 = v7;
  v26 = *((_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788 + 2);
  v87 = contains__modelZboardZmemory95manager_u414(&v24, LOBYTE(v76[0]));
  if ( *v89 )
    goto LABEL_92;
  if ( v87 != 1 )
  {
    v92 = a2;
    v65 = 593i64;
    v22 = v29;
    v23 = v30;
    eqcopy___modelZsimulationZpreorder_u18718(&v74, &v22);
    v71 = v27;
    v72 = (__int64)v28;
    v65 = 596i64;
    v91 = 0;
    v86 = 0;
    v22 = v27;
    v23 = v28;
    v20 = NO_POINT__modelZsimulationZpreorder_u16964;
    v21 = 2147516416i64;
    v86 = eqeq___modelZsimulationZpreorder_u2792(&v22, &v20);
    v91 = v86 == 0;
    if ( !v86 )
    {
      v8 = LOBYTE(v76[0]) == 54 || LOBYTE(v76[0]) == 56;
      v91 = v8;
    }
    if ( v91 )
    {
      v65 = 597i64;
      v85 = v88[1];
      v84 = v85;
      v65 = 598i64;
      p3__modelZsimulationZpreorder_u1974(v62, v76[2], *(unsigned int *)((char *)v76 + 2));
      if ( *v89 )
        goto LABEL_92;
      v65 = 599i64;
      nimZeroMem_60(v31, 104i64);
      v61 = p__modelZmodel95types_u1460((unsigned int)(__int16)v72, (unsigned int)SWORD1(v72));
      if ( *v89 )
        goto LABEL_92;
      teleport_path__modelZsave95mongerZcommon_u5069(&v24, *(unsigned int *)((char *)v76 + 2), v61);
      v32 = v24;
      v33 = v25;
      v34 = v26;
      if ( *v89 )
        goto LABEL_92;
      v35 = 1i64;
      nimZeroMem_60(&v36, 8i64);
      v36 = 256i64;
      v37 = 1;
      add__modelZsave95mongerZcommon_u4119(v88 + 1, v31);
      v65 = 600i64;
      X5BX5Deq___modelZsimulationZpreorder_u17081(v88 + 14, a1, v84);
      if ( *v89 )
        goto LABEL_92;
      v65 = 601i64;
      nimZeroMem_60(&v59, 16i64);
      v59 = add_wire_pins__modelZsimulationZpreorder_u8791;
      v60 = v88;
      v22 = v62[0];
      v23 = (void *)v62[1];
      v20 = v71;
      v21 = v72;
      if ( v88 )
        ((void (__fastcall *)(__int64, __int64 *, __int64 *, _QWORD *))v59)(v84, &v22, &v20, v60);
      else
        ((void (__fastcall *)(__int64, __int64 *, __int64 *))v59)(v84, &v22, &v20);
      if ( *v89 )
        goto LABEL_92;
    }
    v65 = 603i64;
    if ( LOBYTE(v76[0]) == 54 )
    {
      v65 = 607i64;
      v58 = p__modelZmodel95types_u1460(1i64, 0i64);
      if ( *v89 )
        goto LABEL_92;
      v57 = rotate__modelZsave95mongerZcommon_u4629(v58, BYTE6(v76[0]));
      if ( *v89 )
        goto LABEL_92;
      v56 = plus___modelZsave95mongerZcommon_u4308(*(unsigned int *)((char *)v76 + 2), v57);
      if ( *v89 )
        goto LABEL_92;
      v65 = 605i64;
      p3__modelZsimulationZpreorder_u1974(v55, v76[2], v56);
      if ( *v89 )
        goto LABEL_92;
      v65 = 604i64;
      v22 = v55[0];
      v23 = (void *)v55[1];
      add__modelZsimulationZpreorder_u18530(&v74, &v22);
      v65 = 610i64;
      v92 = a1;
    }
    else
    {
      v65 = 612i64;
      if ( LOBYTE(v76[0]) == 56 )
      {
        v65 = 613i64;
        v53 = p__modelZmodel95types_u1460(0xFFFFFFFFi64, 0i64);
        if ( *v89 )
          goto LABEL_92;
        v52 = rotate__modelZsave95mongerZcommon_u4629(v53, BYTE6(v76[0]));
        if ( *v89 )
          goto LABEL_92;
        v54 = plus___modelZsave95mongerZcommon_u4308(*(unsigned int *)((char *)v76 + 2), v52);
        if ( *v89 )
          goto LABEL_92;
        v65 = 614i64;
        p3__modelZsimulationZpreorder_u1974(v51, v76[2], v54);
        if ( *v89 )
          goto LABEL_92;
        v83 = 0i64;
        v66 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v90 = 0i64;
        v82 = v74;
        v81 = v74;
        v65 = 251i64;
        while ( v90 < v81 )
        {
          v65 = 616i64;
          v66 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          if ( v90 < 0 || v90 >= v74 )
          {
            raiseIndexError2(v90, v74 - 1);
            goto LABEL_92;
          }
          v83 = (__int64)v75 + 16 * v90 + 8;
          v65 = 617i64;
          v80 = v88[1];
          v79 = v80;
          v65 = 618i64;
          nimZeroMem_60(v31, 104i64);
          v47 = p__modelZmodel95types_u1460((unsigned int)*(__int16 *)(v83 + 8), (unsigned int)*(__int16 *)(v83 + 10));
          if ( !*v89 )
          {
            teleport_path__modelZsave95mongerZcommon_u5069(&v24, v54, v47);
            v32 = v24;
            v33 = v25;
            v34 = v26;
            if ( !*v89 )
            {
              v35 = 1i64;
              nimZeroMem_60(&v36, 8i64);
              v36 = 256i64;
              v37 = 1;
              add__modelZsave95mongerZcommon_u4119(v88 + 1, v31);
              v65 = 619i64;
              X5BX5Deq___modelZsimulationZpreorder_u17081(v88 + 14, a1, v79);
              if ( !*v89 )
              {
                v65 = 620i64;
                nimZeroMem_60(&v45, 16i64);
                v45 = add_wire_pins__modelZsimulationZpreorder_u8791;
                v46 = v88;
                v22 = v51[0];
                v23 = (void *)v51[1];
                v9 = *(_QWORD *)(v83 + 8);
                v20 = *(_QWORD *)v83;
                v21 = v9;
                if ( v88 )
                  ((void (__fastcall *)(__int64, __int64 *, __int64 *, _QWORD *))v45)(v79, &v22, &v20, v46);
                else
                  ((void (__fastcall *)(__int64, __int64 *, __int64 *))v45)(v79, &v22, &v20);
                if ( !*v89 )
                {
                  v66 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                  ++v90;
                  v65 = 254i64;
                  v78 = v74;
                  if ( v74 == v81 )
                    continue;
                  v22 = TM__8dO79bDlK9csFzRs49cEE7wlw_31;
                  v23 = &TM__8dO79bDlK9csFzRs49cEE7wlw_20;
                  failedAssertImpl__stdZassertions_u234(&v22);
                  if ( !*v89 )
                    continue;
                }
              }
            }
          }
          goto LABEL_92;
        }
        v65 = 622i64;
        v66 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        setLen__modelZsimulationZpreorder_u18633(&v74, 0i64);
        v65 = 626i64;
        v50 = p__modelZmodel95types_u1460(1i64, 0i64);
        if ( *v89 )
          goto LABEL_92;
        v49 = rotate__modelZsave95mongerZcommon_u4629(v50, BYTE6(v76[0]));
        if ( *v89 )
          goto LABEL_92;
        v48 = plus___modelZsave95mongerZcommon_u4308(*(unsigned int *)((char *)v76 + 2), v49);
        if ( *v89 )
          goto LABEL_92;
        v65 = 624i64;
        p3__modelZsimulationZpreorder_u1974(&v71, v76[2], v48);
        if ( *v89 )
          goto LABEL_92;
      }
    }
    v65 = 629i64;
    v70 = p__modelZmodel95types_u1460(13i64, 2i64);
    if ( *v89 )
      goto LABEL_92;
    v65 = 631i64;
    if ( LOBYTE(v76[0]) == 56 )
    {
      v65 = 632i64;
      v70 = p__modelZmodel95types_u1460(13i64, 3i64);
      if ( *v89 )
        goto LABEL_92;
    }
    v65 = 634i64;
    nimZeroMem_60(&v68, 16i64);
    v68 = get_component_at_offset__modelZsimulationZpreorder_u16736;
    v69 = v88;
    v10 = v88
        ? ((__int64 (__fastcall *)(__int64 *, _QWORD, _QWORD *))v68)(v76, v70, v69)
        : ((__int64 (__fastcall *)(__int64 *, _QWORD))v68)(v76, v70);
    v77 = v10;
    if ( *v89 )
      goto LABEL_92;
    v65 = 635i64;
    if ( v77 < 0 || v77 >= v88[12] )
    {
LABEL_67:
      raiseIndexError2(v77, v88[12] - 1i64);
      goto LABEL_92;
    }
    qmemcpy(v73, (const void *)(560 * v77 + v88[13] + 8), sizeof(v73));
    v65 = 637i64;
    if ( LOBYTE(v73[0]) == 118 )
    {
      nimZeroMem_60(&v44, 8i64);
      v65 = 34i64;
      v66 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      if ( a1 >= 0 && a1 < v88[12] )
      {
        v65 = 639i64;
        v66 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        v43 = 0i64;
        v42 = 1i64;
        v43 = (_QWORD *)newSeqPayload(1i64, 48i64, 8i64);
        nimZeroMem_60(v31, 48i64);
        v65 = 294i64;
        v66 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
        v44 = eqdup___modelZsave95mongerZcommon_u3374(v73[1]);
        v31[0] = v44;
        v11 = v43;
        v12 = v31[1];
        v43[1] = v44;
        v11[2] = v12;
        v13 = v32;
        v11[3] = v31[2];
        v11[4] = v13;
        v14 = v34;
        v11[5] = v33;
        v11[6] = v14;
        v65 = 34i64;
        v66 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        v15 = v88[13] + 560 * a1 + 240 + 8;
        v22 = v42;
        v23 = v43;
        eqsink___modelZsave95mongerZversionsZv0_u305(v15, &v22);
        goto LABEL_92;
      }
    }
    else if ( LOBYTE(v73[0]) <= 0x76u && (LOBYTE(v73[0]) == 54 || LOBYTE(v73[0]) == 56) )
    {
      v65 = 641i64;
      v66 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      nimZeroMem_60(&v40, 16i64);
      v40 = (void (__fastcall *)(__int64, __int64, __int64 *, __int64 *))connect_to_ram__modelZsimulationZpreorder_u16965;
      v41 = v88;
      v22 = v74;
      v23 = v75;
      v20 = v71;
      v21 = v72;
      if ( v88 )
        ((void (__fastcall *)(__int64, __int64, __int64 *, __int64 *, _QWORD *))v40)(v77, v92, &v22, &v20, v41);
      else
        v40(v77, v92, &v22, &v20);
      if ( *v89 )
        goto LABEL_92;
      v65 = 34i64;
      v66 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      if ( a1 >= 0 && a1 < v88[12] )
      {
        if ( v77 >= 0 && v77 < v88[12] )
        {
          v16 = v88[13] + 560 * a1 + 240 + 8;
          v17 = *(void **)(v88[13] + 560 * v77 + 256);
          v22 = *(_QWORD *)(v88[13] + 560 * v77 + 248);
          v23 = v17;
          eqcopy___modelZsave95mongerZversionsZv0_u299(v16, &v22);
          goto LABEL_92;
        }
        goto LABEL_67;
      }
    }
    else if ( a1 >= 0 && a1 < v88[12] )
    {
      v39 = 0i64;
      v38 = 0i64;
      v39 = (void *)newSeqPayload(0i64, 48i64, 8i64);
      v18 = v88[13] + 560 * a1 + 240 + 8;
      v22 = v38;
      v23 = v39;
      eqsink___modelZsave95mongerZversionsZv0_u305(v18, &v22);
      goto LABEL_92;
    }
    raiseIndexError2(a1, v88[12] - 1i64);
    goto LABEL_92;
  }
  v65 = 593i64;
  v22 = v74;
  v23 = v75;
  eqdestroy___modelZsimulationZpreorder_u18715(&v22);
  return popFrame_80();
}
