__int64 __fastcall complete_current_level__presenterZutilities_u27016(
        signed __int64 *a1,
        __int64 a2,
        unsigned __int8 a3,
        bool a4)
{
  char *v4; // rdx
  char *v5; // rdx
  char *v6; // rdx
  char *v7; // rdx
  char *v8; // rdx
  signed __int64 v9; // rdx
  _BOOL8 v10; // rdx
  _BOOL8 v11; // rdx
  char *v12; // rdx
  char *v13; // rdx
  signed __int64 v14; // rdx
  char *v15; // rdx
  signed __int64 v16; // rdx
  __int64 v17; // rdx
  char *v18; // rdx
  char *v19; // rdx
  signed __int64 v20; // rdx
  char *v21; // rdx
  signed __int64 v22; // rdx
  bool v23; // al
  char *v24; // rdx
  char *v25; // rdx
  char *v26; // rdx
  unsigned int v27; // r8d
  __int64 v28; // rdx
  __int64 v29; // rdx
  __int64 v30; // rdx
  __int64 v31; // rdx
  __int64 v32; // rdx
  __int64 v33; // rdx
  __int64 v34; // rax
  char *v35; // rdx
  __int64 v36; // rax
  __int64 v37; // rdx
  signed __int64 v38; // rax
  char v39; // dl
  bool v40; // of
  __int64 v41; // rax
  char *v42; // rdx
  char *v43; // rax
  __int64 v44; // rdx
  char *v45; // rax
  __int64 v47; // [rsp+20h] [rbp-60h] BYREF
  __int64 v48; // [rsp+28h] [rbp-58h]
  __int64 v49; // [rsp+30h] [rbp-50h]
  __int64 v50; // [rsp+40h] [rbp-40h] BYREF
  void *v51; // [rsp+48h] [rbp-38h]
  __int64 v52; // [rsp+50h] [rbp-30h]
  __int64 v53; // [rsp+60h] [rbp-20h] BYREF
  void *v54; // [rsp+68h] [rbp-18h]
  __int64 v55; // [rsp+70h] [rbp-10h] BYREF
  char *v56; // [rsp+78h] [rbp-8h]
  _BYTE v57[16]; // [rsp+80h] [rbp+0h] BYREF
  _BYTE v58[72]; // [rsp+90h] [rbp+10h] BYREF
  __int64 v59; // [rsp+D8h] [rbp+58h] BYREF
  __int64 v60; // [rsp+E8h] [rbp+68h] BYREF
  char v61[8]; // [rsp+100h] [rbp+80h] BYREF
  __int64 v62; // [rsp+108h] [rbp+88h]
  char *v63; // [rsp+110h] [rbp+90h]
  unsigned __int8 v64; // [rsp+118h] [rbp+98h]
  __int64 v65[2]; // [rsp+120h] [rbp+A0h] BYREF
  _BYTE v66[128]; // [rsp+130h] [rbp+B0h] BYREF
  __int64 v67; // [rsp+1B0h] [rbp+130h]
  __int64 v68; // [rsp+1B8h] [rbp+138h]
  __int64 v69; // [rsp+1C0h] [rbp+140h]
  __int64 v70[70]; // [rsp+1D0h] [rbp+150h] BYREF
  __int64 v71[70]; // [rsp+400h] [rbp+380h] BYREF
  __int64 v72[138]; // [rsp+630h] [rbp+5B0h] BYREF
  __int64 v73[2]; // [rsp+A80h] [rbp+A00h] BYREF
  char v74; // [rsp+A90h] [rbp+A10h]
  __int64 v75; // [rsp+AB0h] [rbp+A30h]
  __int64 v76; // [rsp+AB8h] [rbp+A38h]
  __int64 v77; // [rsp+B60h] [rbp+AE0h] BYREF
  __int64 v78; // [rsp+B68h] [rbp+AE8h]
  __int64 v79; // [rsp+BC0h] [rbp+B40h] BYREF
  __int64 v80[4]; // [rsp+1030h] [rbp+FB0h] BYREF
  __int64 v81[4]; // [rsp+1050h] [rbp+FD0h] BYREF
  __int64 v82; // [rsp+1070h] [rbp+FF0h] BYREF
  char *v83; // [rsp+1078h] [rbp+FF8h]
  __int64 v84; // [rsp+1088h] [rbp+1008h]
  __int64 v85; // [rsp+1090h] [rbp+1010h]
  void *v86; // [rsp+1098h] [rbp+1018h]
  __int64 v87; // [rsp+10A0h] [rbp+1020h]
  char *v88; // [rsp+10A8h] [rbp+1028h]
  __int64 v89; // [rsp+10B0h] [rbp+1030h]
  _QWORD *v90; // [rsp+10B8h] [rbp+1038h]
  __int64 v91; // [rsp+10C0h] [rbp+1040h] BYREF
  char *v92; // [rsp+10C8h] [rbp+1048h]
  __int64 v93; // [rsp+10D8h] [rbp+1058h]
  __int64 v94; // [rsp+10E0h] [rbp+1060h] BYREF
  _QWORD *v95; // [rsp+10E8h] [rbp+1068h]
  __int64 v96; // [rsp+10F0h] [rbp+1070h]
  void *v97; // [rsp+10F8h] [rbp+1078h]
  __int64 v98; // [rsp+1100h] [rbp+1080h]
  void *v99; // [rsp+1108h] [rbp+1088h]
  __int64 v100; // [rsp+1110h] [rbp+1090h]
  __int64 v101; // [rsp+1120h] [rbp+10A0h] BYREF
  void *v102; // [rsp+1128h] [rbp+10A8h]
  __int64 v103; // [rsp+1130h] [rbp+10B0h] BYREF
  void *v104; // [rsp+1138h] [rbp+10B8h]
  __int64 v105; // [rsp+1140h] [rbp+10C0h]
  __int64 v106; // [rsp+1148h] [rbp+10C8h]
  __int64 v107; // [rsp+1150h] [rbp+10D0h] BYREF
  __int64 v108; // [rsp+1158h] [rbp+10D8h]
  __int64 v109; // [rsp+1160h] [rbp+10E0h]
  __int64 v110; // [rsp+1168h] [rbp+10E8h]
  void *v111; // [rsp+1178h] [rbp+10F8h]
  __int64 v112; // [rsp+1180h] [rbp+1100h]
  void *v113; // [rsp+1188h] [rbp+1108h]
  __int64 v114[3]; // [rsp+1190h] [rbp+1110h] BYREF
  __int64 v115; // [rsp+11A8h] [rbp+1128h]
  __int64 v116; // [rsp+11B0h] [rbp+1130h]
  __int64 v117; // [rsp+11B8h] [rbp+1138h]
  __int64 v118; // [rsp+11C0h] [rbp+1140h]
  __int64 v119; // [rsp+11C8h] [rbp+1148h] BYREF
  __int64 v120[4]; // [rsp+11D0h] [rbp+1150h] BYREF
  __int64 v121; // [rsp+11F0h] [rbp+1170h] BYREF
  char *v122; // [rsp+11F8h] [rbp+1178h]
  __int64 v123; // [rsp+1200h] [rbp+1180h]
  __int64 v124; // [rsp+1208h] [rbp+1188h]
  __int64 v125; // [rsp+1210h] [rbp+1190h]
  __int64 v126; // [rsp+1218h] [rbp+1198h]
  __int64 v127; // [rsp+1220h] [rbp+11A0h]
  __int64 v128; // [rsp+1228h] [rbp+11A8h]
  char v129[8]; // [rsp+1230h] [rbp+11B0h] BYREF
  const char *v130; // [rsp+1238h] [rbp+11B8h]
  __int64 v131; // [rsp+1240h] [rbp+11C0h]
  const char *v132; // [rsp+1248h] [rbp+11C8h]
  __int16 v133; // [rsp+1250h] [rbp+11D0h]
  __int64 v134[4]; // [rsp+1260h] [rbp+11E0h] BYREF
  __int64 v135[4]; // [rsp+1280h] [rbp+1200h] BYREF
  __int64 v136; // [rsp+12A0h] [rbp+1220h] BYREF
  char *v137; // [rsp+12A8h] [rbp+1228h]
  char v138[64]; // [rsp+12B0h] [rbp+1230h] BYREF
  char v139; // [rsp+12F0h] [rbp+1270h]
  char v140; // [rsp+1308h] [rbp+1288h]
  __int64 v141[2]; // [rsp+14E0h] [rbp+1460h] BYREF
  __int64 v142[2]; // [rsp+14F0h] [rbp+1470h] BYREF
  __int64 v143[2]; // [rsp+1500h] [rbp+1480h] BYREF
  __int64 v144[2]; // [rsp+1510h] [rbp+1490h] BYREF
  __int64 v145[2]; // [rsp+1520h] [rbp+14A0h] BYREF
  __int64 v146[5]; // [rsp+1530h] [rbp+14B0h] BYREF
  __int64 v147; // [rsp+1558h] [rbp+14D8h]
  __int64 v148; // [rsp+1560h] [rbp+14E0h]
  _QWORD *v149; // [rsp+1568h] [rbp+14E8h]
  __int64 v150; // [rsp+1570h] [rbp+14F0h]
  __int64 v151; // [rsp+1578h] [rbp+14F8h]
  void *v152; // [rsp+1580h] [rbp+1500h]
  __int64 v153; // [rsp+1588h] [rbp+1508h]
  __int64 v154; // [rsp+1590h] [rbp+1510h]
  __int64 v155; // [rsp+1598h] [rbp+1518h]
  __int64 v156; // [rsp+15A0h] [rbp+1520h]
  char v157; // [rsp+15AFh] [rbp+152Fh]
  __int64 v158; // [rsp+15B0h] [rbp+1530h]
  __int64 v159; // [rsp+15B8h] [rbp+1538h]
  __int64 v160; // [rsp+15C0h] [rbp+1540h]
  __int64 v161; // [rsp+15C8h] [rbp+1548h]
  __int64 v162; // [rsp+15D0h] [rbp+1550h]
  __int64 v163; // [rsp+15D8h] [rbp+1558h]
  __int64 v164; // [rsp+15E0h] [rbp+1560h]
  char v165; // [rsp+15EFh] [rbp+156Fh]
  __int64 v166; // [rsp+15F0h] [rbp+1570h]
  __int64 v167; // [rsp+15F8h] [rbp+1578h]
  __int64 v168; // [rsp+1600h] [rbp+1580h]
  __int64 v169; // [rsp+1608h] [rbp+1588h]
  __int64 v170; // [rsp+1610h] [rbp+1590h]
  __int64 v171; // [rsp+1618h] [rbp+1598h]
  char v172; // [rsp+1627h] [rbp+15A7h]
  __int64 v173; // [rsp+1628h] [rbp+15A8h]
  char v174; // [rsp+1637h] [rbp+15B7h]
  __int64 v175; // [rsp+1638h] [rbp+15B8h]
  __int64 v176; // [rsp+1640h] [rbp+15C0h]
  __int64 v177; // [rsp+1648h] [rbp+15C8h]
  __int64 v178; // [rsp+1650h] [rbp+15D0h]
  char v179; // [rsp+165Fh] [rbp+15DFh]
  __int64 v180; // [rsp+1660h] [rbp+15E0h]
  __int64 v181; // [rsp+1668h] [rbp+15E8h]
  __int64 v182; // [rsp+1670h] [rbp+15F0h]
  __int64 v183; // [rsp+1678h] [rbp+15F8h]
  unsigned __int8 *v184; // [rsp+1680h] [rbp+1600h]
  __int64 v185; // [rsp+1688h] [rbp+1608h]
  char v186; // [rsp+1697h] [rbp+1617h]
  __int64 v187; // [rsp+1698h] [rbp+1618h]
  __int64 v188; // [rsp+16A0h] [rbp+1620h]
  __int64 v189; // [rsp+16A8h] [rbp+1628h]
  char v190; // [rsp+16B5h] [rbp+1635h]
  char v191; // [rsp+16B6h] [rbp+1636h]
  char v192; // [rsp+16B7h] [rbp+1637h]
  __int64 v193; // [rsp+16B8h] [rbp+1638h]
  __int64 v194; // [rsp+16C0h] [rbp+1640h]
  __int64 v195; // [rsp+16C8h] [rbp+1648h]
  __int64 v196; // [rsp+16D0h] [rbp+1650h]
  char v197; // [rsp+16DFh] [rbp+165Fh]
  __int64 v198; // [rsp+16E0h] [rbp+1660h]
  __int64 v199; // [rsp+16E8h] [rbp+1668h]
  __int64 v200; // [rsp+16F0h] [rbp+1670h]
  _BYTE *v201; // [rsp+16F8h] [rbp+1678h]
  char v202; // [rsp+1706h] [rbp+1686h]
  char v203; // [rsp+1707h] [rbp+1687h]
  __int64 v204; // [rsp+1708h] [rbp+1688h]
  __int64 v205; // [rsp+1710h] [rbp+1690h]
  __int64 v206; // [rsp+1718h] [rbp+1698h]
  __int64 v207; // [rsp+1720h] [rbp+16A0h]
  char v208; // [rsp+172Fh] [rbp+16AFh]
  __int64 v209; // [rsp+1730h] [rbp+16B0h]
  __int64 v210; // [rsp+1738h] [rbp+16B8h]
  __int64 v211; // [rsp+1740h] [rbp+16C0h]
  _BYTE *v212; // [rsp+1748h] [rbp+16C8h]
  char v213; // [rsp+1756h] [rbp+16D6h]
  char v214; // [rsp+1757h] [rbp+16D7h]
  __int64 v215; // [rsp+1758h] [rbp+16D8h]
  __int64 v216; // [rsp+1760h] [rbp+16E0h]
  __int64 v217; // [rsp+1768h] [rbp+16E8h]
  _BYTE *v218; // [rsp+1770h] [rbp+16F0h]
  char v219; // [rsp+177Ch] [rbp+16FCh]
  char v220; // [rsp+177Dh] [rbp+16FDh]
  char v221; // [rsp+177Eh] [rbp+16FEh]
  char progress_bool__modelZsave_u1666; // [rsp+177Fh] [rbp+16FFh]
  __int64 tick__modelZsimulationZcompile95thread_u3761; // [rsp+1780h] [rbp+1700h]
  char v224; // [rsp+178Fh] [rbp+170Fh]
  __int64 v225; // [rsp+1790h] [rbp+1710h]
  char v226; // [rsp+179Fh] [rbp+171Fh]
  _BYTE *v227; // [rsp+17A0h] [rbp+1720h]
  __int64 v228; // [rsp+17A8h] [rbp+1728h]
  __int64 v229; // [rsp+17B0h] [rbp+1730h]
  __int64 v230; // [rsp+17B8h] [rbp+1738h]
  __int64 v231; // [rsp+17C0h] [rbp+1740h]
  char v232; // [rsp+17CFh] [rbp+174Fh]
  __int64 v233; // [rsp+17D0h] [rbp+1750h]
  __int64 v234; // [rsp+17D8h] [rbp+1758h]
  __int64 v235; // [rsp+17E0h] [rbp+1760h]
  bool v236; // [rsp+17EDh] [rbp+176Dh]
  char v237; // [rsp+17EEh] [rbp+176Eh]
  bool v238; // [rsp+17EFh] [rbp+176Fh]
  __int64 v239; // [rsp+17F0h] [rbp+1770h]
  char v240; // [rsp+17FEh] [rbp+177Eh]
  unsigned __int8 v241; // [rsp+17FFh] [rbp+177Fh]
  __int64 v242; // [rsp+1800h] [rbp+1780h]
  __int64 v243; // [rsp+1808h] [rbp+1788h]
  __int64 v244; // [rsp+1810h] [rbp+1790h]
  __int64 v245; // [rsp+1818h] [rbp+1798h]
  unsigned __int8 v246; // [rsp+1827h] [rbp+17A7h]
  __int64 v247; // [rsp+1828h] [rbp+17A8h]
  __int64 v248; // [rsp+1830h] [rbp+17B0h]
  bool v249; // [rsp+183Fh] [rbp+17BFh]
  __int64 v250; // [rsp+1840h] [rbp+17C0h]
  __int64 v251; // [rsp+1848h] [rbp+17C8h]
  __int64 v252; // [rsp+1850h] [rbp+17D0h]
  bool v253; // [rsp+1859h] [rbp+17D9h]
  bool v254; // [rsp+185Ah] [rbp+17DAh]
  bool v255; // [rsp+185Bh] [rbp+17DBh]
  bool v256; // [rsp+185Ch] [rbp+17DCh]
  bool v257; // [rsp+185Dh] [rbp+17DDh]
  bool v258; // [rsp+185Eh] [rbp+17DEh]
  char v259; // [rsp+185Fh] [rbp+17DFh]

  v130 = "complete_current_level";
  v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
  v131 = 0i64;
  v133 = 0;
  nimFrame_162(v129);
  v227 = (_BYTE *)nimErrorFlag_157();
  nimZeroMem_132(v138, 560i64);
  v136 = 0i64;
  v137 = 0i64;
  *(_BYTE *)(a2 + 4400) = 0;
  v131 = 1936i64;
  v226 = 0;
  v226 = is_in_level_solution__presenterZutilities_u6341(a2);
  if ( *v227 )
    goto LABEL_329;
  if ( v226 != 1 )
  {
    v131 = 1939i64;
    v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
    v225 = 0i64;
    v4 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
    v55 = *refptr_loaded_level__modelZmodel95types_u830;
    v56 = v4;
    v225 = X5BX5D___modelZboardZboard_u17368(refptr_campaign__modelZmodel95types_u817, &v55);
    if ( *v227 )
      goto LABEL_329;
    v131 = 770i64;
    v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
    eqcopy___modelZboardZschematics_u4046(v138, v225);
    v131 = 1940i64;
    v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
    if ( v139 != 5 && v139 != 6 )
    {
      v131 = 1943i64;
      v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
      v257 = 0;
      v255 = v139 != 0;
      v256 = v139 != 0;
      if ( v139 )
      {
        v224 = 0;
        v5 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
        v55 = *refptr_loaded_level__modelZmodel95types_u830;
        v56 = v5;
        v224 = is_level__presenterZutilitiesZhelper95functions_u2961(11i64, &v55);
        if ( *v227 )
          goto LABEL_329;
        v256 = v224 == 0;
      }
      v257 = v256;
      if ( v256 )
      {
        v131 = 1944i64;
        tick__modelZsimulationZcompile95thread_u3761 = 0i64;
        tick__modelZsimulationZcompile95thread_u3761 = sim_get_tick__modelZsimulationZcompile95thread_u3761();
        if ( *v227 )
          goto LABEL_329;
        v257 = tick__modelZsimulationZcompile95thread_u3761 == -1;
      }
      if ( !v257 )
      {
        v131 = 1948i64;
        v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
        v6 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
        v55 = *refptr_loaded_level__modelZmodel95types_u830;
        v56 = v6;
        v53 = TM__8FyyixzftvDEeBWCL79bP9aA_623;
        v54 = &TM__8FyyixzftvDEeBWCL79bP9aA_84;
        if ( (unsigned __int8)eqStrings_25(&v55, &v53) == 1 )
        {
          v131 = 1949i64;
          v254 = a4;
          if ( a4 )
          {
            progress_bool__modelZsave_u1666 = 0;
            progress_bool__modelZsave_u1666 = get_progress_bool__modelZsave_u1666(10i64);
            if ( *v227 )
              goto LABEL_329;
            v254 = progress_bool__modelZsave_u1666 == 0;
          }
          if ( !v254 )
            goto LABEL_155;
          v131 = 1950i64;
          v221 = 0;
          v221 = steam_unlock_achievement__presenterZutilities_u27094(0i64);
          if ( !*v227 )
            goto LABEL_155;
          goto LABEL_329;
        }
        v131 = 1951i64;
        v7 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
        v55 = *refptr_loaded_level__modelZmodel95types_u830;
        v56 = v7;
        v53 = TM__8FyyixzftvDEeBWCL79bP9aA_624;
        v54 = &TM__8FyyixzftvDEeBWCL79bP9aA_86;
        if ( (unsigned __int8)eqStrings_25(&v55, &v53) == 1 )
        {
          v131 = 1952i64;
          v253 = a4;
          if ( a4 )
          {
            v220 = 0;
            v220 = get_progress_bool__modelZsave_u1666(10i64);
            if ( *v227 )
              goto LABEL_329;
            v253 = v220 == 0;
          }
          if ( !v253 )
            goto LABEL_155;
          v131 = 1953i64;
          v219 = 0;
          v219 = steam_unlock_achievement__presenterZutilities_u27094(6i64);
          if ( !*v227 )
            goto LABEL_155;
LABEL_329:
          v131 = 635i64;
          v132 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
          v55 = v136;
          v56 = v137;
          eqdestroy___modelZmodel95types_u2594(&v55);
          v131 = 770i64;
          v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
          eqdestroy___modelZboardZschematics_u4043(v138);
          return popFrame_162();
        }
        v131 = 1954i64;
        v8 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
        v55 = *refptr_loaded_level__modelZmodel95types_u830;
        v56 = v8;
        v53 = TM__8FyyixzftvDEeBWCL79bP9aA_625;
        v54 = &TM__8FyyixzftvDEeBWCL79bP9aA_463;
        if ( (unsigned __int8)eqStrings_25(&v55, &v53) == 1 )
        {
          v252 = 0i64;
          v251 = 0i64;
          v218 = 0i64;
          v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          v250 = 0i64;
          v131 = 250i64;
          v217 = a1[19];
          v216 = v217;
          v131 = 251i64;
          while ( v250 < v216 )
          {
            v131 = 1957i64;
            v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
            if ( v250 < 0 || v250 >= a1[19] )
            {
              raiseIndexError2(v250, a1[19] - 1);
              goto LABEL_329;
            }
            v9 = a1[20];
            v218 = (_BYTE *)(v9 + 560 * v250 + 8);
            v131 = 1958i64;
            if ( *(_BYTE *)(v9 + 560 * v250 + 480) != 1 )
            {
              v131 = 1961i64;
              v10 = *v218 != 0;
              v128 = v10 + v252;
              if ( __OFADD__(v10, v252) )
                goto LABEL_110;
              v252 = v128;
              v131 = 1962i64;
              v11 = *v218 == 6;
              v127 = v11 + v251;
              if ( __OFADD__(v11, v251) )
                goto LABEL_110;
              v251 = v127;
            }
            else
            {
              v131 = 1959i64;
            }
            v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v250;
            v131 = 254i64;
            v215 = a1[19];
            if ( v215 != v216 )
            {
              v55 = TM__8FyyixzftvDEeBWCL79bP9aA_628;
              v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_140_0;
              failedAssertImpl__stdZassertions_u234(&v55);
              if ( *v227 )
                goto LABEL_329;
            }
          }
          v131 = 1963i64;
          v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
          v249 = v252 == v251;
          if ( v252 == v251 )
            v249 = v251 <= 4;
          if ( v249 )
          {
            v131 = 1964i64;
            v214 = 0;
            v214 = steam_unlock_achievement__presenterZutilities_u27094(10i64);
            if ( *v227 )
              goto LABEL_329;
          }
          goto LABEL_155;
        }
        v131 = 1965i64;
        v12 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
        v55 = *refptr_loaded_level__modelZmodel95types_u830;
        v56 = v12;
        v53 = TM__8FyyixzftvDEeBWCL79bP9aA_629;
        v54 = &TM__8FyyixzftvDEeBWCL79bP9aA_468;
        if ( (unsigned __int8)eqStrings_25(&v55, &v53) == 1 )
        {
          v131 = 1966i64;
          if ( a1[1] <= 17 )
          {
            v131 = 1967i64;
            v213 = 0;
            v213 = steam_unlock_achievement__presenterZutilities_u27094(2i64);
            if ( *v227 )
              goto LABEL_329;
          }
          goto LABEL_155;
        }
        v131 = 1968i64;
        v13 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
        v55 = *refptr_loaded_level__modelZmodel95types_u830;
        v56 = v13;
        v53 = TM__8FyyixzftvDEeBWCL79bP9aA_630;
        v54 = &TM__8FyyixzftvDEeBWCL79bP9aA_470;
        if ( (unsigned __int8)eqStrings_25(&v55, &v53) == 1 )
        {
          v248 = 0i64;
          v212 = 0i64;
          v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          v247 = 0i64;
          v131 = 250i64;
          v211 = a1[19];
          v210 = v211;
          v131 = 251i64;
          while ( v247 < v210 )
          {
            v131 = 1970i64;
            v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
            if ( v247 < 0 || v247 >= a1[19] )
            {
              raiseIndexError2(v247, a1[19] - 1);
              goto LABEL_329;
            }
            v14 = a1[20];
            v212 = (_BYTE *)(v14 + 560 * v247 + 8);
            v131 = 1972i64;
            v246 = 0;
            v246 = *(_BYTE *)(v14 + 560 * v247 + 480) == 0;
            v246 &= 1u;
            if ( v246 == 1 )
              v246 = *v212 != 0;
            v126 = v246 + v248;
            if ( __OFADD__(v246, v248) )
              goto LABEL_110;
            v248 = v126;
            v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v247;
            v131 = 254i64;
            v209 = a1[19];
            if ( v209 != v210 )
            {
              v55 = TM__8FyyixzftvDEeBWCL79bP9aA_632;
              v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_140_0;
              failedAssertImpl__stdZassertions_u234(&v55);
              if ( *v227 )
                goto LABEL_329;
            }
          }
          v131 = 1973i64;
          v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
          if ( v248 <= 5 )
          {
            v131 = 1974i64;
            v208 = 0;
            v208 = steam_unlock_achievement__presenterZutilities_u27094(5i64);
            if ( *v227 )
              goto LABEL_329;
          }
          goto LABEL_155;
        }
        v131 = 1975i64;
        v15 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
        v55 = *refptr_loaded_level__modelZmodel95types_u830;
        v56 = v15;
        v53 = TM__8FyyixzftvDEeBWCL79bP9aA_633;
        v54 = &TM__8FyyixzftvDEeBWCL79bP9aA_474;
        if ( (unsigned __int8)eqStrings_25(&v55, &v53) == 1 )
        {
          v245 = 0i64;
          v207 = 0i64;
          v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          v244 = 0i64;
          v131 = 250i64;
          v206 = a1[19];
          v205 = v206;
          v131 = 251i64;
          while ( v244 < v205 )
          {
            v131 = 1977i64;
            v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
            if ( v244 < 0 || v244 >= a1[19] )
            {
              raiseIndexError2(v244, a1[19] - 1);
              goto LABEL_329;
            }
            v16 = a1[20];
            v207 = v16 + 560 * v244 + 8;
            v131 = 1978i64;
            if ( *(_BYTE *)(v16 + 560 * v244 + 480) != 1 )
            {
              v131 = 1981i64;
              if ( *(_BYTE *)v207 == 30 )
              {
                v131 = 1982i64;
                v17 = *(_QWORD *)(v207 + 232);
                v125 = v17 + v245;
                if ( __OFADD__(v17, v245) )
                  goto LABEL_110;
                v245 = v125;
              }
              else
              {
                v131 = 1983i64;
                if ( *(_BYTE *)v207 == 15 )
                {
                  v131 = 1984i64;
                  v124 = v245 + 1;
                  if ( __OFADD__(1i64, v245) )
                    goto LABEL_110;
                  v245 = v124;
                }
              }
            }
            else
            {
              v131 = 1979i64;
            }
            v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v244;
            v131 = 254i64;
            v204 = a1[19];
            if ( v204 != v205 )
            {
              v55 = TM__8FyyixzftvDEeBWCL79bP9aA_636;
              v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_140_0;
              failedAssertImpl__stdZassertions_u234(&v55);
              if ( *v227 )
                goto LABEL_329;
            }
          }
          v131 = 1986i64;
          v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
          if ( v245 <= 56 )
          {
            v131 = 1987i64;
            v203 = 0;
            v203 = steam_unlock_achievement__presenterZutilities_u27094(7i64);
            if ( *v227 )
              goto LABEL_329;
          }
          goto LABEL_155;
        }
        v131 = 1988i64;
        v18 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
        v55 = *refptr_loaded_level__modelZmodel95types_u830;
        v56 = v18;
        v53 = TM__8FyyixzftvDEeBWCL79bP9aA_637;
        v54 = &TM__8FyyixzftvDEeBWCL79bP9aA_479;
        if ( (unsigned __int8)eqStrings_25(&v55, &v53) == 1 )
        {
          v131 = 1989i64;
          v202 = 0;
          v202 = steam_unlock_achievement__presenterZutilities_u27094(11i64);
          if ( *v227 )
            goto LABEL_329;
          goto LABEL_155;
        }
        v131 = 1990i64;
        v19 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
        v55 = *refptr_loaded_level__modelZmodel95types_u830;
        v56 = v19;
        v53 = TM__8FyyixzftvDEeBWCL79bP9aA_638;
        v54 = &TM__8FyyixzftvDEeBWCL79bP9aA_481;
        if ( (unsigned __int8)eqStrings_25(&v55, &v53) == 1 )
        {
          v243 = 0i64;
          v201 = 0i64;
          v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          v242 = 0i64;
          v131 = 250i64;
          v200 = a1[19];
          v199 = v200;
          v131 = 251i64;
          while ( v242 < v199 )
          {
            v131 = 1992i64;
            v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
            if ( v242 < 0 || v242 >= a1[19] )
            {
              raiseIndexError2(v242, a1[19] - 1);
              goto LABEL_329;
            }
            v20 = a1[20];
            v201 = (_BYTE *)(v20 + 560 * v242 + 8);
            v131 = 1994i64;
            v241 = 0;
            v241 = *(_BYTE *)(v20 + 560 * v242 + 480) == 0;
            v241 &= 1u;
            if ( v241 == 1 )
              v241 = *v201 != 0;
            v123 = v241 + v243;
            if ( __OFADD__(v241, v243) )
            {
LABEL_110:
              raiseOverflow();
              goto LABEL_329;
            }
            v243 = v123;
            v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v242;
            v131 = 254i64;
            v198 = a1[19];
            if ( v198 != v199 )
            {
              v55 = TM__8FyyixzftvDEeBWCL79bP9aA_640;
              v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_140_0;
              failedAssertImpl__stdZassertions_u234(&v55);
              if ( *v227 )
                goto LABEL_329;
            }
          }
          v131 = 1995i64;
          v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
          if ( v243 <= 10 )
          {
            v131 = 1996i64;
            v197 = 0;
            v197 = steam_unlock_achievement__presenterZutilities_u27094(4i64);
            if ( *v227 )
              goto LABEL_329;
          }
          goto LABEL_155;
        }
        v131 = 1997i64;
        v21 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
        v55 = *refptr_loaded_level__modelZmodel95types_u830;
        v56 = v21;
        v53 = TM__8FyyixzftvDEeBWCL79bP9aA_641;
        v54 = &TM__8FyyixzftvDEeBWCL79bP9aA_485;
        if ( (unsigned __int8)eqStrings_25(&v55, &v53) != 1 )
        {
          v131 = 2019i64;
          v24 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
          v55 = *refptr_loaded_level__modelZmodel95types_u830;
          v56 = v24;
          v53 = TM__8FyyixzftvDEeBWCL79bP9aA_643;
          v54 = &TM__8FyyixzftvDEeBWCL79bP9aA_489;
          if ( (unsigned __int8)eqStrings_25(&v55, &v53) != 1 )
          {
            v131 = 2021i64;
            v25 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
            v55 = *refptr_loaded_level__modelZmodel95types_u830;
            v56 = v25;
            v53 = TM__8FyyixzftvDEeBWCL79bP9aA_644;
            v54 = &TM__8FyyixzftvDEeBWCL79bP9aA_491;
            if ( (unsigned __int8)eqStrings_25(&v55, &v53) == 1 )
            {
              v131 = 2022i64;
              v190 = 0;
              v190 = steam_unlock_achievement__presenterZutilities_u27094(12i64);
              if ( *v227 )
                goto LABEL_329;
            }
          }
          else
          {
            v131 = 2020i64;
            v191 = 0;
            v191 = steam_unlock_achievement__presenterZutilities_u27094(8i64);
            if ( *v227 )
              goto LABEL_329;
          }
          goto LABEL_155;
        }
        v240 = 1;
        v196 = 0i64;
        v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v239 = 0i64;
        v131 = 250i64;
        v195 = a1[19];
        v194 = v195;
        v131 = 251i64;
        while ( 1 )
        {
          if ( v239 >= v194 )
            goto LABEL_146;
          v131 = 1999i64;
          v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
          if ( v239 < 0 || v239 >= a1[19] )
          {
            raiseIndexError2(v239, a1[19] - 1);
            goto LABEL_329;
          }
          v22 = a1[20];
          v196 = v22 + 560 * v239 + 8;
          v131 = 2000i64;
          if ( *(_BYTE *)(v22 + 560 * v239 + 480) == 1 )
          {
            v131 = 2001i64;
            goto LABEL_142;
          }
          v131 = 2003i64;
          if ( ((TM__8FyyixzftvDEeBWCL79bP9aA_487[*(_BYTE *)v196 >> 3] >> (*(_BYTE *)v196 & 7)) & 1) != 0 )
          {
            v240 = 0;
            v131 = 2008i64;
            goto LABEL_146;
          }
          v238 = 0;
          v131 = 2010i64;
          v23 = *(_BYTE *)v196 == 18
             || *(_BYTE *)v196 == 20
             || *(_BYTE *)v196 == 19
             || *(_BYTE *)v196 == 23
             || *(_BYTE *)v196 == 21
             || *(_BYTE *)v196 == 22
             || *(_BYTE *)v196 == 24;
          v238 = v23;
          if ( v23 )
          {
            v131 = 2013i64;
            v238 = *(_QWORD *)(v196 + 232) == 1i64;
          }
          if ( v238 )
            break;
LABEL_142:
          v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          ++v239;
          v131 = 254i64;
          v193 = a1[19];
          if ( v193 != v194 )
          {
            v55 = TM__8FyyixzftvDEeBWCL79bP9aA_642;
            v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_140_0;
            failedAssertImpl__stdZassertions_u234(&v55);
            if ( *v227 )
              goto LABEL_329;
          }
        }
        v240 = 0;
        v131 = 2015i64;
LABEL_146:
        v131 = 2017i64;
        v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
        if ( v240 == 1 )
        {
          v131 = 2018i64;
          v192 = 0;
          v192 = steam_unlock_achievement__presenterZutilities_u27094(1i64);
          if ( *v227 )
            goto LABEL_329;
        }
LABEL_155:
        v259 = 0;
        v258 = 0;
        v131 = 2026i64;
        v237 = v140 == 0;
        if ( !v140 )
        {
          v237 = immutable_loaded__modelZboardZboard_u17313();
          if ( *v227 )
            goto LABEL_329;
        }
        if ( v237 != 1 )
        {
          v131 = 2029i64;
          v259 = complete_level__modelZutilities_u8913(a1);
          if ( *v227 )
            goto LABEL_329;
          v131 = 2030i64;
          v258 = v259 == 1;
        }
        else
        {
          v131 = 2027i64;
          v258 = 1;
        }
        v131 = 2032i64;
        v236 = v258;
        if ( !v258 )
          goto LABEL_312;
        nimZeroMem_132(v61, 200i64);
        nimZeroMem_132(v57, 128i64);
        v131 = 2033i64;
        nimZeroMem_132(v61, 200i64);
        v64 = 3;
        v131 = 2035i64;
        get_progress_string__modelZsave_u1680(&v55, 3i64);
        v62 = v55;
        v63 = v56;
        if ( *v227 )
          goto LABEL_311;
        v131 = 27i64;
        v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v65[0] = 0i64;
        v65[1] = 0i64;
        nimZeroMem_132(v66, 128i64);
        v67 = 0i64;
        v68 = 0i64;
        v69 = 0i64;
        v131 = 1699i64;
        v26 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
        v55 = *refptr_loaded_level__modelZmodel95types_u830;
        v56 = v26;
        eqcopy___system_u2661(v57, &v55);
        v131 = 2042i64;
        v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
        if ( v259 != 1 )
        {
LABEL_308:
          v131 = 27i64;
          v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( (v64 & 0x1F) == 3i64 )
          {
            eqsink___presenterZutilities_u28142(v66, v57);
            eqwasMoved___presenterZutilities_u28130(v57);
            v131 = 2112i64;
            v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
            send_network_request__modelZnetworkingZclient_u1848((__int64)v61);
          }
          else
          {
            dollar___modelZnetworkingZnetworking_u20(v146, v64);
            v55 = TM__8FyyixzftvDEeBWCL79bP9aA_661;
            v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_521;
            v53 = v146[0];
            v54 = (void *)v146[1];
            raiseFieldErrorStr(&v55, &v53);
          }
          goto LABEL_311;
        }
        v121 = 0i64;
        v122 = 0i64;
        nimZeroMem_132(v120, 24i64);
        nimZeroMem_132(v72, 104i64);
        nimZeroMem_132(&v119, 8i64);
        nimZeroMem_132(v73, 104i64);
        v189 = 0i64;
        v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v234 = 0i64;
        v131 = 183i64;
        v188 = a1[23];
        v187 = v188;
        v131 = 184i64;
        while ( v234 < v187 )
        {
          v189 = v234;
          v131 = 185i64;
          v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          if ( v234 < 0 || v234 >= a1[23] )
          {
            raiseIndexError2(v234, a1[23] - 1);
            goto LABEL_307;
          }
          eqcopy___modelZsave95mongerZcommon_u3692(v73, a1[24] + 104 * v234 + 8);
          v119 = v189;
          v131 = 185i64;
          v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          eqsink___modelZsave95mongerZcommon_u3698(v72, v73);
          eqwasMoved___modelZsave95mongerZcommon_u3686(v73);
          v131 = 2044i64;
          v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
          v186 = 0;
          v186 = is_tombstone__modelZsave95mongerZcommon_u4884(v72);
          if ( !*v227 )
          {
            if ( v186 || (v131 = 2045i64, v118 = add_wire__modelZsave95mongerZcommon_u4112(v58, v72), !*v227) )
            {
              v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v234;
              v131 = 187i64;
              v185 = a1[23];
              if ( v185 == v187 )
                continue;
              v55 = TM__8FyyixzftvDEeBWCL79bP9aA_645;
              v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_126_0;
              failedAssertImpl__stdZassertions_u234(&v55);
              if ( !*v227 )
                continue;
            }
          }
LABEL_307:
          v131 = 441i64;
          v132 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
          eqdestroy___modelZboardZboard_u15245(v120);
          v131 = 13i64;
          v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\setimpl.nim";
          v55 = v121;
          v56 = v122;
          eqdestroy___modelZboardZboard_u11470(&v55);
          if ( !*v227 )
            goto LABEL_308;
LABEL_311:
          v131 = 27i64;
          v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          eqdestroy___presenterZutilities_u28133(v57);
          v131 = 368i64;
          v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\channels_builtin.nim";
          eqdestroy___modelZnetworkingZclient_u1882(v61);
          if ( !*v227 )
          {
LABEL_312:
            v82 = 0i64;
            v83 = 0i64;
            v149 = 0i64;
            v131 = 2116i64;
            v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
            v42 = (char *)refptr_loaded_level__modelZmodel95types_u830[1];
            v55 = *refptr_loaded_level__modelZmodel95types_u830;
            v56 = v42;
            get_level_post_mortem_dialogues__presenterZutilitiesZhelper95functions_u1705(&v82, a2 + 8, a3, &v55);
            if ( !*v227 )
            {
              v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              v228 = 0i64;
              v148 = v82;
              v147 = v82;
              v131 = 251i64;
              while ( v228 < v147 )
              {
                nimZeroMem_132(v81, 24i64);
                v131 = 2116i64;
                v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                if ( v228 < 0 || v228 >= v82 )
                {
                  raiseIndexError2(v228, v82 - 1);
                  break;
                }
                v43 = &v83[24 * v228];
                v149 = v43 + 8;
                v131 = 934i64;
                v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                v44 = *((_QWORD *)v43 + 2);
                v47 = *((_QWORD *)v43 + 1);
                v48 = v44;
                v49 = *((_QWORD *)v43 + 3);
                eqdup___modelZmodel95types_u2666(&v50, &v47);
                v81[0] = v50;
                v81[1] = (__int64)v51;
                v81[2] = v52;
                v131 = 2117i64;
                v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                v47 = v50;
                v48 = (__int64)v51;
                v49 = v52;
                add__modelZcampaigns_u260(&v136, &v47);
                v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                ++v228;
                v131 = 254i64;
                v146[4] = v82;
                if ( v82 != v147 )
                {
                  v55 = TM__8FyyixzftvDEeBWCL79bP9aA_662;
                  v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_140_0;
                  failedAssertImpl__stdZassertions_u234(&v55);
                  if ( *v227 )
                    break;
                }
              }
            }
            v131 = 635i64;
            v132 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
            v55 = v82;
            v56 = v83;
            eqdestroy___modelZmodel95types_u2594(&v55);
            if ( !*v227 )
            {
              v131 = 2119i64;
              v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
              nimZeroMem_132(v135, 24i64);
              LOBYTE(v135[0]) = 7;
              v47 = v135[0];
              v48 = v135[1];
              v49 = v135[2];
              add__modelZcampaigns_u260(&v136, &v47);
              v131 = 2120i64;
              nimZeroMem_132(v134, 24i64);
              LOBYTE(v134[0]) = 9;
              v47 = v134[0];
              v48 = v134[1];
              v49 = v134[2];
              add__modelZcampaigns_u260(&v136, &v47);
              v131 = 2122i64;
              v146[3] = v136;
              if ( v136 )
              {
                v131 = 2123i64;
                if ( v137 )
                  v45 = v137 + 8;
                else
                  v45 = 0i64;
                reverse__presenterZutilities_u16482(v45, v136);
                if ( !*v227 )
                {
                  v131 = 2124i64;
                  nimZeroMem_132(v80, 24i64);
                  LOBYTE(v80[0]) = 8;
                  v47 = v80[0];
                  v48 = v80[1];
                  v49 = v80[2];
                  add__modelZcampaigns_u260(&v136, &v47);
                  v131 = 2125i64;
                  nimZeroMem_132(v73, 56i64);
                  v73[0] = v136;
                  v73[1] = (__int64)v137;
                  v74 = 1;
                  open__presenterZutilities_u16521(a2 + 3096, v73);
                }
              }
            }
          }
          goto LABEL_329;
        }
        v131 = 185i64;
        eqdestroy___modelZsave95mongerZcommon_u3689(v73);
        eqdestroy___modelZsave95mongerZcommon_u3689(v72);
        v235 = 0i64;
        v184 = 0i64;
        v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v233 = 0i64;
        v131 = 250i64;
        v183 = a1[19];
        v182 = v183;
        v131 = 251i64;
        while ( 2 )
        {
          if ( v233 < v182 )
          {
            v131 = 2050i64;
            v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
            if ( v233 < 0 || v233 >= a1[19] )
            {
              raiseIndexError2(v233, a1[19] - 1);
              goto LABEL_307;
            }
            v184 = (unsigned __int8 *)(a1[20] + 560 * v233 + 8);
            nimZeroMem_132(v73, 1448i64);
            nimZeroMem_132(v70, 560i64);
            v131 = 2051i64;
            if ( *v184 == 78 )
            {
              v181 = 0i64;
              nimZeroMem_132(v71, 560i64);
              v131 = 2052i64;
              v181 = *((_QWORD *)v184 + 49);
              v116 = v181;
              v117 = 0i64;
              v55 = v181;
              v56 = 0i64;
              add__presenterZutilities_u27278(&v121, &v55);
              v131 = 34i64;
              v132 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
              nimZeroMem_132(v72, 560i64);
              eqdup___modelZsave95mongerZversionsZv0_u151(v184, v72);
              qmemcpy(v71, v72, sizeof(v71));
              v131 = 2053i64;
              v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
              add__modelZsave95mongerZversionsZv0_u1028(v58, v71);
              v131 = 170i64;
              v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              eqdestroy___modelZboardZprototype95list_u3239(v73);
              v131 = 2054i64;
              v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
              goto LABEL_197;
            }
            v131 = 2056i64;
            v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
            v180 = 0i64;
            v180 = X5BX5D___modelZboardZprototype95list_u4239(
                     refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
                     *v184);
            if ( !*v227 )
            {
              v131 = 170i64;
              v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              eqcopy___modelZboardZprototype95list_u3242(v73, v180);
              v131 = 2057i64;
              v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
              if ( LOBYTE(v73[0]) == 5 )
              {
                v131 = 170i64;
                v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                eqdestroy___modelZboardZprototype95list_u3239(v73);
                v131 = 2058i64;
                v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                goto LABEL_197;
              }
              v131 = 2060i64;
              v232 = 0;
              v27 = *v184;
              v28 = *((_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788 + 1);
              v50 = *(_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788;
              v51 = (void *)v28;
              v52 = *((_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788 + 2);
              v232 = contains__modelZboardZmemory95manager_u414(&v50, v27);
              if ( !*v227 )
              {
                if ( v232 != 1 )
                  goto LABEL_190;
                v179 = 0;
                v179 = is_immutable_data__modelZsave95mongerZcommon_u5429(v184);
                if ( !*v227 )
                {
                  v232 = v179 == 0;
LABEL_190:
                  if ( v232 == 1 )
                  {
                    v131 = 2061i64;
                    v29 = *((_QWORD *)v184 + 46);
                    v115 = v29 + v235;
                    if ( __OFADD__(v29, v235) )
                    {
                      raiseOverflow();
                      goto LABEL_196;
                    }
                    v235 = v115;
                    v131 = 2062i64;
                    if ( v115 > 524288000 )
                    {
                      *(_BYTE *)(a2 + 4400) = 1;
                      v131 = 170i64;
                      v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                      eqdestroy___modelZboardZprototype95list_u3239(v73);
                      v131 = 441i64;
                      v132 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
                      eqdestroy___modelZboardZboard_u15245(v120);
                      v131 = 13i64;
                      v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\setimpl.nim";
                      v55 = v121;
                      v56 = v122;
                      eqdestroy___modelZboardZboard_u11470(&v55);
                      v131 = 2064i64;
                      v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                      goto LABEL_311;
                    }
                  }
                  v131 = 34i64;
                  v132 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                  nimZeroMem_132(v72, 560i64);
                  eqdup___modelZsave95mongerZversionsZv0_u151(v184, v72);
                  qmemcpy(v70, v72, sizeof(v70));
                  v131 = 2066i64;
                  v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                  add__modelZsave95mongerZversionsZv0_u1028(v58, v70);
                }
              }
            }
LABEL_196:
            v131 = 170i64;
            v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            eqdestroy___modelZboardZprototype95list_u3239(v73);
            if ( *v227 )
              goto LABEL_307;
LABEL_197:
            v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v233;
            v131 = 254i64;
            v178 = a1[19];
            if ( v178 != v182 )
            {
              v55 = TM__8FyyixzftvDEeBWCL79bP9aA_647;
              v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_140_0;
              failedAssertImpl__stdZassertions_u234(&v55);
              if ( *v227 )
                goto LABEL_307;
            }
            continue;
          }
          break;
        }
        v131 = 2070i64;
        v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
        while ( 1 )
        {
          v177 = v121;
          if ( v121 <= 0 )
          {
            nimZeroMem_132(&v107, 8i64);
            v171 = 0i64;
            v170 = 0i64;
            v131 = 767i64;
            v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
            v31 = a1[77];
            v50 = a1[76];
            v51 = (void *)v31;
            v52 = a1[78];
            v169 = len__presenterZutilities_u27713(&v50);
            if ( !*v227 )
            {
              v168 = 0i64;
              v167 = 0i64;
              v131 = 768i64;
              v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
              v166 = a1[76] - 1;
              v167 = v166;
              v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
              v231 = 0i64;
              v131 = 97i64;
              while ( v231 <= v167 )
              {
                v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                v168 = v231;
                v131 = 769i64;
                if ( v231 < 0 || v168 >= a1[76] )
                {
LABEL_239:
                  raiseIndexError2(v168, a1[76] - 1);
                  goto LABEL_307;
                }
                v165 = 0;
                v165 = isFilled__pureZcollectionsZtables_u31_20(*(_QWORD *)(a1[77] + 32 * v168 + 8));
                if ( *v227 )
                  goto LABEL_307;
                if ( v165 == 1 )
                {
                  nimZeroMem_132(&v103, 24i64);
                  v101 = 0i64;
                  v102 = 0i64;
                  v131 = 2092i64;
                  v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                  if ( v168 < 0 )
                    goto LABEL_239;
                  if ( v168 >= a1[76] )
                    goto LABEL_239;
                  v107 = *(_QWORD *)(a1[77] + 32 * v168 + 16);
                  if ( v168 >= a1[76] )
                    goto LABEL_239;
                  v171 = *(_QWORD *)(a1[77] + 32 * v168 + 24);
                  if ( v168 >= a1[76] )
                    goto LABEL_239;
                  v170 = *(_QWORD *)(a1[77] + 32 * v168 + 32);
                  v131 = 2093i64;
                  get_buffer_nontrivial_data__presenterZutilities_u26863(&v50, v171, v170);
                  v103 = v50;
                  v104 = v51;
                  v105 = v52;
                  if ( *v227 )
                    goto LABEL_307;
                  v101 = v103;
                  v102 = v104;
                  v131 = 1772i64;
                  v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\times.nim";
                  eqwasMoved___pureZtimes_u2665(&v103);
                  v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                  v164 = v105;
                  v131 = 2094i64;
                  v163 = v101;
                  if ( v101 > 0 )
                  {
                    v96 = v101;
                    v97 = v102;
                    v131 = 1772i64;
                    v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\times.nim";
                    eqwasMoved___pureZtimes_u2665(&v101);
                    v98 = v96;
                    v99 = v97;
                    v100 = v164;
                    v131 = 2095i64;
                    v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                    v50 = v96;
                    v51 = v97;
                    v52 = v164;
                    X5BX5Deq___modelZnetworkingZnetworking_u1039(&v60, v107, &v50);
                    if ( *v227 )
                      goto LABEL_307;
                  }
                  v131 = 771i64;
                  v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                  v162 = 0i64;
                  v32 = a1[77];
                  v50 = a1[76];
                  v51 = (void *)v32;
                  v52 = a1[78];
                  v162 = len__presenterZutilities_u27713(&v50);
                  if ( *v227 )
                    goto LABEL_307;
                  if ( v162 != v169 )
                  {
                    v55 = TM__8FyyixzftvDEeBWCL79bP9aA_650;
                    v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_216;
                    failedAssertImpl__stdZassertions_u234(&v55);
                    if ( *v227 )
                      goto LABEL_307;
                  }
                  v131 = 1772i64;
                  v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\times.nim";
                  v55 = v101;
                  v56 = (char *)v102;
                  eqdestroy___pureZtimes_u2668(&v55);
                  v131 = 770i64;
                  v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                  eqdestroy___modelZnetworkingZnetworking_u711(&v103);
                }
                v131 = 102i64;
                v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                v106 = v231 + 1;
                if ( __OFADD__(1i64, v231) )
                  goto LABEL_305;
                v231 = v106;
              }
              v94 = 0i64;
              v95 = 0i64;
              nimZeroMem_132(v73, 72i64);
              v131 = 767i64;
              v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
              v33 = *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 1);
              v50 = *(_QWORD *)refptr_level_progress__modelZmodel95types_u825;
              v51 = (void *)v33;
              v52 = *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 2);
              v161 = len__modelZutilities_u5736(&v50);
              if ( !*v227 )
              {
                v160 = 0i64;
                v159 = 0i64;
                v131 = 768i64;
                v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                v158 = *(_QWORD *)refptr_level_progress__modelZmodel95types_u825 - 1i64;
                v159 = v158;
                v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                v230 = 0i64;
                v131 = 97i64;
                while ( v230 <= v159 )
                {
                  v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                  v160 = v230;
                  v131 = 769i64;
                  if ( v230 < 0 || v160 >= *(_QWORD *)refptr_level_progress__modelZmodel95types_u825 )
                  {
LABEL_267:
                    raiseIndexError2(v160, *(_QWORD *)refptr_level_progress__modelZmodel95types_u825 - 1i64);
                    goto LABEL_307;
                  }
                  v157 = 0;
                  v157 = isFilled__pureZcollectionsZtables_u31_20(*(_QWORD *)(*((_QWORD *)refptr_level_progress__modelZmodel95types_u825
                                                                              + 1)
                                                                            + 96 * v160
                                                                            + 8));
                  if ( *v227 )
                    goto LABEL_307;
                  if ( v157 == 1 )
                  {
                    v91 = 0i64;
                    v92 = 0i64;
                    v131 = 1699i64;
                    v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                    if ( v160 < 0 )
                      goto LABEL_267;
                    if ( v160 >= *(_QWORD *)refptr_level_progress__modelZmodel95types_u825 )
                      goto LABEL_267;
                    v34 = *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 1) + 96 * v160;
                    v35 = *(char **)(v34 + 24);
                    v55 = *(_QWORD *)(v34 + 16);
                    v56 = v35;
                    eqcopy___system_u2661(&v94, &v55);
                    v131 = 419i64;
                    v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                    if ( v160 < 0 || v160 >= *(_QWORD *)refptr_level_progress__modelZmodel95types_u825 )
                      goto LABEL_267;
                    eqcopy___modelZboardZschematics_u2147(
                      v73,
                      *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 1) + 96 * v160 + 16 + 16);
                    v131 = 2098i64;
                    v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                    newSeq__presenterZutilities_u28043(&v55, 0i64);
                    v91 = v55;
                    v92 = v56;
                    v156 = 0i64;
                    v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                    v229 = 0i64;
                    v155 = v75;
                    v154 = v75;
                    v131 = 251i64;
                    while ( v229 < v154 )
                    {
                      v153 = 0i64;
                      v152 = 0i64;
                      v131 = 2099i64;
                      v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                      if ( v229 < 0 || v229 >= v75 )
                      {
                        raiseIndexError2(v229, v75 - 1);
                        goto LABEL_307;
                      }
                      v36 = v76 + 24 * v229;
                      v156 = v36 + 8;
                      v131 = 2100i64;
                      v153 = *(_QWORD *)(v36 + 8);
                      v85 = v153;
                      v152 = *(void **)(v36 + 16);
                      v86 = v152;
                      v55 = v153;
                      v56 = (char *)v152;
                      add__modelZscores_u2592(&v91, &v55);
                      v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                      ++v229;
                      v131 = 254i64;
                      v151 = v75;
                      if ( v75 != v154 )
                      {
                        v55 = TM__8FyyixzftvDEeBWCL79bP9aA_652;
                        v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_140_0;
                        failedAssertImpl__stdZassertions_u234(&v55);
                        if ( *v227 )
                          goto LABEL_307;
                      }
                    }
                    v131 = 2101i64;
                    v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                    if ( (v64 & 0x1F) != 3i64 )
                    {
                      dollar___modelZnetworkingZnetworking_u20(v141, v64);
                      v55 = TM__8FyyixzftvDEeBWCL79bP9aA_653;
                      v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_509;
                      v53 = v141[0];
                      v54 = (void *)v141[1];
                      raiseFieldErrorStr(&v55, &v53);
                      goto LABEL_307;
                    }
                    v89 = v94;
                    v90 = v95;
                    v131 = 1699i64;
                    v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                    eqwasMoved___system_u2658(&v94);
                    v72[0] = v89;
                    v72[1] = (__int64)v90;
                    v131 = 2101i64;
                    v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                    v87 = v91;
                    v88 = v92;
                    v72[2] = v91;
                    v72[3] = (__int64)v92;
                    add__presenterZutilities_u28069(v65, v72);
                    v131 = 771i64;
                    v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                    v150 = 0i64;
                    v37 = *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 1);
                    v50 = *(_QWORD *)refptr_level_progress__modelZmodel95types_u825;
                    v51 = (void *)v37;
                    v52 = *((_QWORD *)refptr_level_progress__modelZmodel95types_u825 + 2);
                    v150 = len__modelZutilities_u5736(&v50);
                    if ( *v227 )
                      goto LABEL_307;
                    if ( v150 != v161 )
                    {
                      v55 = TM__8FyyixzftvDEeBWCL79bP9aA_654;
                      v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_216;
                      failedAssertImpl__stdZassertions_u234(&v55);
                      if ( *v227 )
                        goto LABEL_307;
                    }
                  }
                  v131 = 102i64;
                  v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                  v93 = v230 + 1;
                  if ( __OFADD__(1i64, v230) )
                    goto LABEL_305;
                  v230 = v93;
                }
                v131 = 419i64;
                v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                eqdestroy___modelZboardZschematics_u2144(v73);
                v131 = 394i64;
                v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                if ( v95 && (*v95 & 0x4000000000000000i64) == 0 )
                  deallocShared(v95);
                v131 = 2103i64;
                v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                if ( (v64 & 0x1F) == 3i64 )
                {
                  v67 = *a1;
                  v131 = 2104i64;
                  if ( (v64 & 0x1F) == 3i64 )
                  {
                    v68 = a1[1];
                    v131 = 2106i64;
                    if ( v139 == 1 || v139 == 2 )
                    {
                      v131 = 2107i64;
                      if ( (v64 & 0x1F) == 3i64 )
                      {
                        v69 = 1i64;
                      }
                      else
                      {
                        dollar___modelZnetworkingZnetworking_u20(v144, v64);
                        v55 = TM__8FyyixzftvDEeBWCL79bP9aA_658;
                        v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_517;
                        v53 = v144[0];
                        v54 = (void *)v144[1];
                        raiseFieldErrorStr(&v55, &v53);
                      }
                    }
                    else
                    {
                      v131 = 2109i64;
                      if ( (v64 & 0x1F) == 3i64 )
                      {
                        v38 = a1[88];
                        v39 = 0;
                        v40 = __OFADD__(1i64, v38);
                        v41 = v38 + 1;
                        if ( v40 )
                          v39 = 1;
                        v84 = v41;
                        if ( (v39 & 1) != 0 )
LABEL_305:
                          raiseOverflow();
                        else
                          v69 = v84;
                      }
                      else
                      {
                        dollar___modelZnetworkingZnetworking_u20(v145, v64);
                        v55 = TM__8FyyixzftvDEeBWCL79bP9aA_659;
                        v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_517;
                        v53 = v145[0];
                        v54 = (void *)v145[1];
                        raiseFieldErrorStr(&v55, &v53);
                      }
                    }
                  }
                  else
                  {
                    dollar___modelZnetworkingZnetworking_u20(v143, v64);
                    v55 = TM__8FyyixzftvDEeBWCL79bP9aA_657;
                    v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_515;
                    v53 = v143[0];
                    v54 = (void *)v143[1];
                    raiseFieldErrorStr(&v55, &v53);
                  }
                }
                else
                {
                  dollar___modelZnetworkingZnetworking_u20(v142, v64);
                  v55 = TM__8FyyixzftvDEeBWCL79bP9aA_656;
                  v56 = (char *)&TM__8FyyixzftvDEeBWCL79bP9aA_513;
                  v53 = v142[0];
                  v54 = (void *)v142[1];
                  raiseFieldErrorStr(&v55, &v53);
                }
              }
            }
            goto LABEL_307;
          }
          nimZeroMem_132(v73, 1448i64);
          nimZeroMem_132(v71, 560i64);
          v131 = 2071i64;
          pop__presenterZutilities_u27440(v114, &v121);
          v176 = v114[0];
          v175 = v114[1];
          v131 = 2072i64;
          v174 = 0;
          v50 = v120[0];
          v51 = (void *)v120[1];
          v52 = v120[2];
          v174 = contains__modelZboardZboard_u12534(&v50, v114[0]);
          if ( *v227 )
            goto LABEL_224;
          if ( v174 == 1 )
          {
            v131 = 34i64;
            v132 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
            eqdestroy___modelZsave95mongerZversionsZv0_u145(v71);
            v131 = 170i64;
            v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            eqdestroy___modelZboardZprototype95list_u3239(v73);
            v131 = 2073i64;
            v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
            continue;
          }
          v131 = 2075i64;
          get_custom_prototype__modelZboardZcustom95prototype95list_u451(v176, v73);
          if ( *v227 )
            goto LABEL_224;
          v131 = 2076i64;
          v173 = v77;
          if ( v77 > v175 )
          {
            v131 = 2081i64;
            v112 = v176;
            v111 = (void *)(v175 + 1);
            if ( __OFADD__(1i64, v175) )
              goto LABEL_211;
            v113 = v111;
            v55 = v112;
            v56 = (char *)v111;
            add__presenterZutilities_u27278(&v121, &v55);
            v131 = 2083i64;
            if ( v175 < 0
              || v175 >= v77
              || (qmemcpy(v71, (const void *)(560 * v175 + v78 + 8), sizeof(v71)),
                  v131 = 34i64,
                  v132 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim",
                  v175 >= v77) )
            {
              raiseIndexError2(v175, v77 - 1);
              goto LABEL_224;
            }
            eqwasMoved___modelZsave95mongerZversionsZv0_u142(v78 + 560 * v175 + 8, v78);
            v131 = 2084i64;
            v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
            if ( LOBYTE(v71[0]) == 78 )
            {
              v131 = 2085i64;
              v109 = v71[49];
              v110 = 0i64;
              v55 = v71[49];
              v56 = 0i64;
              add__presenterZutilities_u27278(&v121, &v55);
              goto LABEL_224;
            }
            v131 = 2086i64;
            v172 = 0;
            v30 = *((_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788 + 1);
            v50 = *(_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788;
            v51 = (void *)v30;
            v52 = *((_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788 + 2);
            v172 = contains__modelZboardZmemory95manager_u414(&v50, LOBYTE(v71[0]));
            if ( *v227 || v172 != 1 )
              goto LABEL_224;
            v131 = 2087i64;
            v108 = v71[46] + v235;
            if ( __OFADD__(v71[46], v235) )
            {
LABEL_211:
              raiseOverflow();
            }
            else
            {
              v235 = v108;
              v131 = 2088i64;
              if ( v108 > 524288000 )
              {
                *(_BYTE *)(a2 + 4400) = 1;
                v131 = 34i64;
                v132 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                eqdestroy___modelZsave95mongerZversionsZv0_u145(v71);
                v131 = 170i64;
                v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                eqdestroy___modelZboardZprototype95list_u3239(v73);
                v131 = 441i64;
                v132 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
                eqdestroy___modelZboardZboard_u15245(v120);
                v131 = 13i64;
                v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\setimpl.nim";
                v55 = v121;
                v56 = v122;
                eqdestroy___modelZboardZboard_u11470(&v55);
                v131 = 2090i64;
                v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
                goto LABEL_311;
              }
            }
LABEL_224:
            v131 = 34i64;
            v132 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
            eqdestroy___modelZsave95mongerZversionsZv0_u145(v71);
            v131 = 170i64;
            v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            eqdestroy___modelZboardZprototype95list_u3239(v73);
            if ( *v227 )
              goto LABEL_307;
          }
          else
          {
            nimZeroMem_132(v70, 72i64);
            v72[0] = v176;
            v131 = 173i64;
            v132 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
            eqdup___modelZsave95mongerZsave95monger_u2643(&v77, v70);
            v72[1] = v70[0];
            v72[2] = v70[1];
            v72[3] = v70[2];
            v72[4] = v70[3];
            v72[5] = v70[4];
            v72[6] = v70[5];
            v72[7] = v70[6];
            v72[8] = v70[7];
            v72[9] = v70[8];
            nimCopyMem_94(&v72[10], &v79, 1024i64);
            v131 = 2077i64;
            v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
            add__modelZnetworkingZnetworking_u974(&v59, v72);
            v131 = 2078i64;
            incl__modelZboardZboard_u11061(v120, v176);
            if ( *v227 )
              goto LABEL_224;
            v131 = 34i64;
            v132 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
            eqdestroy___modelZsave95mongerZversionsZv0_u145(v71);
            v131 = 170i64;
            v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            eqdestroy___modelZboardZprototype95list_u3239(v73);
            v131 = 2079i64;
            v132 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
          }
        }
      }
    }
  }
  v131 = 635i64;
  v132 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
  v55 = v136;
  v56 = v137;
  eqdestroy___modelZmodel95types_u2594(&v55);
  v131 = 770i64;
  v132 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
  eqdestroy___modelZboardZschematics_u4043(v138);
  return popFrame_162();
}
