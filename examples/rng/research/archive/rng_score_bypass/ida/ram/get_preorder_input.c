__int64 __fastcall get_preorder_input__modelZsimulationZpreorder_u5002(
        _QWORD *a1,
        __int64 *a2,
        __int64 *a3,
        __int64 *a4,
        char a5,
        int a6,
        int a7,
        __int64 a8)
{
  __int64 v8; // rdx
  __int64 v9; // rdx
  _QWORD *v10; // rdx
  _QWORD *v11; // rdx
  _QWORD *v12; // rdx
  _QWORD *v13; // rdx
  _QWORD *v14; // rdx
  __int64 v15; // rdx
  _QWORD *v16; // rdx
  __int64 v17; // rdx
  __int64 v18; // rdx
  __int64 v19; // rdx
  _QWORD *v20; // rdx
  __int64 v21; // rdx
  void *v22; // rdx
  __int64 *address; // rax
  _QWORD *v24; // rdx
  __int64 v25; // rdx
  _QWORD *v26; // rdx
  __int64 v28; // [rsp+20h] [rbp-60h] BYREF
  __int64 v29; // [rsp+28h] [rbp-58h]
  __int64 v30; // [rsp+30h] [rbp-50h]
  __int64 v31; // [rsp+40h] [rbp-40h] BYREF
  _QWORD *v32; // [rsp+48h] [rbp-38h]
  char v33; // [rsp+5Ch] [rbp-24h]
  __int64 v34; // [rsp+60h] [rbp-20h]
  _QWORD *v35; // [rsp+68h] [rbp-18h]
  __int64 v36; // [rsp+70h] [rbp-10h]
  _QWORD *v37; // [rsp+78h] [rbp-8h]
  char v38[2]; // [rsp+80h] [rbp+0h] BYREF
  unsigned int v39; // [rsp+82h] [rbp+2h]
  unsigned __int8 v40; // [rsp+86h] [rbp+6h]
  __int64 v41; // [rsp+208h] [rbp+188h]
  char v42[24]; // [rsp+2B0h] [rbp+230h] BYREF
  __int64 v43; // [rsp+2C8h] [rbp+248h]
  __int64 v44; // [rsp+2D0h] [rbp+250h]
  __int64 v45; // [rsp+2D8h] [rbp+258h]
  __int64 v46[3]; // [rsp+2F8h] [rbp+278h] BYREF
  __int64 v47[4]; // [rsp+310h] [rbp+290h] BYREF
  __int64 v48; // [rsp+330h] [rbp+2B0h]
  __int64 v49; // [rsp+338h] [rbp+2B8h]
  char v50[96]; // [rsp+860h] [rbp+7E0h] BYREF
  __int64 v51; // [rsp+8C0h] [rbp+840h]
  __int64 v52; // [rsp+8C8h] [rbp+848h]
  __int64 v53; // [rsp+8D0h] [rbp+850h]
  __int64 v54; // [rsp+8D8h] [rbp+858h]
  __int64 v55; // [rsp+E10h] [rbp+D90h] BYREF
  _QWORD *v56; // [rsp+E18h] [rbp+D98h]
  __int64 v57; // [rsp+E20h] [rbp+DA0h] BYREF
  _QWORD *v58; // [rsp+E28h] [rbp+DA8h]
  __int64 v59; // [rsp+E30h] [rbp+DB0h] BYREF
  _QWORD *v60; // [rsp+E38h] [rbp+DB8h]
  __int64 v61; // [rsp+E40h] [rbp+DC0h] BYREF
  _QWORD *v62; // [rsp+E48h] [rbp+DC8h]
  __int64 v63; // [rsp+E50h] [rbp+DD0h] BYREF
  _QWORD *v64; // [rsp+E58h] [rbp+DD8h]
  __int64 v65; // [rsp+E60h] [rbp+DE0h] BYREF
  _QWORD *v66; // [rsp+E68h] [rbp+DE8h]
  __int64 v67; // [rsp+E70h] [rbp+DF0h] BYREF
  _QWORD *v68; // [rsp+E78h] [rbp+DF8h]
  __int64 v69; // [rsp+E80h] [rbp+E00h] BYREF
  _QWORD *v70; // [rsp+E88h] [rbp+E08h]
  __int64 v71; // [rsp+E90h] [rbp+E10h] BYREF
  _QWORD *v72; // [rsp+E98h] [rbp+E18h]
  __int64 v73; // [rsp+EA0h] [rbp+E20h]
  _QWORD *v74; // [rsp+EA8h] [rbp+E28h]
  __int64 v75; // [rsp+EB0h] [rbp+E30h]
  _QWORD *v76; // [rsp+EB8h] [rbp+E38h]
  __int64 v77; // [rsp+EC0h] [rbp+E40h]
  _QWORD *v78; // [rsp+EC8h] [rbp+E48h]
  unsigned int v79; // [rsp+EDCh] [rbp+E5Ch] BYREF
  __int64 v80; // [rsp+EE0h] [rbp+E60h] BYREF
  _BYTE *v81; // [rsp+EE8h] [rbp+E68h]
  unsigned int position__modelZboardZcache95opps_u6; // [rsp+EF0h] [rbp+E70h] BYREF
  unsigned int v83; // [rsp+EF4h] [rbp+E74h] BYREF
  __int64 v84; // [rsp+EF8h] [rbp+E78h]
  __int64 v85; // [rsp+F00h] [rbp+E80h]
  __int64 v86; // [rsp+F08h] [rbp+E88h]
  __int64 v87; // [rsp+F10h] [rbp+E90h]
  __int64 v88; // [rsp+F18h] [rbp+E98h]
  __int64 v89; // [rsp+F20h] [rbp+EA0h]
  __int64 v90; // [rsp+F2Ch] [rbp+EACh]
  __int64 v91; // [rsp+F34h] [rbp+EB4h] BYREF
  unsigned int v92; // [rsp+F3Ch] [rbp+EBCh] BYREF
  __int64 v93; // [rsp+F40h] [rbp+EC0h] BYREF
  char *v94; // [rsp+F48h] [rbp+EC8h]
  unsigned int v95; // [rsp+F54h] [rbp+ED4h] BYREF
  __int64 v96; // [rsp+F58h] [rbp+ED8h]
  __int64 v97; // [rsp+F60h] [rbp+EE0h] BYREF
  unsigned int v98; // [rsp+F6Ch] [rbp+EECh]
  unsigned int v99; // [rsp+F70h] [rbp+EF0h] BYREF
  unsigned int v100; // [rsp+F74h] [rbp+EF4h] BYREF
  __int64 v101; // [rsp+F78h] [rbp+EF8h] BYREF
  unsigned int finish__modelZsave95mongerZcommon_u4866; // [rsp+F80h] [rbp+F00h]
  unsigned int start__modelZsave95mongerZcommon_u4863; // [rsp+F84h] [rbp+F04h]
  __int64 v104; // [rsp+F88h] [rbp+F08h] BYREF
  char v105[8]; // [rsp+F90h] [rbp+F10h] BYREF
  const char *v106; // [rsp+F98h] [rbp+F18h]
  __int64 v107; // [rsp+FA0h] [rbp+F20h]
  const char *v108; // [rsp+FA8h] [rbp+F28h]
  __int16 v109; // [rsp+FB0h] [rbp+F30h]
  __int64 v110; // [rsp+FC0h] [rbp+F40h]
  _QWORD *v111; // [rsp+FC8h] [rbp+F48h]
  __int64 v112; // [rsp+FD0h] [rbp+F50h] BYREF
  _QWORD *v113; // [rsp+FD8h] [rbp+F58h]
  __int64 v114; // [rsp+FE0h] [rbp+F60h] BYREF
  _QWORD *v115; // [rsp+FE8h] [rbp+F68h]
  __int64 v116; // [rsp+FF0h] [rbp+F70h] BYREF
  __int64 v117; // [rsp+FF8h] [rbp+F78h]
  __int64 v118; // [rsp+1000h] [rbp+F80h] BYREF
  __int64 v119; // [rsp+1008h] [rbp+F88h]
  __int64 v120; // [rsp+1010h] [rbp+F90h] BYREF
  __int64 v121; // [rsp+1018h] [rbp+F98h]
  __int64 v122; // [rsp+1020h] [rbp+FA0h] BYREF
  __int64 v123; // [rsp+1028h] [rbp+FA8h]
  __int64 v124; // [rsp+1030h] [rbp+FB0h] BYREF
  __int64 v125; // [rsp+1038h] [rbp+FB8h]
  char v126[560]; // [rsp+1040h] [rbp+FC0h] BYREF
  __int64 v127; // [rsp+1270h] [rbp+11F0h] BYREF
  __int64 v128; // [rsp+1278h] [rbp+11F8h]
  __int64 v129; // [rsp+1280h] [rbp+1200h]
  _QWORD *v130; // [rsp+1288h] [rbp+1208h]
  __int64 v131; // [rsp+1290h] [rbp+1210h] BYREF
  _QWORD *v132; // [rsp+1298h] [rbp+1218h]
  __int64 v133[4]; // [rsp+12A0h] [rbp+1220h] BYREF
  __int64 v134; // [rsp+12C0h] [rbp+1240h] BYREF
  __int64 v135; // [rsp+12C8h] [rbp+1248h]
  __int64 v136; // [rsp+12D0h] [rbp+1250h]
  __int64 v137[4]; // [rsp+12E0h] [rbp+1260h] BYREF
  __int64 v138[4]; // [rsp+1300h] [rbp+1280h] BYREF
  __int64 v139; // [rsp+1320h] [rbp+12A0h] BYREF
  __int64 v140; // [rsp+1328h] [rbp+12A8h]
  __int64 v141; // [rsp+1330h] [rbp+12B0h]
  char v142; // [rsp+133Dh] [rbp+12BDh]
  char v143; // [rsp+133Eh] [rbp+12BEh]
  char v144; // [rsp+133Fh] [rbp+12BFh]
  __int64 v145; // [rsp+1340h] [rbp+12C0h]
  __int64 v146; // [rsp+1348h] [rbp+12C8h]
  char v147; // [rsp+1357h] [rbp+12D7h]
  __int64 v148; // [rsp+1358h] [rbp+12D8h]
  __int64 v149; // [rsp+1360h] [rbp+12E0h]
  __int64 v150; // [rsp+1368h] [rbp+12E8h]
  __int64 v151; // [rsp+1370h] [rbp+12F0h]
  __int64 v152; // [rsp+1378h] [rbp+12F8h]
  char v153; // [rsp+1387h] [rbp+1307h]
  __int64 v154; // [rsp+1388h] [rbp+1308h]
  __int64 v155; // [rsp+1390h] [rbp+1310h]
  __int64 v156; // [rsp+1398h] [rbp+1318h]
  __int64 v157; // [rsp+13A0h] [rbp+1320h]
  char v158; // [rsp+13AFh] [rbp+132Fh]
  __int64 v159; // [rsp+13B0h] [rbp+1330h]
  __int64 v160; // [rsp+13B8h] [rbp+1338h]
  __int64 v161; // [rsp+13C0h] [rbp+1340h]
  __int64 v162; // [rsp+13C8h] [rbp+1348h]
  __int64 v163; // [rsp+13D0h] [rbp+1350h]
  char v164; // [rsp+13DFh] [rbp+135Fh]
  __int64 v165; // [rsp+13E0h] [rbp+1360h]
  __int64 v166; // [rsp+13E8h] [rbp+1368h]
  _BYTE *v167; // [rsp+13F0h] [rbp+1370h]
  __int64 v168; // [rsp+13F8h] [rbp+1378h]
  __int64 v169; // [rsp+1400h] [rbp+1380h]
  __int64 v170; // [rsp+1408h] [rbp+1388h]
  __int64 v171; // [rsp+1410h] [rbp+1390h]
  __int64 v172; // [rsp+1418h] [rbp+1398h]
  __int64 v173; // [rsp+1420h] [rbp+13A0h]
  __int64 v174; // [rsp+1428h] [rbp+13A8h]
  __int64 v175; // [rsp+1430h] [rbp+13B0h]
  char *v176; // [rsp+1438h] [rbp+13B8h]
  __int64 v177; // [rsp+1440h] [rbp+13C0h]
  __int64 v178; // [rsp+1448h] [rbp+13C8h]
  __int64 v179; // [rsp+1450h] [rbp+13D0h]
  __int64 v180; // [rsp+1458h] [rbp+13D8h]
  __int64 v181; // [rsp+1460h] [rbp+13E0h]
  unsigned __int16 v182; // [rsp+146Ch] [rbp+13ECh]
  __int16 v183; // [rsp+146Eh] [rbp+13EEh]
  __int64 v184; // [rsp+1470h] [rbp+13F0h]
  __int64 v185; // [rsp+1478h] [rbp+13F8h]
  unsigned __int8 *v186; // [rsp+1480h] [rbp+1400h]
  __int64 v187; // [rsp+1488h] [rbp+1408h]
  char v188; // [rsp+1497h] [rbp+1417h]
  __int64 v189; // [rsp+1498h] [rbp+1418h]
  __int64 v190; // [rsp+14A0h] [rbp+1420h]
  __int64 v191; // [rsp+14A8h] [rbp+1428h]
  char v192; // [rsp+14B7h] [rbp+1437h]
  _BYTE *v193; // [rsp+14B8h] [rbp+1438h]
  __int64 v194; // [rsp+14C0h] [rbp+1440h]
  __int64 v195; // [rsp+14C8h] [rbp+1448h]
  __int64 v196; // [rsp+14D0h] [rbp+1450h]
  __int64 v197; // [rsp+14D8h] [rbp+1458h]
  char v198; // [rsp+14E7h] [rbp+1467h]
  __int64 v199; // [rsp+14E8h] [rbp+1468h]
  __int64 v200; // [rsp+14F0h] [rbp+1470h]
  __int64 v201; // [rsp+14F8h] [rbp+1478h]
  __int64 v202; // [rsp+1500h] [rbp+1480h]
  __int64 v203; // [rsp+1508h] [rbp+1488h]
  __int64 v204; // [rsp+1510h] [rbp+1490h]
  __int64 v205; // [rsp+1518h] [rbp+1498h]

  v8 = a3[1];
  v36 = *a3;
  v37 = (_QWORD *)v8;
  v9 = a4[1];
  v34 = *a4;
  v35 = (_QWORD *)v9;
  v33 = a5;
  v106 = "get_preorder_input";
  v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v107 = 0i64;
  v109 = 0;
  nimFrame_80(v105);
  v193 = (_BYTE *)nimErrorFlag_78();
  nimZeroMem_60(a8, 720i64);
  nimZeroMem_60(&v139, 24i64);
  nimZeroMem_60(v138, 24i64);
  nimZeroMem_60(v137, 24i64);
  nimZeroMem_60(&v134, 24i64);
  nimZeroMem_60(v133, 24i64);
  v131 = 0i64;
  v132 = 0i64;
  v129 = 0i64;
  v130 = 0i64;
  v127 = 0i64;
  v128 = 0i64;
  nimZeroMem_60(v126, 560i64);
  v124 = 0i64;
  v125 = 0i64;
  v122 = 0i64;
  v123 = 0i64;
  v192 = 0;
  v120 = 0i64;
  v121 = 0i64;
  v118 = 0i64;
  v119 = 0i64;
  v116 = 0i64;
  v117 = 0i64;
  nimZeroMem_60(v42, 104i64);
  nimZeroMem_60(&v104, 8i64);
  nimZeroMem_60(v50, 104i64);
  v191 = 0i64;
  v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v205 = 0i64;
  v107 = 183i64;
  v190 = a1[23];
  v189 = v190;
  v107 = 184i64;
  while ( v205 < v189 )
  {
    v191 = v205;
    v107 = 185i64;
    v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    if ( v205 < 0 || v205 >= a1[23] )
    {
      raiseIndexError2(v205, a1[23] - 1i64);
      break;
    }
    eqcopy___modelZsave95mongerZcommon_u3692(v50, a1[24] + 104 * v205 + 8);
    v104 = v191;
    v107 = 185i64;
    v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    eqsink___modelZsave95mongerZcommon_u3698(v42, v50);
    eqwasMoved___modelZsave95mongerZcommon_u3686(v50);
    v107 = 279i64;
    v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
    v188 = 0;
    v188 = is_tombstone__modelZsave95mongerZcommon_u4884(v42);
    if ( *v193 )
      break;
    if ( v188 == 1 )
      goto LABEL_256;
    nimZeroMem_60(&v101, 8i64);
    nimZeroMem_60(&v100, 4i64);
    v100 = v43;
    v107 = 537i64;
    v108 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    v101 = eqdup___modelZsave95mongerZcommon_u4025(v104);
    v107 = 281i64;
    v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
    X5BX5Deq___modelZsimulationZpreorder_u5063(&v134, v100, v101);
    if ( *v193 )
      break;
    v107 = 704i64;
    v108 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    v187 = v44;
    if ( v44 )
    {
      v99 = v43;
      v186 = 0i64;
      v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      v204 = 0i64;
      v185 = v44;
      v184 = v44;
      v107 = 251i64;
      while ( v204 < v184 )
      {
        v107 = 708i64;
        v108 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
        if ( v204 < 0 || v204 >= v44 )
        {
          raiseIndexError2(v204, v44 - 1);
          goto LABEL_42;
        }
        v186 = (unsigned __int8 *)(v45 + 4 * v204 + 8);
        v107 = 709i64;
        if ( *v186 > 7u )
        {
          raiseIndexError2(*v186, 7i64);
          goto LABEL_42;
        }
        v98 = *((_DWORD *)refptr_DIRECTIONS__modelZsave95mongerZcommon_u3356 + *v186);
        v183 = 0;
        v182 = 0;
        v107 = 710i64;
        v108 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
        v182 = *((_WORD *)v186 + 1) - 1;
        v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
        v203 = 0i64;
        v107 = 97i64;
        while ( v203 <= v182 )
        {
          nimZeroMem_60(&v97, 8i64);
          v108 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
          v183 = v203;
          v107 = 711i64;
          pluseq___modelZsave95mongerZcommon_u4332(&v99, v98);
          if ( *v193 )
            goto LABEL_42;
          v100 = v99;
          v107 = 537i64;
          v108 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
          v97 = eqdup___modelZsave95mongerZcommon_u4025(v104);
          v107 = 281i64;
          v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          X5BX5Deq___modelZsimulationZpreorder_u5063(&v134, v100, v97);
          if ( *v193 )
            goto LABEL_42;
          v107 = 102i64;
          v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v96 = v203 + 1;
          if ( __OFADD__(1i64, v203) )
          {
            raiseOverflow();
            goto LABEL_42;
          }
          v203 = v96;
        }
        v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v204;
        v107 = 254i64;
        v181 = v44;
        if ( v44 != v184 )
        {
          v31 = TM__8dO79bDlK9csFzRs49cEE7wlw_266;
          v32 = &TM__8dO79bDlK9csFzRs49cEE7wlw_20;
          failedAssertImpl__stdZassertions_u234(&v31);
          if ( *v193 )
            goto LABEL_42;
        }
      }
    }
    else
    {
      v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      v100 = HIDWORD(v43);
      v107 = 281i64;
      X5BX5Deq___modelZsimulationZpreorder_u5063(&v134, HIDWORD(v43), v104);
      if ( *v193 )
        break;
    }
    v107 = 282i64;
    v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
    v28 = v43;
    v29 = v44;
    v30 = v45;
    start__modelZsave95mongerZcommon_u4863 = get_start__modelZsave95mongerZcommon_u4863(&v28);
    if ( !*v193 )
    {
      incl__modelZboardZboard_u982(v133, start__modelZsave95mongerZcommon_u4863);
      if ( !*v193 )
      {
        v107 = 283i64;
        v28 = v43;
        v29 = v44;
        v30 = v45;
        finish__modelZsave95mongerZcommon_u4866 = get_finish__modelZsave95mongerZcommon_u4866(&v28);
        if ( !*v193 )
        {
          incl__modelZboardZboard_u982(v133, finish__modelZsave95mongerZcommon_u4866);
          if ( !*v193 )
          {
LABEL_256:
            v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v205;
            v107 = 187i64;
            v180 = a1[23];
            if ( v180 == v189 )
              continue;
            v31 = TM__8dO79bDlK9csFzRs49cEE7wlw_267;
            v32 = &TM__8dO79bDlK9csFzRs49cEE7wlw_3;
            failedAssertImpl__stdZassertions_u234(&v31);
            if ( !*v193 )
              continue;
          }
        }
      }
    }
    break;
  }
LABEL_42:
  v107 = 185i64;
  eqdestroy___modelZsave95mongerZcommon_u3689(v50);
  eqdestroy___modelZsave95mongerZcommon_u3689(v42);
  if ( *v193 )
    goto LABEL_247;
  nimZeroMem_60(v38, 560i64);
  v179 = 0i64;
  v202 = 0i64;
  v107 = 183i64;
  v178 = a1[19];
  v177 = v178;
  v107 = 184i64;
  while ( v202 < v177 )
  {
    v179 = v202;
    v107 = 34i64;
    v108 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    if ( v202 < 0 || v202 >= a1[19] )
    {
      raiseIndexError2(v202, a1[19] - 1i64);
      break;
    }
    eqcopy___modelZsave95mongerZversionsZv0_u148(v38, a1[20] + 560 * v202 + 8);
    v107 = 286i64;
    v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
    if ( v179 < 0 || v179 >= a1[19] )
    {
      raiseIndexError2(v179, a1[19] - 1i64);
      break;
    }
    *(_BYTE *)(a1[20] + 560 * v179 + 280) = 0;
    nimZeroMem_60(&v95, 4i64);
    v93 = 0i64;
    v94 = 0i64;
    nimZeroMem_60(v42, 1448i64);
    v176 = 0i64;
    v93 = 0i64;
    v94 = 0i64;
    v107 = 128i64;
    v108 = "D:\\TuringComplete_Phu\\model\\board\\custom_prototype_list.nim";
    nimZeroMem_60(v50, 1448i64);
    get_prototype__modelZboardZcustom95prototype95list_u502(v38, v50);
    if ( !*v193 )
    {
      v107 = 170i64;
      v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      eqsink___modelZboardZprototype95list_u3248(v42, v50);
      v107 = 677i64;
      v108 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
      v31 = v46[0];
      v32 = (_QWORD *)v46[1];
      eqsink___modelZsave95mongerZcommon_u4427(&v93, &v31);
      eqwasMoved___modelZsave95mongerZcommon_u4415(v46);
      v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      v201 = 0i64;
      v175 = v93;
      v174 = v93;
      v107 = 251i64;
      while ( v201 < v174 )
      {
        v107 = 128i64;
        v108 = "D:\\TuringComplete_Phu\\model\\board\\custom_prototype_list.nim";
        if ( v201 < 0 || v201 >= v93 )
        {
          raiseIndexError2(v201, v93 - 1);
          break;
        }
        v176 = &v94[8 * v201 + 8];
        nimZeroMem_60(&v92, 4i64);
        nimZeroMem_60(&v91, 8i64);
        v107 = 129i64;
        v108 = "D:\\TuringComplete_Phu\\model\\board\\custom_prototype_list.nim";
        v90 = rotate__modelZmodel95types_u1486(*(_QWORD *)v176, v40);
        if ( *v193 )
          break;
        v91 = plus___modelZmodel95types_u1470(v90, v39);
        if ( *v193 )
          break;
        v173 = 0i64;
        v172 = 0i64;
        v107 = 672i64;
        v108 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
        v89 = SHIWORD(v91) - 1i64;
        if ( v89 < -32768 || v89 > 0x7FFF )
        {
LABEL_92:
          raiseOverflow();
          break;
        }
        v172 = (__int16)v89;
        v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
        v200 = 0i64;
        v107 = 97i64;
        while ( v200 <= v172 )
        {
          v173 = v200;
          v171 = 0i64;
          v170 = 0i64;
          v107 = 673i64;
          v108 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
          v87 = SWORD2(v91) - 1i64;
          if ( v87 < -32768 || v87 > 0x7FFF )
            goto LABEL_92;
          v170 = (__int16)v87;
          v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v199 = 0i64;
          v107 = 97i64;
          while ( v199 <= v170 )
          {
            v171 = v199;
            v107 = 674i64;
            v108 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
            if ( v199 < -32768 || v171 > 0x7FFF )
            {
              raiseRangeErrorI(v171, -32768i64, 0x7FFFi64);
              goto LABEL_105;
            }
            v86 = (__int16)v91 + (__int64)(__int16)v171;
            if ( v86 < -32768 || v86 > 0x7FFF )
              goto LABEL_92;
            LOWORD(v92) = v86;
            if ( v173 < -32768 || v173 > 0x7FFF )
            {
              raiseRangeErrorI(v173, -32768i64, 0x7FFFi64);
              goto LABEL_105;
            }
            v85 = SWORD1(v91) + (__int64)(__int16)v173;
            if ( v85 < -32768 || v85 > 0x7FFF )
              goto LABEL_92;
            HIWORD(v92) = v85;
            v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v95 = v92;
            v107 = 289i64;
            v198 = 0;
            v28 = v139;
            v29 = v140;
            v30 = v141;
            v198 = contains__modelZboardZboard_u6779(&v28, v92);
            if ( *v193 )
              goto LABEL_105;
            if ( !v198 )
            {
              v28 = v134;
              v29 = v135;
              v30 = v136;
              v198 = contains__modelZsimulationZpreorder_u6669(&v28, v95);
              if ( *v193 )
                goto LABEL_105;
            }
            if ( v198 != 1 )
            {
              v107 = 292i64;
              incl__modelZboardZboard_u982(&v139, v95);
              if ( *v193 )
                goto LABEL_105;
              v107 = 293i64;
              X5BX5Deq___modelZsimulationZpreorder_u6762(v137, v95, v179);
              if ( *v193 )
                goto LABEL_105;
            }
            else
            {
              v107 = 290i64;
              if ( v179 < 0 || v179 >= a1[19] )
              {
                raiseIndexError2(v179, a1[19] - 1i64);
                goto LABEL_105;
              }
              *(_BYTE *)(a1[20] + 560 * v179 + 280) = 1;
            }
            v107 = 102i64;
            v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
            v84 = v199 + 1;
            if ( __OFADD__(1i64, v199) )
              goto LABEL_92;
            v199 = v84;
          }
          v88 = v200 + 1;
          if ( __OFADD__(1i64, v200) )
            goto LABEL_92;
          v200 = v88;
        }
        v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v201;
        v107 = 254i64;
        v169 = v93;
        if ( v93 != v174 )
        {
          v31 = TM__8dO79bDlK9csFzRs49cEE7wlw_274;
          v32 = &TM__8dO79bDlK9csFzRs49cEE7wlw_20;
          failedAssertImpl__stdZassertions_u234(&v31);
          if ( *v193 )
            break;
        }
      }
    }
LABEL_105:
    v107 = 170i64;
    v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    eqdestroy___modelZboardZprototype95list_u3239(v42);
    v107 = 677i64;
    v108 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    v31 = v93;
    v32 = v94;
    eqdestroy___modelZsave95mongerZcommon_u4418(&v31);
    if ( *v193 )
      break;
    nimZeroMem_60(&v83, 4i64);
    nimZeroMem_60(&position__modelZboardZcache95opps_u6, 4i64);
    v107 = 20i64;
    v108 = "D:\\TuringComplete_Phu\\model\\board\\cache_opps.nim";
    if ( v38[0] == 78 )
    {
      v107 = 21i64;
      v168 = v41;
      v80 = 0i64;
      v81 = 0i64;
      nimZeroMem_60(v42, 1448i64);
      v167 = 0i64;
      v80 = 0i64;
      v81 = 0i64;
      v107 = 23i64;
      v108 = "D:\\TuringComplete_Phu\\model\\board\\cache_opps.nim";
      nimZeroMem_60(v50, 1448i64);
      get_custom_prototype__modelZboardZcustom95prototype95list_u451(v168, v50);
      if ( !*v193 )
      {
        v107 = 170i64;
        v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        eqsink___modelZboardZprototype95list_u3248(v42, v50);
        v107 = 934i64;
        v31 = v47[0];
        v32 = (_QWORD *)v47[1];
        eqsink___modelZboardZprototype95list_u1720(&v80, &v31);
        eqwasMoved___modelZboardZprototype95list_u1708(v47);
        v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v197 = 0i64;
        v166 = v80;
        v165 = v80;
        v107 = 251i64;
        while ( v197 < v165 )
        {
          v107 = 23i64;
          v108 = "D:\\TuringComplete_Phu\\model\\board\\cache_opps.nim";
          if ( v197 < 0 || v197 >= v80 )
          {
            raiseIndexError2(v197, v80 - 1);
            break;
          }
          v167 = &v81[56 * v197 + 8];
          v107 = 24i64;
          if ( v81[56 * v197 + 57] != 1 )
          {
            v107 = 50i64;
            position__modelZboardZcache95opps_u6 = get_position__modelZboardZcache95opps_u6(v39, v167, v40);
            if ( *v193 )
              break;
            v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v83 = position__modelZboardZcache95opps_u6;
            v107 = 296i64;
            v164 = 0;
            v28 = v139;
            v29 = v140;
            v30 = v141;
            v164 = contains__modelZboardZboard_u6779(&v28, position__modelZboardZcache95opps_u6);
            if ( *v193 )
              break;
            if ( v164 != 1 )
            {
              v107 = 299i64;
              incl__modelZboardZboard_u982(&v139, v83);
              if ( *v193 )
                break;
              v107 = 300i64;
              X5BX5Deq___modelZsimulationZpreorder_u6762(v138, v83, v179);
              if ( *v193 )
                break;
            }
            else
            {
              v107 = 297i64;
              if ( v179 < 0 || v179 >= a1[19] )
              {
                raiseIndexError2(v179, a1[19] - 1i64);
                break;
              }
              *(_BYTE *)(a1[20] + 560 * v179 + 280) = 1;
            }
          }
          v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          ++v197;
          v107 = 254i64;
          v163 = v80;
          if ( v80 != v165 )
          {
            v31 = TM__8dO79bDlK9csFzRs49cEE7wlw_275;
            v32 = &TM__8dO79bDlK9csFzRs49cEE7wlw_20;
            failedAssertImpl__stdZassertions_u234(&v31);
            if ( *v193 )
              break;
          }
        }
      }
      v107 = 170i64;
      v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      eqdestroy___modelZboardZprototype95list_u3239(v42);
      v107 = 934i64;
      v31 = v80;
      v32 = v81;
      eqdestroy___modelZboardZprototype95list_u1711(&v31);
      if ( *v193 )
        break;
    }
    else
    {
      nimZeroMem_60(v50, 1448i64);
      v107 = 28i64;
      v108 = "D:\\TuringComplete_Phu\\model\\board\\cache_opps.nim";
      v162 = 0i64;
      v162 = X5BX5D___modelZboardZprototype95list_u4239(
               refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
               (unsigned __int8)v38[0]);
      if ( !*v193 )
      {
        v107 = 170i64;
        v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        eqcopy___modelZboardZprototype95list_u3242(v50, v162);
        v161 = 0i64;
        v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v196 = 0i64;
        v160 = v51;
        v159 = v51;
        v107 = 251i64;
        while ( v196 < v159 )
        {
          v107 = 29i64;
          v108 = "D:\\TuringComplete_Phu\\model\\board\\cache_opps.nim";
          if ( v196 < 0 || v196 >= v51 )
          {
            raiseIndexError2(v196, v51 - 1);
            goto LABEL_168;
          }
          v161 = v52 + 56 * v196 + 8;
          v107 = 30i64;
          if ( *(_BYTE *)(v52 + 56 * v196 + 57) != 1 )
          {
            v107 = 50i64;
            position__modelZboardZcache95opps_u6 = get_position__modelZboardZcache95opps_u6(v39, v161, v40);
            if ( *v193 )
              goto LABEL_168;
            v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v83 = position__modelZboardZcache95opps_u6;
            v107 = 296i64;
            v158 = 0;
            v28 = v139;
            v29 = v140;
            v30 = v141;
            v158 = contains__modelZboardZboard_u6779(&v28, position__modelZboardZcache95opps_u6);
            if ( *v193 )
              goto LABEL_168;
            if ( v158 != 1 )
            {
              v107 = 299i64;
              incl__modelZboardZboard_u982(&v139, v83);
              if ( *v193 )
                goto LABEL_168;
              v107 = 300i64;
              X5BX5Deq___modelZsimulationZpreorder_u6762(v138, v83, v179);
              if ( *v193 )
                goto LABEL_168;
            }
            else
            {
              v107 = 297i64;
              if ( v179 < 0 || v179 >= a1[19] )
              {
LABEL_141:
                raiseIndexError2(v179, a1[19] - 1i64);
                goto LABEL_168;
              }
              *(_BYTE *)(a1[20] + 560 * v179 + 280) = 1;
            }
          }
          v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          ++v196;
          v107 = 254i64;
          v157 = v51;
          if ( v51 != v159 )
          {
            v31 = TM__8dO79bDlK9csFzRs49cEE7wlw_276;
            v32 = &TM__8dO79bDlK9csFzRs49cEE7wlw_20;
            failedAssertImpl__stdZassertions_u234(&v31);
            if ( *v193 )
              goto LABEL_168;
          }
        }
        v156 = 0i64;
        v195 = 0i64;
        v155 = v53;
        v154 = v53;
        v107 = 251i64;
        while ( v195 < v154 )
        {
          v107 = 33i64;
          v108 = "D:\\TuringComplete_Phu\\model\\board\\cache_opps.nim";
          if ( v195 < 0 || v195 >= v53 )
          {
            raiseIndexError2(v195, v53 - 1);
            break;
          }
          v156 = v54 + 56 * v195 + 8;
          v107 = 34i64;
          if ( *(_BYTE *)(v54 + 56 * v195 + 57) != 1 )
          {
            v107 = 50i64;
            position__modelZboardZcache95opps_u6 = get_position__modelZboardZcache95opps_u6(v39, v156, v40);
            if ( *v193 )
              break;
            v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v83 = position__modelZboardZcache95opps_u6;
            v107 = 296i64;
            v153 = 0;
            v28 = v139;
            v29 = v140;
            v30 = v141;
            v153 = contains__modelZboardZboard_u6779(&v28, position__modelZboardZcache95opps_u6);
            if ( *v193 )
              break;
            if ( v153 != 1 )
            {
              v107 = 299i64;
              incl__modelZboardZboard_u982(&v139, v83);
              if ( *v193 )
                break;
              v107 = 300i64;
              X5BX5Deq___modelZsimulationZpreorder_u6762(v138, v83, v179);
              if ( *v193 )
                break;
            }
            else
            {
              v107 = 297i64;
              if ( v179 < 0 || v179 >= a1[19] )
                goto LABEL_141;
              *(_BYTE *)(a1[20] + 560 * v179 + 280) = 1;
            }
          }
          v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          ++v195;
          v107 = 254i64;
          v152 = v53;
          if ( v53 != v154 )
          {
            v31 = TM__8dO79bDlK9csFzRs49cEE7wlw_277;
            v32 = &TM__8dO79bDlK9csFzRs49cEE7wlw_20;
            failedAssertImpl__stdZassertions_u234(&v31);
            if ( *v193 )
              break;
          }
        }
      }
LABEL_168:
      v107 = 170i64;
      v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      eqdestroy___modelZboardZprototype95list_u3239(v50);
      if ( *v193 )
        break;
    }
    nimZeroMem_60(v42, 1448i64);
    nimZeroMem_60(&v79, 4i64);
    v107 = 39i64;
    v108 = "D:\\TuringComplete_Phu\\model\\board\\cache_opps.nim";
    v151 = 0i64;
    v151 = X5BX5D___modelZboardZprototype95list_u4239(
             refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
             (unsigned __int8)v38[0]);
    if ( !*v193 )
    {
      v107 = 170i64;
      v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      eqcopy___modelZboardZprototype95list_u3242(v42, v151);
      v107 = 40i64;
      v108 = "D:\\TuringComplete_Phu\\model\\board\\cache_opps.nim";
      if ( v38[0] != 78 )
        goto LABEL_173;
      v107 = 41i64;
      v108 = "D:\\TuringComplete_Phu\\model\\board\\cache_opps.nim";
      nimZeroMem_60(v50, 1448i64);
      get_custom_prototype__modelZboardZcustom95prototype95list_u451(v41, v50);
      if ( !*v193 )
      {
        v107 = 170i64;
        v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        eqsink___modelZboardZprototype95list_u3248(v42, v50);
LABEL_173:
        v150 = 0i64;
        v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v194 = 0i64;
        v149 = v48;
        v148 = v48;
        v107 = 251i64;
        while ( v194 < v148 )
        {
          v107 = 43i64;
          v108 = "D:\\TuringComplete_Phu\\model\\board\\cache_opps.nim";
          if ( v194 < 0 || v194 >= v48 )
          {
            raiseIndexError2(v194, v48 - 1);
            break;
          }
          v150 = v49 + 56 * v194 + 8;
          v107 = 44i64;
          if ( *(_BYTE *)(v49 + 56 * v194 + 57) != 1 )
          {
            v107 = 52i64;
            v79 = get_position__modelZboardZcache95opps_u6(v39, v150, v40);
            if ( *v193 )
              break;
            v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v83 = v79;
            v107 = 296i64;
            v147 = 0;
            v28 = v139;
            v29 = v140;
            v30 = v141;
            v147 = contains__modelZboardZboard_u6779(&v28, v79);
            if ( *v193 )
              break;
            if ( v147 != 1 )
            {
              v107 = 299i64;
              incl__modelZboardZboard_u982(&v139, v83);
              if ( *v193 )
                break;
              v107 = 300i64;
              X5BX5Deq___modelZsimulationZpreorder_u6762(v138, v83, v179);
              if ( *v193 )
                break;
            }
            else
            {
              v107 = 297i64;
              if ( v179 < 0 || v179 >= a1[19] )
              {
                raiseIndexError2(v179, a1[19] - 1i64);
                break;
              }
              *(_BYTE *)(a1[20] + 560 * v179 + 280) = 1;
            }
          }
          v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          ++v194;
          v107 = 254i64;
          v146 = v48;
          if ( v48 != v148 )
          {
            v31 = TM__8dO79bDlK9csFzRs49cEE7wlw_278;
            v32 = &TM__8dO79bDlK9csFzRs49cEE7wlw_20;
            failedAssertImpl__stdZassertions_u234(&v31);
            if ( *v193 )
              break;
          }
        }
      }
    }
    v107 = 170i64;
    v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    eqdestroy___modelZboardZprototype95list_u3239(v42);
    if ( !*v193 )
    {
      v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      ++v202;
      v107 = 187i64;
      v145 = a1[19];
      if ( v145 == v177 )
        continue;
      v31 = TM__8dO79bDlK9csFzRs49cEE7wlw_279;
      v32 = &TM__8dO79bDlK9csFzRs49cEE7wlw_3;
      failedAssertImpl__stdZassertions_u234(&v31);
      if ( !*v193 )
        continue;
    }
    break;
  }
  v107 = 34i64;
  v108 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
  eqdestroy___modelZsave95mongerZversionsZv0_u145(v38);
  if ( !*v193 )
  {
    v107 = 304i64;
    v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
    v114 = 0i64;
    v115 = 0i64;
    rawNewString(&v31, *refptr_campaign_name__modelZmodel95types_u826 + *a2 + 1);
    v114 = v31;
    v115 = v32;
    v10 = (_QWORD *)refptr_campaign_name__modelZmodel95types_u826[1];
    v31 = *refptr_campaign_name__modelZmodel95types_u826;
    v32 = v10;
    appendString_25(&v114, &v31);
    v31 = TM__8dO79bDlK9csFzRs49cEE7wlw_280;
    v32 = &TM__8dO79bDlK9csFzRs49cEE7wlw_15;
    appendString_25(&v114, &v31);
    v11 = (_QWORD *)a2[1];
    v31 = *a2;
    v32 = v11;
    appendString_25(&v114, &v31);
    v129 = v114;
    v130 = v115;
    v107 = 306i64;
    if ( !*a2 )
      goto LABEL_244;
    v77 = 0i64;
    v78 = 0i64;
    v75 = 0i64;
    v76 = 0i64;
    v73 = 0i64;
    v74 = 0i64;
    v107 = 308i64;
    v71 = 0i64;
    v72 = 0i64;
    rawNewString(&v31, a2[6] + 11);
    v71 = v31;
    v72 = v32;
    v12 = (_QWORD *)a2[7];
    v31 = a2[6];
    v32 = v12;
    appendString_25(&v71, &v31);
    v31 = TM__8dO79bDlK9csFzRs49cEE7wlw_282;
    v32 = &TM__8dO79bDlK9csFzRs49cEE7wlw_281;
    appendString_25(&v71, &v31);
    v77 = v71;
    v78 = v72;
    v107 = 309i64;
    v69 = 0i64;
    v70 = 0i64;
    rawNewString(&v31, v129 + 8);
    v69 = v31;
    v70 = v32;
    v31 = v129;
    v32 = v130;
    appendString_25(&v69, &v31);
    v31 = TM__8dO79bDlK9csFzRs49cEE7wlw_284;
    v32 = &TM__8dO79bDlK9csFzRs49cEE7wlw_283;
    appendString_25(&v69, &v31);
    v75 = v69;
    v76 = v70;
    v107 = 310i64;
    v67 = 0i64;
    v68 = 0i64;
    rawNewString(&v31, a2[6] + 8);
    v67 = v31;
    v68 = v32;
    v13 = (_QWORD *)a2[7];
    v31 = a2[6];
    v32 = v13;
    appendString_25(&v67, &v31);
    v31 = TM__8dO79bDlK9csFzRs49cEE7wlw_285;
    v32 = &TM__8dO79bDlK9csFzRs49cEE7wlw_283;
    appendString_25(&v67, &v31);
    v73 = v67;
    v74 = v68;
    v107 = 312i64;
    v144 = 0;
    v31 = v77;
    v32 = v78;
    v144 = nosfileExists(&v31);
    if ( !*v193 )
    {
      if ( v144 != 1 )
        goto LABEL_211;
      v65 = 0i64;
      v66 = 0i64;
      v63 = 0i64;
      v64 = 0i64;
      v107 = 313i64;
      v31 = v77;
      v32 = v78;
      readFile__stdZsyncio_u624(&v65, &v31);
      if ( !*v193 )
      {
        v31 = v65;
        v32 = v66;
        preprocess_translation__modelZtranslations_u2042(&v63, &v31, 1i64);
        if ( !*v193 )
        {
          prepareAdd(&v131, v63);
          v31 = v63;
          v32 = v64;
          appendString_25(&v131, &v31);
        }
      }
      v107 = 394i64;
      v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v64 && (*v64 & 0x4000000000000000i64) == 0 )
        deallocShared(v64);
      if ( v66 && (*v66 & 0x4000000000000000i64) == 0 )
        deallocShared(v66);
      if ( !*v193 )
      {
LABEL_211:
        v107 = 315i64;
        v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        v143 = 0;
        v31 = v75;
        v32 = v76;
        v143 = nosfileExists(&v31);
        if ( !*v193 )
        {
          if ( v143 != 1 )
          {
            v107 = 318i64;
            v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v142 = 0;
            v31 = v73;
            v32 = v74;
            v142 = nosfileExists(&v31);
            if ( !*v193 && v142 == 1 )
            {
              v57 = 0i64;
              v58 = 0i64;
              v55 = 0i64;
              v56 = 0i64;
              v107 = 319i64;
              v31 = v73;
              v32 = v74;
              readFile__stdZsyncio_u624(&v57, &v31);
              if ( !*v193 )
              {
                v31 = v57;
                v32 = v58;
                preprocess_translation__modelZtranslations_u2042(&v55, &v31, 1i64);
                if ( !*v193 )
                {
                  prepareAdd(&v131, v55);
                  v31 = v55;
                  v32 = v56;
                  appendString_25(&v131, &v31);
                }
              }
              v107 = 394i64;
              v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              if ( v56 && (*v56 & 0x4000000000000000i64) == 0 )
                deallocShared(v56);
              if ( v58 && (*v58 & 0x4000000000000000i64) == 0 )
                deallocShared(v58);
            }
          }
          else
          {
            v61 = 0i64;
            v62 = 0i64;
            v59 = 0i64;
            v60 = 0i64;
            v107 = 316i64;
            v31 = v75;
            v32 = v76;
            readFile__stdZsyncio_u624(&v61, &v31);
            if ( !*v193 )
            {
              v31 = v61;
              v32 = v62;
              preprocess_translation__modelZtranslations_u2042(&v59, &v31, 1i64);
              if ( !*v193 )
              {
                prepareAdd(&v131, v59);
                v31 = v59;
                v32 = v60;
                appendString_25(&v131, &v31);
              }
            }
            v107 = 394i64;
            v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v60 && (*v60 & 0x4000000000000000i64) == 0 )
              deallocShared(v60);
            if ( v62 && (*v62 & 0x4000000000000000i64) == 0 )
              deallocShared(v62);
          }
        }
      }
    }
    if ( v74 && (*v74 & 0x4000000000000000i64) == 0 )
      deallocShared(v74);
    if ( v76 && (*v76 & 0x4000000000000000i64) == 0 )
      deallocShared(v76);
    if ( v78 && (*v78 & 0x4000000000000000i64) == 0 )
      deallocShared(v78);
    if ( !*v193 )
    {
LABEL_244:
      v107 = 250i64;
      v108 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
      v28 = v133[0];
      v29 = v133[1];
      v30 = v133[2];
      eqsink___modelZboardZboard_u9880(a1 + 98, &v28);
      eqwasMoved___modelZboardZboard_u9868(v133);
      v107 = 275i64;
      v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      v28 = v134;
      v29 = v135;
      v30 = v136;
      eqsink___modelZsimulationZpreorder_u8369(a1 + 95, &v28);
      eqwasMoved___modelZsimulationZpreorder_u8357(&v134);
      v107 = 273i64;
      v28 = v137[0];
      v29 = v137[1];
      v30 = v137[2];
      eqsink___modelZsimulationZpreorder_u8348(a1 + 92, &v28);
      eqwasMoved___modelZsimulationZpreorder_u8336(v137);
      v28 = v138[0];
      v29 = v138[1];
      v30 = v138[2];
      eqsink___modelZsimulationZpreorder_u8348(a1 + 101, &v28);
      eqwasMoved___modelZsimulationZpreorder_u8336(v138);
      v107 = 326i64;
      nimZeroMem_60(a8, 720i64);
      *(_BYTE *)(a8 + 8) = 0;
      v107 = 1699i64;
      v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      v14 = (_QWORD *)refptr_campaign_name__modelZmodel95types_u826[1];
      v31 = *refptr_campaign_name__modelZmodel95types_u826;
      v32 = v14;
      eqdup___system_u2664(&v127, &v31);
      v15 = v128;
      *(_QWORD *)(a8 + 16) = v127;
      *(_QWORD *)(a8 + 24) = v15;
      v107 = 770i64;
      v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
      eqdup___modelZboardZschematics_u4049(a2, v126);
      qmemcpy((void *)(a8 + 32), v126, 0x230ui64);
      v107 = 982i64;
      v108 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
      v16 = (_QWORD *)a1[27];
      v31 = a1[26];
      v32 = v16;
      eqdup___modelZsave95mongerZcommon_u5618(&v124, &v31);
      v17 = v125;
      *(_QWORD *)(a8 + 624) = v124;
      *(_QWORD *)(a8 + 632) = v17;
      v107 = 1699i64;
      v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      v31 = v36;
      v32 = v37;
      eqdup___system_u2664(&v122, &v31);
      v18 = v123;
      *(_QWORD *)(a8 + 648) = v122;
      *(_QWORD *)(a8 + 656) = v18;
      v192 = v33;
      *(_BYTE *)(a8 + 641) = v33;
      v107 = 1699i64;
      v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      v31 = v34;
      v32 = v35;
      eqdup___system_u2664(&v120, &v31);
      v19 = v121;
      *(_QWORD *)(a8 + 664) = v120;
      *(_QWORD *)(a8 + 672) = v19;
      v107 = 72i64;
      v108 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      v20 = (_QWORD *)a1[20];
      v31 = a1[19];
      v32 = v20;
      eqdup___modelZsave95mongerZversionsZv0_u1082(&v118, &v31);
      v21 = v119;
      *(_QWORD *)(a8 + 592) = v118;
      *(_QWORD *)(a8 + 600) = v21;
      v107 = 335i64;
      v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      v112 = 0i64;
      v113 = 0i64;
      wires__modelZsave95mongerZcommon_u4074(&v112, a1 + 19);
      if ( *v193 )
      {
        v31 = v112;
        v32 = v113;
        eqdestroy___modelZsave95mongerZcommon_u3872(&v31);
      }
      else
      {
        v22 = v113;
        *(_QWORD *)(a8 + 608) = v112;
        *(_QWORD *)(a8 + 616) = v22;
        v107 = 1699i64;
        v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        address = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_schematic_path__modelZmodel95types_u80);
        v24 = (_QWORD *)address[1];
        v31 = *address;
        v32 = v24;
        eqdup___system_u2664(&v116, &v31);
        v25 = v117;
        *(_QWORD *)(a8 + 688) = v116;
        *(_QWORD *)(a8 + 696) = v25;
        v110 = v131;
        v111 = v132;
        v107 = 1699i64;
        v108 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        eqwasMoved___system_u2658(&v131);
        v26 = v111;
        *(_QWORD *)(a8 + 704) = v110;
        *(_QWORD *)(a8 + 712) = v26;
        v107 = 27i64;
        *(_BYTE *)(a8 + 640) = 0;
        *(_QWORD *)(a8 + 680) = 0i64;
      }
    }
  }
LABEL_247:
  v107 = 394i64;
  if ( v130 && (*v130 & 0x4000000000000000i64) == 0 )
    deallocShared(v130);
  if ( v132 && (*v132 & 0x4000000000000000i64) == 0 )
    deallocShared(v132);
  v107 = 250i64;
  v108 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  eqdestroy___modelZboardZboard_u9871(v133);
  v107 = 275i64;
  v108 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  eqdestroy___modelZsimulationZpreorder_u8360(&v134);
  v107 = 273i64;
  eqdestroy___modelZsimulationZpreorder_u8339(v137);
  eqdestroy___modelZsimulationZpreorder_u8339(v138);
  v107 = 250i64;
  v108 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  eqdestroy___modelZboardZboard_u9871(&v139);
  return popFrame_80();
}
