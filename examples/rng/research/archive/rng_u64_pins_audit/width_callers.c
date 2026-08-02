/* XREFS TO get_output_word_size @ 0x00000001402367c6 */

/* call 0x0000000140436efd, caller store_output_early_return__modelZsimulationZcode95gen_u222 @ 0x0000000140436d0b */

__int64 __fastcall store_output_early_return__modelZsimulationZcode95gen_u222(_QWORD *a1, __int64 a2)
{
  _QWORD *v2; // rax
  __int64 v3; // rbx
  __int64 v4; // rbx
  __int64 v5; // rbx
  __int64 v6; // rbx
  __int64 v7; // rdx
  __int64 v8; // rdx
  _QWORD *v9; // rcx
  __int64 v10; // rdx
  __int64 v11; // rdx
  __int64 v13; // [rsp+0h] [rbp-80h] BYREF
  __int64 v14; // [rsp+20h] [rbp-60h] BYREF
  __int64 v15; // [rsp+28h] [rbp-58h]
  __int64 v16; // [rsp+30h] [rbp-50h]
  __int64 v17; // [rsp+40h] [rbp-40h] BYREF
  __int64 v18; // [rsp+48h] [rbp-38h]
  __int64 v19; // [rsp+50h] [rbp-30h]
  const char *v20; // [rsp+68h] [rbp-18h]
  __int64 v21; // [rsp+70h] [rbp-10h]
  const char *v22; // [rsp+78h] [rbp-8h]
  __int16 v23; // [rsp+80h] [rbp+0h]
  __int64 v24; // [rsp+90h] [rbp+10h]
  __int64 v25; // [rsp+98h] [rbp+18h]
  __int64 v26; // [rsp+A0h] [rbp+20h]
  __int64 output_word_size__modelZboardZprototype95list_u4333; // [rsp+A8h] [rbp+28h]
  __int64 v28; // [rsp+B0h] [rbp+30h] BYREF
  __int64 v29; // [rsp+B8h] [rbp+38h]
  __int64 v30; // [rsp+C0h] [rbp+40h]
  __int64 v31; // [rsp+C8h] [rbp+48h]
  __int64 v32; // [rsp+D0h] [rbp+50h]
  __int64 v33; // [rsp+D8h] [rbp+58h]
  __int64 v34; // [rsp+E0h] [rbp+60h]
  __int64 v35; // [rsp+E8h] [rbp+68h]
  __int64 v36; // [rsp+F0h] [rbp+70h]
  __int64 v37; // [rsp+F8h] [rbp+78h]
  char v38; // [rsp+10Eh] [rbp+8Eh]
  char v39; // [rsp+10Fh] [rbp+8Fh]
  _BYTE *v40; // [rsp+110h] [rbp+90h]
  unsigned __int8 v41; // [rsp+11Fh] [rbp+9Fh]

  v20 = "store_output_early_return";
  v22 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v21 = 0i64;
  v23 = 0;
  nimFrame_88(&v13 + 12);
  v40 = (_BYTE *)nimErrorFlag_86();
  v41 = 0;
  nimZeroMem_66(&v28, 80i64);
  v21 = 156i64;
  v22 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  if ( a2 < 0 || a2 >= a1[8] )
    goto LABEL_3;
  v2 = (_QWORD *)(a1[9] + 80 * a2);
  v3 = v2[2];
  v28 = v2[1];
  v29 = v3;
  v4 = v2[4];
  v30 = v2[3];
  v31 = v4;
  v5 = v2[6];
  v32 = v2[5];
  v33 = v5;
  v6 = v2[8];
  v34 = v2[7];
  v35 = v6;
  v7 = v2[10];
  v36 = v2[9];
  v37 = v7;
  v21 = 157i64;
  v39 = 0;
  v17 = v29;
  v18 = v30;
  v19 = v31;
  v8 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 1);
  v14 = *(_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435;
  v15 = v8;
  v16 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 2);
  v39 = eqeq___modelZsimulationZcontroller_u106(&v17, &v14);
  if ( v39 == 1 )
  {
    v21 = 157i64;
    v41 = 1;
    goto LABEL_14;
  }
  v21 = 158i64;
  output_word_size__modelZboardZprototype95list_u4333 = get_output_word_size__modelZboardZprototype95list_u4333(
                                                          *(unsigned __int8 *)a1,
                                                          (unsigned __int16)a2,
                                                          a1[28]);
  if ( *v40 )
    goto LABEL_14;
  v21 = 160i64;
  if ( output_word_size__modelZboardZprototype95list_u4333 <= 0 )
  {
    v21 = 161i64;
    v41 = 1;
    goto LABEL_14;
  }
  v21 = 163i64;
  if ( a2 >= 0 && a2 < a1[8] )
  {
    v9 = (_QWORD *)(80 * a2 + a1[9]);
    v10 = v9[3];
    v24 = v9[2];
    v25 = v10;
    v26 = v9[4];
    v21 = 165i64;
    v38 = 0;
    v14 = v24;
    v15 = v10;
    v16 = v26;
    v11 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 1);
    v17 = *(_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435;
    v18 = v11;
    v19 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 2);
    v38 = eqeq___modelZsimulationZcontroller_u106(&v14, &v17);
    if ( v38 == 1 )
    {
      v21 = 166i64;
      v41 = 1;
    }
  }
  else
  {
LABEL_3:
    raiseIndexError2(a2, a1[8] - 1i64);
  }
LABEL_14:
  popFrame_88();
  return v41;
}


/* call 0x0000000140437481, caller store_output__modelZsimulationZcode95gen_u2221 @ 0x0000000140437079 */

__int64 __fastcall store_output__modelZsimulationZcode95gen_u2221(
        _QWORD *a1,
        __int64 a2,
        __int64 a3,
        __int64 *a4,
        __int64 *a5,
        __int64 a6)
{
  __int64 v6; // rdx
  _QWORD *v7; // rdx
  _QWORD *v8; // rax
  __int64 v9; // rbx
  __int64 v10; // rbx
  __int64 v11; // rbx
  __int64 v12; // rbx
  __int64 v13; // rdx
  _QWORD *v14; // rcx
  __int64 v15; // rdx
  __int64 v16; // rdx
  __int64 v18; // [rsp+20h] [rbp-60h] BYREF
  __int64 v19; // [rsp+28h] [rbp-58h]
  __int64 v20; // [rsp+30h] [rbp-50h]
  __int64 v21; // [rsp+40h] [rbp-40h] BYREF
  __int64 v22; // [rsp+48h] [rbp-38h]
  __int64 v23; // [rsp+50h] [rbp-30h]
  __int64 v24; // [rsp+60h] [rbp-20h] BYREF
  _QWORD *v25; // [rsp+68h] [rbp-18h]
  __int64 v26; // [rsp+70h] [rbp-10h]
  _QWORD *v27; // [rsp+78h] [rbp-8h]
  __int64 v28; // [rsp+80h] [rbp+0h]
  _QWORD *v29; // [rsp+88h] [rbp+8h]
  __int64 v30; // [rsp+90h] [rbp+10h] BYREF
  _QWORD *v31; // [rsp+98h] [rbp+18h]
  __int64 (__fastcall *v32)(); // [rsp+A0h] [rbp+20h] BYREF
  __int64 v33; // [rsp+A8h] [rbp+28h]
  __int64 v34; // [rsp+B0h] [rbp+30h]
  _QWORD *v35; // [rsp+B8h] [rbp+38h]
  __int64 v36; // [rsp+C0h] [rbp+40h] BYREF
  _QWORD *v37; // [rsp+C8h] [rbp+48h]
  __int64 v38; // [rsp+D0h] [rbp+50h] BYREF
  _QWORD *v39; // [rsp+D8h] [rbp+58h]
  __int64 (__fastcall *v40)(); // [rsp+E0h] [rbp+60h] BYREF
  __int64 v41; // [rsp+E8h] [rbp+68h]
  __int64 v42; // [rsp+F0h] [rbp+70h] BYREF
  _QWORD *v43; // [rsp+F8h] [rbp+78h]
  __int64 (__fastcall *v44)(); // [rsp+100h] [rbp+80h] BYREF
  __int64 v45; // [rsp+108h] [rbp+88h]
  __int64 v46; // [rsp+110h] [rbp+90h] BYREF
  _QWORD *v47; // [rsp+118h] [rbp+98h]
  __int64 v48; // [rsp+120h] [rbp+A0h]
  _QWORD *v49; // [rsp+128h] [rbp+A8h]
  __int64 v50; // [rsp+130h] [rbp+B0h] BYREF
  _QWORD *v51; // [rsp+138h] [rbp+B8h]
  __int64 v52; // [rsp+140h] [rbp+C0h]
  _QWORD *v53; // [rsp+148h] [rbp+C8h]
  __int64 v54; // [rsp+150h] [rbp+D0h]
  _QWORD *v55; // [rsp+158h] [rbp+D8h]
  __int64 v56; // [rsp+160h] [rbp+E0h] BYREF
  _QWORD *v57; // [rsp+168h] [rbp+E8h]
  __int64 (__fastcall *v58)(); // [rsp+170h] [rbp+F0h] BYREF
  __int64 v59; // [rsp+178h] [rbp+F8h]
  __int64 v60; // [rsp+180h] [rbp+100h]
  _QWORD *v61; // [rsp+188h] [rbp+108h]
  __int64 v62; // [rsp+190h] [rbp+110h] BYREF
  _QWORD *v63; // [rsp+198h] [rbp+118h]
  __int64 (__fastcall *v64)(); // [rsp+1A0h] [rbp+120h] BYREF
  __int64 v65; // [rsp+1A8h] [rbp+128h]
  __int64 v66; // [rsp+1B0h] [rbp+130h] BYREF
  _QWORD *v67; // [rsp+1B8h] [rbp+138h]
  __int64 (__fastcall *v68)(); // [rsp+1C0h] [rbp+140h] BYREF
  __int64 v69; // [rsp+1C8h] [rbp+148h]
  __int64 v70; // [rsp+1D0h] [rbp+150h] BYREF
  _QWORD *v71; // [rsp+1D8h] [rbp+158h]
  __int64 (__fastcall *v72)(); // [rsp+1E0h] [rbp+160h] BYREF
  __int64 v73; // [rsp+1E8h] [rbp+168h]
  __int64 v74; // [rsp+1F0h] [rbp+170h] BYREF
  _QWORD *v75; // [rsp+1F8h] [rbp+178h]
  __int64 (__fastcall *v76)(); // [rsp+200h] [rbp+180h] BYREF
  __int64 v77; // [rsp+208h] [rbp+188h]
  __int64 v78; // [rsp+210h] [rbp+190h] BYREF
  _QWORD *v79; // [rsp+218h] [rbp+198h]
  __int64 (__fastcall *v80)(); // [rsp+220h] [rbp+1A0h] BYREF
  __int64 v81; // [rsp+228h] [rbp+1A8h]
  __int64 v82; // [rsp+230h] [rbp+1B0h] BYREF
  _QWORD *v83; // [rsp+238h] [rbp+1B8h]
  __int64 (__fastcall *v84)(); // [rsp+240h] [rbp+1C0h] BYREF
  __int64 v85; // [rsp+248h] [rbp+1C8h]
  __int64 v86; // [rsp+250h] [rbp+1D0h] BYREF
  _QWORD *v87; // [rsp+258h] [rbp+1D8h]
  __int64 (__fastcall *v88)(); // [rsp+260h] [rbp+1E0h] BYREF
  __int64 v89; // [rsp+268h] [rbp+1E8h]
  __int64 v90; // [rsp+270h] [rbp+1F0h] BYREF
  _QWORD *v91; // [rsp+278h] [rbp+1F8h]
  __int64 (__fastcall *v92)(); // [rsp+280h] [rbp+200h] BYREF
  __int64 v93; // [rsp+288h] [rbp+208h]
  __int64 v94; // [rsp+290h] [rbp+210h] BYREF
  _QWORD *v95; // [rsp+298h] [rbp+218h]
  __int64 (__fastcall *v96)(); // [rsp+2A0h] [rbp+220h] BYREF
  __int64 v97; // [rsp+2A8h] [rbp+228h]
  __int64 (__fastcall *v98)(); // [rsp+2B0h] [rbp+230h] BYREF
  __int64 v99; // [rsp+2B8h] [rbp+238h]
  __int64 (__fastcall *v100)(); // [rsp+2C0h] [rbp+240h] BYREF
  __int64 v101; // [rsp+2C8h] [rbp+248h]
  __int64 v102; // [rsp+2D0h] [rbp+250h] BYREF
  _QWORD *v103; // [rsp+2D8h] [rbp+258h]
  __int64 (__fastcall *v104)(); // [rsp+2E0h] [rbp+260h] BYREF
  __int64 v105; // [rsp+2E8h] [rbp+268h]
  __int64 v106; // [rsp+2F0h] [rbp+270h] BYREF
  _QWORD *v107; // [rsp+2F8h] [rbp+278h]
  __int64 (__fastcall *v108)(); // [rsp+300h] [rbp+280h] BYREF
  __int64 v109; // [rsp+308h] [rbp+288h]
  __int64 v110; // [rsp+310h] [rbp+290h] BYREF
  _QWORD *v111; // [rsp+318h] [rbp+298h]
  __int64 (__fastcall *v112)(); // [rsp+320h] [rbp+2A0h] BYREF
  __int64 v113; // [rsp+328h] [rbp+2A8h]
  __int64 v114; // [rsp+330h] [rbp+2B0h] BYREF
  _QWORD *v115; // [rsp+338h] [rbp+2B8h]
  __int64 (__fastcall *v116)(); // [rsp+340h] [rbp+2C0h] BYREF
  __int64 v117; // [rsp+348h] [rbp+2C8h]
  __int64 v118; // [rsp+350h] [rbp+2D0h] BYREF
  _QWORD *v119; // [rsp+358h] [rbp+2D8h]
  __int64 (__fastcall *v120)(); // [rsp+360h] [rbp+2E0h] BYREF
  __int64 v121; // [rsp+368h] [rbp+2E8h]
  __int64 v122; // [rsp+370h] [rbp+2F0h] BYREF
  _QWORD *v123; // [rsp+378h] [rbp+2F8h]
  __int64 (__fastcall *v124)(); // [rsp+380h] [rbp+300h] BYREF
  __int64 v125; // [rsp+388h] [rbp+308h]
  __int64 v126; // [rsp+390h] [rbp+310h] BYREF
  _QWORD *v127; // [rsp+398h] [rbp+318h]
  __int64 (__fastcall *v128)(); // [rsp+3A0h] [rbp+320h] BYREF
  __int64 v129; // [rsp+3A8h] [rbp+328h]
  __int64 v130; // [rsp+3B0h] [rbp+330h] BYREF
  _QWORD *v131; // [rsp+3B8h] [rbp+338h]
  __int64 (__fastcall *v132)(); // [rsp+3C0h] [rbp+340h] BYREF
  __int64 v133; // [rsp+3C8h] [rbp+348h]
  __int64 v134; // [rsp+3D0h] [rbp+350h] BYREF
  _QWORD *v135; // [rsp+3D8h] [rbp+358h]
  __int64 (__fastcall *v136)(); // [rsp+3E0h] [rbp+360h] BYREF
  __int64 v137; // [rsp+3E8h] [rbp+368h]
  __int64 v138; // [rsp+3F0h] [rbp+370h] BYREF
  _QWORD *v139; // [rsp+3F8h] [rbp+378h]
  __int64 (__fastcall *v140)(); // [rsp+400h] [rbp+380h] BYREF
  __int64 v141; // [rsp+408h] [rbp+388h]
  __int64 v142; // [rsp+410h] [rbp+390h] BYREF
  _QWORD *v143; // [rsp+418h] [rbp+398h]
  __int64 (__fastcall *v144)(); // [rsp+420h] [rbp+3A0h] BYREF
  __int64 v145; // [rsp+428h] [rbp+3A8h]
  __int64 v146; // [rsp+430h] [rbp+3B0h]
  _QWORD *v147; // [rsp+438h] [rbp+3B8h]
  __int64 v148; // [rsp+440h] [rbp+3C0h] BYREF
  _QWORD *v149; // [rsp+448h] [rbp+3C8h]
  __int64 v150; // [rsp+450h] [rbp+3D0h]
  _QWORD *v151; // [rsp+458h] [rbp+3D8h]
  __int64 v152; // [rsp+460h] [rbp+3E0h] BYREF
  _QWORD *v153; // [rsp+468h] [rbp+3E8h]
  __int64 v154; // [rsp+470h] [rbp+3F0h]
  _QWORD *v155; // [rsp+478h] [rbp+3F8h]
  __int64 v156; // [rsp+480h] [rbp+400h] BYREF
  _QWORD *v157; // [rsp+488h] [rbp+408h]
  __int64 v158; // [rsp+490h] [rbp+410h]
  _QWORD *v159; // [rsp+498h] [rbp+418h]
  __int64 v160; // [rsp+4A0h] [rbp+420h] BYREF
  _QWORD *v161; // [rsp+4A8h] [rbp+428h]
  __int64 v162; // [rsp+4B0h] [rbp+430h]
  _QWORD *v163; // [rsp+4B8h] [rbp+438h]
  __int64 v164; // [rsp+4C0h] [rbp+440h] BYREF
  _QWORD *v165; // [rsp+4C8h] [rbp+448h]
  __int64 v166; // [rsp+4D0h] [rbp+450h]
  _QWORD *v167; // [rsp+4D8h] [rbp+458h]
  __int64 v168; // [rsp+4E0h] [rbp+460h] BYREF
  _QWORD *v169; // [rsp+4E8h] [rbp+468h]
  __int64 v170; // [rsp+4F0h] [rbp+470h]
  _QWORD *v171; // [rsp+4F8h] [rbp+478h]
  __int64 v172; // [rsp+500h] [rbp+480h]
  _QWORD *v173; // [rsp+508h] [rbp+488h]
  __int64 v174; // [rsp+510h] [rbp+490h]
  _QWORD *v175; // [rsp+518h] [rbp+498h]
  __int64 v176; // [rsp+520h] [rbp+4A0h]
  _QWORD *v177; // [rsp+528h] [rbp+4A8h]
  __int64 v178; // [rsp+530h] [rbp+4B0h] BYREF
  _QWORD *v179; // [rsp+538h] [rbp+4B8h]
  __int64 v180; // [rsp+540h] [rbp+4C0h]
  _QWORD *v181; // [rsp+548h] [rbp+4C8h]
  __int64 v182; // [rsp+550h] [rbp+4D0h] BYREF
  _QWORD *v183; // [rsp+558h] [rbp+4D8h]
  __int64 v184; // [rsp+560h] [rbp+4E0h]
  _QWORD *v185; // [rsp+568h] [rbp+4E8h]
  __int64 v186; // [rsp+570h] [rbp+4F0h]
  _QWORD *v187; // [rsp+578h] [rbp+4F8h]
  __int64 v188; // [rsp+580h] [rbp+500h] BYREF
  _QWORD *v189; // [rsp+588h] [rbp+508h]
  __int64 v190; // [rsp+590h] [rbp+510h]
  _QWORD *v191; // [rsp+598h] [rbp+518h]
  __int64 v192; // [rsp+5A0h] [rbp+520h]
  _QWORD *v193; // [rsp+5A8h] [rbp+528h]
  __int64 v194; // [rsp+5B0h] [rbp+530h] BYREF
  _QWORD *v195; // [rsp+5B8h] [rbp+538h]
  __int64 v196; // [rsp+5C0h] [rbp+540h]
  _QWORD *v197; // [rsp+5C8h] [rbp+548h]
  __int64 v198; // [rsp+5D0h] [rbp+550h]
  _QWORD *v199; // [rsp+5D8h] [rbp+558h]
  __int64 v200; // [rsp+5E0h] [rbp+560h]
  _QWORD *v201; // [rsp+5E8h] [rbp+568h]
  __int64 v202; // [rsp+5F0h] [rbp+570h]
  _QWORD *v203; // [rsp+5F8h] [rbp+578h]
  __int64 v204; // [rsp+600h] [rbp+580h] BYREF
  _QWORD *v205; // [rsp+608h] [rbp+588h]
  __int64 (__fastcall *v206)(); // [rsp+610h] [rbp+590h] BYREF
  __int64 v207; // [rsp+618h] [rbp+598h]
  __int64 v208; // [rsp+620h] [rbp+5A0h]
  _QWORD *v209; // [rsp+628h] [rbp+5A8h]
  __int64 (__fastcall *v210)(); // [rsp+630h] [rbp+5B0h] BYREF
  __int64 v211; // [rsp+638h] [rbp+5B8h]
  __int64 v212; // [rsp+640h] [rbp+5C0h] BYREF
  _QWORD *v213; // [rsp+648h] [rbp+5C8h]
  __int64 (__fastcall *v214)(); // [rsp+650h] [rbp+5D0h] BYREF
  __int64 v215; // [rsp+658h] [rbp+5D8h]
  __int64 v216; // [rsp+660h] [rbp+5E0h] BYREF
  _QWORD *v217; // [rsp+668h] [rbp+5E8h]
  __int64 (__fastcall *v218)(); // [rsp+670h] [rbp+5F0h] BYREF
  __int64 v219; // [rsp+678h] [rbp+5F8h]
  __int64 v220; // [rsp+680h] [rbp+600h] BYREF
  _QWORD *v221; // [rsp+688h] [rbp+608h]
  __int64 (__fastcall *v222)(); // [rsp+690h] [rbp+610h] BYREF
  __int64 v223; // [rsp+698h] [rbp+618h]
  __int64 v224; // [rsp+6A0h] [rbp+620h]
  _QWORD *v225; // [rsp+6A8h] [rbp+628h]
  __int64 v226; // [rsp+6B0h] [rbp+630h]
  _QWORD *v227; // [rsp+6B8h] [rbp+638h]
  __int64 v228; // [rsp+6C0h] [rbp+640h]
  _QWORD *v229; // [rsp+6C8h] [rbp+648h]
  __int64 v230; // [rsp+6D0h] [rbp+650h] BYREF
  _QWORD *v231; // [rsp+6D8h] [rbp+658h]
  __int64 (__fastcall *v232)(); // [rsp+6E0h] [rbp+660h] BYREF
  __int64 v233; // [rsp+6E8h] [rbp+668h]
  __int64 v234; // [rsp+6F0h] [rbp+670h]
  _QWORD *v235; // [rsp+6F8h] [rbp+678h]
  __int64 v236; // [rsp+700h] [rbp+680h] BYREF
  _QWORD *v237; // [rsp+708h] [rbp+688h]
  __int64 (__fastcall *v238)(); // [rsp+710h] [rbp+690h] BYREF
  __int64 v239; // [rsp+718h] [rbp+698h]
  __int64 v240; // [rsp+720h] [rbp+6A0h] BYREF
  _QWORD *v241; // [rsp+728h] [rbp+6A8h]
  __int64 (__fastcall *v242)(); // [rsp+730h] [rbp+6B0h] BYREF
  __int64 v243; // [rsp+738h] [rbp+6B8h]
  __int64 v244; // [rsp+740h] [rbp+6C0h]
  _QWORD *v245; // [rsp+748h] [rbp+6C8h]
  __int64 v246; // [rsp+750h] [rbp+6D0h]
  _QWORD *v247; // [rsp+758h] [rbp+6D8h]
  __int64 v248; // [rsp+760h] [rbp+6E0h] BYREF
  _QWORD *v249; // [rsp+768h] [rbp+6E8h]
  __int64 (__fastcall *v250)(); // [rsp+770h] [rbp+6F0h] BYREF
  __int64 v251; // [rsp+778h] [rbp+6F8h]
  __int64 v252; // [rsp+780h] [rbp+700h] BYREF
  _QWORD *v253; // [rsp+788h] [rbp+708h]
  __int64 (__fastcall *v254)(); // [rsp+790h] [rbp+710h] BYREF
  __int64 v255; // [rsp+798h] [rbp+718h]
  __int64 v256; // [rsp+7A0h] [rbp+720h] BYREF
  _QWORD *v257; // [rsp+7A8h] [rbp+728h]
  __int64 (__fastcall *v258)(); // [rsp+7B0h] [rbp+730h] BYREF
  __int64 v259; // [rsp+7B8h] [rbp+738h]
  __int64 v260; // [rsp+7C0h] [rbp+740h]
  _QWORD *v261; // [rsp+7C8h] [rbp+748h]
  __int64 v262; // [rsp+7D0h] [rbp+750h]
  _QWORD *v263; // [rsp+7D8h] [rbp+758h]
  __int64 v264; // [rsp+7E0h] [rbp+760h]
  _QWORD *v265; // [rsp+7E8h] [rbp+768h]
  __int64 v266; // [rsp+7F0h] [rbp+770h] BYREF
  _QWORD *v267; // [rsp+7F8h] [rbp+778h]
  __int64 (__fastcall *v268)(); // [rsp+800h] [rbp+780h] BYREF
  __int64 v269; // [rsp+808h] [rbp+788h]
  __int64 v270; // [rsp+810h] [rbp+790h] BYREF
  _QWORD *v271; // [rsp+818h] [rbp+798h]
  __int64 (__fastcall *v272)(); // [rsp+820h] [rbp+7A0h] BYREF
  __int64 v273; // [rsp+828h] [rbp+7A8h]
  __int64 v274; // [rsp+830h] [rbp+7B0h] BYREF
  _QWORD *v275; // [rsp+838h] [rbp+7B8h]
  __int64 (__fastcall *v276)(); // [rsp+840h] [rbp+7C0h] BYREF
  __int64 v277; // [rsp+848h] [rbp+7C8h]
  __int64 v278; // [rsp+850h] [rbp+7D0h]
  _QWORD *v279; // [rsp+858h] [rbp+7D8h]
  __int64 v280; // [rsp+860h] [rbp+7E0h] BYREF
  _QWORD *v281; // [rsp+868h] [rbp+7E8h]
  __int64 v282; // [rsp+870h] [rbp+7F0h]
  _QWORD *v283; // [rsp+878h] [rbp+7F8h]
  __int64 v284; // [rsp+880h] [rbp+800h] BYREF
  _QWORD *v285; // [rsp+888h] [rbp+808h]
  __int64 v286; // [rsp+890h] [rbp+810h]
  _QWORD *v287; // [rsp+898h] [rbp+818h]
  __int64 v288; // [rsp+8A0h] [rbp+820h] BYREF
  _QWORD *v289; // [rsp+8A8h] [rbp+828h]
  __int64 v290; // [rsp+8B0h] [rbp+830h] BYREF
  _QWORD *v291; // [rsp+8B8h] [rbp+838h]
  __int64 (__fastcall *v292)(); // [rsp+8C0h] [rbp+840h] BYREF
  __int64 v293; // [rsp+8C8h] [rbp+848h]
  __int64 v294; // [rsp+8D0h] [rbp+850h] BYREF
  _QWORD *v295; // [rsp+8D8h] [rbp+858h]
  __int64 (__fastcall *v296)(); // [rsp+8E0h] [rbp+860h] BYREF
  __int64 v297; // [rsp+8E8h] [rbp+868h]
  __int64 v298; // [rsp+8F0h] [rbp+870h]
  _QWORD *v299; // [rsp+8F8h] [rbp+878h]
  __int64 v300; // [rsp+900h] [rbp+880h]
  _QWORD *v301; // [rsp+908h] [rbp+888h]
  char v302[8]; // [rsp+910h] [rbp+890h] BYREF
  const char *v303; // [rsp+918h] [rbp+898h]
  __int64 v304; // [rsp+920h] [rbp+8A0h]
  const char *v305; // [rsp+928h] [rbp+8A8h]
  __int16 v306; // [rsp+930h] [rbp+8B0h]
  __int64 v307; // [rsp+940h] [rbp+8C0h]
  __int64 v308; // [rsp+948h] [rbp+8C8h]
  __int64 v309; // [rsp+950h] [rbp+8D0h]
  __int64 v310; // [rsp+960h] [rbp+8E0h] BYREF
  _QWORD *v311; // [rsp+968h] [rbp+8E8h]
  __int64 v312; // [rsp+970h] [rbp+8F0h] BYREF
  _QWORD *v313; // [rsp+978h] [rbp+8F8h]
  __int64 output_word_size__modelZboardZprototype95list_u4333; // [rsp+988h] [rbp+908h]
  __int64 v315; // [rsp+990h] [rbp+910h] BYREF
  __int64 v316; // [rsp+998h] [rbp+918h]
  __int64 v317; // [rsp+9A0h] [rbp+920h]
  __int64 v318; // [rsp+9A8h] [rbp+928h]
  __int64 v319; // [rsp+9B0h] [rbp+930h]
  __int64 v320; // [rsp+9B8h] [rbp+938h]
  __int64 v321; // [rsp+9C0h] [rbp+940h]
  __int64 v322; // [rsp+9C8h] [rbp+948h]
  __int64 v323; // [rsp+9D0h] [rbp+950h]
  __int64 v324; // [rsp+9D8h] [rbp+958h]
  __int64 v325; // [rsp+9E0h] [rbp+960h]
  _QWORD *v326; // [rsp+9E8h] [rbp+968h]
  __int64 v327; // [rsp+9F0h] [rbp+970h] BYREF
  _QWORD *v328; // [rsp+9F8h] [rbp+978h]
  __int64 v329; // [rsp+A00h] [rbp+980h] BYREF
  _QWORD *v330; // [rsp+A08h] [rbp+988h]
  __int64 v331; // [rsp+A10h] [rbp+990h]
  _QWORD *v332; // [rsp+A18h] [rbp+998h]
  __int64 v333; // [rsp+A20h] [rbp+9A0h] BYREF
  _QWORD *v334; // [rsp+A28h] [rbp+9A8h]
  __int64 v335; // [rsp+A30h] [rbp+9B0h]
  _QWORD *v336; // [rsp+A38h] [rbp+9B8h]
  __int64 v337; // [rsp+A48h] [rbp+9C8h]
  char v338; // [rsp+A57h] [rbp+9D7h]
  __int64 v339; // [rsp+A58h] [rbp+9D8h]
  __int64 v340; // [rsp+A60h] [rbp+9E0h]
  __int64 v341; // [rsp+A68h] [rbp+9E8h]
  __int64 v342; // [rsp+A70h] [rbp+9F0h]
  char v343; // [rsp+A7Fh] [rbp+9FFh]
  __int64 v344; // [rsp+A80h] [rbp+A00h]
  bool v345; // [rsp+A8Eh] [rbp+A0Eh]
  char v346; // [rsp+A8Fh] [rbp+A0Fh]
  __int64 v347; // [rsp+A90h] [rbp+A10h]
  __int64 z_state_index__modelZsave95mongerZcommon_u5499; // [rsp+A98h] [rbp+A18h]
  __int64 state_index__modelZsave95mongerZcommon_u5502; // [rsp+AA0h] [rbp+A20h]
  _BYTE *v350; // [rsp+AA8h] [rbp+A28h]
  _BYTE *v351; // [rsp+AB0h] [rbp+A30h]
  char v352; // [rsp+ABFh] [rbp+A3Fh]
  __int64 v353; // [rsp+AC0h] [rbp+A40h]
  _BYTE *v354; // [rsp+AC8h] [rbp+A48h]

  v6 = a4[1];
  v28 = *a4;
  v29 = (_QWORD *)v6;
  v7 = (_QWORD *)a5[1];
  v26 = *a5;
  v27 = v7;
  v303 = "store_output";
  v305 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v304 = 0i64;
  v306 = 0;
  nimFrame_88(v302);
  v354 = (_BYTE *)nimErrorFlag_86();
  v353 = a6;
  v335 = 0i64;
  v336 = 0i64;
  v333 = 0i64;
  v334 = 0i64;
  v331 = 0i64;
  v332 = 0i64;
  v329 = 0i64;
  v330 = 0i64;
  v327 = 0i64;
  v328 = 0i64;
  v325 = 0i64;
  v326 = 0i64;
  v304 = 257i64;
  v352 = 0;
  v352 = store_output_early_return__modelZsimulationZcode95gen_u222(a1, a3);
  if ( *v354 )
    goto LABEL_416;
  if ( v352 == 1 )
  {
    v304 = 394i64;
    v305 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v328 && (*v328 & 0x4000000000000000i64) == 0 )
      deallocShared(v328);
    if ( v330 && (*v330 & 0x4000000000000000i64) == 0 )
      deallocShared(v330);
    if ( v332 && (*v332 & 0x4000000000000000i64) == 0 )
      deallocShared(v332);
    if ( v334 && (*v334 & 0x4000000000000000i64) == 0 )
      deallocShared(v334);
    if ( v336 && (*v336 & 0x4000000000000000i64) == 0 )
      deallocShared(v336);
    return popFrame_88();
  }
  nimZeroMem_66(&v315, 80i64);
  v304 = 260i64;
  v305 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  if ( a3 < 0 || a3 >= a1[8] )
  {
    raiseIndexError2(a3, a1[8] - 1i64);
    goto LABEL_416;
  }
  v8 = (_QWORD *)(a1[9] + 80 * a3);
  v9 = v8[2];
  v315 = v8[1];
  v316 = v9;
  v10 = v8[4];
  v317 = v8[3];
  v318 = v10;
  v11 = v8[6];
  v319 = v8[5];
  v320 = v11;
  v12 = v8[8];
  v321 = v8[7];
  v322 = v12;
  v13 = v8[10];
  v323 = v8[9];
  v324 = v13;
  v304 = 262i64;
  output_word_size__modelZboardZprototype95list_u4333 = get_output_word_size__modelZboardZprototype95list_u4333(
                                                          *(unsigned __int8 *)a1,
                                                          (unsigned __int16)a3,
                                                          a1[28]);
  if ( *v354 )
    goto LABEL_416;
  v304 = 264i64;
  v312 = 0i64;
  v313 = 0i64;
  dollar___modelZsave95mongerZcommon_u260(&v333, output_word_size__modelZboardZprototype95list_u4333);
  if ( *v354 )
    goto LABEL_416;
  rawNewString(&v24, v333 + 2);
  v312 = v24;
  v313 = v25;
  v24 = TM__THWBxVSaWN2Zh7OMooFH0w_528;
  v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_331;
  appendString_29(&v312, &v24);
  v24 = v333;
  v25 = v334;
  appendString_29(&v312, &v24);
  v24 = TM__THWBxVSaWN2Zh7OMooFH0w_529;
  v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_58;
  appendString_29(&v312, &v24);
  v335 = v312;
  v336 = v313;
  v304 = 265i64;
  v310 = 0i64;
  v311 = 0i64;
  dollar___modelZsave95mongerZcommon_u260(&v329, v322);
  if ( *v354 )
    goto LABEL_416;
  rawNewString(&v24, v329 + 2);
  v310 = v24;
  v311 = v25;
  v24 = TM__THWBxVSaWN2Zh7OMooFH0w_530;
  v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_331;
  appendString_29(&v310, &v24);
  v24 = v329;
  v25 = v330;
  appendString_29(&v310, &v24);
  v24 = TM__THWBxVSaWN2Zh7OMooFH0w_531;
  v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_58;
  appendString_29(&v310, &v24);
  v331 = v310;
  v332 = v311;
  v304 = 267i64;
  if ( a3 < 0 || a3 >= a1[8] )
  {
    raiseIndexError2(a3, a1[8] - 1i64);
    goto LABEL_416;
  }
  v14 = (_QWORD *)(80 * a3 + a1[9]);
  v15 = v14[3];
  v307 = v14[2];
  v308 = v15;
  v309 = v14[4];
  v304 = 269i64;
  v21 = v307;
  v22 = v15;
  v23 = v309;
  get_id__modelZsave95mongerZcommon_u5569(&v327, &v21);
  if ( *v354 )
    goto LABEL_416;
  v325 = v26;
  v326 = v27;
  v304 = 272i64;
  if ( !v26 )
  {
    v304 = 273i64;
    v325 = 1i64;
    v326 = &TM__THWBxVSaWN2Zh7OMooFH0w_532;
  }
  v304 = 289i64;
  if ( (_BYTE)v315 == 1 )
  {
    v304 = 290i64;
    v351 = 0i64;
    v21 = v316;
    v22 = v317;
    v23 = v318;
    v351 = (_BYTE *)X5BX5D___modelZsimulationZcode95gen_u1925(v353 + 664, &v21);
    if ( *v354 )
      goto LABEL_416;
    if ( !*v351 )
    {
      v300 = 0i64;
      v301 = 0i64;
      v298 = 0i64;
      v299 = 0i64;
      v304 = 291i64;
      v350 = 0i64;
      v21 = v316;
      v22 = v317;
      v23 = v318;
      v350 = (_BYTE *)X5BX5D___modelZsimulationZcode95gen_u1925(v353 + 664, &v21);
      if ( *v354 )
        goto LABEL_104;
      *v350 = 1;
      v304 = 292i64;
      if ( (_BYTE)v315 != 1 )
      {
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_535;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_534;
        failedAssertImpl__stdZassertions_u234(&v24);
        if ( *v354 )
          goto LABEL_104;
      }
      v304 = 295i64;
      if ( *(_BYTE *)(v353 + 24) )
      {
        v288 = 0i64;
        v289 = 0i64;
        v286 = 0i64;
        v287 = 0i64;
        v284 = 0i64;
        v285 = 0i64;
        v282 = 0i64;
        v283 = 0i64;
        v280 = 0i64;
        v281 = 0i64;
        v278 = 0i64;
        v279 = 0i64;
        v304 = 297i64;
        nimZeroMem_66(&v276, 16i64);
        v276 = add_line__modelZsimulationZcode95gen_u2131;
        v277 = v353;
        v274 = 0i64;
        v275 = 0i64;
        state_index__modelZsave95mongerZcommon_u5502 = 0i64;
        v21 = v307;
        v22 = v308;
        v23 = v309;
        state_index__modelZsave95mongerZcommon_u5502 = get_state_index__modelZsave95mongerZcommon_u5502(&v21, 0i64);
        if ( *v354 )
          goto LABEL_104;
        dollar___systemZdollars_u14(&v288, state_index__modelZsave95mongerZcommon_u5502);
        if ( *v354 )
          goto LABEL_104;
        rawNewString(&v24, v288 + v335 + 31);
        v274 = v24;
        v275 = v25;
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_537;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_536;
        appendString_29(&v274, &v24);
        v24 = v288;
        v25 = v289;
        appendString_29(&v274, &v24);
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_538;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_41;
        appendString_29(&v274, &v24);
        v24 = v335;
        v25 = v336;
        appendString_29(&v274, &v24);
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_539;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_318;
        appendString_29(&v274, &v24);
        v286 = v274;
        v287 = v275;
        v24 = v274;
        v25 = v275;
        if ( v277 )
          ((void (__fastcall *)(__int64 *, __int64))v276)(&v24, v277);
        else
          ((void (__fastcall *)(__int64 *))v276)(&v24);
        if ( *v354 )
          goto LABEL_104;
        v304 = 298i64;
        nimZeroMem_66(&v272, 16i64);
        v272 = add_line__modelZsimulationZcode95gen_u2131;
        v273 = v353;
        v270 = 0i64;
        v271 = 0i64;
        z_state_index__modelZsave95mongerZcommon_u5499 = 0i64;
        v21 = v316;
        v22 = v317;
        v23 = v318;
        z_state_index__modelZsave95mongerZcommon_u5499 = get_z_state_index__modelZsave95mongerZcommon_u5499(&v21);
        if ( *v354 )
          goto LABEL_104;
        dollar___systemZdollars_u14(&v284, z_state_index__modelZsave95mongerZcommon_u5499);
        if ( *v354 )
          goto LABEL_104;
        rawNewString(&v24, v284 + 33);
        v270 = v24;
        v271 = v25;
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_541;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_536;
        appendString_29(&v270, &v24);
        v24 = v284;
        v25 = v285;
        appendString_29(&v270, &v24);
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_543;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_542;
        appendString_29(&v270, &v24);
        v282 = v270;
        v283 = v271;
        v24 = v270;
        v25 = v271;
        if ( v273 )
          ((void (__fastcall *)(__int64 *, __int64))v272)(&v24, v273);
        else
          ((void (__fastcall *)(__int64 *))v272)(&v24);
        if ( *v354 )
          goto LABEL_104;
        v304 = 299i64;
        nimZeroMem_66(&v268, 16i64);
        v268 = add_line__modelZsimulationZcode95gen_u2131;
        v269 = v353;
        v266 = 0i64;
        v267 = 0i64;
        v347 = 0i64;
        v21 = v319;
        v22 = v320;
        v23 = v321;
        v347 = get_z_state_index__modelZsave95mongerZcommon_u5499(&v21);
        if ( *v354 )
          goto LABEL_104;
        dollar___systemZdollars_u14(&v280, v347);
        if ( *v354 )
          goto LABEL_104;
        rawNewString(&v24, v280 + 33);
        v266 = v24;
        v267 = v25;
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_545;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_536;
        appendString_29(&v266, &v24);
        v24 = v280;
        v25 = v281;
        appendString_29(&v266, &v24);
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_546;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_542;
        appendString_29(&v266, &v24);
        v278 = v266;
        v279 = v267;
        v24 = v266;
        v25 = v267;
        if ( v269 )
          ((void (__fastcall *)(__int64 *, __int64))v268)(&v24, v269);
        else
          ((void (__fastcall *)(__int64 *))v268)(&v24);
        if ( *v354 )
          goto LABEL_104;
        v304 = 394i64;
        v305 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v279 && (*v279 & 0x4000000000000000i64) == 0 )
          deallocShared(v279);
        if ( v281 && (*v281 & 0x4000000000000000i64) == 0 )
          deallocShared(v281);
        if ( v283 && (*v283 & 0x4000000000000000i64) == 0 )
          deallocShared(v283);
        if ( v285 && (*v285 & 0x4000000000000000i64) == 0 )
          deallocShared(v285);
        if ( v287 && (*v287 & 0x4000000000000000i64) == 0 )
          deallocShared(v287);
        if ( v289 && (*v289 & 0x4000000000000000i64) == 0 )
          deallocShared(v289);
      }
      v304 = 301i64;
      v305 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v21 = v307;
      v22 = v308;
      v23 = v309;
      incl__modelZsimulationZcode95gen_u2386(v353 + 32, &v21);
      if ( !*v354 )
      {
        v304 = 304i64;
        nimZeroMem_66(&v296, 16i64);
        v296 = add_line__modelZsimulationZcode95gen_u2131;
        v297 = v353;
        v294 = 0i64;
        v295 = 0i64;
        rawNewString(&v24, v327 + v331 + 10);
        v294 = v24;
        v295 = v25;
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_549;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_548;
        appendString_29(&v294, &v24);
        v24 = v327;
        v25 = v328;
        appendString_29(&v294, &v24);
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_551;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_550;
        appendString_29(&v294, &v24);
        v24 = v331;
        v25 = v332;
        appendString_29(&v294, &v24);
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_552;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_333;
        appendString_29(&v294, &v24);
        v300 = v294;
        v301 = v295;
        v24 = v294;
        v25 = v295;
        if ( v297 )
          ((void (__fastcall *)(__int64 *, __int64))v296)(&v24, v297);
        else
          ((void (__fastcall *)(__int64 *))v296)(&v24);
        if ( !*v354 )
        {
          v304 = 305i64;
          nimZeroMem_66(&v292, 16i64);
          v292 = add_line__modelZsimulationZcode95gen_u2131;
          v293 = v353;
          v290 = 0i64;
          v291 = 0i64;
          rawNewString(&v24, 2 * v327 + 19);
          v290 = v24;
          v291 = v25;
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_555;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_554;
          appendString_29(&v290, &v24);
          v24 = v327;
          v25 = v328;
          appendString_29(&v290, &v24);
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_557;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_556;
          appendString_29(&v290, &v24);
          v24 = v327;
          v25 = v328;
          appendString_29(&v290, &v24);
          v298 = v290;
          v299 = v291;
          v24 = v290;
          v25 = v291;
          if ( v293 )
            ((void (__fastcall *)(__int64 *, __int64))v292)(&v24, v293);
          else
            ((void (__fastcall *)(__int64 *))v292)(&v24);
          if ( !*v354 )
          {
            v304 = 307i64;
            if ( *(_BYTE *)(v353 + 24) )
            {
              v264 = 0i64;
              v265 = 0i64;
              v262 = 0i64;
              v263 = 0i64;
              v260 = 0i64;
              v261 = 0i64;
              v304 = 308i64;
              nimZeroMem_66(&v258, 16i64);
              v258 = add_line__modelZsimulationZcode95gen_u2131;
              v259 = v353;
              v256 = 0i64;
              v257 = 0i64;
              rawNewString(&v24, v327 + 21);
              v256 = v24;
              v257 = v25;
              v24 = TM__THWBxVSaWN2Zh7OMooFH0w_560;
              v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_559;
              appendString_29(&v256, &v24);
              v24 = v327;
              v25 = v328;
              appendString_29(&v256, &v24);
              v24 = TM__THWBxVSaWN2Zh7OMooFH0w_562;
              v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_561;
              appendString_29(&v256, &v24);
              v264 = v256;
              v265 = v257;
              v24 = v256;
              v25 = v257;
              if ( v259 )
                ((void (__fastcall *)(__int64 *, __int64))v258)(&v24, v259);
              else
                ((void (__fastcall *)(__int64 *))v258)(&v24);
              if ( !*v354 )
              {
                v304 = 309i64;
                nimZeroMem_66(&v254, 16i64);
                v254 = add_line__modelZsimulationZcode95gen_u2131;
                v255 = v353;
                v252 = 0i64;
                v253 = 0i64;
                rawNewString(&v24, v327 + 25);
                v252 = v24;
                v253 = v25;
                v24 = TM__THWBxVSaWN2Zh7OMooFH0w_565;
                v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_564;
                appendString_29(&v252, &v24);
                v24 = v327;
                v25 = v328;
                appendString_29(&v252, &v24);
                v24 = TM__THWBxVSaWN2Zh7OMooFH0w_566;
                v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_561;
                appendString_29(&v252, &v24);
                v262 = v252;
                v263 = v253;
                v24 = v252;
                v25 = v253;
                if ( v255 )
                  ((void (__fastcall *)(__int64 *, __int64))v254)(&v24, v255);
                else
                  ((void (__fastcall *)(__int64 *))v254)(&v24);
                if ( !*v354 )
                {
                  v304 = 310i64;
                  nimZeroMem_66(&v250, 16i64);
                  v250 = add_line__modelZsimulationZcode95gen_u2131;
                  v251 = v353;
                  v248 = 0i64;
                  v249 = 0i64;
                  rawNewString(&v24, v327 + 18);
                  v248 = v24;
                  v249 = v25;
                  v24 = TM__THWBxVSaWN2Zh7OMooFH0w_569;
                  v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_568;
                  appendString_29(&v248, &v24);
                  v24 = v327;
                  v25 = v328;
                  appendString_29(&v248, &v24);
                  v24 = TM__THWBxVSaWN2Zh7OMooFH0w_570;
                  v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_561;
                  appendString_29(&v248, &v24);
                  v260 = v248;
                  v261 = v249;
                  v24 = v248;
                  v25 = v249;
                  if ( v251 )
                    ((void (__fastcall *)(__int64 *, __int64))v250)(&v24, v251);
                  else
                    ((void (__fastcall *)(__int64 *))v250)(&v24);
                  if ( !*v354 )
                  {
                    v304 = 394i64;
                    v305 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                    if ( v261 && (*v261 & 0x4000000000000000i64) == 0 )
                      deallocShared(v261);
                    if ( v263 && (*v263 & 0x4000000000000000i64) == 0 )
                      deallocShared(v263);
                    if ( v265 && (*v265 & 0x4000000000000000i64) == 0 )
                      deallocShared(v265);
                  }
                }
              }
            }
          }
        }
      }
LABEL_104:
      if ( v299 && (*v299 & 0x4000000000000000i64) == 0 )
        deallocShared(v299);
      if ( v301 && (*v301 & 0x4000000000000000i64) == 0 )
        deallocShared(v301);
      if ( *v354 )
        goto LABEL_416;
    }
  }
  v304 = 312i64;
  v305 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  if ( *(_BYTE *)(v353 + 24) )
  {
    v304 = 337i64;
    v305 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( (__int16)v323 <= 1
      || (v304 = 338i64, (_BYTE)v315 == 1)
      || (v24 = TM__THWBxVSaWN2Zh7OMooFH0w_614,
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_613,
          failedAssertImpl__stdZassertions_u234(&v24),
          !*v354) )
    {
      v304 = 341i64;
      if ( (_BYTE)v315 != 1 )
      {
        v54 = 0i64;
        v55 = 0i64;
        v52 = 0i64;
        v53 = 0i64;
        v50 = 0i64;
        v51 = 0i64;
        v48 = 0i64;
        v49 = 0i64;
        v304 = 367i64;
        v305 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        v46 = 0i64;
        v47 = 0i64;
        rawNewString(&v24, v327 + 6);
        v46 = v24;
        v47 = v25;
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_707;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_706;
        appendString_29(&v46, &v24);
        v24 = v327;
        v25 = v328;
        appendString_29(&v46, &v24);
        v54 = v46;
        v55 = v47;
        v304 = 368i64;
        nimZeroMem_66(&v44, 16i64);
        v44 = add_line__modelZsimulationZcode95gen_u2131;
        v45 = v353;
        v42 = 0i64;
        v43 = 0i64;
        rawNewString(&v24, v54 + v28 + 7);
        v42 = v24;
        v43 = v25;
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_709;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_708;
        appendString_29(&v42, &v24);
        v24 = v54;
        v25 = v55;
        appendString_29(&v42, &v24);
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_710;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_550;
        appendString_29(&v42, &v24);
        v24 = v28;
        v25 = v29;
        appendString_29(&v42, &v24);
        v52 = v42;
        v53 = v43;
        v24 = v42;
        v25 = v43;
        if ( v45 )
          ((void (__fastcall *)(__int64 *, __int64))v44)(&v24, v45);
        else
          ((void (__fastcall *)(__int64 *))v44)(&v24);
        if ( *v354 )
          goto LABEL_416;
        v304 = 369i64;
        nimZeroMem_66(&v40, 16i64);
        v40 = add_line__modelZsimulationZcode95gen_u2131;
        v41 = v353;
        v38 = 0i64;
        v39 = 0i64;
        v339 = 0i64;
        v18 = v307;
        v19 = v308;
        v20 = v309;
        v339 = get_state_index__modelZsave95mongerZcommon_u5502(&v18, 0i64);
        if ( *v354 )
          goto LABEL_416;
        dollar___systemZdollars_u14(&v50, v339);
        if ( *v354 )
          goto LABEL_416;
        rawNewString(&v24, v335 + v50 + v54 + 31);
        v38 = v24;
        v39 = v25;
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_712;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_536;
        appendString_29(&v38, &v24);
        v24 = v50;
        v25 = v51;
        appendString_29(&v38, &v24);
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_713;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_41;
        appendString_29(&v38, &v24);
        v24 = v335;
        v25 = v336;
        appendString_29(&v38, &v24);
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_714;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_593;
        appendString_29(&v38, &v24);
        v24 = v54;
        v25 = v55;
        appendString_29(&v38, &v24);
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_715;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_307;
        appendString_29(&v38, &v24);
        v48 = v38;
        v49 = v39;
        v24 = v38;
        v25 = v39;
        if ( v41 )
          ((void (__fastcall *)(__int64 *, __int64))v40)(&v24, v41);
        else
          ((void (__fastcall *)(__int64 *))v40)(&v24);
        if ( *v354 )
          goto LABEL_416;
        v304 = 370i64;
        v338 = 0;
        v18 = v319;
        v19 = v320;
        v20 = v321;
        v21 = v307;
        v22 = v308;
        v23 = v309;
        v338 = eqeq___modelZsimulationZcontroller_u106(&v18, &v21);
        if ( !v338 )
        {
          v36 = 0i64;
          v37 = 0i64;
          v34 = 0i64;
          v35 = 0i64;
          v304 = 371i64;
          nimZeroMem_66(&v32, 16i64);
          v32 = add_line__modelZsimulationZcode95gen_u2131;
          v33 = v353;
          v30 = 0i64;
          v31 = 0i64;
          v337 = 0i64;
          v18 = v319;
          v19 = v320;
          v20 = v321;
          v337 = get_state_index__modelZsave95mongerZcommon_u5502(&v18, 0i64);
          if ( *v354 )
            goto LABEL_416;
          dollar___systemZdollars_u14(&v36, v337);
          if ( *v354 )
            goto LABEL_416;
          rawNewString(&v24, v335 + v36 + v54 + 31);
          v30 = v24;
          v31 = v25;
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_717;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_536;
          appendString_29(&v30, &v24);
          v24 = v36;
          v25 = v37;
          appendString_29(&v30, &v24);
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_718;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_41;
          appendString_29(&v30, &v24);
          v24 = v335;
          v25 = v336;
          appendString_29(&v30, &v24);
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_719;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_593;
          appendString_29(&v30, &v24);
          v24 = v54;
          v25 = v55;
          appendString_29(&v30, &v24);
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_720;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_307;
          appendString_29(&v30, &v24);
          v34 = v30;
          v35 = v31;
          v24 = v30;
          v25 = v31;
          if ( v33 )
            ((void (__fastcall *)(__int64 *, __int64))v32)(&v24, v33);
          else
            ((void (__fastcall *)(__int64 *))v32)(&v24);
          if ( *v354 )
            goto LABEL_416;
          v304 = 394i64;
          v305 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v35 && (*v35 & 0x4000000000000000i64) == 0 )
            deallocShared(v35);
          if ( v37 && (*v37 & 0x4000000000000000i64) == 0 )
            deallocShared(v37);
        }
        if ( v49 && (*v49 & 0x4000000000000000i64) == 0 )
          deallocShared(v49);
        if ( v51 && (*v51 & 0x4000000000000000i64) == 0 )
          deallocShared(v51);
        if ( v53 && (*v53 & 0x4000000000000000i64) == 0 )
          deallocShared(v53);
        if ( v55 && (*v55 & 0x4000000000000000i64) == 0 )
          deallocShared(v55);
        goto LABEL_416;
      }
      v202 = 0i64;
      v203 = 0i64;
      v200 = 0i64;
      v201 = 0i64;
      v198 = 0i64;
      v199 = 0i64;
      v196 = 0i64;
      v197 = 0i64;
      v194 = 0i64;
      v195 = 0i64;
      v192 = 0i64;
      v193 = 0i64;
      v190 = 0i64;
      v191 = 0i64;
      v188 = 0i64;
      v189 = 0i64;
      v186 = 0i64;
      v187 = 0i64;
      v184 = 0i64;
      v185 = 0i64;
      v182 = 0i64;
      v183 = 0i64;
      v180 = 0i64;
      v181 = 0i64;
      v178 = 0i64;
      v179 = 0i64;
      v176 = 0i64;
      v177 = 0i64;
      v174 = 0i64;
      v175 = 0i64;
      v172 = 0i64;
      v173 = 0i64;
      v170 = 0i64;
      v171 = 0i64;
      v168 = 0i64;
      v169 = 0i64;
      v166 = 0i64;
      v167 = 0i64;
      v164 = 0i64;
      v165 = 0i64;
      v162 = 0i64;
      v163 = 0i64;
      v160 = 0i64;
      v161 = 0i64;
      v158 = 0i64;
      v159 = 0i64;
      v156 = 0i64;
      v157 = 0i64;
      v154 = 0i64;
      v155 = 0i64;
      v152 = 0i64;
      v153 = 0i64;
      v150 = 0i64;
      v151 = 0i64;
      v148 = 0i64;
      v149 = 0i64;
      v146 = 0i64;
      v147 = 0i64;
      v304 = 342i64;
      nimZeroMem_66(&v144, 16i64);
      v144 = add_line__modelZsimulationZcode95gen_u2131;
      v145 = v353;
      v142 = 0i64;
      v143 = 0i64;
      rawNewString(&v24, v325 + 10);
      v142 = v24;
      v143 = v25;
      v24 = TM__THWBxVSaWN2Zh7OMooFH0w_615;
      v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_583;
      appendString_29(&v142, &v24);
      v24 = v325;
      v25 = v326;
      appendString_29(&v142, &v24);
      v24 = TM__THWBxVSaWN2Zh7OMooFH0w_616;
      v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_585;
      appendString_29(&v142, &v24);
      v202 = v142;
      v203 = v143;
      v24 = v142;
      v25 = v143;
      if ( v145 )
        ((void (__fastcall *)(__int64 *, __int64))v144)(&v24, v145);
      else
        ((void (__fastcall *)(__int64 *))v144)(&v24);
      if ( !*v354 )
      {
        v304 = 343i64;
        nimZeroMem_66(&v140, 16i64);
        v140 = add_line__modelZsimulationZcode95gen_u2131;
        v141 = v353;
        v138 = 0i64;
        v139 = 0i64;
        rawNewString(&v24, v335 + v331 + v28 + 20);
        v138 = v24;
        v139 = v25;
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_619;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_618;
        appendString_29(&v138, &v24);
        v24 = v331;
        v25 = v332;
        appendString_29(&v138, &v24);
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_620;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_593;
        appendString_29(&v138, &v24);
        v24 = v335;
        v25 = v336;
        appendString_29(&v138, &v24);
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_621;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_593;
        appendString_29(&v138, &v24);
        v24 = v28;
        v25 = v29;
        appendString_29(&v138, &v24);
        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_622;
        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_307;
        appendString_29(&v138, &v24);
        v200 = v138;
        v201 = v139;
        v24 = v138;
        v25 = v139;
        if ( v141 )
          ((void (__fastcall *)(__int64 *, __int64))v140)(&v24, v141);
        else
          ((void (__fastcall *)(__int64 *))v140)(&v24);
        if ( !*v354 )
        {
          v304 = 344i64;
          nimZeroMem_66(&v136, 16i64);
          v136 = add_line__modelZsimulationZcode95gen_u2131;
          v137 = v353;
          v134 = 0i64;
          v135 = 0i64;
          rawNewString(&v24, 2 * v327 + 41);
          v134 = v24;
          v135 = v25;
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_625;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_624;
          appendString_29(&v134, &v24);
          v24 = v327;
          v25 = v328;
          appendString_29(&v134, &v24);
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_627;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_626;
          appendString_29(&v134, &v24);
          v24 = v327;
          v25 = v328;
          appendString_29(&v134, &v24);
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_629;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_628;
          appendString_29(&v134, &v24);
          v198 = v134;
          v199 = v135;
          v24 = v134;
          v25 = v135;
          if ( v137 )
            ((void (__fastcall *)(__int64 *, __int64))v136)(&v24, v137);
          else
            ((void (__fastcall *)(__int64 *))v136)(&v24);
          if ( !*v354 )
          {
            v304 = 345i64;
            nimZeroMem_66(&v132, 16i64);
            v132 = add_line__modelZsimulationZcode95gen_u2131;
            v133 = v353;
            v130 = 0i64;
            v131 = 0i64;
            rawNewString(&v24, v327 + 72);
            v130 = v24;
            v131 = v25;
            v24 = TM__THWBxVSaWN2Zh7OMooFH0w_632;
            v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_631;
            appendString_29(&v130, &v24);
            v24 = v327;
            v25 = v328;
            appendString_29(&v130, &v24);
            v24 = TM__THWBxVSaWN2Zh7OMooFH0w_633;
            v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_325;
            appendString_29(&v130, &v24);
            v196 = v130;
            v197 = v131;
            v24 = v130;
            v25 = v131;
            if ( v133 )
              ((void (__fastcall *)(__int64 *, __int64))v132)(&v24, v133);
            else
              ((void (__fastcall *)(__int64 *))v132)(&v24);
            if ( !*v354 )
            {
              v304 = 346i64;
              nimZeroMem_66(&v128, 16i64);
              v128 = add_line__modelZsimulationZcode95gen_u2131;
              v129 = v353;
              v126 = 0i64;
              v127 = 0i64;
              dollar___systemZdollars_u14(&v194, a2);
              if ( !*v354 )
              {
                rawNewString(&v24, v194 + 59);
                v126 = v24;
                v127 = v25;
                v24 = TM__THWBxVSaWN2Zh7OMooFH0w_636;
                v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_635;
                appendString_29(&v126, &v24);
                v24 = v194;
                v25 = v195;
                appendString_29(&v126, &v24);
                v24 = TM__THWBxVSaWN2Zh7OMooFH0w_637;
                v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_325;
                appendString_29(&v126, &v24);
                v192 = v126;
                v193 = v127;
                v24 = v126;
                v25 = v127;
                if ( v129 )
                  ((void (__fastcall *)(__int64 *, __int64))v128)(&v24, v129);
                else
                  ((void (__fastcall *)(__int64 *))v128)(&v24);
                if ( !*v354 )
                {
                  v304 = 347i64;
                  nimZeroMem_66(&v124, 16i64);
                  v124 = add_line__modelZsimulationZcode95gen_u2131;
                  v125 = v353;
                  v122 = 0i64;
                  v123 = 0i64;
                  rawNewString(&v24, v327 + 60);
                  v122 = v24;
                  v123 = v25;
                  v24 = TM__THWBxVSaWN2Zh7OMooFH0w_640;
                  v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_639;
                  appendString_29(&v122, &v24);
                  v24 = v327;
                  v25 = v328;
                  appendString_29(&v122, &v24);
                  v24 = TM__THWBxVSaWN2Zh7OMooFH0w_641;
                  v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_325;
                  appendString_29(&v122, &v24);
                  v190 = v122;
                  v191 = v123;
                  v24 = v122;
                  v25 = v123;
                  if ( v125 )
                    ((void (__fastcall *)(__int64 *, __int64))v124)(&v24, v125);
                  else
                    ((void (__fastcall *)(__int64 *))v124)(&v24);
                  if ( !*v354 )
                  {
                    v304 = 348i64;
                    nimZeroMem_66(&v120, 16i64);
                    v120 = add_line__modelZsimulationZcode95gen_u2131;
                    v121 = v353;
                    v118 = 0i64;
                    v119 = 0i64;
                    dollar___systemZdollars_u14(&v188, a3);
                    if ( !*v354 )
                    {
                      rawNewString(&v24, v188 + 50);
                      v118 = v24;
                      v119 = v25;
                      v24 = TM__THWBxVSaWN2Zh7OMooFH0w_644;
                      v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_643;
                      appendString_29(&v118, &v24);
                      v24 = v188;
                      v25 = v189;
                      appendString_29(&v118, &v24);
                      v24 = TM__THWBxVSaWN2Zh7OMooFH0w_645;
                      v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_325;
                      appendString_29(&v118, &v24);
                      v186 = v118;
                      v187 = v119;
                      v24 = v118;
                      v25 = v119;
                      if ( v121 )
                        ((void (__fastcall *)(__int64 *, __int64))v120)(&v24, v121);
                      else
                        ((void (__fastcall *)(__int64 *))v120)(&v24);
                      if ( !*v354 )
                      {
                        v304 = 349i64;
                        nimZeroMem_66(&v116, 16i64);
                        v116 = add_line__modelZsimulationZcode95gen_u2131;
                        v117 = v353;
                        v114 = 0i64;
                        v115 = 0i64;
                        rawNewString(&v24, v327 + 86);
                        v114 = v24;
                        v115 = v25;
                        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_648;
                        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_647;
                        appendString_29(&v114, &v24);
                        v24 = v327;
                        v25 = v328;
                        appendString_29(&v114, &v24);
                        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_649;
                        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_325;
                        appendString_29(&v114, &v24);
                        v184 = v114;
                        v185 = v115;
                        v24 = v114;
                        v25 = v115;
                        if ( v117 )
                          ((void (__fastcall *)(__int64 *, __int64))v116)(&v24, v117);
                        else
                          ((void (__fastcall *)(__int64 *))v116)(&v24);
                        if ( !*v354 )
                        {
                          v304 = 350i64;
                          nimZeroMem_66(&v112, 16i64);
                          v112 = add_line__modelZsimulationZcode95gen_u2131;
                          v113 = v353;
                          v110 = 0i64;
                          v111 = 0i64;
                          dollar___modelZsave95mongerZcommon_u3396(&v182, a1[3]);
                          if ( !*v354 )
                          {
                            rawNewString(&v24, v182 + 69);
                            v110 = v24;
                            v111 = v25;
                            v24 = TM__THWBxVSaWN2Zh7OMooFH0w_652;
                            v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_651;
                            appendString_29(&v110, &v24);
                            v24 = v182;
                            v25 = v183;
                            appendString_29(&v110, &v24);
                            v24 = TM__THWBxVSaWN2Zh7OMooFH0w_653;
                            v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_325;
                            appendString_29(&v110, &v24);
                            v180 = v110;
                            v181 = v111;
                            v24 = v110;
                            v25 = v111;
                            if ( v113 )
                              ((void (__fastcall *)(__int64 *, __int64))v112)(&v24, v113);
                            else
                              ((void (__fastcall *)(__int64 *))v112)(&v24);
                            if ( !*v354 )
                            {
                              v304 = 351i64;
                              nimZeroMem_66(&v108, 16i64);
                              v108 = add_line__modelZsimulationZcode95gen_u2131;
                              v109 = v353;
                              v106 = 0i64;
                              v107 = 0i64;
                              dollar___systemZdollars_u14(&v178, v324);
                              if ( !*v354 )
                              {
                                rawNewString(&v24, v178 + 66);
                                v106 = v24;
                                v107 = v25;
                                v24 = TM__THWBxVSaWN2Zh7OMooFH0w_656;
                                v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_655;
                                appendString_29(&v106, &v24);
                                v24 = v178;
                                v25 = v179;
                                appendString_29(&v106, &v24);
                                v24 = TM__THWBxVSaWN2Zh7OMooFH0w_657;
                                v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_325;
                                appendString_29(&v106, &v24);
                                v176 = v106;
                                v177 = v107;
                                v24 = v106;
                                v25 = v107;
                                if ( v109 )
                                  ((void (__fastcall *)(__int64 *, __int64))v108)(&v24, v109);
                                else
                                  ((void (__fastcall *)(__int64 *))v108)(&v24);
                                if ( !*v354 )
                                {
                                  v304 = 352i64;
                                  nimZeroMem_66(&v104, 16i64);
                                  v104 = add_line__modelZsimulationZcode95gen_u2131;
                                  v105 = v353;
                                  v102 = 0i64;
                                  v103 = 0i64;
                                  rawNewString(&v24, v327 + 53);
                                  v102 = v24;
                                  v103 = v25;
                                  v24 = TM__THWBxVSaWN2Zh7OMooFH0w_660;
                                  v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_659;
                                  appendString_29(&v102, &v24);
                                  v24 = v327;
                                  v25 = v328;
                                  appendString_29(&v102, &v24);
                                  v24 = TM__THWBxVSaWN2Zh7OMooFH0w_661;
                                  v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_325;
                                  appendString_29(&v102, &v24);
                                  v174 = v102;
                                  v175 = v103;
                                  v24 = v102;
                                  v25 = v103;
                                  if ( v105 )
                                    ((void (__fastcall *)(__int64 *, __int64))v104)(&v24, v105);
                                  else
                                    ((void (__fastcall *)(__int64 *))v104)(&v24);
                                  if ( !*v354 )
                                  {
                                    v304 = 353i64;
                                    nimZeroMem_66(&v100, 16i64);
                                    v100 = add_line__modelZsimulationZcode95gen_u2131;
                                    v101 = v353;
                                    v24 = TM__THWBxVSaWN2Zh7OMooFH0w_664;
                                    v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_663;
                                    if ( v353 )
                                      ((void (__fastcall *)(__int64 *, __int64))v100)(&v24, v101);
                                    else
                                      ((void (__fastcall *)(__int64 *))v100)(&v24);
                                    if ( !*v354 )
                                    {
                                      v304 = 354i64;
                                      nimZeroMem_66(&v98, 16i64);
                                      v98 = add_line__modelZsimulationZcode95gen_u2131;
                                      v99 = v353;
                                      v24 = TM__THWBxVSaWN2Zh7OMooFH0w_667;
                                      v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_666;
                                      if ( v353 )
                                        ((void (__fastcall *)(__int64 *, __int64))v98)(&v24, v99);
                                      else
                                        ((void (__fastcall *)(__int64 *))v98)(&v24);
                                      if ( !*v354 )
                                      {
                                        v304 = 355i64;
                                        nimZeroMem_66(&v96, 16i64);
                                        v96 = add_line__modelZsimulationZcode95gen_u2131;
                                        v97 = v353;
                                        v94 = 0i64;
                                        v95 = 0i64;
                                        rawNewString(&v24, v327 + 14);
                                        v94 = v24;
                                        v95 = v25;
                                        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_669;
                                        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_588;
                                        appendString_29(&v94, &v24);
                                        v24 = v327;
                                        v25 = v328;
                                        appendString_29(&v94, &v24);
                                        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_671;
                                        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_670;
                                        appendString_29(&v94, &v24);
                                        v172 = v94;
                                        v173 = v95;
                                        v24 = v94;
                                        v25 = v95;
                                        if ( v97 )
                                          ((void (__fastcall *)(__int64 *, __int64))v96)(&v24, v97);
                                        else
                                          ((void (__fastcall *)(__int64 *))v96)(&v24);
                                        if ( !*v354 )
                                        {
                                          v304 = 356i64;
                                          nimZeroMem_66(&v92, 16i64);
                                          v92 = add_line__modelZsimulationZcode95gen_u2131;
                                          v93 = v353;
                                          v90 = 0i64;
                                          v91 = 0i64;
                                          rawNewString(&v24, v327 + 23);
                                          v90 = v24;
                                          v91 = v25;
                                          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_673;
                                          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_597;
                                          appendString_29(&v90, &v24);
                                          v24 = v327;
                                          v25 = v328;
                                          appendString_29(&v90, &v24);
                                          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_675;
                                          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_674;
                                          appendString_29(&v90, &v24);
                                          v170 = v90;
                                          v171 = v91;
                                          v24 = v90;
                                          v25 = v91;
                                          if ( v93 )
                                            ((void (__fastcall *)(__int64 *, __int64))v92)(&v24, v93);
                                          else
                                            ((void (__fastcall *)(__int64 *))v92)(&v24);
                                          if ( !*v354 )
                                          {
                                            v304 = 357i64;
                                            nimZeroMem_66(&v88, 16i64);
                                            v88 = add_line__modelZsimulationZcode95gen_u2131;
                                            v89 = v353;
                                            v86 = 0i64;
                                            v87 = 0i64;
                                            v344 = 0i64;
                                            v18 = v307;
                                            v19 = v308;
                                            v20 = v309;
                                            v344 = get_state_index__modelZsave95mongerZcommon_u5502(&v18, 0i64);
                                            if ( !*v354 )
                                            {
                                              dollar___systemZdollars_u14(&v168, v344);
                                              if ( !*v354 )
                                              {
                                                rawNewString(&v24, v168 + 38);
                                                v86 = v24;
                                                v87 = v25;
                                                v24 = TM__THWBxVSaWN2Zh7OMooFH0w_678;
                                                v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_677;
                                                appendString_29(&v86, &v24);
                                                v24 = v168;
                                                v25 = v169;
                                                appendString_29(&v86, &v24);
                                                v24 = TM__THWBxVSaWN2Zh7OMooFH0w_680;
                                                v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_679;
                                                appendString_29(&v86, &v24);
                                                v166 = v86;
                                                v167 = v87;
                                                v24 = v86;
                                                v25 = v87;
                                                if ( v89 )
                                                  ((void (__fastcall *)(__int64 *, __int64))v88)(&v24, v89);
                                                else
                                                  ((void (__fastcall *)(__int64 *))v88)(&v24);
                                                if ( !*v354 )
                                                {
                                                  v304 = 358i64;
                                                  v343 = 0;
                                                  v18 = v307;
                                                  v19 = v308;
                                                  v20 = v309;
                                                  v21 = v319;
                                                  v22 = v320;
                                                  v23 = v321;
                                                  v343 = eqeq___modelZsimulationZcontroller_u106(&v18, &v21);
                                                  if ( !v343 )
                                                  {
                                                    v62 = 0i64;
                                                    v63 = 0i64;
                                                    v60 = 0i64;
                                                    v61 = 0i64;
                                                    v304 = 359i64;
                                                    nimZeroMem_66(&v58, 16i64);
                                                    v58 = add_line__modelZsimulationZcode95gen_u2131;
                                                    v59 = v353;
                                                    v56 = 0i64;
                                                    v57 = 0i64;
                                                    v342 = 0i64;
                                                    v18 = v319;
                                                    v19 = v320;
                                                    v20 = v321;
                                                    v342 = get_state_index__modelZsave95mongerZcommon_u5502(&v18, 0i64);
                                                    if ( *v354 )
                                                      goto LABEL_416;
                                                    dollar___systemZdollars_u14(&v62, v342);
                                                    if ( *v354 )
                                                      goto LABEL_416;
                                                    rawNewString(&v24, v62 + 38);
                                                    v56 = v24;
                                                    v57 = v25;
                                                    v24 = TM__THWBxVSaWN2Zh7OMooFH0w_682;
                                                    v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_677;
                                                    appendString_29(&v56, &v24);
                                                    v24 = v62;
                                                    v25 = v63;
                                                    appendString_29(&v56, &v24);
                                                    v24 = TM__THWBxVSaWN2Zh7OMooFH0w_683;
                                                    v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_679;
                                                    appendString_29(&v56, &v24);
                                                    v60 = v56;
                                                    v61 = v57;
                                                    v24 = v56;
                                                    v25 = v57;
                                                    if ( v59 )
                                                      ((void (__fastcall *)(__int64 *, __int64))v58)(&v24, v59);
                                                    else
                                                      ((void (__fastcall *)(__int64 *))v58)(&v24);
                                                    if ( *v354 )
                                                      goto LABEL_416;
                                                    v304 = 394i64;
                                                    v305 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                                                    if ( v61 && (*v61 & 0x4000000000000000i64) == 0 )
                                                      deallocShared(v61);
                                                    if ( v63 && (*v63 & 0x4000000000000000i64) == 0 )
                                                      deallocShared(v63);
                                                  }
                                                  v304 = 360i64;
                                                  v305 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
                                                  nimZeroMem_66(&v84, 16i64);
                                                  v84 = add_line__modelZsimulationZcode95gen_u2131;
                                                  v85 = v353;
                                                  v82 = 0i64;
                                                  v83 = 0i64;
                                                  dollar___systemZdollars_u14(&v164, a2);
                                                  if ( !*v354 )
                                                  {
                                                    rawNewString(&v24, v327 + v164 + 20);
                                                    v82 = v24;
                                                    v83 = v25;
                                                    v24 = TM__THWBxVSaWN2Zh7OMooFH0w_686;
                                                    v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_685;
                                                    appendString_29(&v82, &v24);
                                                    v24 = v327;
                                                    v25 = v328;
                                                    appendString_29(&v82, &v24);
                                                    v24 = TM__THWBxVSaWN2Zh7OMooFH0w_687;
                                                    v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_550;
                                                    appendString_29(&v82, &v24);
                                                    v24 = v164;
                                                    v25 = v165;
                                                    appendString_29(&v82, &v24);
                                                    v162 = v82;
                                                    v163 = v83;
                                                    v24 = v82;
                                                    v25 = v83;
                                                    if ( v85 )
                                                      ((void (__fastcall *)(__int64 *, __int64))v84)(&v24, v85);
                                                    else
                                                      ((void (__fastcall *)(__int64 *))v84)(&v24);
                                                    if ( !*v354 )
                                                    {
                                                      v304 = 361i64;
                                                      nimZeroMem_66(&v80, 16i64);
                                                      v80 = add_line__modelZsimulationZcode95gen_u2131;
                                                      v81 = v353;
                                                      v78 = 0i64;
                                                      v79 = 0i64;
                                                      dollar___modelZsave95mongerZcommon_u3396(&v160, a1[3]);
                                                      if ( !*v354 )
                                                      {
                                                        rawNewString(&v24, v327 + v160 + 24);
                                                        v78 = v24;
                                                        v79 = v25;
                                                        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_690;
                                                        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_689;
                                                        appendString_29(&v78, &v24);
                                                        v24 = v327;
                                                        v25 = v328;
                                                        appendString_29(&v78, &v24);
                                                        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_691;
                                                        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_550;
                                                        appendString_29(&v78, &v24);
                                                        v24 = v160;
                                                        v25 = v161;
                                                        appendString_29(&v78, &v24);
                                                        v158 = v78;
                                                        v159 = v79;
                                                        v24 = v78;
                                                        v25 = v79;
                                                        if ( v81 )
                                                          ((void (__fastcall *)(__int64 *, __int64))v80)(&v24, v81);
                                                        else
                                                          ((void (__fastcall *)(__int64 *))v80)(&v24);
                                                        if ( !*v354 )
                                                        {
                                                          v304 = 362i64;
                                                          nimZeroMem_66(&v76, 16i64);
                                                          v76 = add_line__modelZsimulationZcode95gen_u2131;
                                                          v77 = v353;
                                                          v74 = 0i64;
                                                          v75 = 0i64;
                                                          dollar___systemZdollars_u14(&v156, a3);
                                                          if ( !*v354 )
                                                          {
                                                            rawNewString(&v24, v327 + v156 + 17);
                                                            v74 = v24;
                                                            v75 = v25;
                                                            v24 = TM__THWBxVSaWN2Zh7OMooFH0w_694;
                                                            v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_693;
                                                            appendString_29(&v74, &v24);
                                                            v24 = v327;
                                                            v25 = v328;
                                                            appendString_29(&v74, &v24);
                                                            v24 = TM__THWBxVSaWN2Zh7OMooFH0w_695;
                                                            v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_550;
                                                            appendString_29(&v74, &v24);
                                                            v24 = v156;
                                                            v25 = v157;
                                                            appendString_29(&v74, &v24);
                                                            v154 = v74;
                                                            v155 = v75;
                                                            v24 = v74;
                                                            v25 = v75;
                                                            if ( v77 )
                                                              ((void (__fastcall *)(__int64 *, __int64))v76)(&v24, v77);
                                                            else
                                                              ((void (__fastcall *)(__int64 *))v76)(&v24);
                                                            if ( !*v354 )
                                                            {
                                                              v304 = 363i64;
                                                              nimZeroMem_66(&v72, 16i64);
                                                              v72 = add_line__modelZsimulationZcode95gen_u2131;
                                                              v73 = v353;
                                                              v70 = 0i64;
                                                              v71 = 0i64;
                                                              v341 = 0i64;
                                                              v18 = v316;
                                                              v19 = v317;
                                                              v20 = v318;
                                                              v341 = get_z_state_index__modelZsave95mongerZcommon_u5499(&v18);
                                                              if ( !*v354 )
                                                              {
                                                                dollar___systemZdollars_u14(&v152, v341);
                                                                if ( !*v354 )
                                                                {
                                                                  rawNewString(&v24, v152 + 37);
                                                                  v70 = v24;
                                                                  v71 = v25;
                                                                  v24 = TM__THWBxVSaWN2Zh7OMooFH0w_697;
                                                                  v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_677;
                                                                  appendString_29(&v70, &v24);
                                                                  v24 = v152;
                                                                  v25 = v153;
                                                                  appendString_29(&v70, &v24);
                                                                  v24 = TM__THWBxVSaWN2Zh7OMooFH0w_699;
                                                                  v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_698;
                                                                  appendString_29(&v70, &v24);
                                                                  v150 = v70;
                                                                  v151 = v71;
                                                                  v24 = v70;
                                                                  v25 = v71;
                                                                  if ( v73 )
                                                                    ((void (__fastcall *)(__int64 *, __int64))v72)(
                                                                      &v24,
                                                                      v73);
                                                                  else
                                                                    ((void (__fastcall *)(__int64 *))v72)(&v24);
                                                                  if ( !*v354 )
                                                                  {
                                                                    v304 = 364i64;
                                                                    nimZeroMem_66(&v68, 16i64);
                                                                    v68 = add_line__modelZsimulationZcode95gen_u2131;
                                                                    v69 = v353;
                                                                    v66 = 0i64;
                                                                    v67 = 0i64;
                                                                    v340 = 0i64;
                                                                    v18 = v319;
                                                                    v19 = v320;
                                                                    v20 = v321;
                                                                    v340 = get_z_state_index__modelZsave95mongerZcommon_u5499(&v18);
                                                                    if ( !*v354 )
                                                                    {
                                                                      dollar___systemZdollars_u14(&v148, v340);
                                                                      if ( !*v354 )
                                                                      {
                                                                        rawNewString(&v24, v148 + 37);
                                                                        v66 = v24;
                                                                        v67 = v25;
                                                                        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_701;
                                                                        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_677;
                                                                        appendString_29(&v66, &v24);
                                                                        v24 = v148;
                                                                        v25 = v149;
                                                                        appendString_29(&v66, &v24);
                                                                        v24 = TM__THWBxVSaWN2Zh7OMooFH0w_702;
                                                                        v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_698;
                                                                        appendString_29(&v66, &v24);
                                                                        v146 = v66;
                                                                        v147 = v67;
                                                                        v24 = v66;
                                                                        v25 = v67;
                                                                        if ( v69 )
                                                                          ((void (__fastcall *)(__int64 *, __int64))v68)(
                                                                            &v24,
                                                                            v69);
                                                                        else
                                                                          ((void (__fastcall *)(__int64 *))v68)(&v24);
                                                                        if ( !*v354 )
                                                                        {
                                                                          v304 = 365i64;
                                                                          nimZeroMem_66(&v64, 16i64);
                                                                          v64 = add_line__modelZsimulationZcode95gen_u2131;
                                                                          v65 = v353;
                                                                          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_704;
                                                                          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_605;
                                                                          if ( v353 )
                                                                            ((void (__fastcall *)(__int64 *, __int64))v64)(
                                                                              &v24,
                                                                              v65);
                                                                          else
                                                                            ((void (__fastcall *)(__int64 *))v64)(&v24);
                                                                          if ( !*v354 )
                                                                          {
                                                                            v304 = 394i64;
                                                                            v305 = "C:\\Users\\Admin\\.choosenim\\toolcha"
                                                                                   "ins\\nim-2.2.6\\lib\\system.nim";
                                                                            if ( v147
                                                                              && (*v147 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v147);
                                                                            }
                                                                            if ( v149
                                                                              && (*v149 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v149);
                                                                            }
                                                                            if ( v151
                                                                              && (*v151 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v151);
                                                                            }
                                                                            if ( v153
                                                                              && (*v153 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v153);
                                                                            }
                                                                            if ( v155
                                                                              && (*v155 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v155);
                                                                            }
                                                                            if ( v157
                                                                              && (*v157 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v157);
                                                                            }
                                                                            if ( v159
                                                                              && (*v159 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v159);
                                                                            }
                                                                            if ( v161
                                                                              && (*v161 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v161);
                                                                            }
                                                                            if ( v163
                                                                              && (*v163 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v163);
                                                                            }
                                                                            if ( v165
                                                                              && (*v165 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v165);
                                                                            }
                                                                            if ( v167
                                                                              && (*v167 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v167);
                                                                            }
                                                                            if ( v169
                                                                              && (*v169 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v169);
                                                                            }
                                                                            if ( v171
                                                                              && (*v171 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v171);
                                                                            }
                                                                            if ( v173
                                                                              && (*v173 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v173);
                                                                            }
                                                                            if ( v175
                                                                              && (*v175 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v175);
                                                                            }
                                                                            if ( v177
                                                                              && (*v177 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v177);
                                                                            }
                                                                            if ( v179
                                                                              && (*v179 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v179);
                                                                            }
                                                                            if ( v181
                                                                              && (*v181 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v181);
                                                                            }
                                                                            if ( v183
                                                                              && (*v183 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v183);
                                                                            }
                                                                            if ( v185
                                                                              && (*v185 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v185);
                                                                            }
                                                                            if ( v187
                                                                              && (*v187 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v187);
                                                                            }
                                                                            if ( v189
                                                                              && (*v189 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v189);
                                                                            }
                                                                            if ( v191
                                                                              && (*v191 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v191);
                                                                            }
                                                                            if ( v193
                                                                              && (*v193 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v193);
                                                                            }
                                                                            if ( v195
                                                                              && (*v195 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v195);
                                                                            }
                                                                            if ( v197
                                                                              && (*v197 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v197);
                                                                            }
                                                                            if ( v199
                                                                              && (*v199 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v199);
                                                                            }
                                                                            if ( v201
                                                                              && (*v201 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v201);
                                                                            }
                                                                            if ( v203
                                                                              && (*v203 & 0x4000000000000000i64) == 0 )
                                                                            {
                                                                              deallocShared(v203);
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
  else
  {
    v304 = 315i64;
    v346 = 0;
    v16 = *(_QWORD *)(v353 + 40);
    v21 = *(_QWORD *)(v353 + 32);
    v22 = v16;
    v23 = *(_QWORD *)(v353 + 48);
    v18 = v307;
    v19 = v308;
    v20 = v309;
    v346 = contains__modelZsimulationZcode95gen_u3866(&v21, &v18);
    if ( !*v354 )
    {
      v345 = v346 == 0;
      v304 = 316i64;
      if ( v346 )
        goto LABEL_137;
      v304 = 317i64;
      v18 = v307;
      v19 = v308;
      v20 = v309;
      incl__modelZsimulationZcode95gen_u2386(v353 + 32, &v18);
      if ( !*v354 )
      {
        v304 = 318i64;
        if ( (_BYTE)v315 == 1 )
        {
          v246 = 0i64;
          v247 = 0i64;
          v244 = 0i64;
          v245 = 0i64;
          v304 = 319i64;
          nimZeroMem_66(&v242, 16i64);
          v242 = add_line__modelZsimulationZcode95gen_u2131;
          v243 = v353;
          v240 = 0i64;
          v241 = 0i64;
          rawNewString(&v24, v327 + v331 + 9);
          v240 = v24;
          v241 = v25;
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_572;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_548;
          appendString_29(&v240, &v24);
          v24 = v327;
          v25 = v328;
          appendString_29(&v240, &v24);
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_573;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_550;
          appendString_29(&v240, &v24);
          v24 = v331;
          v25 = v332;
          appendString_29(&v240, &v24);
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_574;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_309;
          appendString_29(&v240, &v24);
          v246 = v240;
          v247 = v241;
          v24 = v240;
          v25 = v241;
          if ( v243 )
            ((void (__fastcall *)(__int64 *, __int64))v242)(&v24, v243);
          else
            ((void (__fastcall *)(__int64 *))v242)(&v24);
          if ( *v354 )
            goto LABEL_416;
          v304 = 320i64;
          nimZeroMem_66(&v238, 16i64);
          v238 = add_line__modelZsimulationZcode95gen_u2131;
          v239 = v353;
          v236 = 0i64;
          v237 = 0i64;
          rawNewString(&v24, 2 * v327 + 19);
          v236 = v24;
          v237 = v25;
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_576;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_554;
          appendString_29(&v236, &v24);
          v24 = v327;
          v25 = v328;
          appendString_29(&v236, &v24);
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_577;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_556;
          appendString_29(&v236, &v24);
          v24 = v327;
          v25 = v328;
          appendString_29(&v236, &v24);
          v244 = v236;
          v245 = v237;
          v24 = v236;
          v25 = v237;
          if ( v239 )
            ((void (__fastcall *)(__int64 *, __int64))v238)(&v24, v239);
          else
            ((void (__fastcall *)(__int64 *))v238)(&v24);
          if ( *v354 )
            goto LABEL_416;
          v304 = 394i64;
          v305 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v245 && (*v245 & 0x4000000000000000i64) == 0 )
            deallocShared(v245);
          if ( v247 && (*v247 & 0x4000000000000000i64) == 0 )
            deallocShared(v247);
        }
        else
        {
          v234 = 0i64;
          v235 = 0i64;
          v304 = 322i64;
          v305 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
          nimZeroMem_66(&v232, 16i64);
          v232 = add_line__modelZsimulationZcode95gen_u2131;
          v233 = v353;
          v230 = 0i64;
          v231 = 0i64;
          rawNewString(&v24, v335 + v327 + v28 + 8);
          v230 = v24;
          v231 = v25;
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_579;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_548;
          appendString_29(&v230, &v24);
          v24 = v327;
          v25 = v328;
          appendString_29(&v230, &v24);
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_580;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_550;
          appendString_29(&v230, &v24);
          v24 = v335;
          v25 = v336;
          appendString_29(&v230, &v24);
          v24 = v28;
          v25 = v29;
          appendString_29(&v230, &v24);
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_581;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_301;
          appendString_29(&v230, &v24);
          v234 = v230;
          v235 = v231;
          v24 = v230;
          v25 = v231;
          if ( v233 )
            ((void (__fastcall *)(__int64 *, __int64))v232)(&v24, v233);
          else
            ((void (__fastcall *)(__int64 *))v232)(&v24);
          if ( *v354 )
            goto LABEL_416;
          v304 = 394i64;
          v305 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v235 && (*v235 & 0x4000000000000000i64) == 0 )
            deallocShared(v235);
        }
LABEL_137:
        v304 = 324i64;
        v305 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        if ( (_BYTE)v315 == 1 )
        {
          v228 = 0i64;
          v229 = 0i64;
          v226 = 0i64;
          v227 = 0i64;
          v224 = 0i64;
          v225 = 0i64;
          v304 = 326i64;
          nimZeroMem_66(&v222, 16i64);
          v222 = add_line__modelZsimulationZcode95gen_u2131;
          v223 = v353;
          v220 = 0i64;
          v221 = 0i64;
          rawNewString(&v24, v325 + 10);
          v220 = v24;
          v221 = v25;
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_584;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_583;
          appendString_29(&v220, &v24);
          v24 = v325;
          v25 = v326;
          appendString_29(&v220, &v24);
          v24 = TM__THWBxVSaWN2Zh7OMooFH0w_586;
          v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_585;
          appendString_29(&v220, &v24);
          v228 = v220;
          v229 = v221;
          v24 = v220;
          v25 = v221;
          if ( v223 )
            ((void (__fastcall *)(__int64 *, __int64))v222)(&v24, v223);
          else
            ((void (__fastcall *)(__int64 *))v222)(&v24);
          if ( !*v354 )
          {
            v304 = 327i64;
            nimZeroMem_66(&v218, 16i64);
            v218 = add_line__modelZsimulationZcode95gen_u2131;
            v219 = v353;
            v216 = 0i64;
            v217 = 0i64;
            rawNewString(&v24, v335 + v331 + v327 + v28 + 14);
            v216 = v24;
            v217 = v25;
            v24 = TM__THWBxVSaWN2Zh7OMooFH0w_589;
            v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_588;
            appendString_29(&v216, &v24);
            v24 = v327;
            v25 = v328;
            appendString_29(&v216, &v24);
            v24 = TM__THWBxVSaWN2Zh7OMooFH0w_591;
            v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_590;
            appendString_29(&v216, &v24);
            v24 = v331;
            v25 = v332;
            appendString_29(&v216, &v24);
            v24 = TM__THWBxVSaWN2Zh7OMooFH0w_592;
            v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_348;
            appendString_29(&v216, &v24);
            v24 = v335;
            v25 = v336;
            appendString_29(&v216, &v24);
            v24 = TM__THWBxVSaWN2Zh7OMooFH0w_594;
            v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_593;
            appendString_29(&v216, &v24);
            v24 = v28;
            v25 = v29;
            appendString_29(&v216, &v24);
            v24 = TM__THWBxVSaWN2Zh7OMooFH0w_595;
            v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_307;
            appendString_29(&v216, &v24);
            v226 = v216;
            v227 = v217;
            v24 = v216;
            v25 = v217;
            if ( v219 )
              ((void (__fastcall *)(__int64 *, __int64))v218)(&v24, v219);
            else
              ((void (__fastcall *)(__int64 *))v218)(&v24);
            if ( !*v354 )
            {
              v304 = 328i64;
              nimZeroMem_66(&v214, 16i64);
              v214 = add_line__modelZsimulationZcode95gen_u2131;
              v215 = v353;
              v212 = 0i64;
              v213 = 0i64;
              rawNewString(&v24, v335 + v331 + v327 + v28 + 23);
              v212 = v24;
              v213 = v25;
              v24 = TM__THWBxVSaWN2Zh7OMooFH0w_598;
              v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_597;
              appendString_29(&v212, &v24);
              v24 = v327;
              v25 = v328;
              appendString_29(&v212, &v24);
              v24 = TM__THWBxVSaWN2Zh7OMooFH0w_600;
              v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_599;
              appendString_29(&v212, &v24);
              v24 = v331;
              v25 = v332;
              appendString_29(&v212, &v24);
              v24 = TM__THWBxVSaWN2Zh7OMooFH0w_601;
              v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_348;
              appendString_29(&v212, &v24);
              v24 = v335;
              v25 = v336;
              appendString_29(&v212, &v24);
              v24 = TM__THWBxVSaWN2Zh7OMooFH0w_602;
              v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_593;
              appendString_29(&v212, &v24);
              v24 = v28;
              v25 = v29;
              appendString_29(&v212, &v24);
              v24 = TM__THWBxVSaWN2Zh7OMooFH0w_603;
              v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_307;
              appendString_29(&v212, &v24);
              v224 = v212;
              v225 = v213;
              v24 = v212;
              v25 = v213;
              if ( v215 )
                ((void (__fastcall *)(__int64 *, __int64))v214)(&v24, v215);
              else
                ((void (__fastcall *)(__int64 *))v214)(&v24);
              if ( !*v354 )
              {
                v304 = 329i64;
                nimZeroMem_66(&v210, 16i64);
                v210 = add_line__modelZsimulationZcode95gen_u2131;
                v211 = v353;
                v24 = TM__THWBxVSaWN2Zh7OMooFH0w_606;
                v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_605;
                if ( v353 )
                  ((void (__fastcall *)(__int64 *, __int64))v210)(&v24, v211);
                else
                  ((void (__fastcall *)(__int64 *))v210)(&v24);
                if ( !*v354 )
                {
                  v304 = 394i64;
                  v305 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                  if ( v225 && (*v225 & 0x4000000000000000i64) == 0 )
                    deallocShared(v225);
                  if ( v227 && (*v227 & 0x4000000000000000i64) == 0 )
                    deallocShared(v227);
                  if ( v229 && (*v229 & 0x4000000000000000i64) == 0 )
                    deallocShared(v229);
                }
              }
            }
          }
        }
        else
        {
          v304 = 332i64;
          v305 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
          if ( !v345 )
          {
            v208 = 0i64;
            v209 = 0i64;
            v304 = 333i64;
            nimZeroMem_66(&v206, 16i64);
            v206 = add_line__modelZsimulationZcode95gen_u2131;
            v207 = v353;
            v204 = 0i64;
            v205 = 0i64;
            rawNewString(&v24, v335 + v327 + v28 + 4);
            v204 = v24;
            v205 = v25;
            v24 = TM__THWBxVSaWN2Zh7OMooFH0w_609;
            v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_608;
            appendString_29(&v204, &v24);
            v24 = v327;
            v25 = v328;
            appendString_29(&v204, &v24);
            v24 = TM__THWBxVSaWN2Zh7OMooFH0w_610;
            v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_550;
            appendString_29(&v204, &v24);
            v24 = v335;
            v25 = v336;
            appendString_29(&v204, &v24);
            v24 = v28;
            v25 = v29;
            appendString_29(&v204, &v24);
            v24 = TM__THWBxVSaWN2Zh7OMooFH0w_611;
            v25 = &TM__THWBxVSaWN2Zh7OMooFH0w_301;
            appendString_29(&v204, &v24);
            v208 = v204;
            v209 = v205;
            v24 = v204;
            v25 = v205;
            if ( v207 )
              ((void (__fastcall *)(__int64 *, __int64))v206)(&v24, v207);
            else
              ((void (__fastcall *)(__int64 *))v206)(&v24);
            if ( !*v354 )
            {
              v304 = 394i64;
              v305 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              if ( v209 )
              {
                if ( (*v209 & 0x4000000000000000i64) == 0 )
                  deallocShared(v209);
              }
            }
          }
        }
      }
    }
  }
LABEL_416:
  if ( v328 && (*v328 & 0x4000000000000000i64) == 0 )
    deallocShared(v328);
  if ( v330 && (*v330 & 0x4000000000000000i64) == 0 )
    deallocShared(v330);
  if ( v332 && (*v332 & 0x4000000000000000i64) == 0 )
    deallocShared(v332);
  if ( v334 && (*v334 & 0x4000000000000000i64) == 0 )
    deallocShared(v334);
  if ( v336 && (*v336 & 0x4000000000000000i64) == 0 )
    deallocShared(v336);
  return popFrame_88();
}


/* call 0x000000014043e06c, caller load_and_output__modelZsimulationZcode95gen_u3940 @ 0x000000014043df90 */

__int64 __fastcall load_and_output__modelZsimulationZcode95gen_u3940(
        __int64 a1,
        __int64 a2,
        __int64 a3,
        __int64 *a4,
        __int64 a5)
{
  __int64 v5; // rdx
  __int64 v6; // rdx
  __int64 v7; // rdx
  __int64 v8; // rdx
  __int64 v10[2]; // [rsp+30h] [rbp-50h] BYREF
  __int64 v11; // [rsp+40h] [rbp-40h] BYREF
  _QWORD *v12; // [rsp+48h] [rbp-38h]
  __int64 v13; // [rsp+50h] [rbp-30h] BYREF
  __int64 v14; // [rsp+58h] [rbp-28h]
  __int64 v15; // [rsp+60h] [rbp-20h]
  __int64 v16; // [rsp+70h] [rbp-10h]
  __int64 v17; // [rsp+78h] [rbp-8h]
  __int64 v18; // [rsp+80h] [rbp+0h] BYREF
  _QWORD *v19; // [rsp+88h] [rbp+8h]
  __int64 (__fastcall *v20)(); // [rsp+90h] [rbp+10h] BYREF
  __int64 v21; // [rsp+98h] [rbp+18h]
  __int64 v22; // [rsp+A0h] [rbp+20h] BYREF
  _QWORD *v23; // [rsp+A8h] [rbp+28h]
  __int64 (__fastcall *v24)(); // [rsp+B0h] [rbp+30h] BYREF
  __int64 v25; // [rsp+B8h] [rbp+38h]
  __int64 v26; // [rsp+C0h] [rbp+40h] BYREF
  _QWORD *v27; // [rsp+C8h] [rbp+48h]
  __int64 v28; // [rsp+D0h] [rbp+50h]
  _QWORD *v29; // [rsp+D8h] [rbp+58h]
  __int64 v30; // [rsp+E0h] [rbp+60h] BYREF
  _QWORD *v31; // [rsp+E8h] [rbp+68h]
  __int64 v32; // [rsp+F0h] [rbp+70h]
  _QWORD *v33; // [rsp+F8h] [rbp+78h]
  __int64 v34; // [rsp+100h] [rbp+80h] BYREF
  _QWORD *v35; // [rsp+108h] [rbp+88h]
  __int64 v36; // [rsp+110h] [rbp+90h] BYREF
  _QWORD *v37; // [rsp+118h] [rbp+98h]
  __int64 v38; // [rsp+120h] [rbp+A0h] BYREF
  _QWORD *v39; // [rsp+128h] [rbp+A8h]
  __int64 v40; // [rsp+130h] [rbp+B0h] BYREF
  _QWORD *v41; // [rsp+138h] [rbp+B8h]
  __int64 v42; // [rsp+140h] [rbp+C0h] BYREF
  _QWORD *v43; // [rsp+148h] [rbp+C8h]
  __int64 v44; // [rsp+150h] [rbp+D0h] BYREF
  _QWORD *v45; // [rsp+158h] [rbp+D8h]
  char v46[8]; // [rsp+160h] [rbp+E0h] BYREF
  const char *v47; // [rsp+168h] [rbp+E8h]
  __int64 v48; // [rsp+170h] [rbp+F0h]
  const char *v49; // [rsp+178h] [rbp+F8h]
  __int16 v50; // [rsp+180h] [rbp+100h]
  void (__fastcall *v51)(__int64, __int64, __int64, __int64 *, __int64 *); // [rsp+190h] [rbp+110h] BYREF
  __int64 v52; // [rsp+198h] [rbp+118h]
  __int64 output_word_size__modelZboardZprototype95list_u4333; // [rsp+1A8h] [rbp+128h]
  __int64 v54; // [rsp+1B0h] [rbp+130h]
  _QWORD *v55; // [rsp+1B8h] [rbp+138h]
  __int64 v56; // [rsp+1C8h] [rbp+148h]
  __int64 v57; // [rsp+1D0h] [rbp+150h]
  __int64 state_index__modelZsave95mongerZcommon_u5502; // [rsp+1D8h] [rbp+158h]
  __int64 v59; // [rsp+1E0h] [rbp+160h]
  _BYTE *v60; // [rsp+1E8h] [rbp+168h]

  v5 = a4[1];
  v16 = *a4;
  v17 = v5;
  v47 = "load_and_output";
  v49 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v48 = 0i64;
  v50 = 0;
  nimFrame_88(v46);
  v60 = (_BYTE *)nimErrorFlag_86();
  v59 = a5;
  v54 = 0i64;
  v55 = 0i64;
  v48 = 378i64;
  output_word_size__modelZboardZprototype95list_u4333 = get_output_word_size__modelZboardZprototype95list_u4333(
                                                          *(_BYTE *)a1,
                                                          a3,
                                                          *(_QWORD *)(a1 + 224));
  if ( !*v60 )
  {
    v48 = 379i64;
    if ( output_word_size__modelZboardZprototype95list_u4333 <= 0 )
    {
      v48 = 394i64;
      v49 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v55 && (*v55 & 0x4000000000000000i64) == 0 )
        deallocShared(v55);
      return popFrame_88();
    }
    v48 = 382i64;
    v49 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( *(_BYTE *)(v59 + 24) == 1 )
    {
      v44 = 0i64;
      v45 = 0i64;
      v42 = 0i64;
      v43 = 0i64;
      v48 = 383i64;
      v40 = 0i64;
      v41 = 0i64;
      dollar___modelZsave95mongerZcommon_u260(&v44, output_word_size__modelZboardZprototype95list_u4333);
      if ( !*v60 )
      {
        state_index__modelZsave95mongerZcommon_u5502 = 0i64;
        v6 = *(_QWORD *)(a1 + 120);
        v13 = *(_QWORD *)(a1 + 112);
        v14 = v6;
        v15 = *(_QWORD *)(a1 + 128);
        state_index__modelZsave95mongerZcommon_u5502 = get_state_index__modelZsave95mongerZcommon_u5502(&v13, 0i64);
        if ( !*v60 )
        {
          dollar___systemZdollars_u14(&v42, state_index__modelZsave95mongerZcommon_u5502);
          if ( !*v60 )
          {
            rawNewString(&v11, v44 + v42 + 31);
            v40 = v11;
            v41 = v12;
            v11 = TM__THWBxVSaWN2Zh7OMooFH0w_918;
            v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_327;
            appendString_29(&v40, &v11);
            v11 = v44;
            v12 = v45;
            appendString_29(&v40, &v11);
            v11 = TM__THWBxVSaWN2Zh7OMooFH0w_919;
            v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_305;
            appendString_29(&v40, &v11);
            v11 = v42;
            v12 = v43;
            appendString_29(&v40, &v11);
            v11 = TM__THWBxVSaWN2Zh7OMooFH0w_920;
            v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_325;
            appendString_29(&v40, &v11);
            v54 = v40;
            v55 = v41;
            v48 = 394i64;
            v49 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v43 && (*v43 & 0x4000000000000000i64) == 0 )
              deallocShared(v43);
            if ( v45 && (*v45 & 0x4000000000000000i64) == 0 )
              deallocShared(v45);
LABEL_48:
            v48 = 389i64;
            v49 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
            nimZeroMem_66(&v51, 16i64);
            v51 = (void (__fastcall *)(__int64, __int64, __int64, __int64 *, __int64 *))store_output__modelZsimulationZcode95gen_u2221;
            v52 = v59;
            v11 = v54;
            v12 = v55;
            v10[0] = v16;
            v10[1] = v17;
            if ( v59 )
              ((void (__fastcall *)(__int64, __int64, __int64, __int64 *, __int64 *, __int64))v51)(
                a1,
                a2,
                a3,
                &v11,
                v10,
                v52);
            else
              v51(a1, a2, a3, &v11, v10);
          }
        }
      }
    }
    else
    {
      v38 = 0i64;
      v39 = 0i64;
      v36 = 0i64;
      v37 = 0i64;
      v34 = 0i64;
      v35 = 0i64;
      v32 = 0i64;
      v33 = 0i64;
      v30 = 0i64;
      v31 = 0i64;
      v28 = 0i64;
      v29 = 0i64;
      v48 = 385i64;
      v49 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v26 = 0i64;
      v27 = 0i64;
      dollar___systemZdollars_u14(&v38, a2);
      if ( !*v60 )
      {
        rawNewString(&v11, v38 + 6);
        v26 = v11;
        v27 = v12;
        v11 = TM__THWBxVSaWN2Zh7OMooFH0w_921;
        v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_706;
        appendString_29(&v26, &v11);
        v11 = v38;
        v12 = v39;
        appendString_29(&v26, &v11);
        v54 = v26;
        v55 = v27;
        v48 = 386i64;
        nimZeroMem_66(&v24, 16i64);
        v24 = add_line__modelZsimulationZcode95gen_u2131;
        v25 = v59;
        v22 = 0i64;
        v23 = 0i64;
        dollar___modelZsave95mongerZcommon_u260(&v36, output_word_size__modelZboardZprototype95list_u4333);
        if ( !*v60 )
        {
          v57 = 0i64;
          v7 = *(_QWORD *)(a1 + 96);
          v13 = *(_QWORD *)(a1 + 88);
          v14 = v7;
          v15 = *(_QWORD *)(a1 + 104);
          v57 = get_state_index__modelZsave95mongerZcommon_u5502(&v13, 0i64);
          if ( !*v60 )
          {
            dollar___systemZdollars_u14(&v34, v57);
            if ( !*v60 )
            {
              rawNewString(&v11, v36 + v54 + v34 + 38);
              v22 = v11;
              v23 = v12;
              v11 = TM__THWBxVSaWN2Zh7OMooFH0w_922;
              v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_708;
              appendString_29(&v22, &v11);
              v11 = v54;
              v12 = v55;
              appendString_29(&v22, &v11);
              v11 = TM__THWBxVSaWN2Zh7OMooFH0w_924;
              v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_923;
              appendString_29(&v22, &v11);
              v11 = v36;
              v12 = v37;
              appendString_29(&v22, &v11);
              v11 = TM__THWBxVSaWN2Zh7OMooFH0w_925;
              v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_305;
              appendString_29(&v22, &v11);
              v11 = v34;
              v12 = v35;
              appendString_29(&v22, &v11);
              v11 = TM__THWBxVSaWN2Zh7OMooFH0w_926;
              v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_325;
              appendString_29(&v22, &v11);
              v32 = v22;
              v33 = v23;
              v11 = v22;
              v12 = v23;
              if ( v25 )
                ((void (__fastcall *)(__int64 *, __int64))v24)(&v11, v25);
              else
                ((void (__fastcall *)(__int64 *))v24)(&v11);
              if ( !*v60 )
              {
                v48 = 387i64;
                nimZeroMem_66(&v20, 16i64);
                v20 = add_line__modelZsimulationZcode95gen_u2131;
                v21 = v59;
                v18 = 0i64;
                v19 = 0i64;
                v56 = 0i64;
                v8 = *(_QWORD *)(a1 + 120);
                v13 = *(_QWORD *)(a1 + 112);
                v14 = v8;
                v15 = *(_QWORD *)(a1 + 128);
                v56 = get_state_index__modelZsave95mongerZcommon_u5502(&v13, 0i64);
                if ( !*v60 )
                {
                  dollar___systemZdollars_u14(&v30, v56);
                  if ( !*v60 )
                  {
                    rawNewString(&v11, v30 + v54 + 45);
                    v18 = v11;
                    v19 = v12;
                    v11 = TM__THWBxVSaWN2Zh7OMooFH0w_928;
                    v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_536;
                    appendString_29(&v18, &v11);
                    v11 = v30;
                    v12 = v31;
                    appendString_29(&v18, &v11);
                    v11 = TM__THWBxVSaWN2Zh7OMooFH0w_929;
                    v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_41;
                    appendString_29(&v18, &v11);
                    v11 = v54;
                    v12 = v55;
                    appendString_29(&v18, &v11);
                    v11 = TM__THWBxVSaWN2Zh7OMooFH0w_931;
                    v12 = &TM__THWBxVSaWN2Zh7OMooFH0w_930;
                    appendString_29(&v18, &v11);
                    v28 = v18;
                    v29 = v19;
                    v11 = v18;
                    v12 = v19;
                    if ( v21 )
                      ((void (__fastcall *)(__int64 *, __int64))v20)(&v11, v21);
                    else
                      ((void (__fastcall *)(__int64 *))v20)(&v11);
                    if ( !*v60 )
                    {
                      v48 = 394i64;
                      v49 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                      if ( v29 && (*v29 & 0x4000000000000000i64) == 0 )
                        deallocShared(v29);
                      if ( v31 && (*v31 & 0x4000000000000000i64) == 0 )
                        deallocShared(v31);
                      if ( v33 && (*v33 & 0x4000000000000000i64) == 0 )
                        deallocShared(v33);
                      if ( v35 && (*v35 & 0x4000000000000000i64) == 0 )
                        deallocShared(v35);
                      if ( v37 && (*v37 & 0x4000000000000000i64) == 0 )
                        deallocShared(v37);
                      if ( v39 && (*v39 & 0x4000000000000000i64) == 0 )
                        deallocShared(v39);
                      goto LABEL_48;
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
  v48 = 394i64;
  v49 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v55 && (*v55 & 0x4000000000000000i64) == 0 )
    deallocShared(v55);
  return popFrame_88();
}


/* call 0x000000014043f7db, caller store_word__modelZsimulationZcode95gen_u2201 @ 0x000000014043f4c0 */

__int64 __fastcall store_word__modelZsimulationZcode95gen_u2201(
        __int64 *a1,
        __int64 a2,
        unsigned __int16 a3,
        __int64 *a4,
        __int64 a5)
{
  __int64 v5; // rbx
  __int64 v6; // rdx
  __int64 v7; // rdx
  __int64 v9; // [rsp+20h] [rbp-60h] BYREF
  _QWORD *v10; // [rsp+28h] [rbp-58h]
  __int64 v11; // [rsp+30h] [rbp-50h] BYREF
  __int64 v12; // [rsp+38h] [rbp-48h]
  __int64 v13; // [rsp+40h] [rbp-40h]
  __int64 v14[4]; // [rsp+50h] [rbp-30h] BYREF
  __int64 v15; // [rsp+70h] [rbp-10h]
  _QWORD *v16; // [rsp+78h] [rbp-8h]
  __int64 v17; // [rsp+80h] [rbp+0h]
  __int64 v18; // [rsp+88h] [rbp+8h]
  char v19[8]; // [rsp+90h] [rbp+10h] BYREF
  const char *v20; // [rsp+98h] [rbp+18h]
  __int64 v21; // [rsp+A0h] [rbp+20h]
  const char *v22; // [rsp+A8h] [rbp+28h]
  __int16 v23; // [rsp+B0h] [rbp+30h]
  __int64 v24; // [rsp+C0h] [rbp+40h] BYREF
  _QWORD *v25; // [rsp+C8h] [rbp+48h]
  __int64 (__fastcall *v26)(); // [rsp+D0h] [rbp+50h] BYREF
  __int64 v27; // [rsp+D8h] [rbp+58h]
  __int64 output_word_size__modelZboardZprototype95list_u4333; // [rsp+E8h] [rbp+68h]
  __int64 v29; // [rsp+F0h] [rbp+70h]
  _QWORD *v30; // [rsp+F8h] [rbp+78h]
  __int64 v31; // [rsp+100h] [rbp+80h] BYREF
  _QWORD *v32; // [rsp+108h] [rbp+88h]
  __int64 v33; // [rsp+110h] [rbp+90h] BYREF
  _QWORD *v34; // [rsp+118h] [rbp+98h]
  __int64 v35[70]; // [rsp+120h] [rbp+A0h] BYREF
  __int64 state_index__modelZsave95mongerZcommon_u5502; // [rsp+350h] [rbp+2D0h]
  char v37; // [rsp+35Fh] [rbp+2DFh]
  __int64 v38; // [rsp+360h] [rbp+2E0h]
  _BYTE *v39; // [rsp+368h] [rbp+2E8h]

  v5 = a1[1];
  v17 = *a1;
  v18 = v5;
  v6 = a4[1];
  v15 = *a4;
  v16 = (_QWORD *)v6;
  v20 = "store_word";
  v22 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v21 = 0i64;
  v23 = 0;
  nimFrame_88(v19);
  v39 = (_BYTE *)nimErrorFlag_86();
  v38 = a5;
  nimZeroMem_66(v35, 560i64);
  v33 = 0i64;
  v34 = 0i64;
  v31 = 0i64;
  v32 = 0i64;
  v29 = 0i64;
  v30 = 0i64;
  v21 = 239i64;
  v22 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  if ( *(_BYTE *)(v38 + 24) == 1 )
  {
    v21 = 394i64;
    v22 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    return popFrame_88();
  }
  v21 = 241i64;
  v22 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  if ( a2 >= 0 && a2 < v17 )
  {
    qmemcpy(v35, (const void *)(560 * a2 + v18 + 8), sizeof(v35));
    v21 = 243i64;
    v37 = 0;
    v14[0] = v35[11];
    v14[1] = v35[12];
    v14[2] = v35[13];
    v7 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 1);
    v11 = *(_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435;
    v12 = v7;
    v13 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 2);
    v37 = eqeq___modelZsimulationZcontroller_u106(v14, &v11);
    if ( v37 != 1
      || (v9 = TM__THWBxVSaWN2Zh7OMooFH0w_949,
          v10 = &TM__THWBxVSaWN2Zh7OMooFH0w_948,
          failedAssertImpl__stdZassertions_u234(&v9),
          !*v39) )
    {
      v21 = 245i64;
      output_word_size__modelZboardZprototype95list_u4333 = get_output_word_size__modelZboardZprototype95list_u4333(
                                                              v35[0],
                                                              a3,
                                                              v35[28]);
      if ( !*v39 )
      {
        v21 = 246i64;
        if ( output_word_size__modelZboardZprototype95list_u4333 <= 0 )
        {
          v21 = 394i64;
          v22 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v30 && (*v30 & 0x4000000000000000i64) == 0 )
            deallocShared(v30);
          if ( v32 && (*v32 & 0x4000000000000000i64) == 0 )
            deallocShared(v32);
          if ( v34 && (*v34 & 0x4000000000000000i64) == 0 )
            goto LABEL_33;
          return popFrame_88();
        }
        v21 = 248i64;
        v22 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        nimZeroMem_66(&v26, 16i64);
        v26 = add_line__modelZsimulationZcode95gen_u2131;
        v27 = v38;
        v24 = 0i64;
        v25 = 0i64;
        state_index__modelZsave95mongerZcommon_u5502 = 0i64;
        v11 = v35[11];
        v12 = v35[12];
        v13 = v35[13];
        state_index__modelZsave95mongerZcommon_u5502 = get_state_index__modelZsave95mongerZcommon_u5502(&v11, 0i64);
        if ( !*v39 )
        {
          dollar___systemZdollars_u14(&v33, state_index__modelZsave95mongerZcommon_u5502);
          if ( !*v39 )
          {
            dollar___modelZsave95mongerZcommon_u260(&v31, output_word_size__modelZboardZprototype95list_u4333);
            if ( !*v39 )
            {
              rawNewString(&v9, v31 + v33 + v15 + 33);
              v24 = v9;
              v25 = v10;
              v9 = TM__THWBxVSaWN2Zh7OMooFH0w_950;
              v10 = &TM__THWBxVSaWN2Zh7OMooFH0w_536;
              appendString_29(&v24, &v9);
              v9 = v33;
              v10 = v34;
              appendString_29(&v24, &v9);
              v9 = TM__THWBxVSaWN2Zh7OMooFH0w_952;
              v10 = &TM__THWBxVSaWN2Zh7OMooFH0w_951;
              appendString_29(&v24, &v9);
              v9 = v31;
              v10 = v32;
              appendString_29(&v24, &v9);
              v9 = TM__THWBxVSaWN2Zh7OMooFH0w_953;
              v10 = &TM__THWBxVSaWN2Zh7OMooFH0w_348;
              appendString_29(&v24, &v9);
              v9 = v15;
              v10 = v16;
              appendString_29(&v24, &v9);
              v9 = TM__THWBxVSaWN2Zh7OMooFH0w_954;
              v10 = &TM__THWBxVSaWN2Zh7OMooFH0w_307;
              appendString_29(&v24, &v9);
              v29 = v24;
              v30 = v25;
              v9 = v24;
              v10 = v25;
              if ( v27 )
                ((void (__fastcall *)(__int64 *, __int64))v26)(&v9, v27);
              else
                ((void (__fastcall *)(__int64 *))v26)(&v9);
            }
          }
        }
      }
    }
  }
  else
  {
    raiseIndexError2(a2, v17 - 1);
  }
  v21 = 394i64;
  v22 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v30 && (*v30 & 0x4000000000000000i64) == 0 )
    deallocShared(v30);
  if ( v32 && (*v32 & 0x4000000000000000i64) == 0 )
    deallocShared(v32);
  if ( v34 && (*v34 & 0x4000000000000000i64) == 0 )
LABEL_33:
    deallocShared(v34);
  return popFrame_88();
}


/* call 0x000000014049b876, caller generate_source @ 0x000000014048b0bd */

_QWORD *__fastcall generate_source(
        _QWORD *a1,
        __int64 *a2,
        __int64 a3,
        __int64 *a4,
        __int64 *a5,
        int a6,
        __int64 *a7,
        __int64 a8,
        __int64 a9,
        __int64 *a10)
{
  __int64 v10; // rax
  __int64 v11; // rdx
  __int64 v12; // rdx
  __int64 v13; // rdx
  __int64 v14; // rdx
  __int64 v15; // rdx
  __int64 v16; // rdx
  __int64 v17; // rdx
  __int64 v18; // r10
  __int64 v19; // r10
  __int64 v20; // r10
  _QWORD *v21; // rax
  __int64 v22; // rbx
  __int64 v23; // rbx
  __int64 v24; // rbx
  __int64 v25; // rbx
  __int64 v26; // rdx
  __int64 v27; // rdx
  __int64 v28; // rax
  char v29; // dl
  bool v30; // of
  __int64 v31; // rax
  __int64 v32; // rdx
  bool v33; // dl
  __int64 v34; // r10
  __int64 v35; // r10
  __int64 v36; // rdx
  int v37; // eax
  __int64 v38; // rdx
  __int64 v39; // rdx
  __int64 v40; // rdx
  __int64 v41; // rax
  __int64 v42; // rdx
  __int64 v43; // rdx
  __int64 v44; // rdx
  __int64 v45; // rdx
  int v46; // eax
  __int64 v47; // rdx
  int v48; // eax
  __int64 v49; // rdx
  int v50; // eax
  __int64 v51; // rdx
  int v52; // eax
  __int64 v53; // rdx
  __int64 v54; // rdx
  __int64 v55; // rdx
  int v56; // eax
  __int64 v57; // rdx
  __int64 v58; // rdx
  __int64 v59; // rdx
  __int64 v60; // rax
  __int64 v61; // rdx
  __int64 v62; // rdx
  __int64 v63; // rdx
  __int64 v64; // rcx
  int v65; // eax
  __int64 v66; // rdx
  char *v67; // rax
  __int64 v68; // rdx
  __int64 v69; // rdx
  __int64 v70; // rdx
  __int64 v71; // rdx
  __int64 v72; // rdx
  _QWORD *v73; // rax
  __int64 v74; // rbx
  __int64 v75; // rbx
  __int64 v76; // rbx
  __int64 v77; // rbx
  __int64 v78; // rdx
  __int64 v79; // rdx
  __int64 v80; // rdx
  bool v81; // cl
  __int64 v82; // rdx
  char *v83; // rcx
  __int64 v84; // rax
  __int64 v85; // rdx
  _QWORD *v86; // rcx
  __int64 v87; // rdx
  __int64 v88; // rcx
  __int64 v89; // rdx
  __int64 v90; // rdx
  __int64 v91; // rax
  __int64 v92; // rdx
  __int64 v93; // rdx
  __int64 v94; // rdx
  __int64 v96; // [rsp+30h] [rbp-50h] BYREF
  char *v97; // [rsp+38h] [rbp-48h]
  __int64 v98; // [rsp+40h] [rbp-40h] BYREF
  char *v99; // [rsp+48h] [rbp-38h]
  __int64 v100; // [rsp+50h] [rbp-30h] BYREF
  __int64 v101; // [rsp+58h] [rbp-28h]
  __int64 v102; // [rsp+60h] [rbp-20h]
  __int64 v103; // [rsp+70h] [rbp-10h] BYREF
  __int64 v104; // [rsp+78h] [rbp-8h]
  __int64 v105; // [rsp+80h] [rbp+0h]
  __int64 v106; // [rsp+90h] [rbp+10h] BYREF
  __int64 v107; // [rsp+98h] [rbp+18h]
  __int64 v108; // [rsp+A0h] [rbp+20h]
  __int64 v109; // [rsp+A8h] [rbp+28h]
  __int64 v110; // [rsp+B0h] [rbp+30h]
  __int64 v111; // [rsp+B8h] [rbp+38h]
  __int64 v112; // [rsp+C0h] [rbp+40h]
  __int64 v113; // [rsp+C8h] [rbp+48h]
  __int64 v114; // [rsp+D0h] [rbp+50h]
  char *v115; // [rsp+D8h] [rbp+58h]
  __int64 v116; // [rsp+E0h] [rbp+60h]
  __int64 v117; // [rsp+E8h] [rbp+68h]
  __int64 v118; // [rsp+F0h] [rbp+70h] BYREF
  __int64 v119; // [rsp+F8h] [rbp+78h]
  __int64 v120; // [rsp+100h] [rbp+80h]
  __int64 v121; // [rsp+108h] [rbp+88h]
  __int64 v122; // [rsp+110h] [rbp+90h]
  __int64 v123; // [rsp+118h] [rbp+98h]
  __int64 v124; // [rsp+120h] [rbp+A0h]
  __int64 v125; // [rsp+128h] [rbp+A8h]
  __int64 v126; // [rsp+130h] [rbp+B0h]
  __int64 v127; // [rsp+138h] [rbp+B8h]
  __int64 v128[70]; // [rsp+140h] [rbp+C0h] BYREF
  __int64 v129; // [rsp+370h] [rbp+2F0h] BYREF
  _QWORD *v130; // [rsp+378h] [rbp+2F8h]
  __int64 v131; // [rsp+380h] [rbp+300h] BYREF
  _QWORD *v132; // [rsp+388h] [rbp+308h]
  unsigned __int64 v133; // [rsp+398h] [rbp+318h]
  __int64 v134; // [rsp+3A0h] [rbp+320h] BYREF
  _QWORD *v135; // [rsp+3A8h] [rbp+328h]
  __int64 v136; // [rsp+3B0h] [rbp+330h]
  _QWORD *v137; // [rsp+3B8h] [rbp+338h]
  __int64 v138; // [rsp+3C0h] [rbp+340h] BYREF
  _QWORD *v139; // [rsp+3C8h] [rbp+348h]
  __int64 v140; // [rsp+3D0h] [rbp+350h]
  _QWORD *v141; // [rsp+3D8h] [rbp+358h]
  __int64 v142; // [rsp+3E0h] [rbp+360h] BYREF
  _QWORD *v143; // [rsp+3E8h] [rbp+368h]
  __int64 v144; // [rsp+3F0h] [rbp+370h]
  _QWORD *v145; // [rsp+3F8h] [rbp+378h]
  __int64 v146; // [rsp+400h] [rbp+380h] BYREF
  _QWORD *v147; // [rsp+408h] [rbp+388h]
  __int64 v148; // [rsp+410h] [rbp+390h] BYREF
  _QWORD *v149; // [rsp+418h] [rbp+398h]
  __int64 v150; // [rsp+420h] [rbp+3A0h] BYREF
  _QWORD *v151; // [rsp+428h] [rbp+3A8h]
  __int64 v152; // [rsp+430h] [rbp+3B0h] BYREF
  _QWORD *v153; // [rsp+438h] [rbp+3B8h]
  __int64 (__fastcall *v154)(); // [rsp+440h] [rbp+3C0h] BYREF
  _QWORD *v155; // [rsp+448h] [rbp+3C8h]
  __int64 v156; // [rsp+450h] [rbp+3D0h] BYREF
  _QWORD *v157; // [rsp+458h] [rbp+3D8h]
  __int64 (__fastcall *v158)(); // [rsp+460h] [rbp+3E0h] BYREF
  _QWORD *v159; // [rsp+468h] [rbp+3E8h]
  __int64 (__fastcall *v160)(); // [rsp+470h] [rbp+3F0h] BYREF
  _QWORD *v161; // [rsp+478h] [rbp+3F8h]
  __int64 (__fastcall *v162)(); // [rsp+480h] [rbp+400h] BYREF
  _QWORD *v163; // [rsp+488h] [rbp+408h]
  __int64 (__fastcall *v164)(); // [rsp+490h] [rbp+410h] BYREF
  _QWORD *v165; // [rsp+498h] [rbp+418h]
  __int64 v166; // [rsp+4A0h] [rbp+420h] BYREF
  _QWORD *v167; // [rsp+4A8h] [rbp+428h]
  __int64 (__fastcall *v168)(); // [rsp+4B0h] [rbp+430h] BYREF
  _QWORD *v169; // [rsp+4B8h] [rbp+438h]
  __int64 v170; // [rsp+4C0h] [rbp+440h] BYREF
  _QWORD *v171; // [rsp+4C8h] [rbp+448h]
  __int64 (__fastcall *v172)(); // [rsp+4D0h] [rbp+450h] BYREF
  _QWORD *v173; // [rsp+4D8h] [rbp+458h]
  __int64 v174; // [rsp+4E0h] [rbp+460h] BYREF
  _QWORD *v175; // [rsp+4E8h] [rbp+468h]
  __int64 (__fastcall *v176)(); // [rsp+4F0h] [rbp+470h] BYREF
  _QWORD *v177; // [rsp+4F8h] [rbp+478h]
  __int64 v178; // [rsp+500h] [rbp+480h] BYREF
  _QWORD *v179; // [rsp+508h] [rbp+488h]
  __int64 (__fastcall *v180)(); // [rsp+510h] [rbp+490h] BYREF
  _QWORD *v181; // [rsp+518h] [rbp+498h]
  __int64 v182; // [rsp+520h] [rbp+4A0h] BYREF
  _QWORD *v183; // [rsp+528h] [rbp+4A8h]
  __int64 (__fastcall *v184)(); // [rsp+530h] [rbp+4B0h] BYREF
  _QWORD *v185; // [rsp+538h] [rbp+4B8h]
  __int64 v186; // [rsp+540h] [rbp+4C0h] BYREF
  _QWORD *v187; // [rsp+548h] [rbp+4C8h]
  __int64 v188; // [rsp+550h] [rbp+4D0h] BYREF
  _QWORD *v189; // [rsp+558h] [rbp+4D8h]
  __int64 v190; // [rsp+560h] [rbp+4E0h] BYREF
  _QWORD *v191; // [rsp+568h] [rbp+4E8h]
  _QWORD *(__fastcall *v192)(__int64 *, __int64, __int64, __int64, unsigned __int8, __int64); // [rsp+570h] [rbp+4F0h] BYREF
  _QWORD *v193; // [rsp+578h] [rbp+4F8h]
  __int64 v194; // [rsp+580h] [rbp+500h] BYREF
  _QWORD *v195; // [rsp+588h] [rbp+508h]
  __int64 (__fastcall *v196)(); // [rsp+590h] [rbp+510h] BYREF
  _QWORD *v197; // [rsp+598h] [rbp+518h]
  __int64 v198; // [rsp+5A0h] [rbp+520h] BYREF
  _QWORD *v199; // [rsp+5A8h] [rbp+528h]
  __int64 v200; // [rsp+5B0h] [rbp+530h]
  _QWORD *v201; // [rsp+5B8h] [rbp+538h]
  __int64 v202; // [rsp+5C0h] [rbp+540h]
  _QWORD *v203; // [rsp+5C8h] [rbp+548h]
  __int64 v204; // [rsp+5D0h] [rbp+550h]
  _QWORD *v205; // [rsp+5D8h] [rbp+558h]
  __int64 v206; // [rsp+5E0h] [rbp+560h]
  _QWORD *v207; // [rsp+5E8h] [rbp+568h]
  __int64 v208; // [rsp+5F0h] [rbp+570h]
  _QWORD *v209; // [rsp+5F8h] [rbp+578h]
  __int64 v210; // [rsp+600h] [rbp+580h] BYREF
  _QWORD *v211; // [rsp+608h] [rbp+588h]
  __int64 v212; // [rsp+610h] [rbp+590h]
  _QWORD *v213; // [rsp+618h] [rbp+598h]
  __int64 v214; // [rsp+620h] [rbp+5A0h] BYREF
  _QWORD *v215; // [rsp+628h] [rbp+5A8h]
  __int64 v216; // [rsp+630h] [rbp+5B0h] BYREF
  _QWORD *v217; // [rsp+638h] [rbp+5B8h]
  __int64 v218; // [rsp+640h] [rbp+5C0h]
  _QWORD *v219; // [rsp+648h] [rbp+5C8h]
  __int64 v220; // [rsp+650h] [rbp+5D0h] BYREF
  _QWORD *v221; // [rsp+658h] [rbp+5D8h]
  __int64 v222; // [rsp+660h] [rbp+5E0h]
  _QWORD *v223; // [rsp+668h] [rbp+5E8h]
  __int64 v224; // [rsp+670h] [rbp+5F0h] BYREF
  _QWORD *v225; // [rsp+678h] [rbp+5F8h]
  __int64 v226; // [rsp+680h] [rbp+600h]
  _QWORD *v227; // [rsp+688h] [rbp+608h]
  __int64 v228; // [rsp+690h] [rbp+610h]
  _QWORD *v229; // [rsp+698h] [rbp+618h]
  __int64 v230; // [rsp+6A0h] [rbp+620h] BYREF
  _QWORD *v231; // [rsp+6A8h] [rbp+628h]
  __int64 v232; // [rsp+6B0h] [rbp+630h] BYREF
  _QWORD *v233; // [rsp+6B8h] [rbp+638h]
  __int64 v234; // [rsp+6C0h] [rbp+640h]
  _QWORD *v235; // [rsp+6C8h] [rbp+648h]
  __int64 v236; // [rsp+6D0h] [rbp+650h] BYREF
  _QWORD *v237; // [rsp+6D8h] [rbp+658h]
  __int64 v238; // [rsp+6E0h] [rbp+660h]
  _QWORD *v239; // [rsp+6E8h] [rbp+668h]
  __int64 v240; // [rsp+6F0h] [rbp+670h] BYREF
  _QWORD *v241; // [rsp+6F8h] [rbp+678h]
  __int64 v242; // [rsp+700h] [rbp+680h] BYREF
  _QWORD *v243; // [rsp+708h] [rbp+688h]
  __int64 v244; // [rsp+718h] [rbp+698h]
  __int64 v245; // [rsp+720h] [rbp+6A0h] BYREF
  __int64 v246; // [rsp+728h] [rbp+6A8h]
  __int64 v247; // [rsp+730h] [rbp+6B0h] BYREF
  __int64 v248; // [rsp+738h] [rbp+6B8h]
  __int64 v249; // [rsp+740h] [rbp+6C0h]
  __int64 v250; // [rsp+750h] [rbp+6D0h] BYREF
  _QWORD *v251; // [rsp+758h] [rbp+6D8h]
  __int64 v252; // [rsp+760h] [rbp+6E0h]
  _QWORD *v253; // [rsp+768h] [rbp+6E8h]
  __int64 v254; // [rsp+778h] [rbp+6F8h]
  __int64 v255; // [rsp+780h] [rbp+700h] BYREF
  _QWORD *v256; // [rsp+788h] [rbp+708h]
  __int64 v257; // [rsp+790h] [rbp+710h] BYREF
  _QWORD *v258; // [rsp+798h] [rbp+718h]
  __int64 v259; // [rsp+7A0h] [rbp+720h]
  _QWORD *v260; // [rsp+7A8h] [rbp+728h]
  __int64 v261; // [rsp+7B0h] [rbp+730h]
  _QWORD *v262; // [rsp+7B8h] [rbp+738h]
  __int64 v263; // [rsp+7C0h] [rbp+740h] BYREF
  _QWORD *v264; // [rsp+7C8h] [rbp+748h]
  __int64 v265; // [rsp+7D0h] [rbp+750h] BYREF
  _QWORD *v266; // [rsp+7D8h] [rbp+758h]
  __int64 v267; // [rsp+7E0h] [rbp+760h] BYREF
  _QWORD *v268; // [rsp+7E8h] [rbp+768h]
  __int64 v269; // [rsp+7F0h] [rbp+770h]
  _QWORD *v270; // [rsp+7F8h] [rbp+778h]
  __int64 v271; // [rsp+800h] [rbp+780h] BYREF
  _QWORD *v272; // [rsp+808h] [rbp+788h]
  __int64 v273; // [rsp+810h] [rbp+790h] BYREF
  __int64 v274; // [rsp+818h] [rbp+798h]
  __int64 v275; // [rsp+820h] [rbp+7A0h]
  _QWORD *v276; // [rsp+828h] [rbp+7A8h]
  __int64 v277; // [rsp+830h] [rbp+7B0h] BYREF
  _QWORD *v278; // [rsp+838h] [rbp+7B8h]
  __int64 v279; // [rsp+840h] [rbp+7C0h] BYREF
  _QWORD *v280; // [rsp+848h] [rbp+7C8h]
  __int64 v281; // [rsp+858h] [rbp+7D8h]
  __int64 v282; // [rsp+860h] [rbp+7E0h] BYREF
  _QWORD *v283; // [rsp+868h] [rbp+7E8h]
  __int64 v284; // [rsp+870h] [rbp+7F0h]
  _QWORD *v285; // [rsp+878h] [rbp+7F8h]
  __int64 v286; // [rsp+880h] [rbp+800h] BYREF
  _QWORD *v287; // [rsp+888h] [rbp+808h]
  __int64 v288; // [rsp+890h] [rbp+810h] BYREF
  _QWORD *v289; // [rsp+898h] [rbp+818h]
  __int64 v290; // [rsp+8A0h] [rbp+820h] BYREF
  _QWORD *v291; // [rsp+8A8h] [rbp+828h]
  __int64 v292; // [rsp+8B8h] [rbp+838h]
  __int64 v293; // [rsp+8C0h] [rbp+840h] BYREF
  _QWORD *v294; // [rsp+8C8h] [rbp+848h]
  __int64 v295; // [rsp+8D0h] [rbp+850h]
  _QWORD *v296; // [rsp+8D8h] [rbp+858h]
  __int64 v297; // [rsp+8E0h] [rbp+860h] BYREF
  _QWORD *v298; // [rsp+8E8h] [rbp+868h]
  __int64 v299; // [rsp+8F0h] [rbp+870h] BYREF
  _QWORD *v300; // [rsp+8F8h] [rbp+878h]
  __int64 v301; // [rsp+908h] [rbp+888h]
  __int64 v302; // [rsp+910h] [rbp+890h] BYREF
  _QWORD *v303; // [rsp+918h] [rbp+898h]
  __int64 v304; // [rsp+920h] [rbp+8A0h]
  _QWORD *v305; // [rsp+928h] [rbp+8A8h]
  __int64 v306; // [rsp+930h] [rbp+8B0h] BYREF
  _QWORD *v307; // [rsp+938h] [rbp+8B8h]
  __int64 v308; // [rsp+940h] [rbp+8C0h] BYREF
  _QWORD *v309; // [rsp+948h] [rbp+8C8h]
  __int64 v310; // [rsp+950h] [rbp+8D0h]
  _QWORD *v311; // [rsp+958h] [rbp+8D8h]
  __int64 v312; // [rsp+960h] [rbp+8E0h] BYREF
  _QWORD *v313; // [rsp+968h] [rbp+8E8h]
  __int64 v314; // [rsp+970h] [rbp+8F0h] BYREF
  _QWORD *v315; // [rsp+978h] [rbp+8F8h]
  __int64 v316; // [rsp+980h] [rbp+900h] BYREF
  _QWORD *v317; // [rsp+988h] [rbp+908h]
  __int64 v318; // [rsp+990h] [rbp+910h]
  _QWORD *v319; // [rsp+998h] [rbp+918h]
  __int64 v320; // [rsp+9A0h] [rbp+920h] BYREF
  _QWORD *v321; // [rsp+9A8h] [rbp+928h]
  __int64 v322; // [rsp+9B8h] [rbp+938h]
  __int64 v323; // [rsp+9C0h] [rbp+940h] BYREF
  _QWORD *v324; // [rsp+9C8h] [rbp+948h]
  __int64 v325; // [rsp+9D0h] [rbp+950h] BYREF
  _QWORD *v326; // [rsp+9D8h] [rbp+958h]
  __int64 v327; // [rsp+9E0h] [rbp+960h]
  _QWORD *v328; // [rsp+9E8h] [rbp+968h]
  __int64 v329; // [rsp+9F0h] [rbp+970h] BYREF
  _QWORD *v330; // [rsp+9F8h] [rbp+978h]
  __int64 v331; // [rsp+A00h] [rbp+980h] BYREF
  _QWORD *v332; // [rsp+A08h] [rbp+988h]
  __int64 v333; // [rsp+A10h] [rbp+990h] BYREF
  _QWORD *v334; // [rsp+A18h] [rbp+998h]
  __int64 v335; // [rsp+A20h] [rbp+9A0h]
  _QWORD *v336; // [rsp+A28h] [rbp+9A8h]
  __int64 v337; // [rsp+A30h] [rbp+9B0h] BYREF
  _QWORD *v338; // [rsp+A38h] [rbp+9B8h]
  __int64 v339; // [rsp+A48h] [rbp+9C8h]
  __int64 v340; // [rsp+A50h] [rbp+9D0h] BYREF
  _QWORD *v341; // [rsp+A58h] [rbp+9D8h]
  __int64 v342; // [rsp+A60h] [rbp+9E0h] BYREF
  _QWORD *v343; // [rsp+A68h] [rbp+9E8h]
  __int64 output_word_size__modelZboardZprototype95list_u4333; // [rsp+A78h] [rbp+9F8h]
  __int64 v345; // [rsp+A80h] [rbp+A00h]
  _QWORD *v346; // [rsp+A88h] [rbp+A08h]
  __int64 v347; // [rsp+A90h] [rbp+A10h] BYREF
  _QWORD *v348; // [rsp+A98h] [rbp+A18h]
  __int64 v349; // [rsp+AA0h] [rbp+A20h] BYREF
  _QWORD *v350; // [rsp+AA8h] [rbp+A28h]
  __int64 v351; // [rsp+AB0h] [rbp+A30h] BYREF
  _QWORD *v352; // [rsp+AB8h] [rbp+A38h]
  __int64 v353; // [rsp+AC0h] [rbp+A40h] BYREF
  _QWORD *v354; // [rsp+AC8h] [rbp+A48h]
  __int64 v355; // [rsp+AD0h] [rbp+A50h]
  _QWORD *v356; // [rsp+AD8h] [rbp+A58h]
  __int64 v357; // [rsp+AE0h] [rbp+A60h] BYREF
  _QWORD *v358; // [rsp+AE8h] [rbp+A68h]
  __int64 v359; // [rsp+AF0h] [rbp+A70h] BYREF
  _QWORD *v360; // [rsp+AF8h] [rbp+A78h]
  __int64 v361; // [rsp+B00h] [rbp+A80h]
  _QWORD *v362; // [rsp+B08h] [rbp+A88h]
  __int64 v363; // [rsp+B10h] [rbp+A90h] BYREF
  _QWORD *v364; // [rsp+B18h] [rbp+A98h]
  __int64 v365; // [rsp+B20h] [rbp+AA0h] BYREF
  _QWORD *v366; // [rsp+B28h] [rbp+AA8h]
  __int64 v367; // [rsp+B30h] [rbp+AB0h]
  _QWORD *v368; // [rsp+B38h] [rbp+AB8h]
  __int64 v369; // [rsp+B40h] [rbp+AC0h] BYREF
  _QWORD *v370; // [rsp+B48h] [rbp+AC8h]
  __int64 v371; // [rsp+B50h] [rbp+AD0h] BYREF
  __int64 v372; // [rsp+B58h] [rbp+AD8h]
  __int64 v373; // [rsp+B60h] [rbp+AE0h] BYREF
  _QWORD *v374; // [rsp+B68h] [rbp+AE8h]
  __int64 v375; // [rsp+B70h] [rbp+AF0h] BYREF
  __int64 v376; // [rsp+B78h] [rbp+AF8h]
  _QWORD *(__fastcall *v377)(__int64 *, __int64, __int64, __int64, char, __int64); // [rsp+B80h] [rbp+B00h] BYREF
  _QWORD *v378; // [rsp+B88h] [rbp+B08h]
  __int64 v379; // [rsp+B90h] [rbp+B10h] BYREF
  __int64 v380; // [rsp+B98h] [rbp+B18h]
  __int64 v381; // [rsp+BA0h] [rbp+B20h] BYREF
  _QWORD *v382; // [rsp+BA8h] [rbp+B28h]
  __int64 v383; // [rsp+BB0h] [rbp+B30h] BYREF
  __int64 v384; // [rsp+BB8h] [rbp+B38h]
  __int64 v385; // [rsp+BC0h] [rbp+B40h] BYREF
  _QWORD *v386; // [rsp+BC8h] [rbp+B48h]
  __int64 v387; // [rsp+BD0h] [rbp+B50h] BYREF
  _QWORD *v388; // [rsp+BD8h] [rbp+B58h]
  __int64 v389; // [rsp+BE0h] [rbp+B60h] BYREF
  _QWORD *v390; // [rsp+BE8h] [rbp+B68h]
  __int64 v391; // [rsp+BF0h] [rbp+B70h]
  _QWORD *v392; // [rsp+BF8h] [rbp+B78h]
  __int64 v393; // [rsp+C00h] [rbp+B80h] BYREF
  _QWORD *v394; // [rsp+C08h] [rbp+B88h]
  __int64 v395; // [rsp+C10h] [rbp+B90h] BYREF
  _QWORD *v396; // [rsp+C18h] [rbp+B98h]
  __int64 v397; // [rsp+C20h] [rbp+BA0h]
  _QWORD *v398; // [rsp+C28h] [rbp+BA8h]
  __int64 v399; // [rsp+C30h] [rbp+BB0h] BYREF
  _QWORD *v400; // [rsp+C38h] [rbp+BB8h]
  __int64 v401; // [rsp+C40h] [rbp+BC0h]
  __int64 v402; // [rsp+C48h] [rbp+BC8h]
  __int64 (__fastcall *v403)(); // [rsp+C50h] [rbp+BD0h] BYREF
  _QWORD *v404; // [rsp+C58h] [rbp+BD8h]
  __int64 v405; // [rsp+C60h] [rbp+BE0h] BYREF
  __int64 v406; // [rsp+C68h] [rbp+BE8h]
  __int64 v407; // [rsp+C78h] [rbp+BF8h]
  __int64 (__fastcall *v408)(); // [rsp+C80h] [rbp+C00h] BYREF
  _QWORD *v409; // [rsp+C88h] [rbp+C08h]
  __int64 v410; // [rsp+C98h] [rbp+C18h]
  __int64 (__fastcall *v411)(); // [rsp+CA0h] [rbp+C20h] BYREF
  _QWORD *v412; // [rsp+CA8h] [rbp+C28h]
  __int64 v413; // [rsp+CB8h] [rbp+C38h]
  __int64 (__fastcall *v414)(); // [rsp+CC0h] [rbp+C40h] BYREF
  _QWORD *v415; // [rsp+CC8h] [rbp+C48h]
  __int64 v416; // [rsp+CD0h] [rbp+C50h] BYREF
  _QWORD *v417; // [rsp+CD8h] [rbp+C58h]
  __int64 v418; // [rsp+CE0h] [rbp+C60h]
  _QWORD *v419; // [rsp+CE8h] [rbp+C68h]
  __int64 v420; // [rsp+CF0h] [rbp+C70h] BYREF
  _QWORD *v421; // [rsp+CF8h] [rbp+C78h]
  __int64 v422; // [rsp+D00h] [rbp+C80h] BYREF
  _QWORD *v423; // [rsp+D08h] [rbp+C88h]
  __int64 v424; // [rsp+D10h] [rbp+C90h]
  _QWORD *v425; // [rsp+D18h] [rbp+C98h]
  __int64 v426; // [rsp+D20h] [rbp+CA0h] BYREF
  _QWORD *v427; // [rsp+D28h] [rbp+CA8h]
  __int64 v428; // [rsp+D30h] [rbp+CB0h] BYREF
  _QWORD *v429; // [rsp+D38h] [rbp+CB8h]
  __int64 v430; // [rsp+D40h] [rbp+CC0h] BYREF
  _QWORD *v431; // [rsp+D48h] [rbp+CC8h]
  __int64 v432; // [rsp+D50h] [rbp+CD0h] BYREF
  __int64 v433; // [rsp+D58h] [rbp+CD8h]
  __int64 v434; // [rsp+D60h] [rbp+CE0h] BYREF
  __int64 v435; // [rsp+D68h] [rbp+CE8h]
  __int64 v436; // [rsp+D70h] [rbp+CF0h] BYREF
  _QWORD *v437; // [rsp+D78h] [rbp+CF8h]
  __int64 v438; // [rsp+D80h] [rbp+D00h] BYREF
  _QWORD *v439; // [rsp+D88h] [rbp+D08h]
  __int64 v440; // [rsp+D90h] [rbp+D10h]
  _QWORD *v441; // [rsp+D98h] [rbp+D18h]
  __int64 v442; // [rsp+DA0h] [rbp+D20h] BYREF
  _QWORD *v443; // [rsp+DA8h] [rbp+D28h]
  __int64 v444; // [rsp+DB0h] [rbp+D30h] BYREF
  _QWORD *v445; // [rsp+DB8h] [rbp+D38h]
  __int64 v446; // [rsp+DC0h] [rbp+D40h]
  _QWORD *v447; // [rsp+DC8h] [rbp+D48h]
  __int64 v448; // [rsp+DD0h] [rbp+D50h] BYREF
  _QWORD *v449; // [rsp+DD8h] [rbp+D58h]
  __int64 v450; // [rsp+DE0h] [rbp+D60h] BYREF
  _QWORD *v451; // [rsp+DE8h] [rbp+D68h]
  __int64 v452; // [rsp+DF0h] [rbp+D70h]
  _QWORD *v453; // [rsp+DF8h] [rbp+D78h]
  __int64 v454; // [rsp+E00h] [rbp+D80h] BYREF
  _QWORD *v455; // [rsp+E08h] [rbp+D88h]
  __int64 v456; // [rsp+E10h] [rbp+D90h] BYREF
  _QWORD *v457; // [rsp+E18h] [rbp+D98h]
  __int64 v458; // [rsp+E20h] [rbp+DA0h]
  _QWORD *v459; // [rsp+E28h] [rbp+DA8h]
  __int64 v460; // [rsp+E30h] [rbp+DB0h] BYREF
  _QWORD *v461; // [rsp+E38h] [rbp+DB8h]
  __int64 v462; // [rsp+E40h] [rbp+DC0h] BYREF
  _QWORD *v463; // [rsp+E48h] [rbp+DC8h]
  __int64 v464; // [rsp+E50h] [rbp+DD0h]
  _QWORD *v465; // [rsp+E58h] [rbp+DD8h]
  __int64 v466; // [rsp+E60h] [rbp+DE0h] BYREF
  _QWORD *v467; // [rsp+E68h] [rbp+DE8h]
  __int64 v468; // [rsp+E70h] [rbp+DF0h] BYREF
  _QWORD *v469; // [rsp+E78h] [rbp+DF8h]
  __int64 v470; // [rsp+E80h] [rbp+E00h]
  _QWORD *v471; // [rsp+E88h] [rbp+E08h]
  __int64 v472; // [rsp+E90h] [rbp+E10h] BYREF
  _QWORD *v473; // [rsp+E98h] [rbp+E18h]
  __int64 v474; // [rsp+EA0h] [rbp+E20h] BYREF
  _QWORD *v475; // [rsp+EA8h] [rbp+E28h]
  __int64 v476; // [rsp+EB0h] [rbp+E30h]
  _QWORD *v477; // [rsp+EB8h] [rbp+E38h]
  __int64 v478; // [rsp+EC0h] [rbp+E40h] BYREF
  _QWORD *v479; // [rsp+EC8h] [rbp+E48h]
  __int64 v480; // [rsp+ED0h] [rbp+E50h] BYREF
  _QWORD *v481; // [rsp+ED8h] [rbp+E58h]
  __int64 v482; // [rsp+EE0h] [rbp+E60h]
  _QWORD *v483; // [rsp+EE8h] [rbp+E68h]
  __int64 v484; // [rsp+EF0h] [rbp+E70h] BYREF
  _QWORD *v485; // [rsp+EF8h] [rbp+E78h]
  __int64 v486; // [rsp+F00h] [rbp+E80h] BYREF
  _QWORD *v487; // [rsp+F08h] [rbp+E88h]
  __int64 v488; // [rsp+F10h] [rbp+E90h]
  _QWORD *v489; // [rsp+F18h] [rbp+E98h]
  __int64 v490; // [rsp+F20h] [rbp+EA0h] BYREF
  _QWORD *v491; // [rsp+F28h] [rbp+EA8h]
  __int64 v492; // [rsp+F30h] [rbp+EB0h] BYREF
  _QWORD *v493; // [rsp+F38h] [rbp+EB8h]
  __int64 v494; // [rsp+F40h] [rbp+EC0h]
  _QWORD *v495; // [rsp+F48h] [rbp+EC8h]
  __int64 v496; // [rsp+F50h] [rbp+ED0h] BYREF
  _QWORD *v497; // [rsp+F58h] [rbp+ED8h]
  __int64 v498; // [rsp+F60h] [rbp+EE0h] BYREF
  _QWORD *v499; // [rsp+F68h] [rbp+EE8h]
  __int64 v500; // [rsp+F70h] [rbp+EF0h]
  _QWORD *v501; // [rsp+F78h] [rbp+EF8h]
  __int64 v502; // [rsp+F80h] [rbp+F00h] BYREF
  _QWORD *v503; // [rsp+F88h] [rbp+F08h]
  __int64 v504; // [rsp+F90h] [rbp+F10h] BYREF
  _QWORD *v505; // [rsp+F98h] [rbp+F18h]
  __int64 v506; // [rsp+FA0h] [rbp+F20h] BYREF
  _QWORD *v507; // [rsp+FA8h] [rbp+F28h]
  __int64 v508; // [rsp+FB0h] [rbp+F30h] BYREF
  __int64 v509; // [rsp+FB8h] [rbp+F38h]
  __int64 v510; // [rsp+FC0h] [rbp+F40h] BYREF
  __int64 v511; // [rsp+FC8h] [rbp+F48h]
  __int64 v512; // [rsp+FD0h] [rbp+F50h] BYREF
  _QWORD *v513; // [rsp+FD8h] [rbp+F58h]
  __int64 v514; // [rsp+FE0h] [rbp+F60h] BYREF
  _QWORD *v515; // [rsp+FE8h] [rbp+F68h]
  __int64 v516; // [rsp+FF0h] [rbp+F70h]
  _QWORD *v517; // [rsp+FF8h] [rbp+F78h]
  __int64 v518; // [rsp+1000h] [rbp+F80h] BYREF
  _QWORD *v519; // [rsp+1008h] [rbp+F88h]
  __int64 v520; // [rsp+1010h] [rbp+F90h] BYREF
  _QWORD *v521; // [rsp+1018h] [rbp+F98h]
  __int64 v522; // [rsp+1020h] [rbp+FA0h]
  _QWORD *v523; // [rsp+1028h] [rbp+FA8h]
  __int64 v524; // [rsp+1030h] [rbp+FB0h] BYREF
  _QWORD *v525; // [rsp+1038h] [rbp+FB8h]
  __int64 v526; // [rsp+1040h] [rbp+FC0h] BYREF
  _QWORD *v527; // [rsp+1048h] [rbp+FC8h]
  __int64 v528; // [rsp+1050h] [rbp+FD0h]
  _QWORD *v529; // [rsp+1058h] [rbp+FD8h]
  __int64 v530; // [rsp+1060h] [rbp+FE0h] BYREF
  _QWORD *v531; // [rsp+1068h] [rbp+FE8h]
  __int64 v532; // [rsp+1070h] [rbp+FF0h] BYREF
  __int64 v533; // [rsp+1078h] [rbp+FF8h]
  __int64 v534; // [rsp+1080h] [rbp+1000h] BYREF
  __int64 v535; // [rsp+1088h] [rbp+1008h]
  __int64 v536; // [rsp+1098h] [rbp+1018h]
  __int64 v537; // [rsp+10A0h] [rbp+1020h]
  __int64 v538; // [rsp+10A8h] [rbp+1028h]
  __int64 v539; // [rsp+10B0h] [rbp+1030h] BYREF
  _QWORD *v540; // [rsp+10B8h] [rbp+1038h]
  __int64 (__fastcall *v541)(int, int, int, int, __int64, __int64); // [rsp+10C0h] [rbp+1040h] BYREF
  _QWORD *v542; // [rsp+10C8h] [rbp+1048h]
  __int64 (__fastcall *v543)(int, int, int, int, __int64, __int64); // [rsp+10D0h] [rbp+1050h] BYREF
  _QWORD *v544; // [rsp+10D8h] [rbp+1058h]
  __int64 v545; // [rsp+10E8h] [rbp+1068h]
  __int64 v546; // [rsp+10F0h] [rbp+1070h] BYREF
  _QWORD *v547; // [rsp+10F8h] [rbp+1078h]
  __int64 v548; // [rsp+1100h] [rbp+1080h] BYREF
  _QWORD *v549; // [rsp+1108h] [rbp+1088h]
  __int64 v550; // [rsp+1110h] [rbp+1090h] BYREF
  _QWORD *v551; // [rsp+1118h] [rbp+1098h]
  __int64 v552; // [rsp+1120h] [rbp+10A0h]
  _QWORD *v553; // [rsp+1128h] [rbp+10A8h]
  __int64 v554; // [rsp+1130h] [rbp+10B0h] BYREF
  _QWORD *v555; // [rsp+1138h] [rbp+10B8h]
  __int64 v556; // [rsp+1140h] [rbp+10C0h] BYREF
  __int64 v557; // [rsp+1148h] [rbp+10C8h]
  __int64 v558; // [rsp+1150h] [rbp+10D0h] BYREF
  __int64 v559; // [rsp+1158h] [rbp+10D8h]
  __int64 v560; // [rsp+1160h] [rbp+10E0h] BYREF
  __int64 v561; // [rsp+1168h] [rbp+10E8h]
  __int64 v562; // [rsp+1170h] [rbp+10F0h]
  __int64 v563; // [rsp+1180h] [rbp+1100h] BYREF
  char *v564; // [rsp+1188h] [rbp+1108h]
  __int64 v565; // [rsp+1190h] [rbp+1110h]
  _QWORD *v566; // [rsp+1198h] [rbp+1118h]
  __int64 v567; // [rsp+11A0h] [rbp+1120h] BYREF
  _QWORD *v568; // [rsp+11A8h] [rbp+1128h]
  __int64 v569; // [rsp+11B0h] [rbp+1130h]
  _QWORD *v570; // [rsp+11B8h] [rbp+1138h]
  __int64 v571; // [rsp+11C0h] [rbp+1140h] BYREF
  _QWORD *v572; // [rsp+11C8h] [rbp+1148h]
  __int64 v573; // [rsp+11D0h] [rbp+1150h] BYREF
  __int64 v574; // [rsp+11D8h] [rbp+1158h]
  __int64 v575; // [rsp+11E0h] [rbp+1160h]
  _QWORD *v576; // [rsp+11E8h] [rbp+1168h]
  __int64 v577; // [rsp+11F0h] [rbp+1170h] BYREF
  _QWORD *v578; // [rsp+11F8h] [rbp+1178h]
  __int64 v579; // [rsp+1200h] [rbp+1180h] BYREF
  _QWORD *v580; // [rsp+1208h] [rbp+1188h]
  __int64 v581; // [rsp+1210h] [rbp+1190h] BYREF
  _QWORD *v582; // [rsp+1218h] [rbp+1198h]
  __int64 v583; // [rsp+1220h] [rbp+11A0h] BYREF
  _QWORD *v584; // [rsp+1228h] [rbp+11A8h]
  __int64 v585; // [rsp+1230h] [rbp+11B0h] BYREF
  _QWORD *v586; // [rsp+1238h] [rbp+11B8h]
  __int64 v587; // [rsp+1240h] [rbp+11C0h] BYREF
  __int64 v588; // [rsp+1248h] [rbp+11C8h]
  __int64 v589; // [rsp+1250h] [rbp+11D0h] BYREF
  __int64 v590; // [rsp+1258h] [rbp+11D8h]
  __int64 v591; // [rsp+1260h] [rbp+11E0h] BYREF
  _QWORD *v592; // [rsp+1268h] [rbp+11E8h]
  __int64 v593[2]; // [rsp+1270h] [rbp+11F0h] BYREF
  __int64 v594; // [rsp+1280h] [rbp+1200h]
  _QWORD *v595; // [rsp+1288h] [rbp+1208h]
  __int64 v596; // [rsp+1290h] [rbp+1210h] BYREF
  _QWORD *v597; // [rsp+1298h] [rbp+1218h]
  __int64 v598; // [rsp+12A0h] [rbp+1220h] BYREF
  _QWORD *v599; // [rsp+12A8h] [rbp+1228h]
  __int64 v600; // [rsp+12B0h] [rbp+1230h] BYREF
  _QWORD *v601; // [rsp+12B8h] [rbp+1238h]
  __int64 v602; // [rsp+12C0h] [rbp+1240h] BYREF
  _QWORD *v603; // [rsp+12C8h] [rbp+1248h]
  __int64 v604; // [rsp+12D0h] [rbp+1250h] BYREF
  _QWORD *v605; // [rsp+12D8h] [rbp+1258h]
  __int64 v606; // [rsp+12E0h] [rbp+1260h] BYREF
  _QWORD *v607; // [rsp+12E8h] [rbp+1268h]
  __int64 v608; // [rsp+12F0h] [rbp+1270h]
  _QWORD *v609; // [rsp+12F8h] [rbp+1278h]
  __int64 v610; // [rsp+1300h] [rbp+1280h] BYREF
  _QWORD *v611; // [rsp+1308h] [rbp+1288h]
  __int64 v612; // [rsp+1310h] [rbp+1290h] BYREF
  _QWORD *v613; // [rsp+1318h] [rbp+1298h]
  __int64 v614; // [rsp+1320h] [rbp+12A0h]
  _QWORD *v615; // [rsp+1328h] [rbp+12A8h]
  __int64 v616; // [rsp+1330h] [rbp+12B0h] BYREF
  _QWORD *v617; // [rsp+1338h] [rbp+12B8h]
  __int64 v618; // [rsp+1340h] [rbp+12C0h] BYREF
  _QWORD *v619; // [rsp+1348h] [rbp+12C8h]
  __int64 v620; // [rsp+1350h] [rbp+12D0h] BYREF
  _QWORD *v621; // [rsp+1358h] [rbp+12D8h]
  __int64 v622; // [rsp+1360h] [rbp+12E0h]
  _QWORD *v623; // [rsp+1368h] [rbp+12E8h]
  __int64 v624; // [rsp+1370h] [rbp+12F0h] BYREF
  _QWORD *v625; // [rsp+1378h] [rbp+12F8h]
  __int64 v626; // [rsp+1380h] [rbp+1300h] BYREF
  _QWORD *v627; // [rsp+1388h] [rbp+1308h]
  __int64 v628; // [rsp+1390h] [rbp+1310h] BYREF
  _QWORD *v629; // [rsp+1398h] [rbp+1318h]
  __int64 v630; // [rsp+13A8h] [rbp+1328h]
  __int64 v631[3]; // [rsp+13B0h] [rbp+1330h] BYREF
  __int64 v632; // [rsp+13C8h] [rbp+1348h]
  __int64 v633; // [rsp+13D0h] [rbp+1350h] BYREF
  __int64 v634; // [rsp+13D8h] [rbp+1358h]
  __int64 v635; // [rsp+13E8h] [rbp+1368h]
  __int64 v636; // [rsp+13F0h] [rbp+1370h] BYREF
  __int64 v637; // [rsp+13F8h] [rbp+1378h]
  __int64 v638; // [rsp+1408h] [rbp+1388h]
  __int64 v639; // [rsp+1410h] [rbp+1390h] BYREF
  __int64 v640; // [rsp+1418h] [rbp+1398h]
  __int64 v641; // [rsp+1420h] [rbp+13A0h] BYREF
  __int64 v642; // [rsp+1428h] [rbp+13A8h]
  __int64 v643; // [rsp+1430h] [rbp+13B0h]
  void *v644; // [rsp+1438h] [rbp+13B8h]
  __int64 v645; // [rsp+1440h] [rbp+13C0h] BYREF
  __int64 v646; // [rsp+1448h] [rbp+13C8h]
  __int64 v647; // [rsp+1450h] [rbp+13D0h]
  void *v648; // [rsp+1458h] [rbp+13D8h]
  __int64 v649; // [rsp+1460h] [rbp+13E0h] BYREF
  __int64 v650; // [rsp+1468h] [rbp+13E8h]
  __int64 v651[2]; // [rsp+1470h] [rbp+13F0h] BYREF
  __int64 v652; // [rsp+1480h] [rbp+1400h]
  __int64 v653; // [rsp+1488h] [rbp+1408h]
  __int64 v654; // [rsp+1490h] [rbp+1410h] BYREF
  _QWORD *v655; // [rsp+1498h] [rbp+1418h]
  __int64 v656[2]; // [rsp+14A0h] [rbp+1420h] BYREF
  __int64 v657; // [rsp+14B0h] [rbp+1430h]
  _QWORD *v658; // [rsp+14B8h] [rbp+1438h]
  char v659[8]; // [rsp+14C0h] [rbp+1440h] BYREF
  const char *v660; // [rsp+14C8h] [rbp+1448h]
  __int64 v661; // [rsp+14D0h] [rbp+1450h]
  const char *v662; // [rsp+14D8h] [rbp+1458h]
  __int16 v663; // [rsp+14E0h] [rbp+1460h]
  __int64 v664; // [rsp+14F0h] [rbp+1470h] BYREF
  _QWORD *v665; // [rsp+14F8h] [rbp+1478h]
  __int64 v666; // [rsp+1500h] [rbp+1480h] BYREF
  __int64 v667; // [rsp+1508h] [rbp+1488h]
  __int64 v668; // [rsp+1510h] [rbp+1490h]
  __int64 v669; // [rsp+1518h] [rbp+1498h]
  __int64 v670; // [rsp+1520h] [rbp+14A0h]
  __int64 v671; // [rsp+1530h] [rbp+14B0h] BYREF
  _QWORD *v672; // [rsp+1538h] [rbp+14B8h]
  __int64 v673; // [rsp+1540h] [rbp+14C0h]
  _QWORD *v674; // [rsp+1548h] [rbp+14C8h]
  __int64 v675; // [rsp+1550h] [rbp+14D0h] BYREF
  _QWORD *v676; // [rsp+1558h] [rbp+14D8h]
  __int64 v677; // [rsp+1560h] [rbp+14E0h] BYREF
  _QWORD *v678; // [rsp+1568h] [rbp+14E8h]
  __int64 v679; // [rsp+1570h] [rbp+14F0h] BYREF
  _QWORD *v680; // [rsp+1578h] [rbp+14F8h]
  __int64 v681; // [rsp+1580h] [rbp+1500h] BYREF
  _QWORD *v682; // [rsp+1588h] [rbp+1508h]
  __int64 v683; // [rsp+1590h] [rbp+1510h] BYREF
  _QWORD *v684; // [rsp+1598h] [rbp+1518h]
  __int64 v685; // [rsp+15A0h] [rbp+1520h] BYREF
  _QWORD *v686; // [rsp+15A8h] [rbp+1528h]
  __int64 v687; // [rsp+15B0h] [rbp+1530h] BYREF
  _QWORD *v688; // [rsp+15B8h] [rbp+1538h]
  __int64 v689; // [rsp+15C0h] [rbp+1540h] BYREF
  _QWORD *v690; // [rsp+15C8h] [rbp+1548h]
  __int64 v691; // [rsp+15D0h] [rbp+1550h] BYREF
  _QWORD *v692; // [rsp+15D8h] [rbp+1558h]
  __int64 v693; // [rsp+15E0h] [rbp+1560h] BYREF
  _QWORD *v694; // [rsp+15E8h] [rbp+1568h]
  __int64 v695; // [rsp+15F0h] [rbp+1570h] BYREF
  _QWORD *v696; // [rsp+15F8h] [rbp+1578h]
  __int64 v697; // [rsp+1600h] [rbp+1580h] BYREF
  _QWORD *v698; // [rsp+1608h] [rbp+1588h]
  __int64 v699; // [rsp+1610h] [rbp+1590h] BYREF
  _QWORD *v700; // [rsp+1618h] [rbp+1598h]
  __int64 v701; // [rsp+1620h] [rbp+15A0h] BYREF
  __int64 v702; // [rsp+1628h] [rbp+15A8h]
  __int64 v703; // [rsp+1630h] [rbp+15B0h] BYREF
  __int64 v704; // [rsp+1638h] [rbp+15B8h]
  __int64 v705; // [rsp+1640h] [rbp+15C0h] BYREF
  __int64 v706; // [rsp+1648h] [rbp+15C8h]
  __int64 v707; // [rsp+1650h] [rbp+15D0h]
  _QWORD *v708; // [rsp+1658h] [rbp+15D8h]
  __int64 v709; // [rsp+1660h] [rbp+15E0h] BYREF
  _QWORD *v710; // [rsp+1668h] [rbp+15E8h]
  __int64 v711; // [rsp+1670h] [rbp+15F0h] BYREF
  __int64 v712; // [rsp+1678h] [rbp+15F8h]
  __int64 v713[2]; // [rsp+1680h] [rbp+1600h] BYREF
  __int64 v714[2]; // [rsp+1690h] [rbp+1610h] BYREF
  __int64 v715[2]; // [rsp+16A0h] [rbp+1620h] BYREF
  __int64 v716[2]; // [rsp+16B0h] [rbp+1630h] BYREF
  __int64 v717[2]; // [rsp+16C0h] [rbp+1640h] BYREF
  __int64 v718[2]; // [rsp+16D0h] [rbp+1650h] BYREF
  __int64 v719[2]; // [rsp+16E0h] [rbp+1660h] BYREF
  __int64 v720[2]; // [rsp+16F0h] [rbp+1670h] BYREF
  __int64 v721[2]; // [rsp+1700h] [rbp+1680h] BYREF
  __int64 v722[2]; // [rsp+1710h] [rbp+1690h] BYREF
  __int64 v723[2]; // [rsp+1720h] [rbp+16A0h] BYREF
  __int64 v724[2]; // [rsp+1730h] [rbp+16B0h] BYREF
  __int64 v725[2]; // [rsp+1740h] [rbp+16C0h] BYREF
  __int64 v726[2]; // [rsp+1750h] [rbp+16D0h] BYREF
  __int64 v727[2]; // [rsp+1760h] [rbp+16E0h] BYREF
  __int64 v728[2]; // [rsp+1770h] [rbp+16F0h] BYREF
  __int64 v729[2]; // [rsp+1780h] [rbp+1700h] BYREF
  __int64 v730[2]; // [rsp+1790h] [rbp+1710h] BYREF
  __int64 v731[2]; // [rsp+17A0h] [rbp+1720h] BYREF
  __int64 v732[2]; // [rsp+17B0h] [rbp+1730h] BYREF
  __int64 v733[2]; // [rsp+17C0h] [rbp+1740h] BYREF
  __int64 v734[2]; // [rsp+17D0h] [rbp+1750h] BYREF
  __int64 v735[2]; // [rsp+17E0h] [rbp+1760h] BYREF
  __int64 v736[2]; // [rsp+17F0h] [rbp+1770h] BYREF
  __int64 v737[2]; // [rsp+1800h] [rbp+1780h] BYREF
  __int64 v738[2]; // [rsp+1810h] [rbp+1790h] BYREF
  __int64 v739[2]; // [rsp+1820h] [rbp+17A0h] BYREF
  __int64 v740[2]; // [rsp+1830h] [rbp+17B0h] BYREF
  __int64 v741[2]; // [rsp+1840h] [rbp+17C0h] BYREF
  __int64 v742[2]; // [rsp+1850h] [rbp+17D0h] BYREF
  __int64 v743[2]; // [rsp+1860h] [rbp+17E0h] BYREF
  __int64 v744[2]; // [rsp+1870h] [rbp+17F0h] BYREF
  __int64 v745[2]; // [rsp+1880h] [rbp+1800h] BYREF
  __int64 v746[2]; // [rsp+1890h] [rbp+1810h] BYREF
  __int64 v747[2]; // [rsp+18A0h] [rbp+1820h] BYREF
  __int64 v748[2]; // [rsp+18B0h] [rbp+1830h] BYREF
  __int64 v749[2]; // [rsp+18C0h] [rbp+1840h] BYREF
  __int64 v750[2]; // [rsp+18E0h] [rbp+1860h] BYREF
  __int64 v751[2]; // [rsp+1900h] [rbp+1880h] BYREF
  __int64 v752[4]; // [rsp+1920h] [rbp+18A0h] BYREF
  __int64 v753; // [rsp+1940h] [rbp+18C0h]
  __int64 v754; // [rsp+1948h] [rbp+18C8h]
  unsigned __int64 v755; // [rsp+1950h] [rbp+18D0h]
  __int64 v756; // [rsp+1958h] [rbp+18D8h]
  bool v757; // [rsp+1966h] [rbp+18E6h]
  char v758; // [rsp+1967h] [rbp+18E7h]
  __int64 v759; // [rsp+1968h] [rbp+18E8h]
  __int64 v760; // [rsp+1970h] [rbp+18F0h]
  __int64 v761; // [rsp+1978h] [rbp+18F8h]
  _QWORD *v762; // [rsp+1980h] [rbp+1900h]
  __int64 v763; // [rsp+1988h] [rbp+1908h]
  __int64 v764; // [rsp+1990h] [rbp+1910h]
  __int64 v765; // [rsp+1998h] [rbp+1918h]
  __int64 v766; // [rsp+19A0h] [rbp+1920h]
  char v767; // [rsp+19AFh] [rbp+192Fh]
  __int64 v768; // [rsp+19B0h] [rbp+1930h]
  __int64 v769; // [rsp+19B8h] [rbp+1938h]
  __int64 v770; // [rsp+19C0h] [rbp+1940h]
  __int64 v771; // [rsp+19C8h] [rbp+1948h]
  __int64 v772; // [rsp+19D0h] [rbp+1950h]
  __int64 v773; // [rsp+19D8h] [rbp+1958h]
  char v774; // [rsp+19E7h] [rbp+1967h]
  __int64 v775; // [rsp+19E8h] [rbp+1968h]
  __int64 v776; // [rsp+19F0h] [rbp+1970h]
  __int64 v777; // [rsp+19F8h] [rbp+1978h]
  char *v778; // [rsp+1A00h] [rbp+1980h]
  __int64 v779; // [rsp+1A08h] [rbp+1988h]
  char v780; // [rsp+1A17h] [rbp+1997h]
  __int64 v781; // [rsp+1A18h] [rbp+1998h]
  __int64 v782; // [rsp+1A20h] [rbp+19A0h]
  __int64 v783; // [rsp+1A28h] [rbp+19A8h]
  __int64 *v784; // [rsp+1A30h] [rbp+19B0h]
  __int64 v785; // [rsp+1A38h] [rbp+19B8h]
  char v786; // [rsp+1A46h] [rbp+19C6h]
  char v787; // [rsp+1A47h] [rbp+19C7h]
  __int64 v788; // [rsp+1A48h] [rbp+19C8h]
  __int64 v789; // [rsp+1A50h] [rbp+19D0h]
  __int64 v790; // [rsp+1A58h] [rbp+19D8h]
  __int64 v791; // [rsp+1A60h] [rbp+19E0h]
  __int64 allocation_top__modelZsave95mongerZcommon_u5497; // [rsp+1A68h] [rbp+19E8h]
  __int64 v793; // [rsp+1A70h] [rbp+19F0h]
  char v794; // [rsp+1A7Fh] [rbp+19FFh]
  __int64 v795; // [rsp+1A80h] [rbp+1A00h]
  __int64 v796; // [rsp+1A88h] [rbp+1A08h]
  _QWORD *v797; // [rsp+1A90h] [rbp+1A10h]
  __int64 v798; // [rsp+1A98h] [rbp+1A18h]
  char v799; // [rsp+1AA7h] [rbp+1A27h]
  __int64 v800; // [rsp+1AA8h] [rbp+1A28h]
  __int64 v801; // [rsp+1AB0h] [rbp+1A30h]
  _QWORD *v802; // [rsp+1AB8h] [rbp+1A38h]
  __int64 v803; // [rsp+1AC0h] [rbp+1A40h]
  __int64 v804; // [rsp+1AC8h] [rbp+1A48h]
  __int64 v805; // [rsp+1AD0h] [rbp+1A50h]
  __int64 v806; // [rsp+1AD8h] [rbp+1A58h]
  __int64 v807; // [rsp+1AE0h] [rbp+1A60h]
  __int64 v808; // [rsp+1AE8h] [rbp+1A68h]
  __int64 v809; // [rsp+1AF0h] [rbp+1A70h]
  __int64 v810; // [rsp+1AF8h] [rbp+1A78h]
  char *v811; // [rsp+1B00h] [rbp+1A80h]
  __int64 v812; // [rsp+1B08h] [rbp+1A88h]
  __int64 v813; // [rsp+1B10h] [rbp+1A90h]
  __int64 v814; // [rsp+1B18h] [rbp+1A98h]
  __int64 v815; // [rsp+1B20h] [rbp+1AA0h]
  __int64 v816; // [rsp+1B28h] [rbp+1AA8h]
  __int64 v817; // [rsp+1B30h] [rbp+1AB0h]
  __int64 v818; // [rsp+1B38h] [rbp+1AB8h]
  __int64 v819; // [rsp+1B40h] [rbp+1AC0h]
  __int64 v820; // [rsp+1B48h] [rbp+1AC8h]
  __int64 v821; // [rsp+1B50h] [rbp+1AD0h]
  __int64 v822; // [rsp+1B58h] [rbp+1AD8h]
  __int64 v823; // [rsp+1B60h] [rbp+1AE0h]
  __int64 v824; // [rsp+1B68h] [rbp+1AE8h]
  __int64 v825; // [rsp+1B70h] [rbp+1AF0h]
  __int64 state_index__modelZsave95mongerZcommon_u5502; // [rsp+1B78h] [rbp+1AF8h]
  __int64 v827; // [rsp+1B80h] [rbp+1B00h]
  __int64 v828; // [rsp+1B88h] [rbp+1B08h]
  __int64 v829; // [rsp+1B90h] [rbp+1B10h]
  __int64 v830; // [rsp+1B98h] [rbp+1B18h]
  __int64 v831; // [rsp+1BA0h] [rbp+1B20h]
  __int64 v832; // [rsp+1BA8h] [rbp+1B28h]
  __int64 v833; // [rsp+1BB0h] [rbp+1B30h]
  char v834; // [rsp+1BBFh] [rbp+1B3Fh]
  __int64 v835; // [rsp+1BC0h] [rbp+1B40h]
  __int64 v836; // [rsp+1BC8h] [rbp+1B48h]
  char *v837; // [rsp+1BD0h] [rbp+1B50h]
  __int64 v838; // [rsp+1BD8h] [rbp+1B58h]
  __int64 v839; // [rsp+1BE0h] [rbp+1B60h]
  __int64 v840; // [rsp+1BE8h] [rbp+1B68h]
  __int64 v841; // [rsp+1BF0h] [rbp+1B70h]
  __int64 v842; // [rsp+1BF8h] [rbp+1B78h]
  __int64 v843; // [rsp+1C00h] [rbp+1B80h]
  __int64 v844; // [rsp+1C08h] [rbp+1B88h]
  __int64 v845; // [rsp+1C10h] [rbp+1B90h]
  __int64 v846; // [rsp+1C18h] [rbp+1B98h]
  __int64 v847; // [rsp+1C20h] [rbp+1BA0h]
  __int64 v848; // [rsp+1C28h] [rbp+1BA8h]
  __int64 v849; // [rsp+1C30h] [rbp+1BB0h]
  _QWORD *v850; // [rsp+1C38h] [rbp+1BB8h]
  __int64 v851; // [rsp+1C40h] [rbp+1BC0h]
  __int64 v852; // [rsp+1C48h] [rbp+1BC8h]
  __int64 v853; // [rsp+1C50h] [rbp+1BD0h]
  __int64 v854; // [rsp+1C58h] [rbp+1BD8h]
  __int64 v855; // [rsp+1C60h] [rbp+1BE0h]
  __int64 v856; // [rsp+1C68h] [rbp+1BE8h]
  __int64 v857; // [rsp+1C70h] [rbp+1BF0h]
  __int64 v858; // [rsp+1C78h] [rbp+1BF8h]
  __int64 v859; // [rsp+1C80h] [rbp+1C00h]
  __int64 v860; // [rsp+1C88h] [rbp+1C08h]
  __int64 v861; // [rsp+1C90h] [rbp+1C10h]
  __int64 v862; // [rsp+1C98h] [rbp+1C18h]
  __int64 v863; // [rsp+1CA0h] [rbp+1C20h]
  __int64 v864; // [rsp+1CA8h] [rbp+1C28h]
  __int64 v865; // [rsp+1CB0h] [rbp+1C30h]
  __int64 v866; // [rsp+1CB8h] [rbp+1C38h]
  __int64 v867; // [rsp+1CC0h] [rbp+1C40h]
  __int64 v868; // [rsp+1CC8h] [rbp+1C48h]
  __int64 v869; // [rsp+1CD0h] [rbp+1C50h]
  __int64 v870; // [rsp+1CD8h] [rbp+1C58h]
  __int64 v871; // [rsp+1CE0h] [rbp+1C60h]
  __int64 v872; // [rsp+1CE8h] [rbp+1C68h]
  __int64 v873; // [rsp+1CF0h] [rbp+1C70h]
  __int64 v874; // [rsp+1CF8h] [rbp+1C78h]
  __int64 v875; // [rsp+1D00h] [rbp+1C80h]
  __int64 v876; // [rsp+1D08h] [rbp+1C88h]
  __int64 v877; // [rsp+1D10h] [rbp+1C90h]
  __int64 v878; // [rsp+1D18h] [rbp+1C98h]
  __int64 v879; // [rsp+1D20h] [rbp+1CA0h]
  __int64 v880; // [rsp+1D28h] [rbp+1CA8h]
  __int64 v881; // [rsp+1D30h] [rbp+1CB0h]
  __int64 v882; // [rsp+1D38h] [rbp+1CB8h]
  __int64 v883; // [rsp+1D40h] [rbp+1CC0h]
  __int64 v884; // [rsp+1D48h] [rbp+1CC8h]
  __int64 v885; // [rsp+1D50h] [rbp+1CD0h]
  __int64 v886; // [rsp+1D58h] [rbp+1CD8h]
  __int64 v887; // [rsp+1D60h] [rbp+1CE0h]
  __int64 v888; // [rsp+1D68h] [rbp+1CE8h]
  __int64 v889; // [rsp+1D70h] [rbp+1CF0h]
  __int64 v890; // [rsp+1D78h] [rbp+1CF8h]
  __int64 v891; // [rsp+1D80h] [rbp+1D00h]
  __int64 v892; // [rsp+1D88h] [rbp+1D08h]
  __int64 v893; // [rsp+1D90h] [rbp+1D10h]
  __int64 v894; // [rsp+1D98h] [rbp+1D18h]
  __int64 v895; // [rsp+1DA0h] [rbp+1D20h]
  __int64 v896; // [rsp+1DA8h] [rbp+1D28h]
  __int64 v897; // [rsp+1DB0h] [rbp+1D30h]
  __int64 v898; // [rsp+1DB8h] [rbp+1D38h]
  __int64 v899; // [rsp+1DC0h] [rbp+1D40h]
  __int64 v900; // [rsp+1DC8h] [rbp+1D48h]
  __int64 v901; // [rsp+1DD0h] [rbp+1D50h]
  __int64 v902; // [rsp+1DD8h] [rbp+1D58h]
  __int64 v903; // [rsp+1DE0h] [rbp+1D60h]
  __int64 v904; // [rsp+1DE8h] [rbp+1D68h]
  __int64 v905; // [rsp+1DF0h] [rbp+1D70h]
  __int64 v906; // [rsp+1DF8h] [rbp+1D78h]
  __int64 v907; // [rsp+1E00h] [rbp+1D80h]
  __int64 v908; // [rsp+1E08h] [rbp+1D88h]
  __int64 v909; // [rsp+1E10h] [rbp+1D90h]
  __int64 v910; // [rsp+1E18h] [rbp+1D98h]
  __int64 v911; // [rsp+1E20h] [rbp+1DA0h]
  __int64 v912; // [rsp+1E28h] [rbp+1DA8h]
  __int64 v913; // [rsp+1E30h] [rbp+1DB0h]
  __int64 v914; // [rsp+1E38h] [rbp+1DB8h]
  __int64 v915; // [rsp+1E40h] [rbp+1DC0h]
  __int64 v916; // [rsp+1E48h] [rbp+1DC8h]
  __int64 v917; // [rsp+1E50h] [rbp+1DD0h]
  __int64 v918; // [rsp+1E58h] [rbp+1DD8h]
  __int64 v919; // [rsp+1E60h] [rbp+1DE0h]
  __int64 v920; // [rsp+1E68h] [rbp+1DE8h]
  __int64 v921; // [rsp+1E70h] [rbp+1DF0h]
  __int64 v922; // [rsp+1E78h] [rbp+1DF8h]
  __int64 v923; // [rsp+1E80h] [rbp+1E00h]
  __int64 v924; // [rsp+1E88h] [rbp+1E08h]
  __int64 v925; // [rsp+1E90h] [rbp+1E10h]
  __int64 v926; // [rsp+1E98h] [rbp+1E18h]
  __int64 v927; // [rsp+1EA0h] [rbp+1E20h]
  __int64 v928; // [rsp+1EA8h] [rbp+1E28h]
  __int64 v929; // [rsp+1EB0h] [rbp+1E30h]
  __int64 v930; // [rsp+1EB8h] [rbp+1E38h]
  __int64 v931; // [rsp+1EC0h] [rbp+1E40h]
  __int64 v932; // [rsp+1EC8h] [rbp+1E48h]
  __int64 v933; // [rsp+1ED0h] [rbp+1E50h]
  __int64 v934; // [rsp+1ED8h] [rbp+1E58h]
  __int64 v935; // [rsp+1EE0h] [rbp+1E60h]
  __int64 v936; // [rsp+1EE8h] [rbp+1E68h]
  __int64 v937; // [rsp+1EF0h] [rbp+1E70h]
  __int64 v938; // [rsp+1EF8h] [rbp+1E78h]
  __int64 v939; // [rsp+1F00h] [rbp+1E80h]
  __int64 v940; // [rsp+1F08h] [rbp+1E88h]
  __int64 v941; // [rsp+1F10h] [rbp+1E90h]
  __int64 v942; // [rsp+1F18h] [rbp+1E98h]
  __int64 v943; // [rsp+1F20h] [rbp+1EA0h]
  __int64 v944; // [rsp+1F28h] [rbp+1EA8h]
  __int64 v945; // [rsp+1F30h] [rbp+1EB0h]
  __int64 v946; // [rsp+1F38h] [rbp+1EB8h]
  __int64 v947; // [rsp+1F40h] [rbp+1EC0h]
  __int64 v948; // [rsp+1F48h] [rbp+1EC8h]
  __int64 v949; // [rsp+1F50h] [rbp+1ED0h]
  __int64 v950; // [rsp+1F58h] [rbp+1ED8h]
  __int64 v951; // [rsp+1F60h] [rbp+1EE0h]
  __int64 v952; // [rsp+1F68h] [rbp+1EE8h]
  __int64 v953; // [rsp+1F70h] [rbp+1EF0h]
  __int64 v954; // [rsp+1F78h] [rbp+1EF8h]
  __int64 v955; // [rsp+1F80h] [rbp+1F00h]
  __int64 v956; // [rsp+1F88h] [rbp+1F08h]
  __int64 v957; // [rsp+1F90h] [rbp+1F10h]
  __int64 v958; // [rsp+1F98h] [rbp+1F18h]
  __int64 v959; // [rsp+1FA0h] [rbp+1F20h]
  __int64 v960; // [rsp+1FA8h] [rbp+1F28h]
  __int64 v961; // [rsp+1FB0h] [rbp+1F30h]
  __int64 v962; // [rsp+1FB8h] [rbp+1F38h]
  __int64 v963; // [rsp+1FC0h] [rbp+1F40h]
  __int64 v964; // [rsp+1FC8h] [rbp+1F48h]
  __int64 v965; // [rsp+1FD0h] [rbp+1F50h]
  __int64 v966; // [rsp+1FD8h] [rbp+1F58h]
  __int64 v967; // [rsp+1FE0h] [rbp+1F60h]
  char v968; // [rsp+1FEFh] [rbp+1F6Fh]
  __int64 v969; // [rsp+1FF0h] [rbp+1F70h]
  __int64 v970; // [rsp+1FF8h] [rbp+1F78h]
  __int64 v971; // [rsp+2000h] [rbp+1F80h]
  unsigned __int8 v972; // [rsp+200Fh] [rbp+1F8Fh]
  __int64 v973; // [rsp+2010h] [rbp+1F90h]
  _QWORD *v974; // [rsp+2018h] [rbp+1F98h]
  _BYTE *v975; // [rsp+2020h] [rbp+1FA0h]
  __int64 v976; // [rsp+2028h] [rbp+1FA8h]
  __int64 v977; // [rsp+2030h] [rbp+1FB0h]
  char *v978; // [rsp+2038h] [rbp+1FB8h]
  _BYTE *v979; // [rsp+2040h] [rbp+1FC0h]
  char v980; // [rsp+204Eh] [rbp+1FCEh]
  unsigned __int8 v981; // [rsp+204Fh] [rbp+1FCFh]
  __int64 v982; // [rsp+2050h] [rbp+1FD0h]
  char v983; // [rsp+205Fh] [rbp+1FDFh]
  __int64 v984; // [rsp+2060h] [rbp+1FE0h]
  __int64 v985; // [rsp+2068h] [rbp+1FE8h]
  __int64 v986; // [rsp+2070h] [rbp+1FF0h]
  __int64 v987; // [rsp+2078h] [rbp+1FF8h]
  __int64 v988; // [rsp+2080h] [rbp+2000h]
  __int64 v989; // [rsp+2088h] [rbp+2008h]
  char v990; // [rsp+2097h] [rbp+2017h]
  __int64 v991; // [rsp+2098h] [rbp+2018h]
  __int64 v992; // [rsp+20A0h] [rbp+2020h]
  __int64 v993; // [rsp+20A8h] [rbp+2028h]
  __int64 v994; // [rsp+20B0h] [rbp+2030h]
  __int64 v995; // [rsp+20B8h] [rbp+2038h]
  _QWORD *v996; // [rsp+20C0h] [rbp+2040h]
  char v997; // [rsp+20CAh] [rbp+204Ah]
  char v998; // [rsp+20CBh] [rbp+204Bh]
  char v999; // [rsp+20CCh] [rbp+204Ch]
  char v1000; // [rsp+20CDh] [rbp+204Dh]
  char v1001; // [rsp+20CEh] [rbp+204Eh]
  char v1002; // [rsp+20CFh] [rbp+204Fh]
  __int64 v1003; // [rsp+20D0h] [rbp+2050h]
  __int64 v1004; // [rsp+20D8h] [rbp+2058h]
  _QWORD *v1005; // [rsp+20E0h] [rbp+2060h]
  _QWORD *v1006; // [rsp+20E8h] [rbp+2068h]
  _BYTE *v1007; // [rsp+20F0h] [rbp+2070h]
  __int64 v1008; // [rsp+20F8h] [rbp+2078h]
  __int64 v1009; // [rsp+2100h] [rbp+2080h]
  bool v1010; // [rsp+210Dh] [rbp+208Dh]
  bool v1011; // [rsp+210Eh] [rbp+208Eh]
  bool v1012; // [rsp+210Fh] [rbp+208Fh]
  __int64 v1013; // [rsp+2110h] [rbp+2090h]
  __int64 v1014; // [rsp+2118h] [rbp+2098h]
  __int64 v1015; // [rsp+2120h] [rbp+20A0h]
  __int64 v1016; // [rsp+2128h] [rbp+20A8h]
  __int64 v1017; // [rsp+2130h] [rbp+20B0h]
  char v1018; // [rsp+213Fh] [rbp+20BFh]
  __int64 v1019; // [rsp+2140h] [rbp+20C0h]
  __int64 v1020; // [rsp+2148h] [rbp+20C8h]
  __int64 v1021; // [rsp+2150h] [rbp+20D0h]
  __int64 v1022; // [rsp+2158h] [rbp+20D8h]
  __int64 v1023; // [rsp+2160h] [rbp+20E0h]
  __int64 v1024; // [rsp+2168h] [rbp+20E8h]
  __int64 v1025; // [rsp+2170h] [rbp+20F0h]
  __int64 v1026; // [rsp+2178h] [rbp+20F8h]
  bool v1027; // [rsp+2185h] [rbp+2105h]
  char v1028; // [rsp+2186h] [rbp+2106h]
  char v1029; // [rsp+2187h] [rbp+2107h]
  __int64 v1030; // [rsp+2188h] [rbp+2108h]
  __int64 v1031; // [rsp+2190h] [rbp+2110h]
  bool v1032; // [rsp+219Fh] [rbp+211Fh]
  __int64 v1033; // [rsp+21A0h] [rbp+2120h]
  __int64 v1034; // [rsp+21A8h] [rbp+2128h]
  __int64 v1035; // [rsp+21B0h] [rbp+2130h]
  __int64 v1036; // [rsp+21B8h] [rbp+2138h]
  __int64 v1037; // [rsp+21C0h] [rbp+2140h]
  __int64 v1038; // [rsp+21C8h] [rbp+2148h]
  __int64 v1039; // [rsp+21D0h] [rbp+2150h]
  __int64 v1040; // [rsp+21D8h] [rbp+2158h]
  __int64 v1041; // [rsp+21E0h] [rbp+2160h]
  __int64 v1042; // [rsp+21E8h] [rbp+2168h]
  __int64 v1043; // [rsp+21F0h] [rbp+2170h]
  __int64 v1044; // [rsp+21F8h] [rbp+2178h]
  __int64 v1045; // [rsp+2200h] [rbp+2180h]
  __int64 v1046; // [rsp+2208h] [rbp+2188h]
  __int64 v1047; // [rsp+2210h] [rbp+2190h]
  __int64 v1048; // [rsp+2218h] [rbp+2198h]
  __int64 v1049; // [rsp+2220h] [rbp+21A0h]
  __int64 v1050; // [rsp+2228h] [rbp+21A8h]
  __int64 v1051; // [rsp+2230h] [rbp+21B0h]
  __int64 v1052; // [rsp+2238h] [rbp+21B8h]
  __int64 v1053; // [rsp+2240h] [rbp+21C0h]
  __int64 v1054; // [rsp+2248h] [rbp+21C8h]
  __int64 v1055; // [rsp+2250h] [rbp+21D0h]
  __int64 v1056; // [rsp+2258h] [rbp+21D8h]
  __int64 v1057; // [rsp+2260h] [rbp+21E0h]
  __int64 v1058; // [rsp+2268h] [rbp+21E8h]
  __int64 v1059; // [rsp+2270h] [rbp+21F0h]
  __int64 v1060; // [rsp+2278h] [rbp+21F8h]
  __int64 v1061; // [rsp+2280h] [rbp+2200h]
  __int64 v1062; // [rsp+2288h] [rbp+2208h]
  __int64 v1063; // [rsp+2290h] [rbp+2210h]
  __int64 v1064; // [rsp+2298h] [rbp+2218h]
  __int64 v1065; // [rsp+22A0h] [rbp+2220h]
  __int64 v1066; // [rsp+22A8h] [rbp+2228h]
  __int64 v1067; // [rsp+22B0h] [rbp+2230h]
  __int64 v1068; // [rsp+22B8h] [rbp+2238h]
  __int64 v1069; // [rsp+22C0h] [rbp+2240h]
  __int64 v1070; // [rsp+22C8h] [rbp+2248h]
  __int64 v1071; // [rsp+22D0h] [rbp+2250h]
  __int64 v1072; // [rsp+22D8h] [rbp+2258h]
  __int64 v1073; // [rsp+22E0h] [rbp+2260h]
  __int64 v1074; // [rsp+22E8h] [rbp+2268h]

  v10 = *a2;
  v11 = a2[1];
  v116 = v10;
  v117 = v11;
  v12 = a4[1];
  v114 = *a4;
  v115 = (char *)v12;
  v13 = a5[1];
  v112 = *a5;
  v113 = v13;
  v14 = a7[1];
  v110 = *a7;
  v111 = v14;
  v15 = a10[1];
  v108 = *a10;
  v109 = v15;
  v660 = "generate_source";
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v661 = 0i64;
  v663 = 0;
  nimFrame_88(v659);
  v1007 = (_BYTE *)nimErrorFlag_86();
  v711 = 0i64;
  v712 = 0i64;
  v1006 = 0i64;
  v709 = 0i64;
  v710 = 0i64;
  v707 = 0i64;
  v708 = 0i64;
  v705 = 0i64;
  v706 = 0i64;
  v703 = 0i64;
  v704 = 0i64;
  v701 = 0i64;
  v702 = 0i64;
  v699 = 0i64;
  v700 = 0i64;
  v697 = 0i64;
  v698 = 0i64;
  v695 = 0i64;
  v696 = 0i64;
  v693 = 0i64;
  v694 = 0i64;
  v691 = 0i64;
  v692 = 0i64;
  v689 = 0i64;
  v690 = 0i64;
  v687 = 0i64;
  v688 = 0i64;
  v685 = 0i64;
  v686 = 0i64;
  v683 = 0i64;
  v684 = 0i64;
  v681 = 0i64;
  v682 = 0i64;
  v679 = 0i64;
  v680 = 0i64;
  v677 = 0i64;
  v678 = 0i64;
  v675 = 0i64;
  v676 = 0i64;
  v673 = 0i64;
  v674 = 0i64;
  v661 = 74i64;
  v1005 = 0i64;
  v1005 = (_QWORD *)nimNewObj(712i64, 8i64);
  *v1005 = &NTIv2__BB9aIMNxPr4uLQDzddoDQPQ_;
  v1006 = v1005;
  v661 = 770i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
  eqcopy___modelZboardZschematics_u4046(v1005 + 13, a3);
  v661 = 982i64;
  v662 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
  v106 = v112;
  v107 = v113;
  eqcopy___modelZsave95mongerZcommon_u5615(v1006 + 10, &v106);
  v661 = 1699i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  v106 = v108;
  v107 = v109;
  eqcopy___system_u2661(&v709, &v106);
  v661 = 77i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v671 = 0i64;
  v672 = 0i64;
  rawNewString(&v106, v116 + v1006[13] + 1);
  v671 = v106;
  v672 = (_QWORD *)v107;
  v106 = v116;
  v107 = v117;
  appendString_29(&v671, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_5;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_4;
  appendString_29(&v671, &v106);
  v16 = v1006[14];
  v106 = v1006[13];
  v107 = v16;
  appendString_29(&v671, &v106);
  v707 = v671;
  v708 = v672;
  v661 = 79i64;
  if ( v1006[13] )
  {
    v657 = 0i64;
    v658 = 0i64;
    v661 = 80i64;
    v654 = 0i64;
    v655 = 0i64;
    rawNewString(&v106, v707 + 9);
    v654 = v106;
    v655 = (_QWORD *)v107;
    v106 = TM__THWBxVSaWN2Zh7OMooFH0w_7;
    v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_6;
    appendString_29(&v654, &v106);
    v106 = v707;
    v107 = (__int64)v708;
    appendString_29(&v654, &v106);
    v657 = v654;
    v658 = v655;
    v656[0] = v654;
    v656[1] = (__int64)v655;
    log__globals_u23(v656, 1i64);
    if ( *v1007 )
      goto LABEL_1728;
    v661 = 82i64;
    if ( !v709 )
    {
      v652 = 0i64;
      v653 = 0i64;
      v661 = 83i64;
      v649 = 0i64;
      v650 = 0i64;
      rawNewString(&v106, v707 + 51);
      v649 = v106;
      v650 = v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_9;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_8;
      appendString_29(&v649, &v106);
      v106 = v707;
      v107 = (__int64)v708;
      appendString_29(&v649, &v106);
      v652 = v649;
      v653 = v650;
      v651[0] = v649;
      v651[1] = v650;
      log__globals_u23(v651, 1i64);
      if ( !*v1007 )
      {
        v661 = 84i64;
        quit__system_u8243_1(0i64);
      }
      goto LABEL_1728;
    }
    if ( v658 && (*v658 & 0x4000000000000000i64) == 0 )
      deallocShared(v658);
  }
  else
  {
    v661 = 86i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( *((_BYTE *)v1006 + 168) == 3 )
    {
      v647 = 117i64;
      v648 = &TM__THWBxVSaWN2Zh7OMooFH0w_10;
      v661 = 1542i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\strutils.nim";
      v1004 = 0i64;
      v106 = 117i64;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_10;
      v1004 = indentation__pureZstrutils_u1343(&v106);
      if ( *v1007 )
        goto LABEL_1728;
      v661 = 91i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v645 = 0i64;
      v646 = 0i64;
      v106 = v647;
      v107 = (__int64)v648;
      nsuDedent(&v645, &v106, v1004);
      if ( *v1007 )
      {
        v106 = v645;
        v107 = v646;
        eqdestroy___system_u281_34(&v106);
        goto LABEL_1728;
      }
      v661 = 1699i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      v106 = v645;
      v107 = v646;
      eqsink___system_u2667(&v709, &v106);
    }
    else
    {
      v643 = 122i64;
      v644 = &TM__THWBxVSaWN2Zh7OMooFH0w_12;
      v661 = 1542i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\strutils.nim";
      v1003 = 0i64;
      v106 = 122i64;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_12;
      v1003 = indentation__pureZstrutils_u1343(&v106);
      if ( *v1007 )
        goto LABEL_1728;
      v661 = 96i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v641 = 0i64;
      v642 = 0i64;
      v106 = v643;
      v107 = (__int64)v644;
      nsuDedent(&v641, &v106, v1003);
      if ( *v1007 )
      {
        v106 = v641;
        v107 = v642;
        eqdestroy___system_u281_34(&v106);
        goto LABEL_1728;
      }
      v661 = 1699i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      v106 = v641;
      v107 = v642;
      eqsink___system_u2667(&v709, &v106);
    }
  }
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v1006[12] = 0i64;
  v661 = 99i64;
  v17 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 1);
  v668 = *(_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435;
  v669 = v17;
  v670 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 2);
  *((_BYTE *)v1006 + 24) = 0;
  v661 = 105i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v666 = 0i64;
  v667 = 0i64;
  rawNewString(&v666, 0x4000i64);
  v661 = 1699i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  v106 = v666;
  v107 = v667;
  eqsink___system_u2667(v1006 + 1, &v106);
  v661 = 106i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 1i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_15;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_14;
  appendString_29(v1006 + 1, &v106);
  v1002 = 0;
  v1001 = 0;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
  v1065 = 0i64;
  v661 = 97i64;
  while ( v1065 <= 3 )
  {
    v1001 = v1065;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v1002 = v1065;
    v661 = 115i64;
    v639 = 0i64;
    v640 = 0i64;
    dollar___modelZsimulator95types_u23(&v639, (unsigned __int8)v1065);
    v106 = v639;
    v107 = v640;
    add__stdZenumutils_u70(&v705, &v106);
    v661 = 102i64;
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v638 = v1065 + 1;
    if ( __OFADD__(1i64, v1065) )
    {
LABEL_30:
      raiseOverflow();
      goto LABEL_1728;
    }
    v1065 = v638;
  }
  v1000 = 0;
  v999 = 0;
  v1064 = 0i64;
  v661 = 97i64;
  while ( v1064 <= 6 )
  {
    v999 = v1064;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v1000 = v1064;
    v661 = 117i64;
    v636 = 0i64;
    v637 = 0i64;
    dollar___modelZsimulator95types_u34(&v636, (unsigned __int8)v1064);
    v106 = v636;
    v107 = v637;
    add__stdZenumutils_u70(&v703, &v106);
    v661 = 102i64;
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v635 = v1064 + 1;
    if ( __OFADD__(1i64, v1064) )
      goto LABEL_30;
    v1064 = v635;
  }
  v998 = 0;
  v997 = 0;
  v1063 = 0i64;
  v661 = 97i64;
  while ( v1063 <= 14 )
  {
    v997 = v1063;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v998 = v1063;
    v661 = 119i64;
    v633 = 0i64;
    v634 = 0i64;
    dollar___modelZsimulator95types_u53(&v633, (unsigned __int8)v1063);
    v106 = v633;
    v107 = v634;
    add__stdZenumutils_u70(&v701, &v106);
    v661 = 102i64;
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v632 = v1063 + 1;
    if ( __OFADD__(1i64, v1063) )
      goto LABEL_30;
    v1063 = v632;
  }
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v664 = 0i64;
  v665 = 0i64;
  v661 = 123i64;
  dollar___systemZdollars_u14(&v699, *refptr_simulation_commands__modelZsimulator95types_u82);
  if ( *v1007 )
    goto LABEL_1728;
  v661 = 124i64;
  dollar___systemZdollars_u14(&v697, *refptr_simulation_settings__modelZsimulator95types_u83);
  if ( *v1007 )
    goto LABEL_1728;
  v661 = 125i64;
  dollar___systemZdollars_u14(&v695, *refptr_simulation_input_replay__modelZsimulator95types_u84);
  if ( *v1007 )
    goto LABEL_1728;
  v661 = 126i64;
  dollar___systemZdollars_u14(&v693, *refptr_simulation_output_history_pins__modelZsimulator95types_u85);
  if ( *v1007 )
    goto LABEL_1728;
  v661 = 127i64;
  dollar___systemZdollars_u14(&v691, *refptr_simulation_error_buffer__modelZsimulator95types_u86);
  if ( *v1007 )
    goto LABEL_1728;
  v661 = 128i64;
  dollar___systemZdollars_u14(&v689, *refptr_simulation_ui_buffer__modelZsimulator95types_u87);
  if ( *v1007 )
    goto LABEL_1728;
  v661 = 129i64;
  dollar___systemZdollars_u14(&v687, *refptr_ctl_input_replay_reset__modelZsimulator95types_u90);
  if ( *v1007 )
    goto LABEL_1728;
  v661 = 131i64;
  dollar___systemZdollars_u14(&v685, *refptr_simulation_state__modelZsimulator95types_u81);
  if ( *v1007 )
    goto LABEL_1728;
  v661 = 132i64;
  dollar___systemZdollars_u14(&v683, *refptr_simulation_keyboard_character__modelZsimulator95types_u88);
  if ( *v1007 )
    goto LABEL_1728;
  v661 = 133i64;
  dollar___systemZdollars_u14(&v681, *refptr_simulation_keyboard_coordinate__modelZsimulator95types_u89);
  if ( *v1007 )
    goto LABEL_1728;
  v661 = 136i64;
  v18 = v706 ? v706 + 8 : 0i64;
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_42;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_41;
  nsuJoinSep(&v679, v18, v705, &v106);
  if ( *v1007 )
    goto LABEL_1728;
  v661 = 137i64;
  v19 = v704 ? v704 + 8 : 0i64;
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_45;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_41;
  nsuJoinSep(&v677, v19, v703, &v106);
  if ( *v1007 )
    goto LABEL_1728;
  v661 = 138i64;
  v20 = v702 ? v702 + 8 : 0i64;
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_48;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_41;
  nsuJoinSep(&v675, v20, v701, &v106);
  if ( *v1007 )
    goto LABEL_1728;
  rawNewString(&v106, v677 + v679 + v681 + v683 + v685 + v687 + v689 + v691 + v693 + v695 + v697 + v699 + v675 + 810);
  v664 = v106;
  v665 = (_QWORD *)v107;
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_20;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_19;
  appendString_29(&v664, &v106);
  v106 = v699;
  v107 = (__int64)v700;
  appendString_29(&v664, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_22;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_21;
  appendString_29(&v664, &v106);
  v106 = v697;
  v107 = (__int64)v698;
  appendString_29(&v664, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_24;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_23;
  appendString_29(&v664, &v106);
  v106 = v695;
  v107 = (__int64)v696;
  appendString_29(&v664, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_26;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_25;
  appendString_29(&v664, &v106);
  v106 = v693;
  v107 = (__int64)v694;
  appendString_29(&v664, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_28;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_27;
  appendString_29(&v664, &v106);
  v106 = v691;
  v107 = (__int64)v692;
  appendString_29(&v664, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_30;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_29;
  appendString_29(&v664, &v106);
  v106 = v689;
  v107 = (__int64)v690;
  appendString_29(&v664, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_32;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_31;
  appendString_29(&v664, &v106);
  v106 = v687;
  v107 = (__int64)v688;
  appendString_29(&v664, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_34;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_33;
  appendString_29(&v664, &v106);
  v106 = v685;
  v107 = (__int64)v686;
  appendString_29(&v664, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_36;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_35;
  appendString_29(&v664, &v106);
  v106 = v683;
  v107 = (__int64)v684;
  appendString_29(&v664, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_38;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_37;
  appendString_29(&v664, &v106);
  v106 = v681;
  v107 = (__int64)v682;
  appendString_29(&v664, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_40;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_39;
  appendString_29(&v664, &v106);
  v106 = v679;
  v107 = (__int64)v680;
  appendString_29(&v664, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_44;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_43;
  appendString_29(&v664, &v106);
  v106 = v677;
  v107 = (__int64)v678;
  appendString_29(&v664, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_47;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_46;
  appendString_29(&v664, &v106);
  v106 = v675;
  v107 = (__int64)v676;
  appendString_29(&v664, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_50;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_49;
  appendString_29(&v664, &v106);
  v673 = v664;
  v674 = v665;
  prepareAdd(v1006 + 1, v664);
  v106 = v673;
  v107 = (__int64)v674;
  appendString_29(v1006 + 1, &v106);
  v996 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1066 = 0i64;
  v661 = 250i64;
  v995 = v1006[10];
  v994 = v995;
  v661 = 251i64;
  while ( v1066 < v994 )
  {
    nimZeroMem_66(v128, 560i64);
    v661 = 175i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( v1066 < 0 || v1066 >= v1006[10] )
    {
      raiseIndexError2(v1066, v1006[10] - 1i64);
      goto LABEL_1728;
    }
    v996 = (_QWORD *)(v1006[11] + 8 * v1066 + 8);
    v661 = 176i64;
    if ( (__int64)*v996 < 0 || *v996 >= v114 )
    {
      raiseIndexError2(*v996, v114 - 1);
      goto LABEL_1728;
    }
    qmemcpy(v128, &v115[560 * *v996 + 8], sizeof(v128));
    v993 = 0i64;
    nimZeroMem_66(&v118, 80i64);
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    v1069 = 0i64;
    v992 = v128[8];
    v991 = v128[8];
    v661 = 184i64;
    while ( v1069 < v991 )
    {
      v661 = 178i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v993 = v1069;
      if ( v1069 < 0 || v1069 >= v128[8] )
      {
        raiseIndexError2(v1069, v128[8] - 1);
        goto LABEL_1728;
      }
      v21 = (_QWORD *)(v128[9] + 80 * v1069);
      v22 = v21[2];
      v118 = v21[1];
      v119 = v22;
      v23 = v21[4];
      v120 = v21[3];
      v121 = v23;
      v24 = v21[6];
      v122 = v21[5];
      v123 = v24;
      v25 = v21[8];
      v124 = v21[7];
      v125 = v25;
      v26 = v21[10];
      v126 = v21[9];
      v127 = v26;
      v661 = 179i64;
      if ( (_BYTE)v118 == 1 )
      {
        v661 = 181i64;
        v990 = 0;
        v27 = v1006[84];
        v103 = v1006[83];
        v104 = v27;
        v105 = v1006[85];
        v100 = v119;
        v101 = v120;
        v102 = v121;
        v990 = contains__modelZsimulationZcode95gen_u313(&v103, &v100);
        if ( *v1007 )
          goto LABEL_1728;
        if ( v990 )
        {
          v661 = 184i64;
          v989 = 0i64;
          v100 = v119;
          v101 = v120;
          v102 = v121;
          v989 = X5BX5D___modelZsimulationZcode95gen_u1925(v1006 + 83, &v100);
          if ( *v1007 )
            goto LABEL_1728;
          v28 = *(_QWORD *)(v989 + 8);
          v29 = 0;
          v30 = __OFADD__(1i64, v28);
          v31 = v28 + 1;
          if ( v30 )
            v29 = 1;
          v630 = v31;
          if ( (v29 & 1) != 0 )
          {
            raiseOverflow();
            goto LABEL_1728;
          }
          *(_QWORD *)(v989 + 8) = v630;
        }
        else
        {
          v661 = 182i64;
          nimZeroMem_66(v631, 16i64);
          v631[1] = 1i64;
          v100 = v119;
          v101 = v120;
          v102 = v121;
          v106 = v631[0];
          v107 = 1i64;
          X5BX5Deq___modelZsimulationZcode95gen_u748(v1006 + 83, &v100, &v106);
          if ( *v1007 )
            goto LABEL_1728;
        }
      }
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      ++v1069;
      v661 = 187i64;
      v988 = v128[8];
      if ( v128[8] != v991 )
      {
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_53;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
        failedAssertImpl__stdZassertions_u234(&v106);
        if ( *v1007 )
          goto LABEL_1728;
      }
    }
    ++v1066;
    v661 = 254i64;
    v987 = v1006[10];
    if ( v987 != v994 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_55;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1728;
    }
  }
  nimZeroMem_66(v128, 560i64);
  v986 = 0i64;
  v1068 = 0i64;
  v985 = v114;
  v984 = v114;
  v661 = 184i64;
  while ( v1068 < v984 )
  {
    v661 = 186i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v986 = v1068;
    if ( v1068 < 0 || v1068 >= v114 )
    {
      raiseIndexError2(v1068, v114 - 1);
LABEL_1728:
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v674 && (*v674 & 0x4000000000000000i64) == 0 )
        deallocShared(v674);
      if ( v676 && (*v676 & 0x4000000000000000i64) == 0 )
        deallocShared(v676);
      if ( v678 && (*v678 & 0x4000000000000000i64) == 0 )
        deallocShared(v678);
      if ( v680 && (*v680 & 0x4000000000000000i64) == 0 )
        deallocShared(v680);
      if ( v682 && (*v682 & 0x4000000000000000i64) == 0 )
        deallocShared(v682);
      if ( v684 && (*v684 & 0x4000000000000000i64) == 0 )
        deallocShared(v684);
      if ( v686 && (*v686 & 0x4000000000000000i64) == 0 )
        deallocShared(v686);
      if ( v688 && (*v688 & 0x4000000000000000i64) == 0 )
        deallocShared(v688);
      if ( v690 && (*v690 & 0x4000000000000000i64) == 0 )
        deallocShared(v690);
      if ( v692 && (*v692 & 0x4000000000000000i64) == 0 )
        deallocShared(v692);
      if ( v694 && (*v694 & 0x4000000000000000i64) == 0 )
        deallocShared(v694);
      if ( v696 && (*v696 & 0x4000000000000000i64) == 0 )
        deallocShared(v696);
      if ( v698 && (*v698 & 0x4000000000000000i64) == 0 )
        deallocShared(v698);
      if ( v700 && (*v700 & 0x4000000000000000i64) == 0 )
        deallocShared(v700);
      v661 = 2128i64;
      v106 = v701;
      v107 = v702;
      eqdestroy___system_u3734(&v106);
      v106 = v703;
      v107 = v704;
      eqdestroy___system_u3734(&v106);
      v106 = v705;
      v107 = v706;
      eqdestroy___system_u3734(&v106);
      v661 = 394i64;
      if ( v708 && (*v708 & 0x4000000000000000i64) == 0 )
        deallocShared(v708);
      if ( v710 && (*v710 & 0x4000000000000000i64) == 0 )
        deallocShared(v710);
      goto LABEL_1776;
    }
    qmemcpy(v128, &v115[560 * v1068 + 8], sizeof(v128));
    v661 = 188i64;
    if ( !v128[41] )
      goto LABEL_203;
    v628 = 0i64;
    v629 = 0i64;
    v626 = 0i64;
    v627 = 0i64;
    v624 = 0i64;
    v625 = 0i64;
    v622 = 0i64;
    v623 = 0i64;
    v620 = 0i64;
    v621 = 0i64;
    v618 = 0i64;
    v619 = 0i64;
    v616 = 0i64;
    v617 = 0i64;
    v614 = 0i64;
    v615 = 0i64;
    v612 = 0i64;
    v613 = 0i64;
    v610 = 0i64;
    v611 = 0i64;
    v608 = 0i64;
    v609 = 0i64;
    v661 = 189i64;
    v983 = 0;
    v32 = v1006[87];
    v100 = v1006[86];
    v101 = v32;
    v102 = v1006[88];
    v983 = contains__modelZsimulationZpreorder_u28373(&v100, v128[1]);
    if ( *v1007 )
      goto LABEL_169;
    if ( v983 != 1 )
      goto LABEL_160;
    v600 = 0i64;
    v601 = 0i64;
    v598 = 0i64;
    v599 = 0i64;
    v596 = 0i64;
    v597 = 0i64;
    v594 = 0i64;
    v595 = 0i64;
    v661 = 190i64;
    v591 = 0i64;
    v592 = 0i64;
    dollar___systemZdollars_u14(&v600, v986);
    if ( *v1007 )
      goto LABEL_147;
    dollar___modelZsave95mongerZcommon_u3396(&v598, v128[2]);
    if ( *v1007 )
      goto LABEL_147;
    dollar___modelZsave95mongerZcommon_u132(&v596, LOBYTE(v128[0]));
    rawNewString(&v106, v598 + v600 + v596 + 63);
    v591 = v106;
    v592 = (_QWORD *)v107;
    v106 = TM__THWBxVSaWN2Zh7OMooFH0w_57;
    v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_56;
    appendString_29(&v591, &v106);
    v106 = v600;
    v107 = (__int64)v601;
    appendString_29(&v591, &v106);
    v106 = TM__THWBxVSaWN2Zh7OMooFH0w_59;
    v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_58;
    appendString_29(&v591, &v106);
    v106 = v598;
    v107 = (__int64)v599;
    appendString_29(&v591, &v106);
    v106 = TM__THWBxVSaWN2Zh7OMooFH0w_60;
    v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_58;
    appendString_29(&v591, &v106);
    v106 = v596;
    v107 = (__int64)v597;
    appendString_29(&v591, &v106);
    v594 = v591;
    v595 = v592;
    v593[0] = v591;
    v593[1] = (__int64)v592;
    log__globals_u23(v593, 1i64);
    if ( *v1007 )
    {
LABEL_147:
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v595 && (*v595 & 0x4000000000000000i64) == 0 )
        deallocShared(v595);
      if ( v597 && (*v597 & 0x4000000000000000i64) == 0 )
        deallocShared(v597);
      if ( v599 && (*v599 & 0x4000000000000000i64) == 0 )
        deallocShared(v599);
      if ( v601 && (*v601 & 0x4000000000000000i64) == 0 )
        deallocShared(v601);
      if ( !*v1007 )
      {
LABEL_160:
        v661 = 192i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        v606 = 0i64;
        v607 = 0i64;
        dollar___modelZsave95mongerZcommon_u3396(&v628, v128[1]);
        if ( !*v1007 )
        {
          dollar___systemZdollars_u14(&v626, v128[41]);
          if ( !*v1007 )
          {
            dollar___modelZsave95mongerZcommon_u263(&v624, v128[39]);
            if ( !*v1007 )
            {
              rawNewString(&v106, v626 + v628 + v624 + 68);
              v606 = v106;
              v607 = (_QWORD *)v107;
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_62;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_61;
              appendString_29(&v606, &v106);
              v106 = v628;
              v107 = (__int64)v629;
              appendString_29(&v606, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_64;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_63;
              appendString_29(&v606, &v106);
              v106 = v626;
              v107 = (__int64)v627;
              appendString_29(&v606, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_66;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_65;
              appendString_29(&v606, &v106);
              v106 = v624;
              v107 = (__int64)v625;
              appendString_29(&v606, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_68;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_67;
              appendString_29(&v606, &v106);
              v622 = v606;
              v623 = v607;
              prepareAdd(v1006 + 1, v606);
              v106 = v622;
              v107 = (__int64)v623;
              appendString_29(v1006 + 1, &v106);
              v661 = 193i64;
              v604 = 0i64;
              v605 = 0i64;
              dollar___modelZsave95mongerZcommon_u3396(&v620, v128[1]);
              if ( !*v1007 )
              {
                dollar___systemZdollars_u14(&v618, v128[42]);
                if ( !*v1007 )
                {
                  dollar___modelZsave95mongerZcommon_u263(&v616, v128[39]);
                  if ( !*v1007 )
                  {
                    rawNewString(&v106, v618 + v620 + v616 + 68);
                    v604 = v106;
                    v605 = (_QWORD *)v107;
                    v106 = TM__THWBxVSaWN2Zh7OMooFH0w_70;
                    v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_69;
                    appendString_29(&v604, &v106);
                    v106 = v620;
                    v107 = (__int64)v621;
                    appendString_29(&v604, &v106);
                    v106 = TM__THWBxVSaWN2Zh7OMooFH0w_72;
                    v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_71;
                    appendString_29(&v604, &v106);
                    v106 = v618;
                    v107 = (__int64)v619;
                    appendString_29(&v604, &v106);
                    v106 = TM__THWBxVSaWN2Zh7OMooFH0w_73;
                    v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_65;
                    appendString_29(&v604, &v106);
                    v106 = v616;
                    v107 = (__int64)v617;
                    appendString_29(&v604, &v106);
                    v106 = TM__THWBxVSaWN2Zh7OMooFH0w_74;
                    v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_67;
                    appendString_29(&v604, &v106);
                    v614 = v604;
                    v615 = v605;
                    prepareAdd(v1006 + 1, v604);
                    v106 = v614;
                    v107 = (__int64)v615;
                    appendString_29(v1006 + 1, &v106);
                    v661 = 194i64;
                    v602 = 0i64;
                    v603 = 0i64;
                    dollar___modelZsave95mongerZcommon_u3396(&v612, v128[1]);
                    if ( !*v1007 )
                    {
                      dollar___systemZdollars_u14(&v610, v128[43]);
                      if ( !*v1007 )
                      {
                        rawNewString(&v106, v612 + v610 + 63);
                        v602 = v106;
                        v603 = (_QWORD *)v107;
                        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_76;
                        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_75;
                        appendString_29(&v602, &v106);
                        v106 = v612;
                        v107 = (__int64)v613;
                        appendString_29(&v602, &v106);
                        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_78;
                        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_77;
                        appendString_29(&v602, &v106);
                        v106 = v610;
                        v107 = (__int64)v611;
                        appendString_29(&v602, &v106);
                        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_80;
                        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_79;
                        appendString_29(&v602, &v106);
                        v608 = v602;
                        v609 = v603;
                        prepareAdd(v1006 + 1, v602);
                        v106 = v608;
                        v107 = (__int64)v609;
                        appendString_29(v1006 + 1, &v106);
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
LABEL_169:
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v609 && (*v609 & 0x4000000000000000i64) == 0 )
        deallocShared(v609);
      if ( v611 && (*v611 & 0x4000000000000000i64) == 0 )
        deallocShared(v611);
      if ( v613 && (*v613 & 0x4000000000000000i64) == 0 )
        deallocShared(v613);
      if ( v615 && (*v615 & 0x4000000000000000i64) == 0 )
        deallocShared(v615);
      if ( v617 && (*v617 & 0x4000000000000000i64) == 0 )
        deallocShared(v617);
      if ( v619 && (*v619 & 0x4000000000000000i64) == 0 )
        deallocShared(v619);
      if ( v621 && (*v621 & 0x4000000000000000i64) == 0 )
        deallocShared(v621);
      if ( v623 && (*v623 & 0x4000000000000000i64) == 0 )
        deallocShared(v623);
      if ( v625 && (*v625 & 0x4000000000000000i64) == 0 )
        deallocShared(v625);
      if ( v627 && (*v627 & 0x4000000000000000i64) == 0 )
        deallocShared(v627);
      if ( v629 && (*v629 & 0x4000000000000000i64) == 0 )
        deallocShared(v629);
      if ( *v1007 )
        goto LABEL_1728;
LABEL_203:
      v661 = 196i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      X5BX5Deq___modelZsimulationZpreorder_u11513(v1006 + 86, v128[1], v986);
      if ( *v1007 )
        goto LABEL_1728;
      goto LABEL_204;
    }
    v661 = 394i64;
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v595 && (*v595 & 0x4000000000000000i64) == 0 )
      deallocShared(v595);
    if ( v597 && (*v597 & 0x4000000000000000i64) == 0 )
      deallocShared(v597);
    if ( v599 && (*v599 & 0x4000000000000000i64) == 0 )
      deallocShared(v599);
    if ( v601 && (*v601 & 0x4000000000000000i64) == 0 )
      deallocShared(v601);
    if ( v609 && (*v609 & 0x4000000000000000i64) == 0 )
      deallocShared(v609);
    if ( v611 && (*v611 & 0x4000000000000000i64) == 0 )
      deallocShared(v611);
    if ( v613 && (*v613 & 0x4000000000000000i64) == 0 )
      deallocShared(v613);
    if ( v615 && (*v615 & 0x4000000000000000i64) == 0 )
      deallocShared(v615);
    if ( v617 && (*v617 & 0x4000000000000000i64) == 0 )
      deallocShared(v617);
    if ( v619 && (*v619 & 0x4000000000000000i64) == 0 )
      deallocShared(v619);
    if ( v621 && (*v621 & 0x4000000000000000i64) == 0 )
      deallocShared(v621);
    if ( v623 && (*v623 & 0x4000000000000000i64) == 0 )
      deallocShared(v623);
    if ( v625 && (*v625 & 0x4000000000000000i64) == 0 )
      deallocShared(v625);
    if ( v627 && (*v627 & 0x4000000000000000i64) == 0 )
      deallocShared(v627);
    if ( v629 && (*v629 & 0x4000000000000000i64) == 0 )
      deallocShared(v629);
    v661 = 191i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
LABEL_204:
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1068;
    v661 = 187i64;
    v982 = v114;
    if ( v114 != v984 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_81;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1728;
    }
  }
  nimZeroMem_66(&v118, 40i64);
  v589 = 0i64;
  v590 = 0i64;
  v587 = 0i64;
  v588 = 0i64;
  v585 = 0i64;
  v586 = 0i64;
  v583 = 0i64;
  v584 = 0i64;
  v581 = 0i64;
  v582 = 0i64;
  v579 = 0i64;
  v580 = 0i64;
  v577 = 0i64;
  v578 = 0i64;
  v575 = 0i64;
  v576 = 0i64;
  v573 = 0i64;
  v574 = 0i64;
  v571 = 0i64;
  v572 = 0i64;
  v569 = 0i64;
  v570 = 0i64;
  v567 = 0i64;
  v568 = 0i64;
  v565 = 0i64;
  v566 = 0i64;
  v563 = 0i64;
  v564 = 0i64;
  nimZeroMem_66(&v560, 24i64);
  v558 = 0i64;
  v559 = 0i64;
  v556 = 0i64;
  v557 = 0i64;
  v554 = 0i64;
  v555 = 0i64;
  v552 = 0i64;
  v553 = 0i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  v1006[12] = 8i64;
  v661 = 1409i64;
  prepareAdd(v1006 + 1, 39i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_83;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_82;
  appendString_29(v1006 + 1, &v106);
  v981 = 0;
  v980 = 0;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
  v1072 = 0i64;
  v661 = 97i64;
  while ( v1072 <= 124 )
  {
    v980 = v1072;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v981 = v1072;
    v661 = 1416i64;
    if ( ((TM__THWBxVSaWN2Zh7OMooFH0w_84[(unsigned __int8)v1072 >> 3] >> (v1072 & 7)) & 1) != 0 )
    {
      v661 = 1417i64;
    }
    else
    {
      v661 = 1418i64;
      v979 = 0i64;
      v979 = (_BYTE *)X5BX5D___modelZboardZprototype95list_u4239(
                        refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
                        v981);
      if ( *v1007 )
        goto LABEL_1691;
      if ( *v979 == 5 )
      {
        v661 = 1419i64;
      }
      else
      {
        v661 = 1420i64;
        X5BX5Deq___modelZboardZschematics_u2426(&v118, v981, 0i64);
        if ( *v1007 )
          goto LABEL_1691;
      }
    }
    v661 = 102i64;
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v538 = v1072 + 1;
    if ( __OFADD__(1i64, v1072) )
    {
LABEL_234:
      raiseOverflow();
      goto LABEL_1691;
    }
    v1072 = v538;
  }
  v1067 = 0i64;
  v978 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1071 = 0i64;
  v977 = v114;
  v976 = v114;
  v661 = 251i64;
  while ( v1071 < v976 )
  {
    v661 = 1423i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( v1071 < 0 || v1071 >= v114 )
    {
      raiseIndexError2(v1071, v114 - 1);
      goto LABEL_1691;
    }
    v978 = &v115[560 * v1071 + 8];
    v661 = 1424i64;
    if ( ((TM__THWBxVSaWN2Zh7OMooFH0w_84[(unsigned __int8)*v978 >> 3] >> (*v978 & 7)) & 1) != 0 )
    {
      v661 = 1425i64;
    }
    else
    {
      v661 = 1426i64;
      if ( v978[32] != 1 )
      {
        v661 = 1428i64;
        v975 = 0i64;
        v975 = (_BYTE *)X5BX5D___modelZboardZprototype95list_u4239(
                          refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
                          (unsigned __int8)*v978);
        if ( *v1007 )
          goto LABEL_1691;
        if ( *v975 == 5 )
        {
          v661 = 1429i64;
        }
        else
        {
          v661 = 1430i64;
          v974 = 0i64;
          v974 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(&v118, (unsigned __int8)*v978);
          if ( *v1007 )
            goto LABEL_1691;
          v33 = __OFADD__(1i64, *v974);
          v537 = *v974 + 1i64;
          if ( v33 )
            goto LABEL_234;
          *v974 = v537;
          v661 = 1431i64;
          v536 = v1067 + 1;
          if ( __OFADD__(1i64, v1067) )
            goto LABEL_234;
          v1067 = v536;
        }
      }
      else
      {
        v661 = 1427i64;
      }
    }
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1071;
    v661 = 254i64;
    v973 = v114;
    if ( v114 != v976 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_88;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v972 = 0;
  v971 = 0i64;
  v661 = 1819i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
  v970 = len__modelZboardZschematics_u3722_1(&v118);
  if ( *v1007 )
    goto LABEL_1691;
  v661 = 1387i64;
  if ( v120 > 0 )
  {
    v1070 = v121;
    v661 = 1389i64;
    while ( 1 )
    {
      if ( v1070 < 0 )
        goto LABEL_260;
      v661 = 1390i64;
      if ( v1070 >= v118 )
        break;
      v969 = *(_QWORD *)(v119 + 32 * v1070 + 16);
      v661 = 1391i64;
      if ( v1070 >= v118 )
        break;
      v968 = 0;
      v968 = isFilled__pureZcollectionsZtables_u31_9(*(_QWORD *)(v119 + 32 * v1070 + 8));
      if ( *v1007 )
        goto LABEL_1691;
      if ( v968 == 1 )
      {
        v661 = 1434i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        if ( v1070 < 0 )
          break;
        if ( v1070 >= v118 )
          break;
        v972 = *(_BYTE *)(v119 + 32 * v1070 + 24);
        if ( v1070 >= v118 )
          break;
        v971 = *(_QWORD *)(v119 + 32 * v1070 + 32);
        v661 = 1435i64;
        v534 = 0i64;
        v535 = 0i64;
        dollar___modelZsave95mongerZcommon_u132(&v534, v972);
        v106 = v534;
        v107 = v535;
        add__stdZenumutils_u70(&v587, &v106);
        v661 = 1436i64;
        v532 = 0i64;
        v533 = 0i64;
        dollar___systemZdollars_u14(&v532, v971);
        if ( *v1007 )
        {
          v106 = v532;
          v107 = v533;
          eqdestroy___system_u281_34(&v106);
          goto LABEL_1691;
        }
        v106 = v532;
        v107 = v533;
        add__stdZenumutils_u70(&v589, &v106);
        v661 = 1822i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
        v967 = 0i64;
        v967 = len__modelZboardZschematics_u3722_1(&v118);
        if ( *v1007 )
          goto LABEL_1691;
        if ( v967 != v970 )
        {
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_90;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_89;
          failedAssertImpl__stdZassertions_u234(&v106);
          if ( *v1007 )
            goto LABEL_1691;
        }
      }
      v661 = 1393i64;
      v1070 = v969;
    }
    raiseIndexError2(v1070, v118 - 1);
    goto LABEL_1691;
  }
LABEL_260:
  v661 = 1438i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 250i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_92;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_91;
  appendString_29(v1006 + 1, &v106);
  v661 = 1454i64;
  if ( v588 )
    v34 = v588 + 8;
  else
    v34 = 0i64;
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_93;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_41;
  nsuJoinSep(&v585, v34, v587, &v106);
  if ( *v1007 )
    goto LABEL_1691;
  prepareAdd(v1006 + 1, v585);
  v106 = v585;
  v107 = (__int64)v586;
  appendString_29(v1006 + 1, &v106);
  v550 = 0i64;
  v551 = 0i64;
  v661 = 1462i64;
  dollar___systemZdollars_u14(&v583, a8);
  if ( *v1007 )
    goto LABEL_1691;
  v661 = 1464i64;
  dollar___systemZdollars_u14(&v581, a9);
  if ( *v1007 )
    goto LABEL_1691;
  v661 = 1466i64;
  dollar___systemZdollars_u14(&v579, v1067);
  if ( *v1007 )
    goto LABEL_1691;
  v661 = 1470i64;
  v35 = v590 ? v590 + 8 : 0i64;
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_102;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_41;
  nsuJoinSep(&v577, v35, v589, &v106);
  if ( *v1007 )
    goto LABEL_1691;
  rawNewString(&v106, v579 + v581 + v583 + v577 + 401);
  v550 = v106;
  v551 = (_QWORD *)v107;
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_95;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_94;
  appendString_29(&v550, &v106);
  v106 = v583;
  v107 = (__int64)v584;
  appendString_29(&v550, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_97;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_96;
  appendString_29(&v550, &v106);
  v106 = v581;
  v107 = (__int64)v582;
  appendString_29(&v550, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_99;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_98;
  appendString_29(&v550, &v106);
  v106 = v579;
  v107 = (__int64)v580;
  appendString_29(&v550, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_101;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_100;
  appendString_29(&v550, &v106);
  v106 = v577;
  v107 = (__int64)v578;
  appendString_29(&v550, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_104;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_103;
  appendString_29(&v550, &v106);
  v575 = v550;
  v576 = v551;
  prepareAdd(v1006 + 1, v550);
  v106 = v575;
  v107 = (__int64)v576;
  appendString_29(v1006 + 1, &v106);
  v966 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1074 = 0i64;
  v661 = 250i64;
  v965 = v1006[27];
  v964 = v965;
  v661 = 251i64;
  while ( v1074 < v964 )
  {
    v661 = 1480i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( v1074 < 0 || v1074 >= v1006[27] )
    {
      raiseIndexError2(v1074, v1006[27] - 1i64);
      goto LABEL_1691;
    }
    v966 = v1006[28] + 304 * v1074 + 8;
    v963 = 0i64;
    v962 = 0i64;
    v961 = 0i64;
    v960 = 0i64;
    v959 = 0i64;
    v958 = 0i64;
    v957 = 0i64;
    v530 = 0i64;
    v531 = 0i64;
    v528 = 0i64;
    v529 = 0i64;
    v661 = 1481i64;
    if ( *(_QWORD *)v966 )
    {
      v661 = 1484i64;
      switch ( *(_BYTE *)(v966 + 32) )
      {
        case 0:
          v661 = 1486i64;
          if ( (*(_BYTE *)(v966 + 32) & 7) == 0 )
          {
            v963 = *(_QWORD *)(v966 + 48);
            v1062 = v963;
            goto LABEL_300;
          }
          dollar___modelZmodel95types_u218(v713, *(unsigned __int8 *)(v966 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_106;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_105;
          v98 = v713[0];
          v99 = (char *)v713[1];
          raiseFieldErrorStr(&v106, &v98);
          break;
        case 1:
          v661 = 1488i64;
          if ( (*(_BYTE *)(v966 + 32) & 7) == 1i64 )
          {
            v962 = *(_QWORD *)(v966 + 48);
            v1062 = v962;
            goto LABEL_300;
          }
          dollar___modelZmodel95types_u218(v714, *(unsigned __int8 *)(v966 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_108;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_107;
          v98 = v714[0];
          v99 = (char *)v714[1];
          raiseFieldErrorStr(&v106, &v98);
          break;
        case 2:
          v661 = 1490i64;
          if ( (*(_BYTE *)(v966 + 32) & 7) == 2i64 )
          {
            v961 = *(_QWORD *)(v966 + 48);
            v1062 = v961;
            goto LABEL_300;
          }
          dollar___modelZmodel95types_u218(v715, *(unsigned __int8 *)(v966 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_110;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_109;
          v98 = v715[0];
          v99 = (char *)v715[1];
          raiseFieldErrorStr(&v106, &v98);
          break;
        case 3:
          v661 = 1492i64;
          if ( (*(_BYTE *)(v966 + 32) & 7) == 3i64 )
          {
            v960 = *(_QWORD *)(v966 + 48);
            v1062 = v960;
            goto LABEL_300;
          }
          dollar___modelZmodel95types_u218(v716, *(unsigned __int8 *)(v966 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_112;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_111;
          v98 = v716[0];
          v99 = (char *)v716[1];
          raiseFieldErrorStr(&v106, &v98);
          break;
        case 4:
          v661 = 1494i64;
          if ( (*(_BYTE *)(v966 + 32) & 7) == 4i64 )
          {
            v959 = *(_QWORD *)(v966 + 48);
            v1062 = v959;
            goto LABEL_300;
          }
          dollar___modelZmodel95types_u218(v717, *(unsigned __int8 *)(v966 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_114;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_113;
          v98 = v717[0];
          v99 = (char *)v717[1];
          raiseFieldErrorStr(&v106, &v98);
          break;
        case 5:
          v661 = 1498i64;
          if ( (*(_BYTE *)(v966 + 32) & 7) == 5i64 )
          {
            v957 = *(_QWORD *)(v966 + 48);
            v1062 = v957;
            goto LABEL_300;
          }
          dollar___modelZmodel95types_u218(v719, *(unsigned __int8 *)(v966 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_118;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_117;
          v98 = v719[0];
          v99 = (char *)v719[1];
          raiseFieldErrorStr(&v106, &v98);
          break;
        case 6:
          v661 = 1496i64;
          if ( (*(_BYTE *)(v966 + 32) & 7) == 6i64 )
          {
            v958 = *(_QWORD *)(v966 + 48);
            v1062 = v958;
LABEL_300:
            v661 = 1500i64;
            v526 = 0i64;
            v527 = 0i64;
            dollar___systemZdollars_u14(&v530, v1062);
            if ( !*v1007 )
            {
              rawNewString(&v106, *(_QWORD *)v966 + v530 + 66);
              v526 = v106;
              v527 = (_QWORD *)v107;
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_120;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
              appendString_29(&v526, &v106);
              v36 = *(_QWORD *)(v966 + 8);
              v106 = *(_QWORD *)v966;
              v107 = v36;
              appendString_29(&v526, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_122;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_121;
              appendString_29(&v526, &v106);
              v106 = v530;
              v107 = (__int64)v531;
              appendString_29(&v526, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_124;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_123;
              appendString_29(&v526, &v106);
              v528 = v526;
              v529 = v527;
              prepareAdd(v1006 + 1, v526);
              v106 = v528;
              v107 = (__int64)v529;
              appendString_29(v1006 + 1, &v106);
            }
          }
          else
          {
            dollar___modelZmodel95types_u218(v718, *(unsigned __int8 *)(v966 + 32));
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_116;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_115;
            v98 = v718[0];
            v99 = (char *)v718[1];
            raiseFieldErrorStr(&v106, &v98);
          }
          break;
      }
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v529 && (*v529 & 0x4000000000000000i64) == 0 )
        deallocShared(v529);
      if ( v531 && (*v531 & 0x4000000000000000i64) == 0 )
        deallocShared(v531);
      if ( *v1007 )
        goto LABEL_1691;
    }
    else
    {
      v661 = 1482i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    }
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1074;
    v661 = 254i64;
    v956 = v1006[27];
    if ( v956 != v964 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_125;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v661 = 1504i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 60i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_127;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_126;
  appendString_29(v1006 + 1, &v106);
  v955 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1061 = 0i64;
  v661 = 250i64;
  v954 = v1006[27];
  v953 = v954;
  v661 = 251i64;
  while ( 2 )
  {
    if ( v1061 < v953 )
    {
      v661 = 1512i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      if ( v1061 < 0 || v1061 >= v1006[27] )
      {
        raiseIndexError2(v1061, v1006[27] - 1i64);
        goto LABEL_1691;
      }
      v955 = v1006[28] + 304 * v1061 + 8;
      v952 = 0i64;
      v951 = 0i64;
      v524 = 0i64;
      v525 = 0i64;
      v522 = 0i64;
      v523 = 0i64;
      v661 = 1513i64;
      if ( !*(_QWORD *)v955 )
      {
        v661 = 1514i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
LABEL_338:
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v1061;
        v661 = 254i64;
        v950 = v1006[27];
        if ( v950 != v953 )
        {
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_134;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
          failedAssertImpl__stdZassertions_u234(&v106);
          if ( *v1007 )
            goto LABEL_1691;
        }
        continue;
      }
      v661 = 1516i64;
      v37 = *(unsigned __int8 *)(v955 + 32);
      if ( v37 == 1 )
      {
        v661 = 1518i64;
        if ( (*(_BYTE *)(v955 + 32) & 7) == 1i64 )
        {
          v952 = *(_QWORD *)(v955 + 64);
          v1060 = v952;
          goto LABEL_329;
        }
        dollar___modelZmodel95types_u218(v720, *(unsigned __int8 *)(v955 + 32));
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_128;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_107;
        v98 = v720[0];
        v99 = (char *)v720[1];
        raiseFieldErrorStr(&v106, &v98);
      }
      else
      {
        if ( v37 != 3 )
        {
          v661 = 1522i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
          goto LABEL_338;
        }
        v661 = 1520i64;
        if ( (*(_BYTE *)(v955 + 32) & 7) != 3i64 )
        {
          dollar___modelZmodel95types_u218(v721, *(unsigned __int8 *)(v955 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_129;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_111;
          v98 = v721[0];
          v99 = (char *)v721[1];
          raiseFieldErrorStr(&v106, &v98);
          goto LABEL_331;
        }
        v951 = *(_QWORD *)(v955 + 64);
        v1060 = v951;
LABEL_329:
        v661 = 1524i64;
        v520 = 0i64;
        v521 = 0i64;
        dollar___systemZdollars_u14(&v524, v1060);
        if ( !*v1007 )
        {
          rawNewString(&v106, *(_QWORD *)v955 + v524 + 47);
          v520 = v106;
          v521 = (_QWORD *)v107;
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_130;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
          appendString_29(&v520, &v106);
          v38 = *(_QWORD *)(v955 + 8);
          v106 = *(_QWORD *)v955;
          v107 = v38;
          appendString_29(&v520, &v106);
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_131;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_121;
          appendString_29(&v520, &v106);
          v106 = v524;
          v107 = (__int64)v525;
          appendString_29(&v520, &v106);
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_133;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_132;
          appendString_29(&v520, &v106);
          v522 = v520;
          v523 = v521;
          prepareAdd(v1006 + 1, v520);
          v106 = v522;
          v107 = (__int64)v523;
          appendString_29(v1006 + 1, &v106);
        }
      }
LABEL_331:
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v523 && (*v523 & 0x4000000000000000i64) == 0 )
        deallocShared(v523);
      if ( v525 && (*v525 & 0x4000000000000000i64) == 0 )
        deallocShared(v525);
      if ( *v1007 )
        goto LABEL_1691;
      goto LABEL_338;
    }
    break;
  }
  v661 = 1528i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 62i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_136;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_135;
  appendString_29(v1006 + 1, &v106);
  v949 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1059 = 0i64;
  v661 = 250i64;
  v948 = v1006[27];
  v947 = v948;
  v661 = 251i64;
  while ( 2 )
  {
    if ( v1059 < v947 )
    {
      v661 = 1536i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      if ( v1059 < 0 || v1059 >= v1006[27] )
      {
        raiseIndexError2(v1059, v1006[27] - 1i64);
        goto LABEL_1691;
      }
      v949 = v1006[28] + 304 * v1059 + 8;
      v518 = 0i64;
      v519 = 0i64;
      v516 = 0i64;
      v517 = 0i64;
      v661 = 1537i64;
      if ( !*(_QWORD *)v949 )
      {
        v661 = 1538i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
LABEL_395:
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v1059;
        v661 = 254i64;
        v936 = v1006[27];
        if ( v936 != v947 )
        {
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_151;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
          failedAssertImpl__stdZassertions_u234(&v106);
          if ( *v1007 )
            goto LABEL_1691;
        }
        continue;
      }
      v661 = 1540i64;
      if ( *(_BYTE *)(v949 + 32) == 5 )
      {
        v512 = 0i64;
        v513 = 0i64;
        v661 = 1699i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v39 = *(_QWORD *)(v949 + 8);
        v106 = *(_QWORD *)v949;
        v107 = v39;
        eqcopy___system_u2661(&v512, &v106);
        v946 = 0i64;
        v510 = 0i64;
        v511 = 0i64;
        v508 = 0i64;
        v509 = 0i64;
        v661 = 635i64;
        v662 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
        if ( (*(_BYTE *)(v949 + 32) & 7) != 5i64 )
        {
          dollar___modelZmodel95types_u218(v722, *(unsigned __int8 *)(v949 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_137;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_117;
          v98 = v722[0];
          v99 = (char *)v722[1];
          raiseFieldErrorStr(&v106, &v98);
          goto LABEL_388;
        }
        v40 = *(_QWORD *)(v949 + 208);
        v106 = *(_QWORD *)(v949 + 200);
        v107 = v40;
        eqcopy___modelZmodel95types_u2915(&v508, &v106);
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v1058 = 0i64;
        v945 = v508;
        v944 = v508;
        v661 = 184i64;
        while ( v1058 < v944 )
        {
          v946 = v1058;
          v661 = 635i64;
          v662 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
          if ( v1058 < 0 || v1058 >= v508 )
          {
            raiseIndexError2(v1058, v508 - 1);
            goto LABEL_388;
          }
          v41 = v509 + 16 * v1058;
          v42 = *(_QWORD *)(v41 + 16);
          v106 = *(_QWORD *)(v41 + 8);
          v107 = v42;
          eqcopy___modelZmodel95types_u2936(&v510, &v106);
          nimZeroMem_66(v128, 40i64);
          v943 = 0i64;
          v661 = 1543i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
          nimZeroMem_66(v128, 40i64);
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          v1057 = 0i64;
          v942 = v510;
          v941 = v510;
          v661 = 184i64;
          while ( v1057 < v941 )
          {
            v506 = 0i64;
            v507 = 0i64;
            v504 = 0i64;
            v505 = 0i64;
            v502 = 0i64;
            v503 = 0i64;
            v500 = 0i64;
            v501 = 0i64;
            v943 = v1057;
            v661 = 934i64;
            v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v1057 < 0 || v1057 >= v510 )
            {
              raiseIndexError2(v1057, v510 - 1);
              goto LABEL_388;
            }
            eqcopy___modelZmodel95types_u3002(v128, v511 + 40 * v1057 + 8);
            v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
            v940 = v128[1];
            v498 = 0i64;
            v499 = 0i64;
            v661 = 1546i64;
            dollar___systemZdollars_u14(&v506, v946);
            if ( *v1007 )
              goto LABEL_388;
            dollar___systemZdollars_u14(&v504, v943);
            if ( *v1007 )
              goto LABEL_388;
            v661 = 1547i64;
            dollar___systemZdollars_u14(&v502, v940);
            if ( *v1007 )
              goto LABEL_388;
            rawNewString(&v106, v504 + v506 + v512 + v502 + 51);
            v498 = v106;
            v499 = (_QWORD *)v107;
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_138;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
            appendString_29(&v498, &v106);
            v106 = v512;
            v107 = (__int64)v513;
            appendString_29(&v498, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_140;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_139;
            appendString_29(&v498, &v106);
            v106 = v506;
            v107 = (__int64)v507;
            appendString_29(&v498, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_142;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_141;
            appendString_29(&v498, &v106);
            v106 = v504;
            v107 = (__int64)v505;
            appendString_29(&v498, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_144;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_143;
            appendString_29(&v498, &v106);
            v106 = v502;
            v107 = (__int64)v503;
            appendString_29(&v498, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_145;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_132;
            appendString_29(&v498, &v106);
            v500 = v498;
            v501 = v499;
            prepareAdd(v1006 + 1, v498);
            v106 = v500;
            v107 = (__int64)v501;
            appendString_29(v1006 + 1, &v106);
            v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v1057;
            v661 = 187i64;
            v939 = v510;
            if ( v510 != v941 )
            {
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_146;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
              failedAssertImpl__stdZassertions_u234(&v106);
              if ( *v1007 )
                goto LABEL_388;
            }
            v661 = 394i64;
            v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v501 && (*v501 & 0x4000000000000000i64) == 0 )
              deallocShared(v501);
            if ( v503 && (*v503 & 0x4000000000000000i64) == 0 )
              deallocShared(v503);
            if ( v505 && (*v505 & 0x4000000000000000i64) == 0 )
              deallocShared(v505);
            if ( v507 && (*v507 & 0x4000000000000000i64) == 0 )
              deallocShared(v507);
          }
          v661 = 934i64;
          eqdestroy___modelZmodel95types_u2999(v128);
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          ++v1058;
          v661 = 187i64;
          v938 = v508;
          if ( v508 != v944 )
          {
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_147;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
            failedAssertImpl__stdZassertions_u234(&v106);
            if ( *v1007 )
              goto LABEL_388;
          }
        }
        v661 = 635i64;
        v662 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
        v106 = v508;
        v107 = v509;
        eqdestroy___modelZmodel95types_u2912(&v106);
        v106 = v510;
        v107 = v511;
        eqdestroy___modelZmodel95types_u2933(&v106);
        v661 = 394i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v513 && (*v513 & 0x4000000000000000i64) == 0 )
          deallocShared(v513);
      }
      v661 = 1549i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v937 = *(_QWORD *)(v949 + 24);
      v661 = 1551i64;
      v514 = 0i64;
      v515 = 0i64;
      dollar___systemZdollars_u14(&v518, v937);
      if ( !*v1007 )
      {
        rawNewString(&v106, *(_QWORD *)v949 + v518 + 47);
        v514 = v106;
        v515 = (_QWORD *)v107;
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_148;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
        appendString_29(&v514, &v106);
        v43 = *(_QWORD *)(v949 + 8);
        v106 = *(_QWORD *)v949;
        v107 = v43;
        appendString_29(&v514, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_149;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_121;
        appendString_29(&v514, &v106);
        v106 = v518;
        v107 = (__int64)v519;
        appendString_29(&v514, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_150;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_132;
        appendString_29(&v514, &v106);
        v516 = v514;
        v517 = v515;
        prepareAdd(v1006 + 1, v514);
        v106 = v516;
        v107 = (__int64)v517;
        appendString_29(v1006 + 1, &v106);
      }
LABEL_388:
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v517 && (*v517 & 0x4000000000000000i64) == 0 )
        deallocShared(v517);
      if ( v519 && (*v519 & 0x4000000000000000i64) == 0 )
        deallocShared(v519);
      if ( *v1007 )
        goto LABEL_1691;
      goto LABEL_395;
    }
    break;
  }
  v661 = 1555i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 59i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_153;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_152;
  appendString_29(v1006 + 1, &v106);
  v935 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1056 = 0i64;
  v661 = 250i64;
  v934 = v1006[27];
  v933 = v934;
  v661 = 251i64;
  while ( v1056 < v933 )
  {
    v661 = 1563i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( v1056 < 0 || v1056 >= v1006[27] )
    {
      raiseIndexError2(v1056, v1006[27] - 1i64);
      goto LABEL_1691;
    }
    v935 = v1006[28] + 304 * v1056 + 8;
    v932 = 0i64;
    v931 = 0i64;
    v930 = 0i64;
    v929 = 0i64;
    v928 = 0i64;
    v927 = 0i64;
    v496 = 0i64;
    v497 = 0i64;
    v494 = 0i64;
    v495 = 0i64;
    v661 = 1564i64;
    if ( *(_QWORD *)v935 )
    {
      v661 = 1567i64;
      switch ( *(_BYTE *)(v935 + 32) )
      {
        case 0:
          v661 = 1569i64;
          if ( (*(_BYTE *)(v935 + 32) & 7) != 0 )
          {
            dollar___modelZmodel95types_u218(v723, *(unsigned __int8 *)(v935 + 32));
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_154;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_105;
            v98 = v723[0];
            v99 = (char *)v723[1];
            raiseFieldErrorStr(&v106, &v98);
            goto LABEL_428;
          }
          v932 = *(_QWORD *)(v935 + 96);
          v1055 = v932;
          goto LABEL_426;
        case 1:
          v661 = 1571i64;
          if ( (*(_BYTE *)(v935 + 32) & 7) != 1i64 )
          {
            dollar___modelZmodel95types_u218(v724, *(unsigned __int8 *)(v935 + 32));
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_155;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_107;
            v98 = v724[0];
            v99 = (char *)v724[1];
            raiseFieldErrorStr(&v106, &v98);
            goto LABEL_428;
          }
          v931 = *(_QWORD *)(v935 + 96);
          v1055 = v931;
          goto LABEL_426;
        case 2:
          v661 = 1573i64;
          if ( (*(_BYTE *)(v935 + 32) & 7) != 2i64 )
          {
            dollar___modelZmodel95types_u218(v725, *(unsigned __int8 *)(v935 + 32));
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_156;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_109;
            v98 = v725[0];
            v99 = (char *)v725[1];
            raiseFieldErrorStr(&v106, &v98);
            goto LABEL_428;
          }
          v930 = *(_QWORD *)(v935 + 80);
          v1055 = v930;
          goto LABEL_426;
        case 3:
          v661 = 1575i64;
          if ( (*(_BYTE *)(v935 + 32) & 7) != 3i64 )
          {
            dollar___modelZmodel95types_u218(v726, *(unsigned __int8 *)(v935 + 32));
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_157;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_111;
            v98 = v726[0];
            v99 = (char *)v726[1];
            raiseFieldErrorStr(&v106, &v98);
            goto LABEL_428;
          }
          v929 = *(_QWORD *)(v935 + 96);
          v1055 = v929;
          goto LABEL_426;
        case 5:
          v661 = 1579i64;
          if ( (*(_BYTE *)(v935 + 32) & 7) != 5i64 )
          {
            dollar___modelZmodel95types_u218(v728, *(unsigned __int8 *)(v935 + 32));
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_159;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_117;
            v98 = v728[0];
            v99 = (char *)v728[1];
            raiseFieldErrorStr(&v106, &v98);
            goto LABEL_428;
          }
          v927 = *(_QWORD *)(v935 + 112);
          v1055 = v927;
          goto LABEL_426;
        case 6:
          v661 = 1577i64;
          if ( (*(_BYTE *)(v935 + 32) & 7) == 6i64 )
          {
            v928 = *(_QWORD *)(v935 + 112);
            v1055 = v928;
LABEL_426:
            v661 = 1583i64;
            v492 = 0i64;
            v493 = 0i64;
            dollar___systemZdollars_u14(&v496, v1055);
            if ( !*v1007 )
            {
              rawNewString(&v106, *(_QWORD *)v935 + v496 + 47);
              v492 = v106;
              v493 = (_QWORD *)v107;
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_160;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
              appendString_29(&v492, &v106);
              v44 = *(_QWORD *)(v935 + 8);
              v106 = *(_QWORD *)v935;
              v107 = v44;
              appendString_29(&v492, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_161;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_121;
              appendString_29(&v492, &v106);
              v106 = v496;
              v107 = (__int64)v497;
              appendString_29(&v492, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_162;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_132;
              appendString_29(&v492, &v106);
              v494 = v492;
              v495 = v493;
              prepareAdd(v1006 + 1, v492);
              v106 = v494;
              v107 = (__int64)v495;
              appendString_29(v1006 + 1, &v106);
            }
          }
          else
          {
            dollar___modelZmodel95types_u218(v727, *(unsigned __int8 *)(v935 + 32));
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_158;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_115;
            v98 = v727[0];
            v99 = (char *)v727[1];
            raiseFieldErrorStr(&v106, &v98);
          }
LABEL_428:
          v661 = 394i64;
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v495 && (*v495 & 0x4000000000000000i64) == 0 )
            deallocShared(v495);
          if ( v497 && (*v497 & 0x4000000000000000i64) == 0 )
            deallocShared(v497);
          if ( !*v1007 )
            goto LABEL_435;
          goto LABEL_1691;
        default:
          v661 = 1581i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
          goto LABEL_435;
      }
    }
    v661 = 1565i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
LABEL_435:
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1056;
    v661 = 254i64;
    v926 = v1006[27];
    if ( v926 != v933 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_163;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v661 = 1587i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 73i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_165;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_164;
  appendString_29(v1006 + 1, &v106);
  v925 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1054 = 0i64;
  v661 = 250i64;
  v924 = v1006[27];
  v923 = v924;
  v661 = 251i64;
  while ( v1054 < v923 )
  {
    v661 = 1595i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( v1054 < 0 || v1054 >= v1006[27] )
    {
      raiseIndexError2(v1054, v1006[27] - 1i64);
      goto LABEL_1691;
    }
    v925 = v1006[28] + 304 * v1054 + 8;
    v922 = 0i64;
    v490 = 0i64;
    v491 = 0i64;
    v488 = 0i64;
    v489 = 0i64;
    v661 = 1596i64;
    if ( *(_QWORD *)v925 )
    {
      v661 = 1599i64;
      if ( *(_BYTE *)(v925 + 32) == 6 )
      {
        v661 = 1601i64;
        if ( (*(_BYTE *)(v925 + 32) & 7) == 6i64 )
        {
          v922 = *(_QWORD *)(v925 + 176);
          v921 = v922;
          v661 = 1605i64;
          v486 = 0i64;
          v487 = 0i64;
          dollar___systemZdollars_u14(&v490, v922);
          if ( !*v1007 )
          {
            rawNewString(&v106, *(_QWORD *)v925 + v490 + 47);
            v486 = v106;
            v487 = (_QWORD *)v107;
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_167;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
            appendString_29(&v486, &v106);
            v45 = *(_QWORD *)(v925 + 8);
            v106 = *(_QWORD *)v925;
            v107 = v45;
            appendString_29(&v486, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_168;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_121;
            appendString_29(&v486, &v106);
            v106 = v490;
            v107 = (__int64)v491;
            appendString_29(&v486, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_169;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_132;
            appendString_29(&v486, &v106);
            v488 = v486;
            v489 = v487;
            prepareAdd(v1006 + 1, v486);
            v106 = v488;
            v107 = (__int64)v489;
            appendString_29(v1006 + 1, &v106);
          }
        }
        else
        {
          dollar___modelZmodel95types_u218(v729, *(unsigned __int8 *)(v925 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_166;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_115;
          v98 = v729[0];
          v99 = (char *)v729[1];
          raiseFieldErrorStr(&v106, &v98);
        }
        v661 = 394i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v489 && (*v489 & 0x4000000000000000i64) == 0 )
          deallocShared(v489);
        if ( v491 && (*v491 & 0x4000000000000000i64) == 0 )
          deallocShared(v491);
        if ( *v1007 )
          goto LABEL_1691;
      }
      else
      {
        v661 = 1603i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      }
    }
    else
    {
      v661 = 1597i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    }
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1054;
    v661 = 254i64;
    v920 = v1006[27];
    if ( v920 != v923 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_170;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v661 = 1609i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 70i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_172;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_171;
  appendString_29(v1006 + 1, &v106);
  v919 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1053 = 0i64;
  v661 = 250i64;
  v918 = v1006[27];
  v917 = v918;
  v661 = 251i64;
  while ( 2 )
  {
    if ( v1053 < v917 )
    {
      v661 = 1617i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      if ( v1053 < 0 || v1053 >= v1006[27] )
      {
        raiseIndexError2(v1053, v1006[27] - 1i64);
        goto LABEL_1691;
      }
      v919 = v1006[28] + 304 * v1053 + 8;
      v916 = 0i64;
      v915 = 0i64;
      v484 = 0i64;
      v485 = 0i64;
      v482 = 0i64;
      v483 = 0i64;
      v661 = 1618i64;
      if ( !*(_QWORD *)v919 )
      {
        v661 = 1619i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
LABEL_489:
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v1053;
        v661 = 254i64;
        v914 = v1006[27];
        if ( v914 != v917 )
        {
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_178;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
          failedAssertImpl__stdZassertions_u234(&v106);
          if ( *v1007 )
            goto LABEL_1691;
        }
        continue;
      }
      v661 = 1621i64;
      v46 = *(unsigned __int8 *)(v919 + 32);
      if ( v46 == 5 )
      {
        v661 = 1625i64;
        if ( (*(_BYTE *)(v919 + 32) & 7) != 5i64 )
        {
          dollar___modelZmodel95types_u218(v731, *(unsigned __int8 *)(v919 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_174;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_117;
          v98 = v731[0];
          v99 = (char *)v731[1];
          raiseFieldErrorStr(&v106, &v98);
          goto LABEL_482;
        }
        v915 = *(_QWORD *)(v919 + 144);
        v1052 = v915;
      }
      else
      {
        if ( v46 != 6 )
        {
          v661 = 1627i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
          goto LABEL_489;
        }
        v661 = 1623i64;
        if ( (*(_BYTE *)(v919 + 32) & 7) != 6i64 )
        {
          dollar___modelZmodel95types_u218(v730, *(unsigned __int8 *)(v919 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_173;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_115;
          v98 = v730[0];
          v99 = (char *)v730[1];
          raiseFieldErrorStr(&v106, &v98);
          goto LABEL_482;
        }
        v916 = *(_QWORD *)(v919 + 208);
        v1052 = v916;
      }
      v661 = 1629i64;
      v480 = 0i64;
      v481 = 0i64;
      dollar___systemZdollars_u14(&v484, v1052);
      if ( !*v1007 )
      {
        rawNewString(&v106, *(_QWORD *)v919 + v484 + 47);
        v480 = v106;
        v481 = (_QWORD *)v107;
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_175;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
        appendString_29(&v480, &v106);
        v47 = *(_QWORD *)(v919 + 8);
        v106 = *(_QWORD *)v919;
        v107 = v47;
        appendString_29(&v480, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_176;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_121;
        appendString_29(&v480, &v106);
        v106 = v484;
        v107 = (__int64)v485;
        appendString_29(&v480, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_177;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_132;
        appendString_29(&v480, &v106);
        v482 = v480;
        v483 = v481;
        prepareAdd(v1006 + 1, v480);
        v106 = v482;
        v107 = (__int64)v483;
        appendString_29(v1006 + 1, &v106);
      }
LABEL_482:
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v483 && (*v483 & 0x4000000000000000i64) == 0 )
        deallocShared(v483);
      if ( v485 && (*v485 & 0x4000000000000000i64) == 0 )
        deallocShared(v485);
      if ( *v1007 )
        goto LABEL_1691;
      goto LABEL_489;
    }
    break;
  }
  v661 = 1633i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 60i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_180;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_179;
  appendString_29(v1006 + 1, &v106);
  v913 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1051 = 0i64;
  v661 = 250i64;
  v912 = v1006[27];
  v911 = v912;
  v661 = 251i64;
  while ( 2 )
  {
    if ( v1051 < v911 )
    {
      v661 = 1641i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      if ( v1051 < 0 || v1051 >= v1006[27] )
      {
        raiseIndexError2(v1051, v1006[27] - 1i64);
        goto LABEL_1691;
      }
      v913 = v1006[28] + 304 * v1051 + 8;
      v910 = 0i64;
      v909 = 0i64;
      v908 = 0i64;
      v907 = 0i64;
      v478 = 0i64;
      v479 = 0i64;
      v476 = 0i64;
      v477 = 0i64;
      v661 = 1642i64;
      if ( !*(_QWORD *)v913 )
      {
        v661 = 1643i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
LABEL_528:
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v1051;
        v661 = 254i64;
        v906 = v1006[27];
        if ( v906 != v911 )
        {
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_188;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
          failedAssertImpl__stdZassertions_u234(&v106);
          if ( *v1007 )
            goto LABEL_1691;
        }
        continue;
      }
      v661 = 1645i64;
      v48 = *(unsigned __int8 *)(v913 + 32);
      if ( v48 != 6 )
      {
        if ( *(unsigned __int8 *)(v913 + 32) > 6u )
        {
LABEL_518:
          v661 = 1655i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
          goto LABEL_528;
        }
        if ( v48 == 5 )
        {
          v661 = 1653i64;
          if ( (*(_BYTE *)(v913 + 32) & 7) != 5i64 )
          {
            dollar___modelZmodel95types_u218(v735, *(unsigned __int8 *)(v913 + 32));
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_184;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_117;
            v98 = v735[0];
            v99 = (char *)v735[1];
            raiseFieldErrorStr(&v106, &v98);
            goto LABEL_521;
          }
          v907 = *(_QWORD *)(v913 + 128);
          v1050 = v907;
          goto LABEL_519;
        }
        if ( *(_BYTE *)(v913 + 32) )
        {
          if ( v48 != 1 )
            goto LABEL_518;
          v661 = 1649i64;
          if ( (*(_BYTE *)(v913 + 32) & 7) != 1i64 )
          {
            dollar___modelZmodel95types_u218(v733, *(unsigned __int8 *)(v913 + 32));
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_182;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_107;
            v98 = v733[0];
            v99 = (char *)v733[1];
            raiseFieldErrorStr(&v106, &v98);
            goto LABEL_521;
          }
          v909 = *(_QWORD *)(v913 + 112);
          v1050 = v909;
LABEL_519:
          v661 = 1657i64;
          v474 = 0i64;
          v475 = 0i64;
          dollar___systemZdollars_u14(&v478, v1050);
          if ( !*v1007 )
          {
            rawNewString(&v106, *(_QWORD *)v913 + v478 + 47);
            v474 = v106;
            v475 = (_QWORD *)v107;
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_185;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
            appendString_29(&v474, &v106);
            v49 = *(_QWORD *)(v913 + 8);
            v106 = *(_QWORD *)v913;
            v107 = v49;
            appendString_29(&v474, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_186;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_121;
            appendString_29(&v474, &v106);
            v106 = v478;
            v107 = (__int64)v479;
            appendString_29(&v474, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_187;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_132;
            appendString_29(&v474, &v106);
            v476 = v474;
            v477 = v475;
            prepareAdd(v1006 + 1, v474);
            v106 = v476;
            v107 = (__int64)v477;
            appendString_29(v1006 + 1, &v106);
          }
        }
        else
        {
          v661 = 1647i64;
          if ( (*(_BYTE *)(v913 + 32) & 7) == 0 )
          {
            v910 = *(_QWORD *)(v913 + 112);
            v1050 = v910;
            goto LABEL_519;
          }
          dollar___modelZmodel95types_u218(v732, *(unsigned __int8 *)(v913 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_181;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_105;
          v98 = v732[0];
          v99 = (char *)v732[1];
          raiseFieldErrorStr(&v106, &v98);
        }
LABEL_521:
        v661 = 394i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v477 && (*v477 & 0x4000000000000000i64) == 0 )
          deallocShared(v477);
        if ( v479 && (*v479 & 0x4000000000000000i64) == 0 )
          deallocShared(v479);
        if ( *v1007 )
          goto LABEL_1691;
        goto LABEL_528;
      }
      v661 = 1651i64;
      if ( (*(_BYTE *)(v913 + 32) & 7) != 6i64 )
      {
        dollar___modelZmodel95types_u218(v734, *(unsigned __int8 *)(v913 + 32));
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_183;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_115;
        v98 = v734[0];
        v99 = (char *)v734[1];
        raiseFieldErrorStr(&v106, &v98);
        goto LABEL_521;
      }
      v908 = *(_QWORD *)(v913 + 128);
      v1050 = v908;
      goto LABEL_519;
    }
    break;
  }
  v661 = 1661i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 68i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_190;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_189;
  appendString_29(v1006 + 1, &v106);
  v905 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1049 = 0i64;
  v661 = 250i64;
  v904 = v1006[27];
  v903 = v904;
  v661 = 251i64;
  while ( 2 )
  {
    if ( v1049 < v903 )
    {
      v661 = 1669i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      if ( v1049 < 0 || v1049 >= v1006[27] )
      {
        raiseIndexError2(v1049, v1006[27] - 1i64);
        goto LABEL_1691;
      }
      v905 = v1006[28] + 304 * v1049 + 8;
      v902 = 0i64;
      v901 = 0i64;
      v472 = 0i64;
      v473 = 0i64;
      v470 = 0i64;
      v471 = 0i64;
      v661 = 1670i64;
      if ( !*(_QWORD *)v905 )
      {
        v661 = 1671i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
LABEL_557:
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v1049;
        v661 = 254i64;
        v900 = v1006[27];
        if ( v900 != v903 )
        {
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_196;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
          failedAssertImpl__stdZassertions_u234(&v106);
          if ( *v1007 )
            goto LABEL_1691;
        }
        continue;
      }
      v661 = 1673i64;
      v50 = *(unsigned __int8 *)(v905 + 32);
      if ( v50 == 2 )
      {
        v661 = 1675i64;
        if ( (*(_BYTE *)(v905 + 32) & 7) == 2i64 )
        {
          v902 = *(_QWORD *)(v905 + 96);
          v1048 = v902;
          goto LABEL_548;
        }
        dollar___modelZmodel95types_u218(v736, *(unsigned __int8 *)(v905 + 32));
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_191;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_109;
        v98 = v736[0];
        v99 = (char *)v736[1];
        raiseFieldErrorStr(&v106, &v98);
      }
      else
      {
        if ( v50 != 6 )
        {
          v661 = 1679i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
          goto LABEL_557;
        }
        v661 = 1677i64;
        if ( (*(_BYTE *)(v905 + 32) & 7) != 6i64 )
        {
          dollar___modelZmodel95types_u218(v737, *(unsigned __int8 *)(v905 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_192;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_115;
          v98 = v737[0];
          v99 = (char *)v737[1];
          raiseFieldErrorStr(&v106, &v98);
          goto LABEL_550;
        }
        v901 = *(_QWORD *)(v905 + 144);
        v1048 = v901;
LABEL_548:
        v661 = 1681i64;
        v468 = 0i64;
        v469 = 0i64;
        dollar___systemZdollars_u14(&v472, v1048);
        if ( !*v1007 )
        {
          rawNewString(&v106, *(_QWORD *)v905 + v472 + 47);
          v468 = v106;
          v469 = (_QWORD *)v107;
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_193;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
          appendString_29(&v468, &v106);
          v51 = *(_QWORD *)(v905 + 8);
          v106 = *(_QWORD *)v905;
          v107 = v51;
          appendString_29(&v468, &v106);
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_194;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_121;
          appendString_29(&v468, &v106);
          v106 = v472;
          v107 = (__int64)v473;
          appendString_29(&v468, &v106);
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_195;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_132;
          appendString_29(&v468, &v106);
          v470 = v468;
          v471 = v469;
          prepareAdd(v1006 + 1, v468);
          v106 = v470;
          v107 = (__int64)v471;
          appendString_29(v1006 + 1, &v106);
        }
      }
LABEL_550:
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v471 && (*v471 & 0x4000000000000000i64) == 0 )
        deallocShared(v471);
      if ( v473 && (*v473 & 0x4000000000000000i64) == 0 )
        deallocShared(v473);
      if ( *v1007 )
        goto LABEL_1691;
      goto LABEL_557;
    }
    break;
  }
  v661 = 1685i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 72i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_198;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_197;
  appendString_29(v1006 + 1, &v106);
  v899 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1047 = 0i64;
  v661 = 250i64;
  v898 = v1006[27];
  v897 = v898;
  v661 = 251i64;
  while ( 2 )
  {
    if ( v1047 < v897 )
    {
      v661 = 1693i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      if ( v1047 < 0 || v1047 >= v1006[27] )
      {
        raiseIndexError2(v1047, v1006[27] - 1i64);
        goto LABEL_1691;
      }
      v899 = v1006[28] + 304 * v1047 + 8;
      v896 = 0i64;
      v895 = 0i64;
      v894 = 0i64;
      v466 = 0i64;
      v467 = 0i64;
      v464 = 0i64;
      v465 = 0i64;
      v661 = 1694i64;
      if ( !*(_QWORD *)v899 )
      {
        v661 = 1695i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
LABEL_592:
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v1047;
        v661 = 254i64;
        v893 = v1006[27];
        if ( v893 != v897 )
        {
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_205;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
          failedAssertImpl__stdZassertions_u234(&v106);
          if ( *v1007 )
            goto LABEL_1691;
        }
        continue;
      }
      v661 = 1697i64;
      v52 = *(unsigned __int8 *)(v899 + 32);
      if ( v52 != 6 )
      {
        if ( *(unsigned __int8 *)(v899 + 32) > 6u )
        {
LABEL_582:
          v661 = 1705i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
          goto LABEL_592;
        }
        if ( v52 == 2 )
        {
          v661 = 1699i64;
          if ( (*(_BYTE *)(v899 + 32) & 7) == 2i64 )
          {
            v896 = *(_QWORD *)(v899 + 112);
            v1046 = v896;
            goto LABEL_583;
          }
          dollar___modelZmodel95types_u218(v738, *(unsigned __int8 *)(v899 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_199;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_109;
          v98 = v738[0];
          v99 = (char *)v738[1];
          raiseFieldErrorStr(&v106, &v98);
        }
        else
        {
          if ( v52 != 3 )
            goto LABEL_582;
          v661 = 1701i64;
          if ( (*(_BYTE *)(v899 + 32) & 7) != 3i64 )
          {
            dollar___modelZmodel95types_u218(v739, *(unsigned __int8 *)(v899 + 32));
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_200;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_111;
            v98 = v739[0];
            v99 = (char *)v739[1];
            raiseFieldErrorStr(&v106, &v98);
            goto LABEL_585;
          }
          v895 = *(_QWORD *)(v899 + 112);
          v1046 = v895;
LABEL_583:
          v661 = 1707i64;
          v462 = 0i64;
          v463 = 0i64;
          dollar___systemZdollars_u14(&v466, v1046);
          if ( !*v1007 )
          {
            rawNewString(&v106, *(_QWORD *)v899 + v466 + 47);
            v462 = v106;
            v463 = (_QWORD *)v107;
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_202;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
            appendString_29(&v462, &v106);
            v53 = *(_QWORD *)(v899 + 8);
            v106 = *(_QWORD *)v899;
            v107 = v53;
            appendString_29(&v462, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_203;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_121;
            appendString_29(&v462, &v106);
            v106 = v466;
            v107 = (__int64)v467;
            appendString_29(&v462, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_204;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_132;
            appendString_29(&v462, &v106);
            v464 = v462;
            v465 = v463;
            prepareAdd(v1006 + 1, v462);
            v106 = v464;
            v107 = (__int64)v465;
            appendString_29(v1006 + 1, &v106);
          }
        }
LABEL_585:
        v661 = 394i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v465 && (*v465 & 0x4000000000000000i64) == 0 )
          deallocShared(v465);
        if ( v467 && (*v467 & 0x4000000000000000i64) == 0 )
          deallocShared(v467);
        if ( *v1007 )
          goto LABEL_1691;
        goto LABEL_592;
      }
      v661 = 1703i64;
      if ( (*(_BYTE *)(v899 + 32) & 7) != 6i64 )
      {
        dollar___modelZmodel95types_u218(v740, *(unsigned __int8 *)(v899 + 32));
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_201;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_115;
        v98 = v740[0];
        v99 = (char *)v740[1];
        raiseFieldErrorStr(&v106, &v98);
        goto LABEL_585;
      }
      v894 = *(_QWORD *)(v899 + 160);
      v1046 = v894;
      goto LABEL_583;
    }
    break;
  }
  v661 = 1711i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 72i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_207;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_206;
  appendString_29(v1006 + 1, &v106);
  v892 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1045 = 0i64;
  v661 = 250i64;
  v891 = v1006[27];
  v890 = v891;
  v661 = 251i64;
  while ( v1045 < v890 )
  {
    v661 = 1719i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( v1045 < 0 || v1045 >= v1006[27] )
    {
      raiseIndexError2(v1045, v1006[27] - 1i64);
      goto LABEL_1691;
    }
    v892 = v1006[28] + 304 * v1045 + 8;
    v889 = 0i64;
    v460 = 0i64;
    v461 = 0i64;
    v458 = 0i64;
    v459 = 0i64;
    v661 = 1720i64;
    if ( *(_QWORD *)v892 )
    {
      v661 = 1723i64;
      if ( *(_BYTE *)(v892 + 32) == 3 )
      {
        v661 = 1725i64;
        if ( (*(_BYTE *)(v892 + 32) & 7) == 3i64 )
        {
          v889 = *(_QWORD *)(v892 + 128);
          v888 = v889;
          v661 = 1729i64;
          v456 = 0i64;
          v457 = 0i64;
          dollar___systemZdollars_u14(&v460, v889);
          if ( !*v1007 )
          {
            rawNewString(&v106, *(_QWORD *)v892 + v460 + 47);
            v456 = v106;
            v457 = (_QWORD *)v107;
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_209;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
            appendString_29(&v456, &v106);
            v54 = *(_QWORD *)(v892 + 8);
            v106 = *(_QWORD *)v892;
            v107 = v54;
            appendString_29(&v456, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_210;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_121;
            appendString_29(&v456, &v106);
            v106 = v460;
            v107 = (__int64)v461;
            appendString_29(&v456, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_211;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_132;
            appendString_29(&v456, &v106);
            v458 = v456;
            v459 = v457;
            prepareAdd(v1006 + 1, v456);
            v106 = v458;
            v107 = (__int64)v459;
            appendString_29(v1006 + 1, &v106);
          }
        }
        else
        {
          dollar___modelZmodel95types_u218(v741, *(unsigned __int8 *)(v892 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_208;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_111;
          v98 = v741[0];
          v99 = (char *)v741[1];
          raiseFieldErrorStr(&v106, &v98);
        }
        v661 = 394i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v459 && (*v459 & 0x4000000000000000i64) == 0 )
          deallocShared(v459);
        if ( v461 && (*v461 & 0x4000000000000000i64) == 0 )
          deallocShared(v461);
        if ( *v1007 )
          goto LABEL_1691;
      }
      else
      {
        v661 = 1727i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      }
    }
    else
    {
      v661 = 1721i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    }
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1045;
    v661 = 254i64;
    v887 = v1006[27];
    if ( v887 != v890 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_212;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v661 = 1733i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 74i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_214;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_213;
  appendString_29(v1006 + 1, &v106);
  v886 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1044 = 0i64;
  v661 = 250i64;
  v885 = v1006[27];
  v884 = v885;
  v661 = 251i64;
  while ( v1044 < v884 )
  {
    v661 = 1741i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( v1044 < 0 || v1044 >= v1006[27] )
    {
      raiseIndexError2(v1044, v1006[27] - 1i64);
      goto LABEL_1691;
    }
    v886 = v1006[28] + 304 * v1044 + 8;
    v883 = 0i64;
    v454 = 0i64;
    v455 = 0i64;
    v452 = 0i64;
    v453 = 0i64;
    v661 = 1742i64;
    if ( *(_QWORD *)v886 )
    {
      v661 = 1745i64;
      if ( *(_BYTE *)(v886 + 32) == 6 )
      {
        v661 = 1747i64;
        if ( (*(_BYTE *)(v886 + 32) & 7) == 6i64 )
        {
          v883 = *(_QWORD *)(v886 + 192);
          v882 = v883;
          v661 = 1751i64;
          v450 = 0i64;
          v451 = 0i64;
          dollar___systemZdollars_u14(&v454, v883);
          if ( !*v1007 )
          {
            rawNewString(&v106, *(_QWORD *)v886 + v454 + 47);
            v450 = v106;
            v451 = (_QWORD *)v107;
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_216;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
            appendString_29(&v450, &v106);
            v55 = *(_QWORD *)(v886 + 8);
            v106 = *(_QWORD *)v886;
            v107 = v55;
            appendString_29(&v450, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_217;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_121;
            appendString_29(&v450, &v106);
            v106 = v454;
            v107 = (__int64)v455;
            appendString_29(&v450, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_218;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_132;
            appendString_29(&v450, &v106);
            v452 = v450;
            v453 = v451;
            prepareAdd(v1006 + 1, v450);
            v106 = v452;
            v107 = (__int64)v453;
            appendString_29(v1006 + 1, &v106);
          }
        }
        else
        {
          dollar___modelZmodel95types_u218(v742, *(unsigned __int8 *)(v886 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_215;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_115;
          v98 = v742[0];
          v99 = (char *)v742[1];
          raiseFieldErrorStr(&v106, &v98);
        }
        v661 = 394i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v453 && (*v453 & 0x4000000000000000i64) == 0 )
          deallocShared(v453);
        if ( v455 && (*v455 & 0x4000000000000000i64) == 0 )
          deallocShared(v455);
        if ( *v1007 )
          goto LABEL_1691;
      }
      else
      {
        v661 = 1749i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      }
    }
    else
    {
      v661 = 1743i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    }
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1044;
    v661 = 254i64;
    v881 = v1006[27];
    if ( v881 != v884 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_219;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v661 = 1755i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 71i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_221;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_220;
  appendString_29(v1006 + 1, &v106);
  v880 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1043 = 0i64;
  v661 = 250i64;
  v879 = v1006[27];
  v878 = v879;
  v661 = 251i64;
  while ( 2 )
  {
    if ( v1043 < v878 )
    {
      v661 = 1763i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      if ( v1043 < 0 || v1043 >= v1006[27] )
      {
        raiseIndexError2(v1043, v1006[27] - 1i64);
        goto LABEL_1691;
      }
      v880 = v1006[28] + 304 * v1043 + 8;
      v877 = 0i64;
      v876 = 0i64;
      v875 = 0i64;
      v448 = 0i64;
      v449 = 0i64;
      v446 = 0i64;
      v447 = 0i64;
      v661 = 1764i64;
      if ( !*(_QWORD *)v880 )
      {
        v661 = 1765i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
LABEL_677:
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v1043;
        v661 = 254i64;
        v874 = v1006[27];
        if ( v874 != v878 )
        {
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_228;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
          failedAssertImpl__stdZassertions_u234(&v106);
          if ( *v1007 )
            goto LABEL_1691;
        }
        continue;
      }
      v661 = 1767i64;
      v56 = *(unsigned __int8 *)(v880 + 32);
      if ( v56 == 6 )
      {
        v661 = 1771i64;
        if ( (*(_BYTE *)(v880 + 32) & 7) == 6i64 )
        {
          v876 = *(_QWORD *)(v880 + 224);
          v1042 = v876;
          goto LABEL_668;
        }
        dollar___modelZmodel95types_u218(v744, *(unsigned __int8 *)(v880 + 32));
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_223;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_115;
        v98 = v744[0];
        v99 = (char *)v744[1];
        raiseFieldErrorStr(&v106, &v98);
      }
      else
      {
        if ( *(unsigned __int8 *)(v880 + 32) > 6u )
        {
LABEL_667:
          v661 = 1775i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
          goto LABEL_677;
        }
        if ( v56 == 3 )
        {
          v661 = 1769i64;
          if ( (*(_BYTE *)(v880 + 32) & 7) == 3i64 )
          {
            v877 = *(_QWORD *)(v880 + 144);
            v1042 = v877;
            goto LABEL_668;
          }
          dollar___modelZmodel95types_u218(v743, *(unsigned __int8 *)(v880 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_222;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_111;
          v98 = v743[0];
          v99 = (char *)v743[1];
          raiseFieldErrorStr(&v106, &v98);
        }
        else
        {
          if ( v56 != 5 )
            goto LABEL_667;
          v661 = 1773i64;
          if ( (*(_BYTE *)(v880 + 32) & 7) != 5i64 )
          {
            dollar___modelZmodel95types_u218(v745, *(unsigned __int8 *)(v880 + 32));
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_224;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_117;
            v98 = v745[0];
            v99 = (char *)v745[1];
            raiseFieldErrorStr(&v106, &v98);
            goto LABEL_670;
          }
          v875 = *(_QWORD *)(v880 + 160);
          v1042 = v875;
LABEL_668:
          v661 = 1777i64;
          v444 = 0i64;
          v445 = 0i64;
          dollar___systemZdollars_u14(&v448, v1042);
          if ( !*v1007 )
          {
            rawNewString(&v106, *(_QWORD *)v880 + v448 + 47);
            v444 = v106;
            v445 = (_QWORD *)v107;
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_225;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
            appendString_29(&v444, &v106);
            v57 = *(_QWORD *)(v880 + 8);
            v106 = *(_QWORD *)v880;
            v107 = v57;
            appendString_29(&v444, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_226;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_121;
            appendString_29(&v444, &v106);
            v106 = v448;
            v107 = (__int64)v449;
            appendString_29(&v444, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_227;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_132;
            appendString_29(&v444, &v106);
            v446 = v444;
            v447 = v445;
            prepareAdd(v1006 + 1, v444);
            v106 = v446;
            v107 = (__int64)v447;
            appendString_29(v1006 + 1, &v106);
          }
        }
      }
LABEL_670:
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v447 && (*v447 & 0x4000000000000000i64) == 0 )
        deallocShared(v447);
      if ( v449 && (*v449 & 0x4000000000000000i64) == 0 )
        deallocShared(v449);
      if ( *v1007 )
        goto LABEL_1691;
      goto LABEL_677;
    }
    break;
  }
  v661 = 1781i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 61i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_230;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_229;
  appendString_29(v1006 + 1, &v106);
  v873 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1041 = 0i64;
  v661 = 250i64;
  v872 = v1006[27];
  v871 = v872;
  v661 = 251i64;
  while ( 2 )
  {
    if ( v1041 < v871 )
    {
      v661 = 1789i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      if ( v1041 < 0 || v1041 >= v1006[27] )
      {
        raiseIndexError2(v1041, v1006[27] - 1i64);
        goto LABEL_1691;
      }
      v873 = v1006[28] + 304 * v1041 + 8;
      v870 = 0i64;
      v442 = 0i64;
      v443 = 0i64;
      v440 = 0i64;
      v441 = 0i64;
      v661 = 1790i64;
      if ( !*(_QWORD *)v873 )
      {
        v661 = 1791i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        goto LABEL_750;
      }
      v661 = 1793i64;
      if ( *(_BYTE *)(v873 + 32) )
      {
        if ( *(_BYTE *)(v873 + 32) != 5 )
        {
          v661 = 1807i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
          goto LABEL_750;
        }
        v436 = 0i64;
        v437 = 0i64;
        v661 = 1699i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v58 = *(_QWORD *)(v873 + 8);
        v106 = *(_QWORD *)v873;
        v107 = v58;
        eqcopy___system_u2661(&v436, &v106);
        v869 = 0i64;
        v434 = 0i64;
        v435 = 0i64;
        v432 = 0i64;
        v433 = 0i64;
        v661 = 635i64;
        v662 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
        if ( (*(_BYTE *)(v873 + 32) & 7) == 5i64 )
        {
          v59 = *(_QWORD *)(v873 + 208);
          v106 = *(_QWORD *)(v873 + 200);
          v107 = v59;
          eqcopy___modelZmodel95types_u2915(&v432, &v106);
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          v1039 = 0i64;
          v868 = v432;
          v867 = v432;
          v661 = 184i64;
          while ( v1039 < v867 )
          {
            v869 = v1039;
            v661 = 635i64;
            v662 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
            if ( v1039 < 0 || v1039 >= v432 )
            {
              raiseIndexError2(v1039, v432 - 1);
              goto LABEL_737;
            }
            v60 = v433 + 16 * v1039;
            v61 = *(_QWORD *)(v60 + 16);
            v106 = *(_QWORD *)(v60 + 8);
            v107 = v61;
            eqcopy___modelZmodel95types_u2936(&v434, &v106);
            nimZeroMem_66(v128, 40i64);
            v866 = 0i64;
            v661 = 1799i64;
            v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
            nimZeroMem_66(v128, 40i64);
            v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            v1038 = 0i64;
            v865 = v434;
            v864 = v434;
            v661 = 184i64;
            while ( v1038 < v864 )
            {
              v430 = 0i64;
              v431 = 0i64;
              v428 = 0i64;
              v429 = 0i64;
              v426 = 0i64;
              v427 = 0i64;
              v424 = 0i64;
              v425 = 0i64;
              v866 = v1038;
              v661 = 934i64;
              v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              if ( v1038 < 0 || v1038 >= v434 )
              {
                raiseIndexError2(v1038, v434 - 1);
                goto LABEL_737;
              }
              eqcopy___modelZmodel95types_u3002(v128, v435 + 40 * v1038 + 8);
              v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
              v863 = v128[4];
              v422 = 0i64;
              v423 = 0i64;
              v661 = 1802i64;
              dollar___systemZdollars_u14(&v430, v869);
              if ( *v1007 )
                goto LABEL_737;
              dollar___systemZdollars_u14(&v428, v866);
              if ( *v1007 )
                goto LABEL_737;
              v661 = 1803i64;
              dollar___systemZdollars_u14(&v426, v863);
              if ( *v1007 )
                goto LABEL_737;
              rawNewString(&v106, v428 + v430 + v436 + v426 + 36);
              v422 = v106;
              v423 = (_QWORD *)v107;
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_233;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
              appendString_29(&v422, &v106);
              v106 = v436;
              v107 = (__int64)v437;
              appendString_29(&v422, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_234;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_139;
              appendString_29(&v422, &v106);
              v106 = v430;
              v107 = (__int64)v431;
              appendString_29(&v422, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_235;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_141;
              appendString_29(&v422, &v106);
              v106 = v428;
              v107 = (__int64)v429;
              appendString_29(&v422, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_237;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_236;
              appendString_29(&v422, &v106);
              v106 = v426;
              v107 = (__int64)v427;
              appendString_29(&v422, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_239;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_238;
              appendString_29(&v422, &v106);
              v424 = v422;
              v425 = v423;
              prepareAdd(v1006 + 1, v422);
              v106 = v424;
              v107 = (__int64)v425;
              appendString_29(v1006 + 1, &v106);
              v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v1038;
              v661 = 187i64;
              v862 = v434;
              if ( v434 != v864 )
              {
                v106 = TM__THWBxVSaWN2Zh7OMooFH0w_240;
                v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
                failedAssertImpl__stdZassertions_u234(&v106);
                if ( *v1007 )
                  goto LABEL_737;
              }
              v661 = 394i64;
              v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              if ( v425 && (*v425 & 0x4000000000000000i64) == 0 )
                deallocShared(v425);
              if ( v427 && (*v427 & 0x4000000000000000i64) == 0 )
                deallocShared(v427);
              if ( v429 && (*v429 & 0x4000000000000000i64) == 0 )
                deallocShared(v429);
              if ( v431 && (*v431 & 0x4000000000000000i64) == 0 )
                deallocShared(v431);
            }
            v661 = 934i64;
            eqdestroy___modelZmodel95types_u2999(v128);
            v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v1039;
            v661 = 187i64;
            v861 = v432;
            if ( v432 != v867 )
            {
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_241;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
              failedAssertImpl__stdZassertions_u234(&v106);
              if ( *v1007 )
                goto LABEL_737;
            }
          }
          v661 = 635i64;
          v662 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
          v106 = v432;
          v107 = v433;
          eqdestroy___modelZmodel95types_u2912(&v106);
          v106 = v434;
          v107 = v435;
          eqdestroy___modelZmodel95types_u2933(&v106);
          v661 = 394i64;
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v437 && (*v437 & 0x4000000000000000i64) == 0 )
            deallocShared(v437);
          if ( v441 && (*v441 & 0x4000000000000000i64) == 0 )
            deallocShared(v441);
          if ( v443 && (*v443 & 0x4000000000000000i64) == 0 )
            deallocShared(v443);
          v661 = 1805i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
LABEL_750:
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          ++v1041;
          v661 = 254i64;
          v860 = v1006[27];
          if ( v860 != v871 )
          {
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_246;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
            failedAssertImpl__stdZassertions_u234(&v106);
            if ( *v1007 )
              goto LABEL_1691;
          }
          continue;
        }
        dollar___modelZmodel95types_u218(v747, *(unsigned __int8 *)(v873 + 32));
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_232;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_117;
        v98 = v747[0];
        v99 = (char *)v747[1];
        raiseFieldErrorStr(&v106, &v98);
LABEL_737:
        v661 = 394i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v437 && (*v437 & 0x4000000000000000i64) == 0 )
          deallocShared(v437);
        if ( !*v1007 )
        {
LABEL_741:
          v661 = 1808i64;
          v438 = 0i64;
          v439 = 0i64;
          dollar___systemZdollars_u14(&v442, v1040);
          if ( !*v1007 )
          {
            rawNewString(&v106, *(_QWORD *)v873 + v442 + 32);
            v438 = v106;
            v439 = (_QWORD *)v107;
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_242;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
            appendString_29(&v438, &v106);
            v62 = *(_QWORD *)(v873 + 8);
            v106 = *(_QWORD *)v873;
            v107 = v62;
            appendString_29(&v438, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_244;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_243;
            appendString_29(&v438, &v106);
            v106 = v442;
            v107 = (__int64)v443;
            appendString_29(&v438, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_245;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_238;
            appendString_29(&v438, &v106);
            v440 = v438;
            v441 = v439;
            prepareAdd(v1006 + 1, v438);
            v106 = v440;
            v107 = (__int64)v441;
            appendString_29(v1006 + 1, &v106);
          }
        }
      }
      else
      {
        v661 = 1795i64;
        if ( (*(_BYTE *)(v873 + 32) & 7) == 0 )
        {
          v870 = *(_QWORD *)(v873 + 136);
          v1040 = v870;
          goto LABEL_741;
        }
        dollar___modelZmodel95types_u218(v746, *(unsigned __int8 *)(v873 + 32));
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_231;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_105;
        v98 = v746[0];
        v99 = (char *)v746[1];
        raiseFieldErrorStr(&v106, &v98);
      }
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v441 && (*v441 & 0x4000000000000000i64) == 0 )
        deallocShared(v441);
      if ( v443 && (*v443 & 0x4000000000000000i64) == 0 )
        deallocShared(v443);
      if ( *v1007 )
        goto LABEL_1691;
      goto LABEL_750;
    }
    break;
  }
  v661 = 1810i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 67i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_248;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_247;
  appendString_29(v1006 + 1, &v106);
  v859 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1037 = 0i64;
  v661 = 250i64;
  v858 = v1006[27];
  v857 = v858;
  v661 = 251i64;
  while ( v1037 < v857 )
  {
    v661 = 1818i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( v1037 < 0 || v1037 >= v1006[27] )
    {
      raiseIndexError2(v1037, v1006[27] - 1i64);
      goto LABEL_1691;
    }
    v859 = v1006[28] + 304 * v1037 + 8;
    v856 = 0i64;
    v420 = 0i64;
    v421 = 0i64;
    v418 = 0i64;
    v419 = 0i64;
    v661 = 1819i64;
    if ( *(_QWORD *)v859 )
    {
      v661 = 1822i64;
      if ( *(_BYTE *)(v859 + 32) == 4 )
      {
        v661 = 1824i64;
        if ( (*(_BYTE *)(v859 + 32) & 7) == 4i64 )
        {
          v856 = *(_QWORD *)(v859 + 104);
          v855 = v856;
          v661 = 1827i64;
          v416 = 0i64;
          v417 = 0i64;
          dollar___systemZdollars_u14(&v420, v856);
          if ( !*v1007 )
          {
            rawNewString(&v106, *(_QWORD *)v859 + v420 + 32);
            v416 = v106;
            v417 = (_QWORD *)v107;
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_250;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_119;
            appendString_29(&v416, &v106);
            v63 = *(_QWORD *)(v859 + 8);
            v106 = *(_QWORD *)v859;
            v107 = v63;
            appendString_29(&v416, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_251;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_243;
            appendString_29(&v416, &v106);
            v106 = v420;
            v107 = (__int64)v421;
            appendString_29(&v416, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_252;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_238;
            appendString_29(&v416, &v106);
            v418 = v416;
            v419 = v417;
            prepareAdd(v1006 + 1, v416);
            v106 = v418;
            v107 = (__int64)v419;
            appendString_29(v1006 + 1, &v106);
          }
        }
        else
        {
          dollar___modelZmodel95types_u218(v748, *(unsigned __int8 *)(v859 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_249;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_113;
          v98 = v748[0];
          v99 = (char *)v748[1];
          raiseFieldErrorStr(&v106, &v98);
        }
        v661 = 394i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v419 && (*v419 & 0x4000000000000000i64) == 0 )
          deallocShared(v419);
        if ( v421 && (*v421 & 0x4000000000000000i64) == 0 )
          deallocShared(v421);
        if ( *v1007 )
          goto LABEL_1691;
      }
      else
      {
        v661 = 1826i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      }
    }
    else
    {
      v661 = 1820i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    }
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1037;
    v661 = 254i64;
    v854 = v1006[27];
    if ( v854 != v857 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_253;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v661 = 1829i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 82i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_255;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_254;
  appendString_29(v1006 + 1, &v106);
  v1073 = 0i64;
  v853 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1036 = 0i64;
  v661 = 250i64;
  v852 = v1006[27];
  v851 = v852;
  v661 = 251i64;
  while ( v1036 < v851 )
  {
    v661 = 1850i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( v1036 < 0 || v1036 >= v1006[27] )
    {
      raiseIndexError2(v1036, v1006[27] - 1i64);
      goto LABEL_1691;
    }
    v64 = v1006[28];
    v853 = v64 + 304 * v1036 + 8;
    v661 = 1851i64;
    v65 = *(unsigned __int8 *)(v64 + 304 * v1036 + 40);
    if ( v65 == 6 )
    {
      v850 = 0i64;
      v405 = 0i64;
      v406 = 0i64;
      v661 = 635i64;
      v662 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
      if ( (*(_BYTE *)(v853 + 32) & 7) != 6i64 )
      {
        dollar___modelZmodel95types_u218(v752, *(unsigned __int8 *)(v853 + 32));
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_276;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_115;
        v98 = v752[0];
        v99 = (char *)v752[1];
        raiseFieldErrorStr(&v106, &v98);
        goto LABEL_1691;
      }
      v66 = *(_QWORD *)(v853 + 256);
      v106 = *(_QWORD *)(v853 + 248);
      v107 = v66;
      eqcopy___modelZmodel95types_u3192(&v405, &v106);
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      v1035 = 0i64;
      v849 = v405;
      v848 = v405;
      v661 = 251i64;
      while ( v1035 < v848 )
      {
        v661 = 1871i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        if ( v1035 < 0 || v1035 >= v405 )
        {
          raiseIndexError2(v1035, v405 - 1);
          goto LABEL_1691;
        }
        v850 = (_QWORD *)(v406 + 16 * v1035 + 8);
        v661 = 1872i64;
        nimZeroMem_66(&v403, 16i64);
        v403 = add_ui_set_instruction__modelZsimulationZcode95gen_u6900;
        v404 = v1006;
        if ( v1006 )
          ((void (__fastcall *)(__int64, _QWORD, _QWORD, _QWORD *))v403)(v1073, *v850, v850[1], v404);
        else
          ((void (__fastcall *)(__int64, _QWORD, _QWORD))v403)(v1073, *v850, v850[1]);
        if ( !*v1007 )
        {
          v661 = 1873i64;
          v402 = v1073 + 1;
          if ( __OFADD__(1i64, v1073) )
            goto LABEL_1148;
          v1073 = v402;
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          ++v1035;
          v661 = 254i64;
          v847 = v405;
          if ( v405 == v848 )
            continue;
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_279;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
          failedAssertImpl__stdZassertions_u234(&v106);
          if ( !*v1007 )
            continue;
        }
        goto LABEL_1691;
      }
      v661 = 635i64;
      v662 = "D:\\TuringComplete_Phu\\model\\model_types.nim";
      v106 = v405;
      v107 = v406;
      eqdestroy___modelZmodel95types_u3189(&v106);
    }
    else if ( *(unsigned __int8 *)(v64 + 304 * v1036 + 40) <= 6u )
    {
      if ( v65 == 3 )
      {
        v661 = 1865i64;
        nimZeroMem_66(&v408, 16i64);
        v408 = add_ui_set_instruction__modelZsimulationZcode95gen_u6900;
        v409 = v1006;
        if ( (*(_BYTE *)(v853 + 32) & 7) != 3i64 )
        {
          dollar___modelZmodel95types_u218(v751, *(unsigned __int8 *)(v853 + 32));
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_272;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_111;
          v98 = v751[0];
          v99 = (char *)v751[1];
          raiseFieldErrorStr(&v106, &v98);
          goto LABEL_1691;
        }
        if ( v409 )
          ((void (__fastcall *)(__int64, _QWORD, _QWORD, _QWORD *))v408)(
            v1073,
            *(_QWORD *)(v853 + 152),
            *(_QWORD *)(v853 + 160),
            v409);
        else
          ((void (__fastcall *)(__int64, _QWORD, _QWORD))v408)(v1073, *(_QWORD *)(v853 + 152), *(_QWORD *)(v853 + 160));
        if ( *v1007 )
          goto LABEL_1691;
        v661 = 1869i64;
        v407 = v1073 + 1;
        if ( __OFADD__(1i64, v1073) )
          goto LABEL_1148;
        v1073 = v407;
      }
      else if ( *(unsigned __int8 *)(v64 + 304 * v1036 + 40) <= 3u )
      {
        if ( v65 == 1 )
        {
          v661 = 1853i64;
          nimZeroMem_66(&v414, 16i64);
          v414 = add_ui_set_instruction__modelZsimulationZcode95gen_u6900;
          v415 = v1006;
          if ( (*(_BYTE *)(v853 + 32) & 7) != 1i64 )
          {
            dollar___modelZmodel95types_u218(v749, *(unsigned __int8 *)(v853 + 32));
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_264;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_107;
            v98 = v749[0];
            v99 = (char *)v749[1];
            raiseFieldErrorStr(&v106, &v98);
            goto LABEL_1691;
          }
          if ( v415 )
            ((void (__fastcall *)(__int64, _QWORD, _QWORD, _QWORD *))v414)(
              v1073,
              *(_QWORD *)(v853 + 120),
              *(_QWORD *)(v853 + 128),
              v415);
          else
            ((void (__fastcall *)(__int64, _QWORD, _QWORD))v414)(
              v1073,
              *(_QWORD *)(v853 + 120),
              *(_QWORD *)(v853 + 128));
          if ( *v1007 )
            goto LABEL_1691;
          v661 = 1857i64;
          v413 = v1073 + 1;
          if ( __OFADD__(1i64, v1073) )
            goto LABEL_1148;
          v1073 = v413;
        }
        else if ( v65 == 2 )
        {
          v661 = 1859i64;
          nimZeroMem_66(&v411, 16i64);
          v411 = add_ui_set_instruction__modelZsimulationZcode95gen_u6900;
          v412 = v1006;
          if ( (*(_BYTE *)(v853 + 32) & 7) != 2i64 )
          {
            dollar___modelZmodel95types_u218(v750, *(unsigned __int8 *)(v853 + 32));
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_268;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_109;
            v98 = v750[0];
            v99 = (char *)v750[1];
            raiseFieldErrorStr(&v106, &v98);
            goto LABEL_1691;
          }
          if ( v412 )
            ((void (__fastcall *)(__int64, _QWORD, _QWORD, _QWORD *))v411)(
              v1073,
              *(_QWORD *)(v853 + 120),
              *(_QWORD *)(v853 + 128),
              v412);
          else
            ((void (__fastcall *)(__int64, _QWORD, _QWORD))v411)(
              v1073,
              *(_QWORD *)(v853 + 120),
              *(_QWORD *)(v853 + 128));
          if ( *v1007 )
            goto LABEL_1691;
          v661 = 1863i64;
          v410 = v1073 + 1;
          if ( __OFADD__(1i64, v1073) )
            goto LABEL_1148;
          v1073 = v410;
        }
      }
    }
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1036;
    v661 = 254i64;
    v846 = v1006[27];
    if ( v846 != v851 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_280;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v661 = 1877i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 2i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_282;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_281;
  appendString_29(v1006 + 1, &v106);
  v845 = 0i64;
  nimZeroMem_66(v128, 560i64);
  v844 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1034 = 0i64;
  v843 = v114;
  v842 = v114;
  v661 = 184i64;
  while ( v1034 < v842 )
  {
    v661 = 1882i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v844 = v1034;
    if ( v1034 < 0 || v1034 >= v114 )
    {
      raiseIndexError2(v1034, v114 - 1);
      goto LABEL_1691;
    }
    qmemcpy(v128, &v115[560 * v1034 + 8], sizeof(v128));
    v661 = 1883i64;
    if ( LOBYTE(v128[4]) != 1 )
    {
      v661 = 1886i64;
      if ( LOBYTE(v128[0]) == 118 )
      {
        v661 = 1892i64;
        add__modelZsave95mongerZcommon_u5717(&v573, v844);
      }
      else if ( LOBYTE(v128[0]) <= 0x76u )
      {
        if ( LOBYTE(v128[0]) == 62 )
        {
          v661 = 1890i64;
          v668 = v128[14];
          v669 = v128[15];
          v670 = v128[16];
        }
        else if ( LOBYTE(v128[0]) == 93 )
        {
          v661 = 1888i64;
          v845 = v844;
        }
      }
    }
    else
    {
      v661 = 1884i64;
    }
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1034;
    v661 = 187i64;
    v841 = v114;
    if ( v114 != v842 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_283;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v661 = 1896i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 292i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_285;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_284;
  appendString_29(v1006 + 1, &v106);
  v661 = 1905i64;
  prepareAdd(v1006 + 1, 60i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_287;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_286;
  appendString_29(v1006 + 1, &v106);
  v661 = 1907i64;
  prepareAdd(v1006 + 1, 56i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_289;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_288;
  appendString_29(v1006 + 1, &v106);
  nimZeroMem_66(v128, 560i64);
  v840 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1033 = 0i64;
  v839 = v114;
  v838 = v114;
  v661 = 184i64;
  while ( v1033 < v838 )
  {
    v661 = 1909i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v840 = v1033;
    if ( v1033 < 0 || v1033 >= v114 )
    {
      raiseIndexError2(v1033, v114 - 1);
      goto LABEL_1691;
    }
    qmemcpy(v128, &v115[560 * v1033 + 8], sizeof(v128));
    v661 = 1910i64;
    v1032 = LOBYTE(v128[59]) == 0;
    if ( LOBYTE(v128[59]) )
      v1032 = v128[24] == 0;
    if ( !v1032 )
    {
      v661 = 1911i64;
      if ( LOBYTE(v128[0]) == 91 )
      {
        v661 = 1913i64;
        if ( v128[30] <= 0 )
        {
          raiseIndexError2(0i64, v128[30] - 1);
          goto LABEL_1691;
        }
        v401 = *(_QWORD *)(v128[31] + 8);
        v837 = 0i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v1031 = 0i64;
        v836 = v114;
        v835 = v114;
        v661 = 251i64;
        while ( v1031 < v835 )
        {
          v661 = 1914i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
          if ( v1031 < 0 || v1031 >= v114 )
          {
            raiseIndexError2(v1031, v114 - 1);
            goto LABEL_1691;
          }
          v67 = &v115[560 * v1031];
          v837 = v67 + 8;
          v661 = 1915i64;
          v834 = 0;
          v834 = eqeq___modelZsave95mongerZversionsZv7_u353(*((_QWORD *)v67 + 2), v401);
          if ( v834 == 1 )
          {
            v399 = 0i64;
            v400 = 0i64;
            v397 = 0i64;
            v398 = 0i64;
            v661 = 1699i64;
            v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            v68 = *((_QWORD *)v837 + 25);
            v106 = *((_QWORD *)v837 + 24);
            v107 = v68;
            eqcopy___system_u2661(&v399, &v106);
            v661 = 1917i64;
            v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
            v395 = 0i64;
            v396 = 0i64;
            rawNewString(&v106, v128[24] + *((_QWORD *)v837 + 24) + 39);
            v395 = v106;
            v396 = (_QWORD *)v107;
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_291;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_290;
            appendString_29(&v395, &v106);
            v106 = v128[24];
            v107 = v128[25];
            appendString_29(&v395, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_293;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_292;
            appendString_29(&v395, &v106);
            v69 = *((_QWORD *)v837 + 25);
            v106 = *((_QWORD *)v837 + 24);
            v107 = v69;
            appendString_29(&v395, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_295;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_294;
            appendString_29(&v395, &v106);
            v397 = v395;
            v398 = v396;
            prepareAdd(v1006 + 1, v395);
            v106 = v397;
            v107 = (__int64)v398;
            appendString_29(v1006 + 1, &v106);
            v661 = 394i64;
            v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v398 && (*v398 & 0x4000000000000000i64) == 0 )
              deallocShared(v398);
            if ( v400 && (*v400 & 0x4000000000000000i64) == 0 )
              deallocShared(v400);
            v661 = 1918i64;
            v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
            break;
          }
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          ++v1031;
          v661 = 254i64;
          v833 = v114;
          if ( v114 != v835 )
          {
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_296;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
            failedAssertImpl__stdZassertions_u234(&v106);
            if ( *v1007 )
              goto LABEL_1691;
          }
        }
      }
    }
    ++v1033;
    v661 = 187i64;
    v832 = v114;
    if ( v114 != v838 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_297;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v661 = 1919i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 2i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_298;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_281;
  appendString_29(v1006 + 1, &v106);
  v661 = 1922i64;
  prepareAdd(v1006 + 1, 37i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_300;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_299;
  appendString_29(v1006 + 1, &v106);
  nimZeroMem_66(v128, 560i64);
  v831 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1030 = 0i64;
  v830 = v114;
  v829 = v114;
  v661 = 184i64;
  while ( 2 )
  {
    if ( v1030 < v829 )
    {
      v661 = 1924i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v831 = v1030;
      if ( v1030 < 0 || v1030 >= v114 )
      {
        raiseIndexError2(v1030, v114 - 1);
        goto LABEL_1691;
      }
      qmemcpy(v128, &v115[560 * v1030 + 8], sizeof(v128));
      v393 = 0i64;
      v394 = 0i64;
      v391 = 0i64;
      v392 = 0i64;
      v661 = 1925i64;
      v1029 = v128[4];
      if ( !LOBYTE(v128[4]) )
        v1029 = LOBYTE(v128[59]) == 0;
      if ( v1029 == 1 )
      {
        v661 = 1926i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        goto LABEL_953;
      }
      v393 = 0i64;
      v394 = &TM__THWBxVSaWN2Zh7OMooFH0w_301;
      v661 = 1930i64;
      if ( LOBYTE(v128[0]) > 0x55u )
      {
LABEL_941:
        if ( v394 && (*v394 & 0x4000000000000000i64) == 0 )
          deallocShared(v394);
        v661 = 1946i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
LABEL_953:
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v1030;
        v661 = 187i64;
        v825 = v114;
        if ( v114 != v829 )
        {
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_374;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
          failedAssertImpl__stdZassertions_u234(&v106);
          if ( *v1007 )
            goto LABEL_1691;
        }
        continue;
      }
      if ( LOBYTE(v128[0]) >= 0x54u )
      {
        v661 = 1934i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        v828 = v128[6];
        v1028 = v128[6] == 0;
        if ( v128[6] )
        {
          if ( v128[6] <= 0 )
          {
            raiseIndexError2(0i64, v128[6] - 1);
            goto LABEL_946;
          }
          v70 = *(_QWORD *)(v128[7] + 24);
          v100 = *(_QWORD *)(v128[7] + 16);
          v101 = v70;
          v102 = *(_QWORD *)(v128[7] + 32);
          v71 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 1);
          v103 = *(_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435;
          v104 = v71;
          v105 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 2);
          v1028 = eqeq___modelZsimulationZcontroller_u106(&v100, &v103);
        }
        if ( v1028 == 1 )
        {
          v661 = 1699i64;
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_310;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_309;
          eqsink___system_u2667(&v393, &v106);
          goto LABEL_945;
        }
        v381 = 0i64;
        v382 = 0i64;
        v661 = 1937i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        v379 = 0i64;
        v380 = 0i64;
        nimZeroMem_66(&v377, 16i64);
        v377 = input__modelZsimulationZcode95gen_u4122;
        v378 = v1006;
        if ( v1006 )
        {
          v377(&v381, (__int64)v128, 0i64, v128[28], 0, (__int64)v378);
        }
        else
        {
          ((void (__fastcall *)(__int64 *, __int64 *, _QWORD, __int64, _DWORD))v377)(&v106, v128, 0i64, v128[28], 0);
          v381 = v106;
          v382 = (_QWORD *)v107;
        }
        if ( *v1007 )
        {
LABEL_946:
          v661 = 394i64;
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v392 && (*v392 & 0x4000000000000000i64) == 0 )
            deallocShared(v392);
          if ( v394 && (*v394 & 0x4000000000000000i64) == 0 )
            deallocShared(v394);
          if ( *v1007 )
            goto LABEL_1691;
          goto LABEL_953;
        }
        rawNewString(&v106, v381 + 10);
        v379 = v106;
        v380 = v107;
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_312;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_311;
        appendString_29(&v379, &v106);
        v106 = v381;
        v107 = (__int64)v382;
        appendString_29(&v379, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_352;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_325;
        appendString_29(&v379, &v106);
        v661 = 1699i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v106 = v379;
        v107 = v380;
        eqsink___system_u2667(&v393, &v106);
        v661 = 394i64;
        if ( v382 && (*v382 & 0x4000000000000000i64) == 0 )
          deallocShared(v382);
LABEL_945:
        v661 = 1948i64;
        v389 = 0i64;
        v390 = 0i64;
        rawNewString(&v106, v128[24] + v393 + 31);
        v389 = v106;
        v390 = (_QWORD *)v107;
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_369;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_368;
        appendString_29(&v389, &v106);
        v106 = v128[24];
        v107 = v128[25];
        appendString_29(&v389, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_371;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_370;
        appendString_29(&v389, &v106);
        v106 = v393;
        v107 = (__int64)v394;
        appendString_29(&v389, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_373;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_372;
        appendString_29(&v389, &v106);
        v391 = v389;
        v392 = v390;
        prepareAdd(v1006 + 1, v389);
        v106 = v391;
        v107 = (__int64)v392;
        appendString_29(v1006 + 1, &v106);
        goto LABEL_946;
      }
      if ( LOBYTE(v128[0]) < 0x52u )
      {
        if ( LOBYTE(v128[0]) <= 0x27u )
        {
          if ( LOBYTE(v128[0]) < 0x26u )
            goto LABEL_941;
          v373 = 0i64;
          v374 = 0i64;
          v661 = 1944i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
          v371 = 0i64;
          v372 = 0i64;
          load_memory_word__modelZsimulationZcode95gen_u2133(&v373, v128, v128[28]);
          if ( !*v1007 )
          {
            rawNewString(&v106, v373 + 10);
            v371 = v106;
            v372 = v107;
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_356;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_311;
            appendString_29(&v371, &v106);
            v106 = v373;
            v107 = (__int64)v374;
            appendString_29(&v371, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_367;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_325;
            appendString_29(&v371, &v106);
            v661 = 1699i64;
            v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            v106 = v371;
            v107 = v372;
            eqsink___system_u2667(&v393, &v106);
            v661 = 394i64;
            if ( v374 && (*v374 & 0x4000000000000000i64) == 0 )
              deallocShared(v374);
            goto LABEL_945;
          }
          goto LABEL_946;
        }
        if ( LOBYTE(v128[0]) != 55 )
          goto LABEL_941;
        v387 = 0i64;
        v388 = 0i64;
        v385 = 0i64;
        v386 = 0i64;
        v661 = 1932i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        v383 = 0i64;
        v384 = 0i64;
        dollar___modelZsave95mongerZcommon_u260(&v387, v128[28]);
        if ( *v1007 )
          goto LABEL_946;
        state_index__modelZsave95mongerZcommon_u5502 = 0i64;
        v100 = v128[11];
        v101 = v128[12];
        v102 = v128[13];
        state_index__modelZsave95mongerZcommon_u5502 = get_state_index__modelZsave95mongerZcommon_u5502(&v100, 0i64);
        if ( *v1007 )
          goto LABEL_946;
        dollar___systemZdollars_u14(&v385, state_index__modelZsave95mongerZcommon_u5502);
        if ( *v1007 )
          goto LABEL_946;
        rawNewString(&v106, v387 + v385 + 41);
        v383 = v106;
        v384 = v107;
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_304;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_303;
        appendString_29(&v383, &v106);
        v106 = v387;
        v107 = (__int64)v388;
        appendString_29(&v383, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_306;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_305;
        appendString_29(&v383, &v106);
        v106 = v385;
        v107 = (__int64)v386;
        appendString_29(&v383, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_308;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_307;
        appendString_29(&v383, &v106);
        v661 = 1699i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v106 = v383;
        v107 = v384;
        eqsink___system_u2667(&v393, &v106);
        v661 = 394i64;
        if ( v386 && (*v386 & 0x4000000000000000i64) == 0 )
          deallocShared(v386);
        if ( v388 && (*v388 & 0x4000000000000000i64) == 0 )
          deallocShared(v388);
        goto LABEL_945;
      }
      v661 = 1939i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v827 = v128[32];
      v1027 = v128[32] == 0;
      if ( v128[32] )
      {
        if ( v128[32] <= 0 )
        {
LABEL_931:
          raiseIndexError2(0i64, v128[32] - 1);
          goto LABEL_946;
        }
        v1027 = *(_QWORD *)(v128[33] + 40) == 0i64;
      }
      if ( v1027 )
      {
        v661 = 1699i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_353;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_309;
        eqsink___system_u2667(&v393, &v106);
        goto LABEL_945;
      }
      v661 = 1942i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v375 = 0i64;
      v376 = 0i64;
      if ( v128[32] > 0 )
      {
        rawNewString(&v106, *(_QWORD *)(v128[33] + 40) + 10i64);
        v375 = v106;
        v376 = v107;
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_354;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_311;
        appendString_29(&v375, &v106);
        v72 = *(_QWORD *)(v128[33] + 48);
        v106 = *(_QWORD *)(v128[33] + 40);
        v107 = v72;
        appendString_29(&v375, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_355;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_325;
        appendString_29(&v375, &v106);
        v661 = 1699i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v106 = v375;
        v107 = v376;
        eqsink___system_u2667(&v393, &v106);
        goto LABEL_945;
      }
      goto LABEL_931;
    }
    break;
  }
  v661 = 1950i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 2i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_375;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_281;
  appendString_29(v1006 + 1, &v106);
  nimZeroMem_66(v128, 560i64);
  v824 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1026 = 0i64;
  v823 = v114;
  v822 = v114;
  v661 = 184i64;
  while ( v1026 < v822 )
  {
    v661 = 1952i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v824 = v1026;
    if ( v1026 < 0 || v1026 >= v114 )
    {
      raiseIndexError2(v1026, v114 - 1);
      goto LABEL_1691;
    }
    qmemcpy(v128, &v115[560 * v1026 + 8], sizeof(v128));
    v369 = 0i64;
    v370 = 0i64;
    v367 = 0i64;
    v368 = 0i64;
    v661 = 1953i64;
    if ( LOBYTE(v128[0]) == 54 )
    {
      v661 = 1955i64;
      v365 = 0i64;
      v366 = 0i64;
      dollar___systemZdollars_u14(&v369, v824);
      if ( !*v1007 )
      {
        rawNewString(&v106, v369 + 19);
        v365 = v106;
        v366 = (_QWORD *)v107;
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_377;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_376;
        appendString_29(&v365, &v106);
        v106 = v369;
        v107 = (__int64)v370;
        appendString_29(&v365, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_379;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_378;
        appendString_29(&v365, &v106);
        v367 = v365;
        v368 = v366;
        prepareAdd(v1006 + 1, v365);
        v106 = v367;
        v107 = (__int64)v368;
        appendString_29(v1006 + 1, &v106);
      }
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v368 && (*v368 & 0x4000000000000000i64) == 0 )
        deallocShared(v368);
      if ( v370 && (*v370 & 0x4000000000000000i64) == 0 )
        deallocShared(v370);
      if ( *v1007 )
        goto LABEL_1691;
    }
    else
    {
      v661 = 1954i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    }
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1026;
    v661 = 187i64;
    v821 = v114;
    if ( v114 != v822 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_380;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v661 = 1957i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 46i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_382;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_381;
  appendString_29(v1006 + 1, &v106);
  nimZeroMem_66(v128, 560i64);
  v820 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1025 = 0i64;
  v819 = v114;
  v818 = v114;
  v661 = 184i64;
  while ( v1025 < v818 )
  {
    v661 = 1958i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v820 = v1025;
    if ( v1025 < 0 || v1025 >= v114 )
    {
      raiseIndexError2(v1025, v114 - 1);
      goto LABEL_1691;
    }
    qmemcpy(v128, &v115[560 * v1025 + 8], sizeof(v128));
    v363 = 0i64;
    v364 = 0i64;
    v361 = 0i64;
    v362 = 0i64;
    v661 = 1959i64;
    if ( LOBYTE(v128[59]) )
    {
      v661 = 1960i64;
      if ( v128[24] )
      {
        v661 = 1962i64;
        if ( LOBYTE(v128[0]) == 54 )
        {
          v661 = 1966i64;
          v359 = 0i64;
          v360 = 0i64;
          dollar___systemZdollars_u14(&v363, v820);
          if ( !*v1007 )
          {
            rawNewString(&v106, v128[24] + v363 + 42);
            v359 = v106;
            v360 = (_QWORD *)v107;
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_383;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_368;
            appendString_29(&v359, &v106);
            v106 = v128[24];
            v107 = v128[25];
            appendString_29(&v359, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_385;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_384;
            appendString_29(&v359, &v106);
            v106 = v363;
            v107 = (__int64)v364;
            appendString_29(&v359, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_386;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_372;
            appendString_29(&v359, &v106);
            v361 = v359;
            v362 = v360;
            prepareAdd(v1006 + 1, v359);
            v106 = v361;
            v107 = (__int64)v362;
            appendString_29(v1006 + 1, &v106);
          }
          v661 = 394i64;
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v362 && (*v362 & 0x4000000000000000i64) == 0 )
            deallocShared(v362);
          if ( v364 && (*v364 & 0x4000000000000000i64) == 0 )
            deallocShared(v364);
          if ( *v1007 )
            goto LABEL_1691;
        }
        else
        {
          v661 = 1963i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        }
      }
      else
      {
        v661 = 1961i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      }
    }
    else
    {
      v661 = 1959i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    }
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1025;
    v661 = 187i64;
    v817 = v114;
    if ( v114 != v818 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_387;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v661 = 1968i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 2i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_388;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_281;
  appendString_29(v1006 + 1, &v106);
  v661 = 1970i64;
  prepareAdd(v1006 + 1, 58i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_390;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_389;
  appendString_29(v1006 + 1, &v106);
  nimZeroMem_66(v128, 560i64);
  v816 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1024 = 0i64;
  v815 = v114;
  v814 = v114;
  v661 = 184i64;
  while ( v1024 < v814 )
  {
    v661 = 1971i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v816 = v1024;
    if ( v1024 < 0 || v1024 >= v114 )
    {
      raiseIndexError2(v1024, v114 - 1);
      goto LABEL_1691;
    }
    qmemcpy(v128, &v115[560 * v1024 + 8], sizeof(v128));
    v357 = 0i64;
    v358 = 0i64;
    v355 = 0i64;
    v356 = 0i64;
    v661 = 1972i64;
    if ( LOBYTE(v128[59]) )
    {
      v661 = 1973i64;
      if ( v128[24] )
      {
        v661 = 1975i64;
        if ( LOBYTE(v128[0]) == 91 )
        {
          v661 = 1977i64;
          v353 = 0i64;
          v354 = 0i64;
          v813 = 0i64;
          v100 = v128[11];
          v101 = v128[12];
          v102 = v128[13];
          v813 = get_state_index__modelZsave95mongerZcommon_u5502(&v100, 0i64);
          if ( !*v1007 )
          {
            dollar___systemZdollars_u14(&v357, v813);
            if ( !*v1007 )
            {
              rawNewString(&v106, v128[24] + v357 + 90);
              v353 = v106;
              v354 = (_QWORD *)v107;
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_391;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_368;
              appendString_29(&v353, &v106);
              v106 = v128[24];
              v107 = v128[25];
              appendString_29(&v353, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_393;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_392;
              appendString_29(&v353, &v106);
              v106 = v357;
              v107 = (__int64)v358;
              appendString_29(&v353, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_395;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_394;
              appendString_29(&v353, &v106);
              v355 = v353;
              v356 = v354;
              prepareAdd(v1006 + 1, v353);
              v106 = v355;
              v107 = (__int64)v356;
              appendString_29(v1006 + 1, &v106);
            }
          }
          v661 = 394i64;
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v356 && (*v356 & 0x4000000000000000i64) == 0 )
            deallocShared(v356);
          if ( v358 && (*v358 & 0x4000000000000000i64) == 0 )
            deallocShared(v358);
          if ( *v1007 )
            goto LABEL_1691;
        }
        else
        {
          v661 = 1976i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        }
      }
      else
      {
        v661 = 1974i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      }
    }
    else
    {
      v661 = 1972i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    }
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1024;
    v661 = 187i64;
    v812 = v114;
    if ( v114 != v814 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_396;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v661 = 1978i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 2i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_397;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_281;
  appendString_29(v1006 + 1, &v106);
  v661 = 1980i64;
  prepareAdd(v1006 + 1, 54i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_399;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_398;
  appendString_29(v1006 + 1, &v106);
  v811 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1023 = 0i64;
  v810 = v114;
  v809 = v114;
  v661 = 251i64;
  while ( v1023 < v809 )
  {
    v661 = 1981i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( v1023 < 0 || v1023 >= v114 )
    {
      raiseIndexError2(v1023, v114 - 1);
      goto LABEL_1691;
    }
    v811 = &v115[560 * v1023 + 8];
    v661 = 1982i64;
    if ( *(_QWORD *)&v115[560 * v1023 + 200] )
    {
      v808 = 0i64;
      nimZeroMem_66(v128, 80i64);
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      v1022 = 0i64;
      v661 = 183i64;
      v807 = *((_QWORD *)v811 + 8);
      v806 = v807;
      v661 = 184i64;
      while ( v1022 < v806 )
      {
        v661 = 1984i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        v808 = v1022;
        if ( v1022 < 0 || v1022 >= *((_QWORD *)v811 + 8) )
        {
          raiseIndexError2(v1022, *((_QWORD *)v811 + 8) - 1i64);
          goto LABEL_1691;
        }
        v73 = (_QWORD *)(*((_QWORD *)v811 + 9) + 80 * v1022);
        v74 = v73[2];
        v128[0] = v73[1];
        v128[1] = v74;
        v75 = v73[4];
        v128[2] = v73[3];
        v128[3] = v75;
        v76 = v73[6];
        v128[4] = v73[5];
        v128[5] = v76;
        v77 = v73[8];
        v128[6] = v73[7];
        v128[7] = v77;
        v78 = v73[10];
        v128[8] = v73[9];
        v128[9] = v78;
        v351 = 0i64;
        v352 = 0i64;
        v349 = 0i64;
        v350 = 0i64;
        v347 = 0i64;
        v348 = 0i64;
        v345 = 0i64;
        v346 = 0i64;
        v661 = 1985i64;
        if ( v811[472] )
        {
          v661 = 1986i64;
          output_word_size__modelZboardZprototype95list_u4333 = get_output_word_size__modelZboardZprototype95list_u4333(
                                                                  *v811,
                                                                  v808,
                                                                  *((_QWORD *)v811 + 28));
          if ( !*v1007 )
          {
            v661 = 1988i64;
            v342 = 0i64;
            v343 = 0i64;
            dollar___systemZdollars_u14(&v351, v808);
            if ( !*v1007 )
            {
              dollar___modelZsave95mongerZcommon_u260(&v349, output_word_size__modelZboardZprototype95list_u4333);
              if ( !*v1007 )
              {
                v805 = 0i64;
                v79 = *((_QWORD *)v811 + 15);
                v100 = *((_QWORD *)v811 + 14);
                v101 = v79;
                v102 = *((_QWORD *)v811 + 16);
                v805 = get_state_index__modelZsave95mongerZcommon_u5502(&v100, 0i64);
                if ( !*v1007 )
                {
                  dollar___systemZdollars_u14(&v347, v805);
                  if ( !*v1007 )
                  {
                    rawNewString(&v106, v349 + v351 + *((_QWORD *)v811 + 24) + v347 + 90);
                    v342 = v106;
                    v343 = (_QWORD *)v107;
                    v106 = TM__THWBxVSaWN2Zh7OMooFH0w_401;
                    v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_400;
                    appendString_29(&v342, &v106);
                    v80 = *((_QWORD *)v811 + 25);
                    v106 = *((_QWORD *)v811 + 24);
                    v107 = v80;
                    appendString_29(&v342, &v106);
                    v106 = TM__THWBxVSaWN2Zh7OMooFH0w_403;
                    v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_402;
                    appendString_29(&v342, &v106);
                    v106 = v351;
                    v107 = (__int64)v352;
                    appendString_29(&v342, &v106);
                    v106 = TM__THWBxVSaWN2Zh7OMooFH0w_405;
                    v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_404;
                    appendString_29(&v342, &v106);
                    v106 = v349;
                    v107 = (__int64)v350;
                    appendString_29(&v342, &v106);
                    v106 = TM__THWBxVSaWN2Zh7OMooFH0w_406;
                    v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_305;
                    appendString_29(&v342, &v106);
                    v106 = v347;
                    v107 = (__int64)v348;
                    appendString_29(&v342, &v106);
                    v106 = TM__THWBxVSaWN2Zh7OMooFH0w_408;
                    v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_407;
                    appendString_29(&v342, &v106);
                    v345 = v342;
                    v346 = v343;
                    prepareAdd(v1006 + 1, v342);
                    v106 = v345;
                    v107 = (__int64)v346;
                    appendString_29(v1006 + 1, &v106);
                  }
                }
              }
            }
          }
          v661 = 394i64;
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v346 && (*v346 & 0x4000000000000000i64) == 0 )
            deallocShared(v346);
          if ( v348 && (*v348 & 0x4000000000000000i64) == 0 )
            deallocShared(v348);
          if ( v350 && (*v350 & 0x4000000000000000i64) == 0 )
            deallocShared(v350);
          if ( v352 && (*v352 & 0x4000000000000000i64) == 0 )
            deallocShared(v352);
          if ( *v1007 )
            goto LABEL_1691;
        }
        else
        {
          v661 = 1985i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        }
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v1022;
        v661 = 187i64;
        v804 = *((_QWORD *)v811 + 8);
        if ( v804 != v806 )
        {
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_409;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
          failedAssertImpl__stdZassertions_u234(&v106);
          if ( *v1007 )
            goto LABEL_1691;
        }
      }
    }
    else
    {
      v661 = 1983i64;
    }
    ++v1023;
    v661 = 254i64;
    v803 = v114;
    if ( v114 != v809 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_410;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v661 = 1989i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 2i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_411;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_281;
  appendString_29(v1006 + 1, &v106);
  v661 = 1991i64;
  prepareAdd(v1006 + 1, 68i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_413;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_412;
  appendString_29(v1006 + 1, &v106);
  v802 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1021 = 0i64;
  v801 = v573;
  v800 = v573;
  v661 = 251i64;
  while ( v1021 < v800 )
  {
    nimZeroMem_66(v128, 560i64);
    v340 = 0i64;
    v341 = 0i64;
    v661 = 1993i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( v1021 < 0 || v1021 >= v573 )
    {
      raiseIndexError2(v1021, v573 - 1);
      goto LABEL_1691;
    }
    v802 = (_QWORD *)(v574 + 8 * v1021 + 8);
    v661 = 1994i64;
    if ( (__int64)*v802 < 0 || *v802 >= v114 )
    {
      raiseIndexError2(*v802, v114 - 1);
      goto LABEL_1691;
    }
    qmemcpy(v128, &v115[560 * *v802 + 8], sizeof(v128));
    v661 = 1996i64;
    v799 = is_little_endian__modelZboardZmemory95manager_u10(v128);
    if ( *v1007 )
      goto LABEL_1691;
    v339 = v128[1];
    v661 = 1699i64;
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v106 = v128[24];
    v107 = v128[25];
    eqcopy___system_u2661(&v340, &v106);
    v661 = 2000i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( v799 != 1 )
    {
      v331 = 0i64;
      v332 = 0i64;
      v329 = 0i64;
      v330 = 0i64;
      v327 = 0i64;
      v328 = 0i64;
      v661 = 2003i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v325 = 0i64;
      v326 = 0i64;
      dollar___modelZsave95mongerZcommon_u3396(&v331, v339);
      if ( *v1007 )
        goto LABEL_1691;
      dollar___modelZsave95mongerZcommon_u263(&v329, v128[39]);
      if ( *v1007 )
        goto LABEL_1691;
      rawNewString(&v106, v331 + v340 + v329 + 100);
      v325 = v106;
      v326 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_420;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_414;
      appendString_29(&v325, &v106);
      v106 = v340;
      v107 = (__int64)v341;
      appendString_29(&v325, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_421;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_416;
      appendString_29(&v325, &v106);
      v106 = v331;
      v107 = (__int64)v332;
      appendString_29(&v325, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_423;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_422;
      appendString_29(&v325, &v106);
      v106 = v329;
      v107 = (__int64)v330;
      appendString_29(&v325, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_425;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_424;
      appendString_29(&v325, &v106);
      v327 = v325;
      v328 = v326;
      prepareAdd(v1006 + 1, v325);
      v106 = v327;
      v107 = (__int64)v328;
      appendString_29(v1006 + 1, &v106);
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v328 && (*v328 & 0x4000000000000000i64) == 0 )
        deallocShared(v328);
      if ( v330 && (*v330 & 0x4000000000000000i64) == 0 )
        deallocShared(v330);
      if ( v332 && (*v332 & 0x4000000000000000i64) == 0 )
        deallocShared(v332);
    }
    else
    {
      v337 = 0i64;
      v338 = 0i64;
      v335 = 0i64;
      v336 = 0i64;
      v661 = 2001i64;
      v333 = 0i64;
      v334 = 0i64;
      dollar___modelZsave95mongerZcommon_u3396(&v337, v339);
      if ( *v1007 )
        goto LABEL_1691;
      rawNewString(&v106, v340 + v337 + 69);
      v333 = v106;
      v334 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_415;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_414;
      appendString_29(&v333, &v106);
      v106 = v340;
      v107 = (__int64)v341;
      appendString_29(&v333, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_417;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_416;
      appendString_29(&v333, &v106);
      v106 = v337;
      v107 = (__int64)v338;
      appendString_29(&v333, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_419;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_418;
      appendString_29(&v333, &v106);
      v335 = v333;
      v336 = v334;
      prepareAdd(v1006 + 1, v333);
      v106 = v335;
      v107 = (__int64)v336;
      appendString_29(v1006 + 1, &v106);
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v336 && (*v336 & 0x4000000000000000i64) == 0 )
        deallocShared(v336);
      if ( v338 && (*v338 & 0x4000000000000000i64) == 0 )
        deallocShared(v338);
    }
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1021;
    v661 = 254i64;
    v798 = v573;
    if ( v573 != v800 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_426;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
    v661 = 394i64;
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v341 && (*v341 & 0x4000000000000000i64) == 0 )
      deallocShared(v341);
  }
  v661 = 2005i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 2i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_427;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_281;
  appendString_29(v1006 + 1, &v106);
  v661 = 2007i64;
  prepareAdd(v1006 + 1, 62i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_429;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_428;
  appendString_29(v1006 + 1, &v106);
  v797 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1020 = 0i64;
  v796 = v573;
  v795 = v573;
  v661 = 251i64;
  while ( v1020 < v795 )
  {
    nimZeroMem_66(v128, 560i64);
    v323 = 0i64;
    v324 = 0i64;
    v661 = 2009i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( v1020 < 0 || v1020 >= v573 )
    {
      raiseIndexError2(v1020, v573 - 1);
      goto LABEL_1691;
    }
    v797 = (_QWORD *)(v574 + 8 * v1020 + 8);
    v661 = 2010i64;
    if ( (__int64)*v797 < 0 || *v797 >= v114 )
    {
      raiseIndexError2(*v797, v114 - 1);
      goto LABEL_1691;
    }
    qmemcpy(v128, &v115[560 * *v797 + 8], sizeof(v128));
    v322 = v128[1];
    v661 = 1699i64;
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v106 = v128[24];
    v107 = v128[25];
    eqcopy___system_u2661(&v323, &v106);
    v661 = 2014i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v794 = 0;
    v794 = is_little_endian__modelZboardZmemory95manager_u10(v128);
    if ( *v1007 )
      goto LABEL_1691;
    if ( v794 != 1 )
    {
      v314 = 0i64;
      v315 = 0i64;
      v312 = 0i64;
      v313 = 0i64;
      v310 = 0i64;
      v311 = 0i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      v661 = 2021i64;
      v308 = 0i64;
      v309 = 0i64;
      dollar___modelZsave95mongerZcommon_u3396(&v314, v322);
      if ( *v1007 )
        goto LABEL_1691;
      dollar___modelZsave95mongerZcommon_u263(&v312, v128[39]);
      if ( *v1007 )
        goto LABEL_1691;
      rawNewString(&v106, v314 + v323 + v312 + 80);
      v308 = v106;
      v309 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_435;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_414;
      appendString_29(&v308, &v106);
      v106 = v323;
      v107 = (__int64)v324;
      appendString_29(&v308, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_436;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_431;
      appendString_29(&v308, &v106);
      v106 = v314;
      v107 = (__int64)v315;
      appendString_29(&v308, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_438;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_437;
      appendString_29(&v308, &v106);
      v106 = v312;
      v107 = (__int64)v313;
      appendString_29(&v308, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_440;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_439;
      appendString_29(&v308, &v106);
      v310 = v308;
      v311 = v309;
      prepareAdd(v1006 + 1, v308);
      v106 = v310;
      v107 = (__int64)v311;
      appendString_29(v1006 + 1, &v106);
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v311 && (*v311 & 0x4000000000000000i64) == 0 )
        deallocShared(v311);
      if ( v313 && (*v313 & 0x4000000000000000i64) == 0 )
        deallocShared(v313);
      if ( v315 && (*v315 & 0x4000000000000000i64) == 0 )
        deallocShared(v315);
    }
    else
    {
      v320 = 0i64;
      v321 = 0i64;
      v318 = 0i64;
      v319 = 0i64;
      v661 = 2016i64;
      v316 = 0i64;
      v317 = 0i64;
      dollar___modelZsave95mongerZcommon_u3396(&v320, v322);
      if ( *v1007 )
        goto LABEL_1691;
      rawNewString(&v106, v323 + v320 + 53);
      v316 = v106;
      v317 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_430;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_414;
      appendString_29(&v316, &v106);
      v106 = v323;
      v107 = (__int64)v324;
      appendString_29(&v316, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_432;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_431;
      appendString_29(&v316, &v106);
      v106 = v320;
      v107 = (__int64)v321;
      appendString_29(&v316, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_434;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_433;
      appendString_29(&v316, &v106);
      v318 = v316;
      v319 = v317;
      prepareAdd(v1006 + 1, v316);
      v106 = v318;
      v107 = (__int64)v319;
      appendString_29(v1006 + 1, &v106);
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v319 && (*v319 & 0x4000000000000000i64) == 0 )
        deallocShared(v319);
      if ( v321 && (*v321 & 0x4000000000000000i64) == 0 )
        deallocShared(v321);
    }
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1020;
    v661 = 254i64;
    v793 = v573;
    if ( v573 != v795 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_441;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
    v661 = 394i64;
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v324 && (*v324 & 0x4000000000000000i64) == 0 )
      deallocShared(v324);
  }
  v661 = 2024i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 2i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_442;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_281;
  appendString_29(v1006 + 1, &v106);
  v661 = 2029i64;
  v548 = 0i64;
  v549 = 0i64;
  dollar___systemZdollars_u14(&v571, v1006[69]);
  if ( *v1007 )
    goto LABEL_1691;
  rawNewString(&v106, v571 + 322);
  v548 = v106;
  v549 = (_QWORD *)v107;
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_444;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_443;
  appendString_29(&v548, &v106);
  v106 = v571;
  v107 = (__int64)v572;
  appendString_29(&v548, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_446;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_445;
  appendString_29(&v548, &v106);
  v569 = v548;
  v570 = v549;
  prepareAdd(v1006 + 1, v548);
  v106 = v569;
  v107 = (__int64)v570;
  appendString_29(v1006 + 1, &v106);
  v661 = 2052i64;
  prepareAdd(v1006 + 1, 499i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_448;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_447;
  appendString_29(v1006 + 1, &v106);
  v661 = 2079i64;
  prepareAdd(v1006 + 1, 55i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_450;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_449;
  appendString_29(v1006 + 1, &v106);
  v661 = 2080i64;
  prepareAdd(v1006 + 1, 56i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_452;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_451;
  appendString_29(v1006 + 1, &v106);
  v661 = 2081i64;
  v546 = 0i64;
  v547 = 0i64;
  allocation_top__modelZsave95mongerZcommon_u5497 = 0i64;
  allocation_top__modelZsave95mongerZcommon_u5497 = get_allocation_top__modelZsave95mongerZcommon_u5497();
  if ( *v1007 )
    goto LABEL_1691;
  v545 = allocation_top__modelZsave95mongerZcommon_u5497 + 1;
  if ( __OFADD__(1i64, allocation_top__modelZsave95mongerZcommon_u5497) )
  {
LABEL_1148:
    raiseOverflow();
    goto LABEL_1691;
  }
  dollar___systemZdollars_u14(&v567, v545);
  if ( *v1007 )
    goto LABEL_1691;
  rawNewString(&v106, v567 + 38);
  v546 = v106;
  v547 = (_QWORD *)v107;
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_454;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_453;
  appendString_29(&v546, &v106);
  v106 = v567;
  v107 = (__int64)v568;
  appendString_29(&v546, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_457;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_456;
  appendString_29(&v546, &v106);
  v565 = v546;
  v566 = v547;
  prepareAdd(v1006 + 1, v546);
  v106 = v565;
  v107 = (__int64)v566;
  appendString_29(v1006 + 1, &v106);
  nimZeroMem_66(v128, 560i64);
  v791 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1019 = 0i64;
  v790 = v114;
  v789 = v114;
  v661 = 184i64;
  while ( v1019 < v789 )
  {
    v661 = 2084i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v791 = v1019;
    if ( v1019 < 0 || v1019 >= v114 )
    {
      raiseIndexError2(v1019, v114 - 1);
      goto LABEL_1691;
    }
    qmemcpy(v128, &v115[560 * v1019 + 8], sizeof(v128));
    v661 = 2085i64;
    if ( LOBYTE(v128[0]) == 91 )
    {
      v306 = 0i64;
      v307 = 0i64;
      v304 = 0i64;
      v305 = 0i64;
      v661 = 2086i64;
      v302 = 0i64;
      v303 = 0i64;
      v788 = 0i64;
      v100 = v128[11];
      v101 = v128[12];
      v102 = v128[13];
      v788 = get_state_index__modelZsave95mongerZcommon_u5502(&v100, 16i64);
      if ( *v1007 )
        goto LABEL_1691;
      v81 = __OFADD__(*refptr_simulation_state__modelZsimulator95types_u81, v788);
      v301 = *refptr_simulation_state__modelZsimulator95types_u81 + v788;
      if ( v81 )
        goto LABEL_1148;
      dollar___systemZdollars_u14(&v306, v301);
      if ( *v1007 )
        goto LABEL_1691;
      rawNewString(&v106, v306 + 26);
      v302 = v106;
      v303 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_459;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_458;
      appendString_29(&v302, &v106);
      v106 = v306;
      v107 = (__int64)v307;
      appendString_29(&v302, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_462;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_461;
      appendString_29(&v302, &v106);
      v304 = v302;
      v305 = v303;
      prepareAdd(v1006 + 1, v302);
      v106 = v304;
      v107 = (__int64)v305;
      appendString_29(v1006 + 1, &v106);
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v305 && (*v305 & 0x4000000000000000i64) == 0 )
        deallocShared(v305);
      if ( v307 && (*v307 & 0x4000000000000000i64) == 0 )
        deallocShared(v307);
    }
    v661 = 2088i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    if ( LOBYTE(v128[0]) == 118 )
    {
      v661 = 2090i64;
      if ( LOBYTE(v128[4]) != 1 )
      {
        v661 = 2093i64;
        v787 = 0;
        v787 = initial_data__modelZmodel95types_u1497(v128);
        if ( *v1007 )
          goto LABEL_1691;
        if ( !v787 )
        {
          v299 = 0i64;
          v300 = 0i64;
          v297 = 0i64;
          v298 = 0i64;
          v295 = 0i64;
          v296 = 0i64;
          v661 = 2094i64;
          v293 = 0i64;
          v294 = 0i64;
          dollar___modelZsave95mongerZcommon_u3396(&v299, v128[1]);
          if ( *v1007 )
            goto LABEL_1691;
          v292 = plus___modelZsave95mongerZcommon_u229(v128[39], 4096i64);
          if ( *v1007 )
            goto LABEL_1691;
          dollar___modelZsave95mongerZcommon_u263(&v297, v292);
          if ( *v1007 )
            goto LABEL_1691;
          rawNewString(&v106, v299 + v297 + 34);
          v293 = v106;
          v294 = (_QWORD *)v107;
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_464;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_463;
          appendString_29(&v293, &v106);
          v106 = v299;
          v107 = (__int64)v300;
          appendString_29(&v293, &v106);
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_466;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_465;
          appendString_29(&v293, &v106);
          v106 = v297;
          v107 = (__int64)v298;
          appendString_29(&v293, &v106);
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_467;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_456;
          appendString_29(&v293, &v106);
          v295 = v293;
          v296 = v294;
          prepareAdd(v1006 + 1, v293);
          v106 = v295;
          v107 = (__int64)v296;
          appendString_29(v1006 + 1, &v106);
          v661 = 394i64;
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v296 && (*v296 & 0x4000000000000000i64) == 0 )
            deallocShared(v296);
          if ( v298 && (*v298 & 0x4000000000000000i64) == 0 )
            deallocShared(v298);
          if ( v300 && (*v300 & 0x4000000000000000i64) == 0 )
            deallocShared(v300);
        }
        v661 = 2095i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        v1018 = 0;
        v786 = 0;
        v786 = initial_data__modelZmodel95types_u1497(v128);
        if ( *v1007 )
          goto LABEL_1691;
        v1018 = v786 == 5;
        if ( v786 == 5 )
        {
          v82 = v1006[14];
          v106 = v1006[13];
          v107 = v82;
          v98 = TM__THWBxVSaWN2Zh7OMooFH0w_469;
          v99 = (char *)&TM__THWBxVSaWN2Zh7OMooFH0w_468;
          v1018 = eqStrings_15(&v106, &v98);
        }
        if ( v1018 != 1 )
        {
          v290 = 0i64;
          v291 = 0i64;
          v288 = 0i64;
          v289 = 0i64;
          v286 = 0i64;
          v287 = 0i64;
          v284 = 0i64;
          v285 = 0i64;
          v661 = 2099i64;
          v282 = 0i64;
          v283 = 0i64;
          dollar___modelZsave95mongerZcommon_u3396(&v290, v128[1]);
          if ( *v1007 )
            goto LABEL_1691;
          dollar___modelZsave95mongerZcommon_u3396(&v288, v128[1]);
          if ( *v1007 )
            goto LABEL_1691;
          v281 = plus___modelZsave95mongerZcommon_u229(v128[39], 4096i64);
          if ( *v1007 )
            goto LABEL_1691;
          dollar___modelZsave95mongerZcommon_u263(&v286, v281);
          if ( *v1007 )
            goto LABEL_1691;
          rawNewString(&v106, v288 + v290 + v286 + 54);
          v282 = v106;
          v283 = (_QWORD *)v107;
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_471;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_470;
          appendString_29(&v282, &v106);
          v106 = v290;
          v107 = (__int64)v291;
          appendString_29(&v282, &v106);
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_473;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_472;
          appendString_29(&v282, &v106);
          v106 = v288;
          v107 = (__int64)v289;
          appendString_29(&v282, &v106);
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_474;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_465;
          appendString_29(&v282, &v106);
          v106 = v286;
          v107 = (__int64)v287;
          appendString_29(&v282, &v106);
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_475;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_456;
          appendString_29(&v282, &v106);
          v284 = v282;
          v285 = v283;
          prepareAdd(v1006 + 1, v282);
          v106 = v284;
          v107 = (__int64)v285;
          appendString_29(v1006 + 1, &v106);
          v661 = 394i64;
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v285 && (*v285 & 0x4000000000000000i64) == 0 )
            deallocShared(v285);
          if ( v287 && (*v287 & 0x4000000000000000i64) == 0 )
            deallocShared(v287);
          if ( v289 && (*v289 & 0x4000000000000000i64) == 0 )
            deallocShared(v289);
          if ( v291 && (*v291 & 0x4000000000000000i64) == 0 )
            deallocShared(v291);
        }
      }
      else
      {
        v661 = 2091i64;
      }
    }
    else
    {
      v661 = 2089i64;
    }
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1019;
    v661 = 187i64;
    v785 = v114;
    if ( v114 != v789 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_476;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v661 = 2101i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 18i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_478;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_477;
  appendString_29(v1006 + 1, &v106);
  v784 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1017 = 0i64;
  v783 = v114;
  v782 = v114;
  v661 = 251i64;
  while ( 2 )
  {
    if ( v1017 < v782 )
    {
      v661 = 2110i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      if ( v1017 < 0 || v1017 >= v114 )
      {
        raiseIndexError2(v1017, v114 - 1);
        goto LABEL_1691;
      }
      v784 = (__int64 *)&v115[560 * v1017 + 8];
      v279 = 0i64;
      v280 = 0i64;
      v277 = 0i64;
      v278 = 0i64;
      v275 = 0i64;
      v276 = 0i64;
      v273 = 0i64;
      v274 = 0i64;
      v661 = 2111i64;
      v781 = 0i64;
      v781 = X5BX5D___modelZboardZprototype95list_u4239(
               refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
               *(unsigned __int8 *)v784);
      if ( !*v1007 )
      {
        if ( !*(_WORD *)(v781 + 66) )
        {
          v661 = 394i64;
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v276 && (*v276 & 0x4000000000000000i64) == 0 )
            deallocShared(v276);
          if ( v278 && (*v278 & 0x4000000000000000i64) == 0 )
            deallocShared(v278);
          if ( v280 && (*v280 & 0x4000000000000000i64) == 0 )
            deallocShared(v280);
          v661 = 2111i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
          goto LABEL_1274;
        }
        v661 = 2112i64;
        get_property_name__modelZsimulationZcode95gen_u43(&v279, v784);
        if ( !*v1007 )
        {
          v661 = 2113i64;
          if ( !v279 )
          {
            v661 = 394i64;
            v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v276 && (*v276 & 0x4000000000000000i64) == 0 )
              deallocShared(v276);
            if ( v278 && (*v278 & 0x4000000000000000i64) == 0 )
              deallocShared(v278);
            if ( v280 && (*v280 & 0x4000000000000000i64) == 0 )
              deallocShared(v280);
            v661 = 2113i64;
            v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
            goto LABEL_1274;
          }
          v661 = 2114i64;
          v780 = 0;
          if ( v564 )
            v83 = v564 + 8;
          else
            v83 = 0i64;
          v106 = v279;
          v107 = (__int64)v280;
          v780 = contains__stdZenumutils_u50_3(v83, v563, &v106);
          if ( v780 == 1 )
          {
            v661 = 394i64;
            v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v276 && (*v276 & 0x4000000000000000i64) == 0 )
              deallocShared(v276);
            if ( v278 && (*v278 & 0x4000000000000000i64) == 0 )
              deallocShared(v278);
            if ( v280 && (*v280 & 0x4000000000000000i64) == 0 )
              deallocShared(v280);
            v661 = 2114i64;
            v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
            goto LABEL_1274;
          }
          v661 = 2115i64;
          if ( v784[28] <= 0 )
          {
            v661 = 394i64;
            v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v276 && (*v276 & 0x4000000000000000i64) == 0 )
              deallocShared(v276);
            if ( v278 && (*v278 & 0x4000000000000000i64) == 0 )
              deallocShared(v278);
            if ( v280 && (*v280 & 0x4000000000000000i64) == 0 )
              deallocShared(v280);
            v661 = 2115i64;
            v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
LABEL_1274:
            v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v1017;
            v661 = 254i64;
            v779 = v114;
            if ( v114 != v782 )
            {
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_495;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
              failedAssertImpl__stdZassertions_u234(&v106);
              if ( *v1007 )
                goto LABEL_1691;
            }
            continue;
          }
          v661 = 2117i64;
          v271 = 0i64;
          v272 = 0i64;
          dollar___modelZsave95mongerZcommon_u260(&v277, v784[28]);
          if ( !*v1007 )
          {
            rawNewString(&v106, v279 + v277 + 9);
            v271 = v106;
            v272 = (_QWORD *)v107;
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_487;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_486;
            appendString_29(&v271, &v106);
            v106 = v279;
            v107 = (__int64)v280;
            appendString_29(&v271, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_489;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_488;
            appendString_29(&v271, &v106);
            v106 = v277;
            v107 = (__int64)v278;
            appendString_29(&v271, &v106);
            v106 = TM__THWBxVSaWN2Zh7OMooFH0w_491;
            v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_490;
            appendString_29(&v271, &v106);
            v275 = v271;
            v276 = v272;
            prepareAdd(v1006 + 1, v271);
            v106 = v275;
            v107 = (__int64)v276;
            appendString_29(v1006 + 1, &v106);
            v661 = 1699i64;
            v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            v106 = v279;
            v107 = (__int64)v280;
            eqdup___system_u2664(&v273, &v106);
            v661 = 2119i64;
            v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
            v106 = v273;
            v107 = v274;
            add__stdZenumutils_u70(&v563, &v106);
            v661 = 2121i64;
            if ( *(_BYTE *)v784 == 62 )
            {
              v269 = 0i64;
              v270 = 0i64;
              v661 = 2122i64;
              v267 = 0i64;
              v268 = 0i64;
              rawNewString(&v106, v279 + 20);
              v267 = v106;
              v268 = (_QWORD *)v107;
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_492;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_486;
              appendString_29(&v267, &v106);
              v106 = v279;
              v107 = (__int64)v280;
              appendString_29(&v267, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_494;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_493;
              appendString_29(&v267, &v106);
              v269 = v267;
              v270 = v268;
              prepareAdd(v1006 + 1, v267);
              v106 = v269;
              v107 = (__int64)v270;
              appendString_29(v1006 + 1, &v106);
              v661 = 394i64;
              v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              if ( v270 )
              {
                if ( (*v270 & 0x4000000000000000i64) == 0 )
                  deallocShared(v270);
              }
            }
          }
        }
      }
      if ( v276 && (*v276 & 0x4000000000000000i64) == 0 )
        deallocShared(v276);
      if ( v278 && (*v278 & 0x4000000000000000i64) == 0 )
        deallocShared(v278);
      if ( v280 && (*v280 & 0x4000000000000000i64) == 0 )
        deallocShared(v280);
      if ( *v1007 )
        goto LABEL_1691;
      goto LABEL_1274;
    }
    break;
  }
  v661 = 2124i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 17i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_497;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_496;
  appendString_29(v1006 + 1, &v106);
  v778 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1016 = 0i64;
  v777 = v114;
  v776 = v114;
  v661 = 251i64;
  while ( 2 )
  {
    if ( v1016 < v776 )
    {
      v661 = 2129i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      if ( v1016 < 0 || v1016 >= v114 )
      {
        raiseIndexError2(v1016, v114 - 1);
        goto LABEL_1691;
      }
      v778 = &v115[560 * v1016 + 8];
      v265 = 0i64;
      v266 = 0i64;
      v263 = 0i64;
      v264 = 0i64;
      v261 = 0i64;
      v262 = 0i64;
      v259 = 0i64;
      v260 = 0i64;
      v661 = 2130i64;
      v775 = 0i64;
      v775 = X5BX5D___modelZboardZprototype95list_u4239(
               refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
               (unsigned __int8)*v778);
      if ( !*v1007 )
      {
        if ( !*(_WORD *)(v775 + 68) )
        {
          v661 = 394i64;
          v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v260 && (*v260 & 0x4000000000000000i64) == 0 )
            deallocShared(v260);
          if ( v262 && (*v262 & 0x4000000000000000i64) == 0 )
            deallocShared(v262);
          if ( v264 && (*v264 & 0x4000000000000000i64) == 0 )
            deallocShared(v264);
          if ( v266 && (*v266 & 0x4000000000000000i64) == 0 )
            deallocShared(v266);
          v661 = 2130i64;
          v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
          goto LABEL_1350;
        }
        v661 = 2131i64;
        get_property_name__modelZsimulationZcode95gen_u43(&v265, v778);
        if ( !*v1007 )
        {
          v661 = 2132i64;
          if ( !v265 )
          {
            v661 = 394i64;
            v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v260 && (*v260 & 0x4000000000000000i64) == 0 )
              deallocShared(v260);
            if ( v262 && (*v262 & 0x4000000000000000i64) == 0 )
              deallocShared(v262);
            if ( v264 && (*v264 & 0x4000000000000000i64) == 0 )
              deallocShared(v264);
            if ( v266 && (*v266 & 0x4000000000000000i64) == 0 )
              deallocShared(v266);
            v661 = 2132i64;
            v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
            goto LABEL_1350;
          }
          v661 = 2133i64;
          v774 = 0;
          v100 = v560;
          v101 = v561;
          v102 = v562;
          v106 = v265;
          v107 = (__int64)v266;
          v774 = contains__modelZsimulationZcode95gen_u7276(&v100, &v106);
          if ( !*v1007 )
          {
            if ( v774 == 1 )
            {
              v661 = 394i64;
              v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              if ( v260 && (*v260 & 0x4000000000000000i64) == 0 )
                deallocShared(v260);
              if ( v262 && (*v262 & 0x4000000000000000i64) == 0 )
                deallocShared(v262);
              if ( v264 && (*v264 & 0x4000000000000000i64) == 0 )
                deallocShared(v264);
              if ( v266 && (*v266 & 0x4000000000000000i64) == 0 )
                deallocShared(v266);
              v661 = 2133i64;
              v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
LABEL_1350:
              v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v1016;
              v661 = 254i64;
              v772 = v114;
              if ( v114 != v776 )
              {
                v106 = TM__THWBxVSaWN2Zh7OMooFH0w_506;
                v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
                failedAssertImpl__stdZassertions_u234(&v106);
                if ( *v1007 )
                  goto LABEL_1691;
              }
              continue;
            }
            v661 = 2134i64;
            v84 = *((_QWORD *)v778 + 28);
            if ( v84 <= 0 )
              v84 = 1i64;
            v773 = v84;
            v661 = 2136i64;
            v257 = 0i64;
            v258 = 0i64;
            dollar___systemZdollars_u14(&v263, v84);
            if ( !*v1007 )
            {
              rawNewString(&v106, v265 + v263 + 9);
              v257 = v106;
              v258 = (_QWORD *)v107;
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_498;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_486;
              appendString_29(&v257, &v106);
              v106 = v265;
              v107 = (__int64)v266;
              appendString_29(&v257, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_499;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_488;
              appendString_29(&v257, &v106);
              v106 = v263;
              v107 = (__int64)v264;
              appendString_29(&v257, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_500;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_490;
              appendString_29(&v257, &v106);
              v261 = v257;
              v262 = v258;
              prepareAdd(v1006 + 1, v257);
              v106 = v261;
              v107 = (__int64)v262;
              appendString_29(v1006 + 1, &v106);
              v661 = 2137i64;
              v255 = 0i64;
              v256 = 0i64;
              rawNewString(&v106, v265 + 17);
              v255 = v106;
              v256 = (_QWORD *)v107;
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_501;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_486;
              appendString_29(&v255, &v106);
              v106 = v265;
              v107 = (__int64)v266;
              appendString_29(&v255, &v106);
              v106 = TM__THWBxVSaWN2Zh7OMooFH0w_503;
              v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_502;
              appendString_29(&v255, &v106);
              v259 = v255;
              v260 = v256;
              prepareAdd(v1006 + 1, v255);
              v106 = v259;
              v107 = (__int64)v260;
              appendString_29(v1006 + 1, &v106);
              v661 = 2138i64;
              if ( *v778 == 70 )
              {
                v252 = 0i64;
                v253 = 0i64;
                v661 = 2139i64;
                v250 = 0i64;
                v251 = 0i64;
                rawNewString(&v106, v265 + 20);
                v250 = v106;
                v251 = (_QWORD *)v107;
                v106 = TM__THWBxVSaWN2Zh7OMooFH0w_504;
                v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_486;
                appendString_29(&v250, &v106);
                v106 = v265;
                v107 = (__int64)v266;
                appendString_29(&v250, &v106);
                v106 = TM__THWBxVSaWN2Zh7OMooFH0w_505;
                v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_493;
                appendString_29(&v250, &v106);
                v252 = v250;
                v253 = v251;
                prepareAdd(v1006 + 1, v250);
                v106 = v252;
                v107 = (__int64)v253;
                appendString_29(v1006 + 1, &v106);
                v661 = 394i64;
                v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                if ( v253 )
                {
                  if ( (*v253 & 0x4000000000000000i64) == 0 )
                    deallocShared(v253);
                }
              }
              v661 = 2141i64;
              v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
              v254 = bits__modelZsave95mongerZcommon_u192(v773);
              if ( !*v1007 )
              {
                v106 = v265;
                v107 = (__int64)v266;
                X5BX5Deq___modelZsimulationZcode95gen_u7351(&v560, &v106, v254);
              }
            }
          }
        }
      }
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v260 && (*v260 & 0x4000000000000000i64) == 0 )
        deallocShared(v260);
      if ( v262 && (*v262 & 0x4000000000000000i64) == 0 )
        deallocShared(v262);
      if ( v264 && (*v264 & 0x4000000000000000i64) == 0 )
        deallocShared(v264);
      if ( v266 && (*v266 & 0x4000000000000000i64) == 0 )
        deallocShared(v266);
      if ( *v1007 )
        goto LABEL_1691;
      goto LABEL_1350;
    }
    break;
  }
  v661 = 2143i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 86i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_508;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_507;
  appendString_29(v1006 + 1, &v106);
  v1006[12] = 4i64;
  v661 = 2154i64;
  nimZeroMem_66(&v543, 16i64);
  v543 = add_circuit_code__modelZsimulationZcode95gen_u4264;
  v544 = v1006;
  if ( v1006 )
  {
    v106 = v114;
    v107 = (__int64)v115;
    v98 = v563;
    v99 = v564;
    v100 = v560;
    v101 = v561;
    v102 = v562;
    v543((int)&v558, (int)&v106, 1, (int)&v98, (__int64)&v100, (__int64)v544);
  }
  else
  {
    v98 = v114;
    v99 = v115;
    v96 = v563;
    v97 = v564;
    v100 = v560;
    v101 = v561;
    v102 = v562;
    ((void (__fastcall *)(__int64 *, __int64 *, __int64, __int64 *, __int64 *))v543)(&v106, &v98, 1i64, &v96, &v100);
    v558 = v106;
    v559 = v107;
  }
  if ( *v1007 )
    goto LABEL_1691;
  v661 = 2156i64;
  prepareAdd(v1006 + 1, 1665i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2426;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2425;
  appendString_29(v1006 + 1, &v106);
  v661 = 2228i64;
  if ( *((_BYTE *)v1006 + 168) != 3 )
  {
    v661 = 2229i64;
    prepareAdd(v1006 + 1, 62i64);
    v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2428;
    v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2427;
    appendString_29(v1006 + 1, &v106);
  }
  v1006[12] = 12i64;
  v661 = 2235i64;
  nimZeroMem_66(&v541, 16i64);
  v541 = add_circuit_code__modelZsimulationZcode95gen_u4264;
  v542 = v1006;
  if ( v1006 )
  {
    v106 = v114;
    v107 = (__int64)v115;
    v98 = v563;
    v99 = v564;
    v100 = v560;
    v101 = v561;
    v102 = v562;
    v541((int)&v556, (int)&v106, 0, (int)&v98, (__int64)&v100, (__int64)v542);
  }
  else
  {
    v98 = v114;
    v99 = v115;
    v96 = v563;
    v97 = v564;
    v100 = v560;
    v101 = v561;
    v102 = v562;
    ((void (__fastcall *)(__int64 *, __int64 *, _QWORD, __int64 *, __int64 *))v541)(&v106, &v98, 0i64, &v96, &v100);
    v556 = v106;
    v557 = v107;
  }
  if ( *v1007 )
    goto LABEL_1691;
  v661 = 2237i64;
  nimZeroMem_66(&v247, 24i64);
  nimZeroMem_66(&v245, 16i64);
  v661 = 767i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
  v85 = v1006[84];
  v100 = v1006[83];
  v101 = v85;
  v102 = v1006[85];
  v771 = len__modelZsimulationZcode95gen_u8507(&v100);
  if ( *v1007 )
    goto LABEL_1691;
  v770 = 0i64;
  v769 = 0i64;
  v661 = 768i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
  v768 = v1006[83] - 1i64;
  v769 = v768;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
  v1015 = 0i64;
  v661 = 97i64;
  while ( v1015 <= v769 )
  {
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
    v770 = v1015;
    v661 = 769i64;
    if ( v1015 < 0 || v770 >= v1006[83] )
    {
LABEL_1376:
      raiseIndexError2(v770, v1006[83] - 1i64);
      goto LABEL_1691;
    }
    v767 = 0;
    v767 = isFilled__pureZcollectionsZtables_u31_9(*(_QWORD *)(v1006[84] + 48 * v770 + 8));
    if ( *v1007 )
      goto LABEL_1691;
    if ( v767 == 1 )
    {
      v661 = 2238i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      if ( v770 < 0 )
        goto LABEL_1376;
      if ( v770 >= v1006[83] )
        goto LABEL_1376;
      v86 = (_QWORD *)(48 * v770 + v1006[84]);
      v87 = v86[3];
      v247 = v86[2];
      v248 = v87;
      v249 = v86[4];
      if ( v770 >= v1006[83] )
        goto LABEL_1376;
      v88 = v1006[84];
      v89 = *(_QWORD *)(v88 + 48 * v770 + 48);
      v245 = *(_QWORD *)(v88 + 48 * v770 + 40);
      v246 = v89;
      v661 = 2239i64;
      if ( v89 )
      {
        v242 = 0i64;
        v243 = 0i64;
        v240 = 0i64;
        v241 = 0i64;
        v238 = 0i64;
        v239 = 0i64;
        v236 = 0i64;
        v237 = 0i64;
        v100 = v247;
        v101 = v248;
        v102 = v249;
        dollar___modelZsave95mongerZcommon_u5506(&v242, &v100);
        if ( *v1007 )
          goto LABEL_1691;
        v106 = v245;
        v107 = v246;
        dollar___modelZsimulationZcode95gen_u8768(&v240, &v106);
        if ( *v1007 )
          goto LABEL_1691;
        rawNewString(&v106, v242 + v240 + 143);
        v236 = v106;
        v237 = (_QWORD *)v107;
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2431;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2430;
        appendString_29(&v236, &v106);
        v106 = v242;
        v107 = (__int64)v243;
        appendString_29(&v236, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2432;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_58;
        appendString_29(&v236, &v106);
        v106 = v240;
        v107 = (__int64)v241;
        appendString_29(&v236, &v106);
        v238 = v236;
        v239 = v237;
        v106 = v236;
        v107 = (__int64)v237;
        failedAssertImpl__stdZassertions_u234(&v106);
        if ( *v1007 )
          goto LABEL_1691;
        v661 = 394i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v239 && (*v239 & 0x4000000000000000i64) == 0 )
          deallocShared(v239);
        if ( v241 && (*v241 & 0x4000000000000000i64) == 0 )
          deallocShared(v241);
        if ( v243 && (*v243 & 0x4000000000000000i64) == 0 )
          deallocShared(v243);
      }
      v661 = 771i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
      v766 = 0i64;
      v90 = v1006[84];
      v100 = v1006[83];
      v101 = v90;
      v102 = v1006[85];
      v766 = len__modelZsimulationZcode95gen_u8507(&v100);
      if ( *v1007 )
        goto LABEL_1691;
      if ( v766 != v771 )
      {
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2434;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2433;
        failedAssertImpl__stdZassertions_u234(&v106);
        if ( *v1007 )
          goto LABEL_1691;
      }
    }
    v661 = 102i64;
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v244 = v1015 + 1;
    if ( __OFADD__(1i64, v1015) )
    {
LABEL_1396:
      raiseOverflow();
      goto LABEL_1691;
    }
    v1015 = v244;
  }
  nimZeroMem_66(v128, 560i64);
  v765 = 0i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v1014 = 0i64;
  v764 = v114;
  v763 = v114;
  v661 = 184i64;
  while ( v1014 < v763 )
  {
    v661 = 2241i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v765 = v1014;
    if ( v1014 < 0 || v1014 >= v114 )
    {
      raiseIndexError2(v1014, v114 - 1);
      goto LABEL_1691;
    }
    qmemcpy(v128, &v115[560 * v1014 + 8], sizeof(v128));
    v1013 = -1i64;
    v762 = 0i64;
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    v1009 = 0i64;
    v761 = v128[56];
    v760 = v128[56];
    v661 = 251i64;
    while ( v1009 < v760 )
    {
      v661 = 2245i64;
      v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
      if ( v1009 < 0 || v1009 >= v128[56] )
      {
        raiseIndexError2(v1009, v128[56] - 1);
        goto LABEL_1691;
      }
      v762 = (_QWORD *)(v128[57] + 48 * v1009 + 8);
      v661 = 2246i64;
      if ( (__int64)*v762 < 0 || *v762 >= v114 )
      {
        raiseIndexError2(*v762, v114 - 1);
        goto LABEL_1691;
      }
      if ( v115[560 * *v762 + 8] == 54 )
      {
        v661 = 2247i64;
        v1013 = *v762;
        v661 = 2248i64;
        break;
      }
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      ++v1009;
      v661 = 254i64;
      v759 = v128[56];
      if ( v128[56] != v760 )
      {
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2436;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_54;
        failedAssertImpl__stdZassertions_u234(&v106);
        if ( *v1007 )
          goto LABEL_1691;
      }
    }
    v661 = 2250i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    v1012 = 0;
    v1011 = 0;
    v1010 = LOBYTE(v128[0]) == 118;
    if ( LOBYTE(v128[0]) == 118 )
      v1010 = LOBYTE(v128[4]) == 0;
    v1011 = v1010;
    if ( v1010 )
    {
      v758 = 0;
      v758 = initial_data__modelZmodel95types_u1497(v128);
      if ( *v1007 )
        goto LABEL_1691;
      v1011 = v758 == 1;
    }
    v1012 = v1011;
    if ( v1011 )
      v1012 = v1013 != -1;
    v757 = v1012;
    v661 = 2252i64;
    if ( v1012 )
    {
      v234 = 0i64;
      v235 = 0i64;
      v232 = 0i64;
      v233 = 0i64;
      v230 = 0i64;
      v231 = 0i64;
      v228 = 0i64;
      v229 = 0i64;
      v226 = 0i64;
      v227 = 0i64;
      v224 = 0i64;
      v225 = 0i64;
      v222 = 0i64;
      v223 = 0i64;
      v220 = 0i64;
      v221 = 0i64;
      v218 = 0i64;
      v219 = 0i64;
      v216 = 0i64;
      v217 = 0i64;
      v214 = 0i64;
      v215 = 0i64;
      v212 = 0i64;
      v213 = 0i64;
      v210 = 0i64;
      v211 = 0i64;
      v208 = 0i64;
      v209 = 0i64;
      v206 = 0i64;
      v207 = 0i64;
      v204 = 0i64;
      v205 = 0i64;
      v202 = 0i64;
      v203 = 0i64;
      v200 = 0i64;
      v201 = 0i64;
      v661 = 2255i64;
      v198 = 0i64;
      v199 = 0i64;
      dollar___systemZdollars_u14(&v232, v765);
      if ( *v1007 )
        goto LABEL_1691;
      rawNewString(&v106, v232 + 10);
      v198 = v106;
      v199 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2438;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2437;
      appendString_29(&v198, &v106);
      v106 = v232;
      v107 = (__int64)v233;
      appendString_29(&v198, &v106);
      v234 = v198;
      v235 = v199;
      v661 = 2257i64;
      nimZeroMem_66(&v196, 16i64);
      v196 = add_line__modelZsimulationZcode95gen_u2131;
      v197 = v1006;
      v194 = 0i64;
      v195 = 0i64;
      nimZeroMem_66(&v192, 16i64);
      v192 = input__modelZsimulationZcode95gen_u4258;
      v193 = v1006;
      if ( v1013 < 0 || v1013 >= v114 )
      {
        raiseIndexError2(v1013, v114 - 1);
        goto LABEL_1691;
      }
      if ( v193 )
      {
        v192(&v230, (__int64)&v115[560 * v1013 + 8], 1i64, 32i64, 0, (__int64)v193);
      }
      else
      {
        ((void (__fastcall *)(__int64 *, char *, __int64, __int64, _DWORD))v192)(
          &v106,
          &v115[560 * v1013 + 8],
          1i64,
          32i64,
          0);
        v230 = v106;
        v231 = (_QWORD *)v107;
      }
      if ( *v1007 )
        goto LABEL_1691;
      rawNewString(&v106, v234 + v230 + 20);
      v194 = v106;
      v195 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2439;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_897;
      appendString_29(&v194, &v106);
      v106 = v234;
      v107 = (__int64)v235;
      appendString_29(&v194, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2440;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_1028;
      appendString_29(&v194, &v106);
      v106 = v230;
      v107 = (__int64)v231;
      appendString_29(&v194, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2443;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2442;
      appendString_29(&v194, &v106);
      v228 = v194;
      v229 = v195;
      v106 = v194;
      v107 = (__int64)v195;
      if ( v197 )
        ((void (__fastcall *)(__int64 *, _QWORD *))v196)(&v106, v197);
      else
        ((void (__fastcall *)(__int64 *))v196)(&v106);
      if ( *v1007 )
        goto LABEL_1691;
      v661 = 2259i64;
      v190 = 0i64;
      v191 = 0i64;
      dollar___systemZdollars_u14(&v224, v765);
      if ( *v1007 )
        goto LABEL_1691;
      rawNewString(&v106, v224 + 6);
      v190 = v106;
      v191 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2446;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2445;
      appendString_29(&v190, &v106);
      v106 = v224;
      v107 = (__int64)v225;
      appendString_29(&v190, &v106);
      v226 = v190;
      v227 = v191;
      v661 = 2260i64;
      v188 = 0i64;
      v189 = 0i64;
      dollar___systemZdollars_u14(&v220, v765);
      if ( *v1007 )
        goto LABEL_1691;
      rawNewString(&v106, v220 + 6);
      v188 = v106;
      v189 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2448;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2447;
      appendString_29(&v188, &v106);
      v106 = v220;
      v107 = (__int64)v221;
      appendString_29(&v188, &v106);
      v222 = v188;
      v223 = v189;
      v661 = 2261i64;
      v186 = 0i64;
      v187 = 0i64;
      dollar___systemZdollars_u14(&v216, v765);
      if ( *v1007 )
        goto LABEL_1691;
      rawNewString(&v106, v216 + 7);
      v186 = v106;
      v187 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2450;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2449;
      appendString_29(&v186, &v106);
      v106 = v216;
      v107 = (__int64)v217;
      appendString_29(&v186, &v106);
      v218 = v186;
      v219 = v187;
      v661 = 2262i64;
      nimZeroMem_66(&v184, 16i64);
      v184 = add_line__modelZsimulationZcode95gen_u2131;
      v185 = v1006;
      v661 = 2263i64;
      v182 = 0i64;
      v183 = 0i64;
      dollar___modelZsave95mongerZcommon_u3396(&v214, v128[1]);
      if ( *v1007 )
        goto LABEL_1691;
      rawNewString(&v106, v226 + v214 + 30);
      v182 = v106;
      v183 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2451;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_897;
      appendString_29(&v182, &v106);
      v106 = v226;
      v107 = (__int64)v227;
      appendString_29(&v182, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2453;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2452;
      appendString_29(&v182, &v106);
      v106 = v214;
      v107 = (__int64)v215;
      appendString_29(&v182, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2454;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_325;
      appendString_29(&v182, &v106);
      v212 = v182;
      v213 = v183;
      v106 = v182;
      v107 = (__int64)v183;
      if ( v185 )
        ((void (__fastcall *)(__int64 *, _QWORD *))v184)(&v106, v185);
      else
        ((void (__fastcall *)(__int64 *))v184)(&v106);
      if ( *v1007 )
        goto LABEL_1691;
      v661 = 2265i64;
      nimZeroMem_66(&v180, 16i64);
      v180 = add_line__modelZsimulationZcode95gen_u2131;
      v181 = v1006;
      v178 = 0i64;
      v179 = 0i64;
      dollar___modelZsave95mongerZcommon_u3396(&v210, v128[1]);
      if ( *v1007 )
        goto LABEL_1691;
      rawNewString(&v106, v222 + v210 + 21);
      v178 = v106;
      v179 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2456;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_897;
      appendString_29(&v178, &v106);
      v106 = v222;
      v107 = (__int64)v223;
      appendString_29(&v178, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2458;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2457;
      appendString_29(&v178, &v106);
      v106 = v210;
      v107 = (__int64)v211;
      appendString_29(&v178, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2460;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2459;
      appendString_29(&v178, &v106);
      v208 = v178;
      v209 = v179;
      v106 = v178;
      v107 = (__int64)v179;
      if ( v181 )
        ((void (__fastcall *)(__int64 *, _QWORD *))v180)(&v106, v181);
      else
        ((void (__fastcall *)(__int64 *))v180)(&v106);
      if ( *v1007 )
        goto LABEL_1691;
      v661 = 2266i64;
      nimZeroMem_66(&v176, 16i64);
      v176 = add_line__modelZsimulationZcode95gen_u2131;
      v177 = v1006;
      v174 = 0i64;
      v175 = 0i64;
      rawNewString(&v106, v222 + v218 + v226 + 20);
      v174 = v106;
      v175 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2462;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_897;
      appendString_29(&v174, &v106);
      v106 = v218;
      v107 = (__int64)v219;
      appendString_29(&v174, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2463;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_550;
      appendString_29(&v174, &v106);
      v106 = v222;
      v107 = (__int64)v223;
      appendString_29(&v174, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2464;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_1179;
      appendString_29(&v174, &v106);
      v106 = v226;
      v107 = (__int64)v227;
      appendString_29(&v174, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2466;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2465;
      appendString_29(&v174, &v106);
      v206 = v174;
      v207 = v175;
      v106 = v174;
      v107 = (__int64)v175;
      if ( v177 )
        ((void (__fastcall *)(__int64 *, _QWORD *))v176)(&v106, v177);
      else
        ((void (__fastcall *)(__int64 *))v176)(&v106);
      if ( *v1007 )
        goto LABEL_1691;
      v661 = 2267i64;
      nimZeroMem_66(&v172, 16i64);
      v172 = add_line__modelZsimulationZcode95gen_u2131;
      v173 = v1006;
      v170 = 0i64;
      v171 = 0i64;
      rawNewString(&v106, v222 + v218 + 19);
      v170 = v106;
      v171 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2469;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2468;
      appendString_29(&v170, &v106);
      v106 = v222;
      v107 = (__int64)v223;
      appendString_29(&v170, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2471;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2470;
      appendString_29(&v170, &v106);
      v106 = v218;
      v107 = (__int64)v219;
      appendString_29(&v170, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2472;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_995;
      appendString_29(&v170, &v106);
      v204 = v170;
      v205 = v171;
      v106 = v170;
      v107 = (__int64)v171;
      if ( v173 )
        ((void (__fastcall *)(__int64 *, _QWORD *))v172)(&v106, v173);
      else
        ((void (__fastcall *)(__int64 *))v172)(&v106);
      if ( *v1007 )
        goto LABEL_1691;
      v661 = 2268i64;
      nimZeroMem_66(&v168, 16i64);
      v168 = add_line__modelZsimulationZcode95gen_u2131;
      v169 = v1006;
      v166 = 0i64;
      v167 = 0i64;
      rawNewString(&v106, v222 + v234 + 30);
      v166 = v106;
      v167 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2475;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2474;
      appendString_29(&v166, &v106);
      v106 = v222;
      v107 = (__int64)v223;
      appendString_29(&v166, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2477;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2476;
      appendString_29(&v166, &v106);
      v106 = v234;
      v107 = (__int64)v235;
      appendString_29(&v166, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2478;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_995;
      appendString_29(&v166, &v106);
      v202 = v166;
      v203 = v167;
      v106 = v166;
      v107 = (__int64)v167;
      if ( v169 )
        ((void (__fastcall *)(__int64 *, _QWORD *))v168)(&v106, v169);
      else
        ((void (__fastcall *)(__int64 *))v168)(&v106);
      if ( *v1007 )
        goto LABEL_1691;
      v661 = 2269i64;
      nimZeroMem_66(&v164, 16i64);
      v164 = add_line__modelZsimulationZcode95gen_u2131;
      v165 = v1006;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2481;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2480;
      if ( v1006 )
        ((void (__fastcall *)(__int64 *, _QWORD *))v164)(&v106, v165);
      else
        ((void (__fastcall *)(__int64 *))v164)(&v106);
      if ( *v1007 )
        goto LABEL_1691;
      v661 = 2270i64;
      nimZeroMem_66(&v162, 16i64);
      v162 = add_line__modelZsimulationZcode95gen_u2131;
      v163 = v1006;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2484;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2483;
      if ( v1006 )
        ((void (__fastcall *)(__int64 *, _QWORD *))v162)(&v106, v163);
      else
        ((void (__fastcall *)(__int64 *))v162)(&v106);
      if ( *v1007 )
        goto LABEL_1691;
      v661 = 2271i64;
      nimZeroMem_66(&v160, 16i64);
      v160 = add_line__modelZsimulationZcode95gen_u2131;
      v161 = v1006;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2486;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_666;
      if ( v1006 )
        ((void (__fastcall *)(__int64 *, _QWORD *))v160)(&v106, v161);
      else
        ((void (__fastcall *)(__int64 *))v160)(&v106);
      if ( *v1007 )
        goto LABEL_1691;
      v661 = 2272i64;
      nimZeroMem_66(&v158, 16i64);
      v158 = add_line__modelZsimulationZcode95gen_u2131;
      v159 = v1006;
      v156 = 0i64;
      v157 = 0i64;
      rawNewString(&v106, v222 + 9);
      v156 = v106;
      v157 = (_QWORD *)v107;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2488;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_486;
      appendString_29(&v156, &v106);
      v106 = v222;
      v107 = (__int64)v223;
      appendString_29(&v156, &v106);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2490;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2489;
      appendString_29(&v156, &v106);
      v200 = v156;
      v201 = v157;
      v106 = v156;
      v107 = (__int64)v157;
      if ( v159 )
        ((void (__fastcall *)(__int64 *, _QWORD *))v158)(&v106, v159);
      else
        ((void (__fastcall *)(__int64 *))v158)(&v106);
      if ( *v1007 )
        goto LABEL_1691;
      v661 = 2273i64;
      nimZeroMem_66(&v154, 16i64);
      v154 = add_line__modelZsimulationZcode95gen_u2131;
      v155 = v1006;
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2492;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_605;
      if ( v1006 )
        ((void (__fastcall *)(__int64 *, _QWORD *))v154)(&v106, v155);
      else
        ((void (__fastcall *)(__int64 *))v154)(&v106);
      if ( *v1007 )
        goto LABEL_1691;
      v661 = 394i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v201 && (*v201 & 0x4000000000000000i64) == 0 )
        deallocShared(v201);
      if ( v203 && (*v203 & 0x4000000000000000i64) == 0 )
        deallocShared(v203);
      if ( v205 && (*v205 & 0x4000000000000000i64) == 0 )
        deallocShared(v205);
      if ( v207 && (*v207 & 0x4000000000000000i64) == 0 )
        deallocShared(v207);
      if ( v209 && (*v209 & 0x4000000000000000i64) == 0 )
        deallocShared(v209);
      if ( v211 && (*v211 & 0x4000000000000000i64) == 0 )
        deallocShared(v211);
      if ( v213 && (*v213 & 0x4000000000000000i64) == 0 )
        deallocShared(v213);
      if ( v215 && (*v215 & 0x4000000000000000i64) == 0 )
        deallocShared(v215);
      if ( v217 && (*v217 & 0x4000000000000000i64) == 0 )
        deallocShared(v217);
      if ( v219 && (*v219 & 0x4000000000000000i64) == 0 )
        deallocShared(v219);
      if ( v221 && (*v221 & 0x4000000000000000i64) == 0 )
        deallocShared(v221);
      if ( v223 && (*v223 & 0x4000000000000000i64) == 0 )
        deallocShared(v223);
      if ( v225 && (*v225 & 0x4000000000000000i64) == 0 )
        deallocShared(v225);
      if ( v227 && (*v227 & 0x4000000000000000i64) == 0 )
        deallocShared(v227);
      if ( v229 && (*v229 & 0x4000000000000000i64) == 0 )
        deallocShared(v229);
      if ( v231 && (*v231 & 0x4000000000000000i64) == 0 )
        deallocShared(v231);
      if ( v233 && (*v233 & 0x4000000000000000i64) == 0 )
        deallocShared(v233);
      if ( v235 && (*v235 & 0x4000000000000000i64) == 0 )
        deallocShared(v235);
    }
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v1014;
    v661 = 187i64;
    v756 = v114;
    if ( v114 != v763 )
    {
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2494;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
      failedAssertImpl__stdZassertions_u234(&v106);
      if ( *v1007 )
        goto LABEL_1691;
    }
  }
  v661 = 2275i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  prepareAdd(v1006 + 1, 5i64);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2496;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2495;
  appendString_29(v1006 + 1, &v106);
  v661 = 2281i64;
  if ( *((_BYTE *)v1006 + 168) != 3 )
  {
    v661 = 2282i64;
    if ( (__int64)v1006[69] > 0 )
    {
      v152 = 0i64;
      v153 = 0i64;
      v755 = 0i64;
      v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      v1008 = 0i64;
      v754 = v556;
      v753 = v556;
      v661 = 184i64;
      while ( v1008 < v753 )
      {
        v150 = 0i64;
        v151 = 0i64;
        v148 = 0i64;
        v149 = 0i64;
        v146 = 0i64;
        v147 = 0i64;
        v144 = 0i64;
        v145 = 0i64;
        v142 = 0i64;
        v143 = 0i64;
        v140 = 0i64;
        v141 = 0i64;
        v138 = 0i64;
        v139 = 0i64;
        v136 = 0i64;
        v137 = 0i64;
        v755 = v1008;
        v661 = 1699i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v1008 < 0 || v1008 >= v556 )
        {
          raiseIndexError2(v1008, v556 - 1);
          goto LABEL_1691;
        }
        v91 = v557 + 16 * v1008;
        v92 = *(_QWORD *)(v91 + 16);
        v106 = *(_QWORD *)(v91 + 8);
        v107 = v92;
        eqcopy___system_u2661(&v152, &v106);
        v661 = 2284i64;
        v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
        v134 = 0i64;
        v135 = 0i64;
        dollar___systemZdollars_u14(&v150, v755);
        if ( *v1007 )
          goto LABEL_1691;
        v752[3] = v556;
        dollar___systemZdollars_u14(&v148, v556);
        if ( *v1007 )
          goto LABEL_1691;
        v133 = 9 * v755;
        if ( !is_mul_ok(9ui64, v755) )
          goto LABEL_1396;
        dollar___systemZdollars_u14(&v146, v133);
        if ( *v1007 )
          goto LABEL_1691;
        rawNewString(&v106, v148 + v150 + v146 + 48);
        v134 = v106;
        v135 = (_QWORD *)v107;
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2498;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2497;
        appendString_29(&v134, &v106);
        v106 = v150;
        v107 = (__int64)v151;
        appendString_29(&v134, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2500;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2499;
        appendString_29(&v134, &v106);
        v106 = v148;
        v107 = (__int64)v149;
        appendString_29(&v134, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2502;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2501;
        appendString_29(&v134, &v106);
        v106 = v146;
        v107 = (__int64)v147;
        appendString_29(&v134, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2504;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_14;
        appendString_29(&v134, &v106);
        v144 = v134;
        v145 = v135;
        prepareAdd(v1006 + 1, v134);
        v106 = v144;
        v107 = (__int64)v145;
        appendString_29(v1006 + 1, &v106);
        v661 = 2285i64;
        v131 = 0i64;
        v132 = 0i64;
        dollar___systemZdollars_u14(&v142, v755);
        if ( *v1007 )
          goto LABEL_1691;
        rawNewString(&v106, v142 + v152 + 78);
        v131 = v106;
        v132 = (_QWORD *)v107;
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2506;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2505;
        appendString_29(&v131, &v106);
        v106 = v142;
        v107 = (__int64)v143;
        appendString_29(&v131, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2508;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2507;
        appendString_29(&v131, &v106);
        v106 = v152;
        v107 = (__int64)v153;
        appendString_29(&v131, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2510;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2509;
        appendString_29(&v131, &v106);
        v140 = v131;
        v141 = v132;
        prepareAdd(v1006 + 1, v131);
        v106 = v140;
        v107 = (__int64)v141;
        appendString_29(v1006 + 1, &v106);
        v661 = 2286i64;
        v129 = 0i64;
        v130 = 0i64;
        dollar___systemZdollars_u14(&v138, v755);
        if ( *v1007 )
          goto LABEL_1691;
        rawNewString(&v106, v138 + v152 + 78);
        v129 = v106;
        v130 = (_QWORD *)v107;
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2511;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2505;
        appendString_29(&v129, &v106);
        v106 = v138;
        v107 = (__int64)v139;
        appendString_29(&v129, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2513;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2512;
        appendString_29(&v129, &v106);
        v106 = v152;
        v107 = (__int64)v153;
        appendString_29(&v129, &v106);
        v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2514;
        v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_456;
        appendString_29(&v129, &v106);
        v136 = v129;
        v137 = v130;
        prepareAdd(v1006 + 1, v129);
        v106 = v136;
        v107 = (__int64)v137;
        appendString_29(v1006 + 1, &v106);
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v1008;
        v661 = 187i64;
        v752[2] = v556;
        if ( v556 != v753 )
        {
          v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2515;
          v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_52;
          failedAssertImpl__stdZassertions_u234(&v106);
          if ( *v1007 )
            goto LABEL_1691;
        }
        v661 = 394i64;
        v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v137 && (*v137 & 0x4000000000000000i64) == 0 )
          deallocShared(v137);
        if ( v139 && (*v139 & 0x4000000000000000i64) == 0 )
          deallocShared(v139);
        if ( v141 && (*v141 & 0x4000000000000000i64) == 0 )
          deallocShared(v141);
        if ( v143 && (*v143 & 0x4000000000000000i64) == 0 )
          deallocShared(v143);
        if ( v145 && (*v145 & 0x4000000000000000i64) == 0 )
          deallocShared(v145);
        if ( v147 && (*v147 & 0x4000000000000000i64) == 0 )
          deallocShared(v147);
        if ( v149 && (*v149 & 0x4000000000000000i64) == 0 )
          deallocShared(v149);
        if ( v151 && (*v151 & 0x4000000000000000i64) == 0 )
          deallocShared(v151);
      }
      if ( v153 && (*v153 & 0x4000000000000000i64) == 0 )
        deallocShared(v153);
    }
    v661 = 2288i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    prepareAdd(v1006 + 1, 134i64);
    v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2517;
    v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2516;
    appendString_29(v1006 + 1, &v106);
    v661 = 2298i64;
    if ( v1006[69] )
    {
      v661 = 2299i64;
      prepareAdd(v1006 + 1, 138i64);
      v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2519;
      v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2518;
      appendString_29(v1006 + 1, &v106);
    }
  }
  v539 = 0i64;
  v540 = 0i64;
  v661 = 2374i64;
  v106 = v709;
  v107 = (__int64)v710;
  v98 = TM__THWBxVSaWN2Zh7OMooFH0w_2522;
  v99 = (char *)&TM__THWBxVSaWN2Zh7OMooFH0w_14;
  v96 = TM__THWBxVSaWN2Zh7OMooFH0w_2523;
  v97 = (char *)&TM__THWBxVSaWN2Zh7OMooFH0w_2495;
  nsuReplaceStr(&v554, &v106, &v98, &v96);
  if ( *v1007 )
  {
LABEL_1691:
    v661 = 394i64;
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v553 && (*v553 & 0x4000000000000000i64) == 0 )
      deallocShared(v553);
    if ( v555 && (*v555 & 0x4000000000000000i64) == 0 )
      deallocShared(v555);
    v661 = 2128i64;
    v106 = v556;
    v107 = v557;
    eqdestroy___system_u3734(&v106);
    v106 = v558;
    v107 = v559;
    eqdestroy___system_u3734(&v106);
    v661 = 2128i64;
    v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
    eqdestroy___modelZsimulationZcode95gen_u8959(&v560);
    v661 = 2128i64;
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v106 = v563;
    v107 = (__int64)v564;
    eqdestroy___system_u3734(&v106);
    v661 = 394i64;
    if ( v566 && (*v566 & 0x4000000000000000i64) == 0 )
      deallocShared(v566);
    if ( v568 && (*v568 & 0x4000000000000000i64) == 0 )
      deallocShared(v568);
    if ( v570 && (*v570 & 0x4000000000000000i64) == 0 )
      deallocShared(v570);
    if ( v572 && (*v572 & 0x4000000000000000i64) == 0 )
      deallocShared(v572);
    v661 = 982i64;
    v662 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    v106 = v573;
    v107 = v574;
    eqdestroy___modelZsave95mongerZcommon_u5612(&v106);
    v661 = 394i64;
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v576 && (*v576 & 0x4000000000000000i64) == 0 )
      deallocShared(v576);
    if ( v578 && (*v578 & 0x4000000000000000i64) == 0 )
      deallocShared(v578);
    if ( v580 && (*v580 & 0x4000000000000000i64) == 0 )
      deallocShared(v580);
    if ( v582 && (*v582 & 0x4000000000000000i64) == 0 )
      deallocShared(v582);
    if ( v584 && (*v584 & 0x4000000000000000i64) == 0 )
      deallocShared(v584);
    if ( v586 && (*v586 & 0x4000000000000000i64) == 0 )
      deallocShared(v586);
    v661 = 2128i64;
    v106 = v587;
    v107 = v588;
    eqdestroy___system_u3734(&v106);
    v106 = v589;
    v107 = v590;
    eqdestroy___system_u3734(&v106);
    v661 = 1411i64;
    v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
    eqdestroy___modelZboardZschematics_u2219(&v118);
    goto LABEL_1728;
  }
  rawNewString(&v106, v554 + 2992);
  v539 = v106;
  v540 = (_QWORD *)v107;
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2521;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2520;
  appendString_29(&v539, &v106);
  v106 = v554;
  v107 = (__int64)v555;
  appendString_29(&v539, &v106);
  v106 = TM__THWBxVSaWN2Zh7OMooFH0w_2525;
  v107 = (__int64)&TM__THWBxVSaWN2Zh7OMooFH0w_2524;
  appendString_29(&v539, &v106);
  v552 = v539;
  v553 = v540;
  prepareAdd(v1006 + 1, v539);
  v106 = v552;
  v107 = (__int64)v553;
  appendString_29(v1006 + 1, &v106);
  v661 = 1699i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  v93 = v1006[2];
  v106 = v1006[1];
  v107 = v93;
  eqcopy___system_u2661(&v711, &v106);
  v661 = 394i64;
  if ( v553 && (*v553 & 0x4000000000000000i64) == 0 )
    deallocShared(v553);
  if ( v555 && (*v555 & 0x4000000000000000i64) == 0 )
    deallocShared(v555);
  v661 = 2128i64;
  v106 = v556;
  v107 = v557;
  eqdestroy___system_u3734(&v106);
  v106 = v558;
  v107 = v559;
  eqdestroy___system_u3734(&v106);
  v661 = 2128i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  eqdestroy___modelZsimulationZcode95gen_u8959(&v560);
  v661 = 2128i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  v106 = v563;
  v107 = (__int64)v564;
  eqdestroy___system_u3734(&v106);
  v661 = 394i64;
  if ( v566 && (*v566 & 0x4000000000000000i64) == 0 )
    deallocShared(v566);
  if ( v568 && (*v568 & 0x4000000000000000i64) == 0 )
    deallocShared(v568);
  if ( v570 && (*v570 & 0x4000000000000000i64) == 0 )
    deallocShared(v570);
  if ( v572 && (*v572 & 0x4000000000000000i64) == 0 )
    deallocShared(v572);
  v661 = 982i64;
  v662 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
  v106 = v573;
  v107 = v574;
  eqdestroy___modelZsave95mongerZcommon_u5612(&v106);
  v661 = 394i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v576 && (*v576 & 0x4000000000000000i64) == 0 )
    deallocShared(v576);
  if ( v578 && (*v578 & 0x4000000000000000i64) == 0 )
    deallocShared(v578);
  if ( v580 && (*v580 & 0x4000000000000000i64) == 0 )
    deallocShared(v580);
  if ( v582 && (*v582 & 0x4000000000000000i64) == 0 )
    deallocShared(v582);
  if ( v584 && (*v584 & 0x4000000000000000i64) == 0 )
    deallocShared(v584);
  if ( v586 && (*v586 & 0x4000000000000000i64) == 0 )
    deallocShared(v586);
  v661 = 2128i64;
  v106 = v587;
  v107 = v588;
  eqdestroy___system_u3734(&v106);
  v106 = v589;
  v107 = v590;
  eqdestroy___system_u3734(&v106);
  v661 = 1411i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
  eqdestroy___modelZboardZschematics_u2219(&v118);
  v661 = 394i64;
  v662 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v674 && (*v674 & 0x4000000000000000i64) == 0 )
    deallocShared(v674);
  if ( v676 && (*v676 & 0x4000000000000000i64) == 0 )
    deallocShared(v676);
  if ( v678 && (*v678 & 0x4000000000000000i64) == 0 )
    deallocShared(v678);
  if ( v680 && (*v680 & 0x4000000000000000i64) == 0 )
    deallocShared(v680);
  if ( v682 && (*v682 & 0x4000000000000000i64) == 0 )
    deallocShared(v682);
  if ( v684 && (*v684 & 0x4000000000000000i64) == 0 )
    deallocShared(v684);
  if ( v686 && (*v686 & 0x4000000000000000i64) == 0 )
    deallocShared(v686);
  if ( v688 && (*v688 & 0x4000000000000000i64) == 0 )
    deallocShared(v688);
  if ( v690 && (*v690 & 0x4000000000000000i64) == 0 )
    deallocShared(v690);
  if ( v692 && (*v692 & 0x4000000000000000i64) == 0 )
    deallocShared(v692);
  if ( v694 && (*v694 & 0x4000000000000000i64) == 0 )
    deallocShared(v694);
  if ( v696 && (*v696 & 0x4000000000000000i64) == 0 )
    deallocShared(v696);
  if ( v698 && (*v698 & 0x4000000000000000i64) == 0 )
    deallocShared(v698);
  if ( v700 && (*v700 & 0x4000000000000000i64) == 0 )
    deallocShared(v700);
  v661 = 2128i64;
  v106 = v701;
  v107 = v702;
  eqdestroy___system_u3734(&v106);
  v106 = v703;
  v107 = v704;
  eqdestroy___system_u3734(&v106);
  v106 = v705;
  v107 = v706;
  eqdestroy___system_u3734(&v106);
  v661 = 394i64;
  if ( v708 && (*v708 & 0x4000000000000000i64) == 0 )
    deallocShared(v708);
  if ( v710 && (*v710 & 0x4000000000000000i64) == 0 )
    deallocShared(v710);
LABEL_1776:
  v661 = 63i64;
  v662 = "D:\\TuringComplete_Phu\\model\\simulation\\code_gen.nim";
  eqdestroy___modelZsimulationZcode95gen_u9641(v1006);
  popFrame_88();
  v94 = v712;
  *a1 = v711;
  a1[1] = v94;
  return a1;
}


/* data/non-function xref from 0x0000000140beff98 */

/* data/non-function xref from 0x0000000140beffa4 */

/* XREFS TO get_clamped_word_size @ 0x0000000140236b33 */

/* call 0x0000000140245457, caller board_add_component__modelZboardZboard_u21118 @ 0x0000000140243dca */

__int64 __fastcall board_add_component__modelZboardZboard_u21118(
        __int64 a1,
        unsigned __int8 a2,
        __int64 *a3,
        unsigned int a4,
        char a5,
        __int64 a6,
        __int64 *a7,
        __int64 *a8,
        __int64 a9,
        __int64 a10,
        char a11,
        __int64 *a12,
        __int64 *a13,
        __int64 a14,
        __int64 *a15,
        __int64 *a16,
        __int16 a17,
        __int64 *a18,
        char a19)
{
  __int64 v21; // rdx
  __int64 v22; // rdx
  __int64 v23; // rdx
  __int64 v24; // rdx
  __int64 v25; // rdx
  __int64 v26; // rdx
  __int64 v27; // rdx
  __int64 v28; // rdx
  __int64 v29; // rdx
  char *v30; // rax
  __int64 v31; // rbx
  __int64 v32; // rbx
  __int64 v33; // rbx
  __int64 v34; // rbx
  __int64 v35; // rbx
  char *v36; // rax
  __int64 v37; // rbx
  __int64 v38; // rbx
  __int64 v39; // rbx
  __int64 v40; // rbx
  __int64 v41; // rbx
  __int64 v42; // rdx
  __int64 v43; // rdx
  __int64 v44; // rdx
  __int64 v45; // rbx
  __int64 v46; // rbx
  __int64 v47; // rbx
  __int64 v48; // rdx
  __int64 v50; // [rsp+20h] [rbp-60h] BYREF
  __int64 v51; // [rsp+28h] [rbp-58h]
  __int64 v52; // [rsp+30h] [rbp-50h]
  __int64 v53; // [rsp+40h] [rbp-40h] BYREF
  __int64 v54; // [rsp+48h] [rbp-38h]
  __int64 v55; // [rsp+50h] [rbp-30h]
  __int64 v56; // [rsp+60h] [rbp-20h] BYREF
  char *v57; // [rsp+68h] [rbp-18h]
  __int64 v58; // [rsp+70h] [rbp-10h]
  char *v59; // [rsp+78h] [rbp-8h]
  __int64 v60; // [rsp+80h] [rbp+0h]
  char *v61; // [rsp+88h] [rbp+8h]
  __int64 v62; // [rsp+90h] [rbp+10h]
  char *v63; // [rsp+98h] [rbp+18h]
  __int64 v64; // [rsp+A0h] [rbp+20h]
  char *v65; // [rsp+A8h] [rbp+28h]
  char v66; // [rsp+B0h] [rbp+30h]
  __int16 v67; // [rsp+B4h] [rbp+34h]
  char v68; // [rsp+B8h] [rbp+38h]
  char v69; // [rsp+BCh] [rbp+3Ch]
  __int64 v70[182]; // [rsp+C0h] [rbp+40h] BYREF
  __int64 v71; // [rsp+670h] [rbp+5F0h]
  __int64 v72; // [rsp+678h] [rbp+5F8h]
  __int64 v73; // [rsp+680h] [rbp+600h]
  __int64 v74; // [rsp+688h] [rbp+608h]
  __int64 v75; // [rsp+690h] [rbp+610h] BYREF
  char *v76; // [rsp+698h] [rbp+618h]
  char v77[8]; // [rsp+6A0h] [rbp+620h] BYREF
  const char *v78; // [rsp+6A8h] [rbp+628h]
  __int64 v79; // [rsp+6B0h] [rbp+630h]
  const char *v80; // [rsp+6B8h] [rbp+638h]
  __int16 v81; // [rsp+6C0h] [rbp+640h]
  __int64 v82; // [rsp+6D8h] [rbp+658h]
  __int64 v83; // [rsp+6E0h] [rbp+660h]
  _QWORD *v84; // [rsp+6E8h] [rbp+668h]
  __int64 v85; // [rsp+6F0h] [rbp+670h]
  __int64 v86; // [rsp+6F8h] [rbp+678h]
  __int64 v87; // [rsp+700h] [rbp+680h]
  __int64 v88; // [rsp+708h] [rbp+688h]
  __int64 v89[4]; // [rsp+710h] [rbp+690h] BYREF
  __int64 v90[4]; // [rsp+730h] [rbp+6B0h] BYREF
  __int64 v91; // [rsp+750h] [rbp+6D0h] BYREF
  char *v92; // [rsp+758h] [rbp+6D8h]
  __int64 v93; // [rsp+760h] [rbp+6E0h] BYREF
  char *v94; // [rsp+768h] [rbp+6E8h]
  __int64 v95; // [rsp+770h] [rbp+6F0h] BYREF
  char *v96; // [rsp+778h] [rbp+6F8h]
  __int64 v97; // [rsp+780h] [rbp+700h] BYREF
  __int64 v98; // [rsp+788h] [rbp+708h]
  __int64 v99[3]; // [rsp+790h] [rbp+710h] BYREF
  __int64 v100; // [rsp+7A8h] [rbp+728h] BYREF
  __int64 v101[4]; // [rsp+7B0h] [rbp+730h] BYREF
  __int64 v102; // [rsp+7D0h] [rbp+750h] BYREF
  __int64 v103; // [rsp+7D8h] [rbp+758h]
  int v104; // [rsp+7ECh] [rbp+76Ch] BYREF
  __int64 v105[70]; // [rsp+7F0h] [rbp+770h] BYREF
  __int64 v106; // [rsp+A20h] [rbp+9A0h] BYREF
  _QWORD *v107; // [rsp+A28h] [rbp+9A8h]
  __int64 v108; // [rsp+A30h] [rbp+9B0h] BYREF
  char *v109; // [rsp+A38h] [rbp+9B8h]
  char v110[96]; // [rsp+A40h] [rbp+9C0h] BYREF
  __int64 v111; // [rsp+AA0h] [rbp+A20h]
  __int64 v112; // [rsp+AB0h] [rbp+A30h]
  __int64 v113; // [rsp+AC0h] [rbp+A40h]
  __int64 v114; // [rsp+FF0h] [rbp+F70h] BYREF
  char *v115; // [rsp+FF8h] [rbp+F78h]
  __int64 v116; // [rsp+1000h] [rbp+F80h]
  __int64 v117; // [rsp+1008h] [rbp+F88h]
  __int64 v118; // [rsp+1010h] [rbp+F90h]
  __int64 v119; // [rsp+1018h] [rbp+F98h]
  char v121; // [rsp+102Fh] [rbp+FAFh]
  __int64 v122; // [rsp+1030h] [rbp+FB0h]
  __int64 v123; // [rsp+1038h] [rbp+FB8h]
  __int64 v124; // [rsp+1040h] [rbp+FC0h]
  __int64 v125; // [rsp+1048h] [rbp+FC8h]
  __int64 v126; // [rsp+1050h] [rbp+FD0h]
  __int64 v127; // [rsp+1058h] [rbp+FD8h]
  __int64 v128; // [rsp+1060h] [rbp+FE0h]
  __int64 v129; // [rsp+1068h] [rbp+FE8h]
  __int64 v130; // [rsp+1070h] [rbp+FF0h]
  __int64 v131; // [rsp+1078h] [rbp+FF8h]
  __int64 v132; // [rsp+1080h] [rbp+1000h]
  __int64 v133; // [rsp+1088h] [rbp+1008h]
  __int64 v134; // [rsp+1090h] [rbp+1010h]
  char v135; // [rsp+109Fh] [rbp+101Fh]
  __int64 v136; // [rsp+10A0h] [rbp+1020h]
  __int64 v137; // [rsp+10A8h] [rbp+1028h]
  __int64 v138; // [rsp+10B0h] [rbp+1030h]
  __int64 v139; // [rsp+10B8h] [rbp+1038h]
  char v140; // [rsp+10C7h] [rbp+1047h]
  __int64 v141; // [rsp+10C8h] [rbp+1048h]
  __int64 v142; // [rsp+10D0h] [rbp+1050h]
  __int64 *v143; // [rsp+10D8h] [rbp+1058h]
  __int64 v144; // [rsp+10E0h] [rbp+1060h]
  _QWORD *v145; // [rsp+10E8h] [rbp+1068h]
  __int64 v146; // [rsp+10F0h] [rbp+1070h]
  __int64 v147; // [rsp+10F8h] [rbp+1078h]
  __int64 *v148; // [rsp+1100h] [rbp+1080h]
  __int64 v149; // [rsp+1108h] [rbp+1088h]
  char v150; // [rsp+1110h] [rbp+1090h]
  char valid; // [rsp+1111h] [rbp+1091h]
  char v152; // [rsp+1112h] [rbp+1092h]
  char v153; // [rsp+1113h] [rbp+1093h]
  __int16 v154; // [rsp+1114h] [rbp+1094h]
  char v155; // [rsp+1117h] [rbp+1097h]
  __int64 v156; // [rsp+1118h] [rbp+1098h]
  unsigned __int8 v157; // [rsp+1127h] [rbp+10A7h]
  _BYTE *v158; // [rsp+1128h] [rbp+10A8h]
  bool v159; // [rsp+1137h] [rbp+10B7h]
  __int64 v160; // [rsp+1138h] [rbp+10B8h]
  __int64 v161; // [rsp+1140h] [rbp+10C0h]
  __int64 v162; // [rsp+1148h] [rbp+10C8h]
  bool v163; // [rsp+1157h] [rbp+10D7h]
  __int64 v164; // [rsp+1158h] [rbp+10D8h]
  char v165; // [rsp+1165h] [rbp+10E5h]
  char v166; // [rsp+1166h] [rbp+10E6h]
  char v167; // [rsp+1167h] [rbp+10E7h]
  __int64 v168; // [rsp+1168h] [rbp+10E8h]
  unsigned __int16 v169; // [rsp+1176h] [rbp+10F6h]
  __int64 v170; // [rsp+1178h] [rbp+10F8h]
  unsigned __int8 v172; // [rsp+11C8h] [rbp+1148h]

  v21 = a7[1];
  v64 = *a7;
  v65 = (char *)v21;
  v22 = a8[1];
  v62 = *a8;
  v63 = (char *)v22;
  v23 = a16[1];
  v60 = *a16;
  v61 = (char *)v23;
  v24 = a18[1];
  v58 = *a18;
  v59 = (char *)v24;
  v172 = a2;
  v69 = a5;
  v68 = a11;
  v67 = a17;
  v66 = a19;
  v78 = "board_add_component";
  v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  v79 = 0i64;
  v81 = 0;
  nimFrame_73(v77);
  v158 = (_BYTE *)nimErrorFlag_71();
  v170 = 0i64;
  v114 = 0i64;
  v115 = 0i64;
  nimZeroMem_53(v110, 1448i64);
  v108 = 0i64;
  v109 = 0i64;
  v106 = 0i64;
  v107 = 0i64;
  nimZeroMem_53(v105, 560i64);
  v157 = 0;
  v156 = 0i64;
  nimZeroMem_53(&v104, 4i64);
  v155 = 0;
  v102 = 0i64;
  v103 = 0i64;
  nimZeroMem_53(v101, 24i64);
  nimZeroMem_53(&v100, 8i64);
  nimZeroMem_53(v99, 24i64);
  v154 = 0;
  v97 = 0i64;
  v98 = 0i64;
  v95 = 0i64;
  v96 = 0i64;
  v93 = 0i64;
  v94 = 0i64;
  v91 = 0i64;
  v92 = 0i64;
  nimZeroMem_53(v90, 24i64);
  v153 = 0;
  nimZeroMem_53(v89, 24i64);
  v152 = 0;
  v79 = 1072i64;
  v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  v167 = 0;
  v166 = v172 == 78;
  if ( v172 == 78 )
  {
    v166 = notin_custom_prototypes__modelZboardZcustom95prototype95list_u189(a9);
    if ( *v158 )
      goto LABEL_135;
  }
  v167 = v166;
  if ( !v166 )
  {
    v79 = 1073i64;
    v167 = ((TM__CKxtw4nX41tlcDT9cZT8kGA_2[v172 >> 3] >> (v172 & 7)) & 1) != 0;
  }
  if ( v167 == 1 )
  {
    v170 = -1i64;
    v79 = 34i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    v56 = v91;
    v57 = v92;
    eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
    v56 = v93;
    v57 = v94;
    eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
    v56 = v95;
    v57 = v96;
    eqdestroy___modelZsave95mongerZversionsZv0_u448(&v56);
    eqdestroy___modelZsave95mongerZversionsZv0_u145(v105);
    v79 = 394i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v107 && (*v107 & 0x4000000000000000i64) == 0 )
      deallocShared(v107);
    v79 = 34i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    v56 = v108;
    v57 = v109;
    eqdestroy___modelZsave95mongerZversionsZv0_u296(&v56);
    v79 = 170i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    eqdestroy___modelZboardZprototype95list_u3239(v110);
    v79 = 119i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
    v56 = v114;
    v57 = v115;
    eqdestroy___modelZsave95mongerZserialize_u455(&v56);
    goto LABEL_139;
  }
  v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  v88 = a6;
  v79 = 1078i64;
  valid = 0;
  valid = is_valid__modelZsave95mongerZcommon_u3408(a6);
  if ( *v158 )
    goto LABEL_135;
  if ( !valid )
  {
    v79 = 1079i64;
    v88 = new_permanent_id__modelZsave95mongerZcommon_u3402();
    if ( *v158 )
      goto LABEL_135;
  }
  v79 = 119i64;
  v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
  v56 = v60;
  v57 = v61;
  eqcopy___modelZsave95mongerZserialize_u458(&v114, &v56);
  v79 = 1082i64;
  v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  v150 = 0;
  v25 = *((_QWORD *)refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347 + 1);
  v53 = *(_QWORD *)refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347;
  v54 = v25;
  v55 = *((_QWORD *)refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347 + 2);
  v150 = contains__modelZboardZboard_u21313(&v53, v172);
  if ( *v158 )
    goto LABEL_135;
  if ( v150 == 1 )
  {
    v79 = 119i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
    v56 = v60;
    v57 = v61;
    eqcopy___modelZsave95mongerZserialize_u458(&v114, &v56);
    v79 = 1084i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    while ( 1 )
    {
      v149 = v114;
      v148 = 0i64;
      v148 = (__int64 *)X5BX5D___modelZsave95mongerZversionsZv7_u2794(
                          refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347,
                          v172);
      if ( *v158 )
        goto LABEL_135;
      v147 = *v148;
      if ( v149 >= v147 )
      {
        v79 = 1086i64;
        v143 = 0i64;
        v143 = (__int64 *)X5BX5D___modelZsave95mongerZversionsZv7_u2794(
                            refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347,
                            v172);
        if ( *v158 )
          goto LABEL_135;
        v142 = *v143;
        if ( v142 < 0 )
        {
          raiseRangeErrorI(v142, 0i64, 0x7FFFFFFFFFFFFFFFi64);
          goto LABEL_135;
        }
        setLen__modelZsave95mongerZserialize_u475(&v114, v142);
        break;
      }
      v146 = 0i64;
      v79 = 1085i64;
      v145 = 0i64;
      v145 = (_QWORD *)X5BX5D___modelZsave95mongerZversionsZv7_u2794(
                         refptr_COMPONENT_DEFAULT_SETTING__modelZsave95mongerZcommon_u3347,
                         v172);
      if ( *v158 )
        goto LABEL_135;
      v144 = v114;
      if ( v114 < 0 || v144 >= *v145 )
      {
        raiseIndexError2(v144, *v145 - 1i64);
        goto LABEL_135;
      }
      v146 = *(_QWORD *)(v145[1] + 8 * v144 + 8);
      add__modelZsave95mongerZserialize_u151(&v114, v146);
    }
  }
  v87 = a10;
  v79 = 1090i64;
  v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  v141 = 0i64;
  v141 = X5BX5D___modelZboardZprototype95list_u4239(refptr_PROTOTYPES__modelZboardZprototype95list_u3752, v172);
  if ( *v158 )
  {
LABEL_135:
    v79 = 34i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    v56 = v91;
    v57 = v92;
    eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
    v56 = v93;
    v57 = v94;
    eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
    v56 = v95;
    v57 = v96;
    eqdestroy___modelZsave95mongerZversionsZv0_u448(&v56);
    eqdestroy___modelZsave95mongerZversionsZv0_u145(v105);
    v79 = 394i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v107 && (*v107 & 0x4000000000000000i64) == 0 )
      deallocShared(v107);
LABEL_138:
    v79 = 34i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    v56 = v108;
    v57 = v109;
    eqdestroy___modelZsave95mongerZversionsZv0_u296(&v56);
    v79 = 170i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    eqdestroy___modelZboardZprototype95list_u3239(v110);
    v79 = 119i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
    v56 = v114;
    v57 = v115;
    eqdestroy___modelZsave95mongerZserialize_u455(&v56);
    goto LABEL_139;
  }
  v79 = 170i64;
  v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  eqcopy___modelZboardZprototype95list_u3242(v110, v141);
  v79 = 1092i64;
  v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  if ( v172 != 78 )
  {
LABEL_37:
    v79 = 1097i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    if ( v110[0] == 4 )
    {
      v79 = 1098i64;
      v87 = bits__modelZsave95mongerZcommon_u192(1i64);
      if ( *v158 )
        goto LABEL_135;
    }
    v169 = 0;
    v79 = 1101i64;
    v165 = 0;
    v26 = refptr_PROTOTYPES__modelZboardZprototype95list_u3752[1];
    v53 = *refptr_PROTOTYPES__modelZboardZprototype95list_u3752;
    v54 = v26;
    v55 = refptr_PROTOTYPES__modelZboardZprototype95list_u3752[2];
    v165 = contains__modelZboardZboard_u10031(&v53, v172);
    if ( *v158 )
      goto LABEL_135;
    if ( v165 == 1 )
    {
      v139 = 0i64;
      v139 = X5BX5D___modelZboardZprototype95list_u4239(refptr_PROTOTYPES__modelZboardZprototype95list_u3752, v172);
      if ( *v158 )
        goto LABEL_135;
      v165 = *(_WORD *)(v139 + 66) != 0;
    }
    if ( v165 == 1 )
    {
      nimZeroMem_53(v70, 560i64);
      v138 = 0i64;
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      v164 = 0i64;
      v79 = 183i64;
      v137 = *(_QWORD *)a1;
      v136 = v137;
      v79 = 184i64;
      while ( v164 < v136 )
      {
        v138 = v164;
        v79 = 34i64;
        v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        if ( v164 < 0 || v164 >= *(_QWORD *)a1 )
        {
          raiseIndexError2(v164, *(_QWORD *)a1 - 1i64);
          break;
        }
        eqcopy___modelZsave95mongerZversionsZv0_u148(v70, *(_QWORD *)(a1 + 8) + 560 * v164 + 8);
        v79 = 1103i64;
        v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
        v135 = 0;
        v27 = refptr_PROTOTYPES__modelZboardZprototype95list_u3752[1];
        v53 = *refptr_PROTOTYPES__modelZboardZprototype95list_u3752;
        v54 = v27;
        v55 = refptr_PROTOTYPES__modelZboardZprototype95list_u3752[2];
        v135 = contains__modelZboardZboard_u10031(&v53, LOBYTE(v70[0]));
        if ( *v158 )
          break;
        if ( v135 == 1 )
        {
          v79 = 1106i64;
          v134 = 0i64;
          v134 = X5BX5D___modelZboardZprototype95list_u4239(
                   refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
                   LOBYTE(v70[0]));
          if ( *v158 )
            break;
          v79 = 1104i64;
          v169 = max__modelZtranslations_u5440_0(v169, (unsigned __int16)(LOWORD(v70[20]) + *(_WORD *)(v134 + 66)));
        }
        v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v164;
        v79 = 187i64;
        v133 = *(_QWORD *)a1;
        if ( v133 != v136 )
        {
          v56 = TM__CKxtw4nX41tlcDT9cZT8kGA_4;
          v57 = (char *)&TM__CKxtw4nX41tlcDT9cZT8kGA_3;
          failedAssertImpl__stdZassertions_u234(&v56);
          if ( *v158 )
            break;
        }
      }
      v79 = 34i64;
      v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      eqdestroy___modelZsave95mongerZversionsZv0_u145(v70);
      if ( *v158 )
        goto LABEL_135;
    }
    v56 = v58;
    v57 = v59;
    eqcopy___modelZsave95mongerZversionsZv0_u299(&v108, &v56);
    v79 = 1111i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    if ( v172 == 82 || v172 == 83 || v172 == 91 )
    {
      v79 = 1112i64;
      v132 = v108;
      if ( v108 <= 0 )
      {
        v79 = 1113i64;
        nimZeroMem_53(v70, 48i64);
        add__modelZsave95mongerZversionsZv7_u2572(&v108, v70);
      }
    }
    v79 = 1699i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v56 = v62;
    v57 = v63;
    eqcopy___system_u2661(&v106, &v56);
    v79 = 1117i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    v163 = v172 == 101;
    if ( v172 == 101 )
      v163 = v106 == 0;
    if ( v163 )
    {
      v79 = 1118i64;
      v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
      if ( v114 <= 0 )
      {
        raiseIndexError2(0i64, v114 - 1);
        goto LABEL_135;
      }
      v75 = 0i64;
      v76 = 0i64;
      dollar___systemZdollars_u59(&v75, *((_QWORD *)v115 + 1));
      if ( *v158 )
      {
        v56 = v75;
        v57 = v76;
        eqdestroy___system_u281_27(&v56);
        goto LABEL_135;
      }
      v79 = 1699i64;
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      v56 = v75;
      v57 = v76;
      eqsink___system_u2667(&v106, &v56);
    }
    v79 = 1120i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    nimZeroMem_53(v105, 560i64);
    v157 = v172;
    LOBYTE(v105[0]) = v172;
    v156 = a9;
    v105[49] = a9;
    v79 = 629i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    v104 = eqdup___modelZsave95mongerZcommon_u4321(a4);
    *(_DWORD *)((char *)v105 + 2) = v104;
    v155 = v69;
    BYTE6(v105[0]) = v69;
    v105[1] = v88;
    v85 = v114;
    v86 = (__int64)v115;
    v79 = 119i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
    eqwasMoved___modelZsave95mongerZserialize_u452(&v114);
    v105[21] = v85;
    v105[22] = v86;
    LOWORD(v105[20]) = v169;
    v79 = 1699i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v56 = v64;
    v57 = v65;
    eqdup___system_u2664(&v102, &v56);
    v105[24] = v102;
    v105[25] = v103;
    v83 = v106;
    v84 = v107;
    v79 = 1699i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    eqwasMoved___system_u2658(&v106);
    v105[26] = v83;
    v105[27] = (__int64)v84;
    v79 = 23i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v12.nim";
    v28 = a3[1];
    v50 = *a3;
    v51 = v28;
    v52 = a3[2];
    eqdup___modelZsave95mongerZversionsZv12_u295(&v53, &v50);
    v101[0] = v53;
    v101[1] = v54;
    v101[2] = v55;
    v105[46] = v53;
    v105[47] = v54;
    v105[48] = v55;
    v79 = 184i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    v100 = eqdup___modelZsave95mongerZcommon_u182(v87);
    v105[28] = v100;
    v79 = 1132i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    v105[29] = get_clamped_word_size__modelZboardZprototype95list_u4458(v172, v87, 0);
    if ( *v158 )
      goto LABEL_135;
    v79 = 123i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
    v29 = a15[1];
    v53 = *a15;
    v54 = v29;
    v55 = a15[2];
    eqdup___modelZsave95mongerZsave95monger_u880(&v50, &v53);
    v99[0] = v50;
    v99[1] = v51;
    v99[2] = v52;
    v105[53] = v50;
    v105[54] = v51;
    v105[55] = v52;
    v154 = v67;
    LOWORD(v105[23]) = v67;
    v79 = 34i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    v56 = v108;
    v57 = v109;
    eqdup___modelZsave95mongerZversionsZv0_u302(&v97, &v56);
    v105[30] = v97;
    v105[31] = v98;
    v131 = v108;
    v130 = v108;
    v79 = 1177i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
    if ( v108 < 0 )
    {
      raiseRangeErrorI(v130, 0i64, 0x7FFFFFFFFFFFFFFFi64);
      goto LABEL_135;
    }
    newSeq__modelZboardZboard_u21995(&v56, v130);
    v95 = v56;
    v96 = v57;
    v129 = 0i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v162 = 0i64;
    v79 = 129i64;
    while ( v162 < v130 )
    {
      v129 = v162;
      v79 = 934i64;
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      if ( v162 < 0 || v129 >= v95 )
      {
        raiseIndexError2(v129, v95 - 1);
        goto LABEL_135;
      }
      nimZeroMem_53(v70, 72i64);
      eqsink___modelZsave95mongerZversionsZv0_u523(&v96[72 * v129 + 8], v70);
      v79 = 131i64;
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v74 = v162 + 1;
      if ( __OFADD__(1i64, v162) )
        goto LABEL_120;
      v162 = v74;
    }
    v79 = 1136i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    v105[32] = v95;
    v105[33] = (__int64)v96;
    eqwasMoved___modelZsave95mongerZversionsZv0_u445(&v95);
    v79 = 1138i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    v128 = v111;
    v127 = v112;
    v82 = v111 + v112;
    if ( __OFADD__(v111, v112) )
    {
LABEL_120:
      raiseOverflow();
      goto LABEL_135;
    }
    v126 = v82;
    v79 = 1175i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
    if ( v82 < 0 )
    {
      raiseRangeErrorI(v126, 0i64, 0x7FFFFFFFFFFFFFFFi64);
      goto LABEL_135;
    }
    newSeqUninit__modelZboardZboard_u21887(&v56, v126);
    v93 = v56;
    v94 = v57;
    v125 = 0i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v161 = 0i64;
    v79 = 129i64;
    while ( v161 < v126 )
    {
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
      v125 = v161;
      v79 = 1179i64;
      if ( v161 < 0 || v125 >= v93 )
      {
        raiseIndexError2(v125, v93 - 1);
        goto LABEL_135;
      }
      v79 = 1138i64;
      v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
      nimZeroMem_53(v70, 80i64);
      v70[1] = 1i64;
      nimZeroMem_53(&v70[2], 8i64);
      v70[2] = 256i64;
      LOBYTE(v70[3]) = 1;
      v70[4] = 1i64;
      nimZeroMem_53(&v70[5], 8i64);
      v70[5] = 256i64;
      LOBYTE(v70[6]) = 1;
      v30 = &v94[80 * v125];
      v31 = v70[1];
      *((_QWORD *)v30 + 1) = v70[0];
      *((_QWORD *)v30 + 2) = v31;
      v32 = v70[3];
      *((_QWORD *)v30 + 3) = v70[2];
      *((_QWORD *)v30 + 4) = v32;
      v33 = v70[5];
      *((_QWORD *)v30 + 5) = v70[4];
      *((_QWORD *)v30 + 6) = v33;
      v34 = v70[7];
      *((_QWORD *)v30 + 7) = v70[6];
      *((_QWORD *)v30 + 8) = v34;
      v35 = v70[9];
      *((_QWORD *)v30 + 9) = v70[8];
      *((_QWORD *)v30 + 10) = v35;
      v79 = 131i64;
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v73 = v161 + 1;
      if ( __OFADD__(1i64, v161) )
        goto LABEL_120;
      v161 = v73;
    }
    v79 = 1137i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    v105[6] = v93;
    v105[7] = (__int64)v94;
    eqwasMoved___modelZsave95mongerZversionsZv0_u169(&v93);
    v124 = v113;
    v123 = v113;
    v79 = 1175i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
    if ( v113 < 0 )
    {
      raiseRangeErrorI(v123, 0i64, 0x7FFFFFFFFFFFFFFFi64);
      goto LABEL_135;
    }
    newSeqUninit__modelZboardZboard_u21887(&v56, v123);
    v91 = v56;
    v92 = v57;
    v122 = 0i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v160 = 0i64;
    v79 = 129i64;
    while ( v160 < v123 )
    {
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
      v122 = v160;
      v79 = 1179i64;
      if ( v160 < 0 || v122 >= v91 )
      {
        raiseIndexError2(v122, v91 - 1);
        goto LABEL_135;
      }
      v79 = 1140i64;
      v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
      nimZeroMem_53(v70, 80i64);
      v70[1] = 1i64;
      nimZeroMem_53(&v70[2], 8i64);
      v70[2] = 256i64;
      LOBYTE(v70[3]) = 1;
      v70[4] = 1i64;
      nimZeroMem_53(&v70[5], 8i64);
      v70[5] = 256i64;
      LOBYTE(v70[6]) = 1;
      v36 = &v92[80 * v122];
      v37 = v70[1];
      *((_QWORD *)v36 + 1) = v70[0];
      *((_QWORD *)v36 + 2) = v37;
      v38 = v70[3];
      *((_QWORD *)v36 + 3) = v70[2];
      *((_QWORD *)v36 + 4) = v38;
      v39 = v70[5];
      *((_QWORD *)v36 + 5) = v70[4];
      *((_QWORD *)v36 + 6) = v39;
      v40 = v70[7];
      *((_QWORD *)v36 + 7) = v70[6];
      *((_QWORD *)v36 + 8) = v40;
      v41 = v70[9];
      *((_QWORD *)v36 + 9) = v70[8];
      *((_QWORD *)v36 + 10) = v41;
      v79 = 131i64;
      v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v72 = v160 + 1;
      if ( __OFADD__(1i64, v160) )
        goto LABEL_120;
      v160 = v72;
    }
    v79 = 1140i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    v105[8] = v91;
    v105[9] = (__int64)v92;
    eqwasMoved___modelZsave95mongerZversionsZv0_u169(&v91);
    v79 = 131i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
    v42 = a13[1];
    v53 = *a13;
    v54 = v42;
    v55 = a13[2];
    eqdup___modelZsave95mongerZsave95monger_u901(&v50, &v53);
    v90[0] = v50;
    v90[1] = v51;
    v90[2] = v52;
    v105[50] = v50;
    v105[51] = v51;
    v105[52] = v52;
    v153 = v68;
    LOBYTE(v105[59]) = v68;
    v79 = 468i64;
    v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    v43 = a12[1];
    v53 = *a12;
    v54 = v43;
    v55 = a12[2];
    eqdup___modelZsave95mongerZversionsZv0_u123(&v50, &v53);
    v89[0] = v50;
    v89[1] = v51;
    v89[2] = v52;
    v105[60] = v50;
    v105[61] = v51;
    v105[62] = v52;
    v79 = 1145i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    v152 = v66;
    BYTE1(v105[34]) = v66;
    nimZeroMem_53(&v105[10], 80i64);
    v105[11] = 1i64;
    nimZeroMem_53(&v105[12], 8i64);
    v105[12] = 256i64;
    LOBYTE(v105[13]) = 1;
    v105[14] = 1i64;
    nimZeroMem_53(&v105[15], 8i64);
    v105[15] = 256i64;
    LOBYTE(v105[16]) = 1;
    v79 = 1148i64;
    v121 = 0;
    v44 = *((_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788 + 1);
    v50 = *(_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788;
    v51 = v44;
    v52 = *((_QWORD *)refptr_MEMORY_COMPONENTS__modelZsave95mongerZcommon_u1788 + 2);
    v121 = contains__modelZboardZmemory95manager_u414(&v50, LOBYTE(v105[0]));
    if ( *v158 )
      goto LABEL_135;
    if ( v121 == 1 )
    {
      v79 = 1149i64;
      v45 = refptr_DEFAULT_BUFFER__modelZboardZmemory95manager_u9[1];
      v105[39] = *refptr_DEFAULT_BUFFER__modelZboardZmemory95manager_u9;
      v105[40] = v45;
      v46 = refptr_DEFAULT_BUFFER__modelZboardZmemory95manager_u9[3];
      v105[41] = refptr_DEFAULT_BUFFER__modelZboardZmemory95manager_u9[2];
      v105[42] = v46;
      v47 = refptr_DEFAULT_BUFFER__modelZboardZmemory95manager_u9[5];
      v105[43] = refptr_DEFAULT_BUFFER__modelZboardZmemory95manager_u9[4];
      v105[44] = v47;
      v105[45] = refptr_DEFAULT_BUFFER__modelZboardZmemory95manager_u9[6];
    }
    v79 = 1151i64;
    if ( !*(_QWORD *)a1 )
    {
      v56 = TM__CKxtw4nX41tlcDT9cZT8kGA_10;
      v57 = (char *)&TM__CKxtw4nX41tlcDT9cZT8kGA_9;
      failedAssertImpl__stdZassertions_u234(&v56);
      if ( *v158 )
        goto LABEL_135;
    }
    v168 = a14;
    v79 = 1154i64;
    if ( a14 <= 0 )
    {
      v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
      v168 = 1i64;
      v79 = 1159i64;
      while ( 1 )
      {
        v159 = 0;
        v119 = *(_QWORD *)a1;
        v159 = v168 < v119;
        if ( v168 < v119 )
        {
          v79 = 1160i64;
          if ( v168 < 0 || v168 >= *(_QWORD *)a1 )
            goto LABEL_126;
          v159 = *(_BYTE *)(*(_QWORD *)(a1 + 8) + 560 * v168 + 8) != 0;
        }
        if ( !v159 )
          break;
        v79 = 1161i64;
        v71 = v168 + 1;
        if ( __OFADD__(1i64, v168) )
          goto LABEL_120;
        v168 = v71;
      }
      v79 = 1163i64;
      v118 = *(_QWORD *)a1 - 1i64;
      if ( v118 < v168 )
      {
        v79 = 1164i64;
        nimZeroMem_53(v70, 560i64);
        qmemcpy(v70, v105, 0x230ui64);
        v79 = 34i64;
        v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        eqwasMoved___modelZsave95mongerZversionsZv0_u142(v105, v105);
        v79 = 1164i64;
        v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
        add__modelZsave95mongerZversionsZv0_u1028(a1, v70);
        v79 = 1165i64;
        v117 = *(_QWORD *)a1 - 1i64;
        v168 = v117;
        goto LABEL_128;
      }
      v79 = 34i64;
      v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      if ( v168 < 0 || v168 >= *(_QWORD *)a1 )
        goto LABEL_126;
    }
    else
    {
      v79 = 34i64;
      v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      if ( v168 < 0 || v168 >= *(_QWORD *)a1 )
      {
LABEL_126:
        raiseIndexError2(v168, *(_QWORD *)a1 - 1i64);
        goto LABEL_135;
      }
    }
    eqsink___modelZsave95mongerZversionsZv0_u154(*(_QWORD *)(a1 + 8) + 560 * v168 + 8, v105);
    eqwasMoved___modelZsave95mongerZversionsZv0_u142(v105, v48);
LABEL_128:
    v79 = 1169i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    if ( v168
      || (v56 = TM__CKxtw4nX41tlcDT9cZT8kGA_13,
          v57 = (char *)&TM__CKxtw4nX41tlcDT9cZT8kGA_12,
          failedAssertImpl__stdZassertions_u234(&v56),
          !*v158) )
    {
      v79 = 1171i64;
      v116 = 0i64;
      v116 = X5BX5D___modelZboardZprototype95list_u4239(refptr_PROTOTYPES__modelZboardZprototype95list_u3752, v172);
      if ( !*v158 )
      {
        *(_WORD *)(a1 + 48) += *(_WORD *)(v116 + 66);
        v170 = v168;
        v79 = 34i64;
        v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        v56 = v91;
        v57 = v92;
        eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
        v56 = v93;
        v57 = v94;
        eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
        v56 = v95;
        v57 = v96;
        eqdestroy___modelZsave95mongerZversionsZv0_u448(&v56);
        eqdestroy___modelZsave95mongerZversionsZv0_u145(v105);
        v79 = 394i64;
        v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v107 && (*v107 & 0x4000000000000000i64) == 0 )
          deallocShared(v107);
        goto LABEL_138;
      }
    }
    goto LABEL_135;
  }
  v79 = 1093i64;
  v140 = 0;
  v140 = notin_custom_prototypes__modelZboardZcustom95prototype95list_u189(a9);
  if ( *v158 )
    goto LABEL_135;
  if ( v140 != 1 )
  {
    v79 = 1095i64;
    v80 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
    nimZeroMem_53(v70, 1448i64);
    get_custom_prototype__modelZboardZcustom95prototype95list_u451(a9, v70);
    if ( *v158 )
      goto LABEL_135;
    v79 = 170i64;
    v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    eqsink___modelZboardZprototype95list_u3248(v110, v70);
    goto LABEL_37;
  }
  v170 = -1i64;
  v79 = 34i64;
  v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
  v56 = v91;
  v57 = v92;
  eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
  v56 = v93;
  v57 = v94;
  eqdestroy___modelZsave95mongerZversionsZv0_u172(&v56);
  v56 = v95;
  v57 = v96;
  eqdestroy___modelZsave95mongerZversionsZv0_u448(&v56);
  eqdestroy___modelZsave95mongerZversionsZv0_u145(v105);
  v79 = 394i64;
  v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v107 && (*v107 & 0x4000000000000000i64) == 0 )
    deallocShared(v107);
  v79 = 34i64;
  v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
  v56 = v108;
  v57 = v109;
  eqdestroy___modelZsave95mongerZversionsZv0_u296(&v56);
  v79 = 170i64;
  v80 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  eqdestroy___modelZboardZprototype95list_u3239(v110);
  v79 = 119i64;
  v80 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
  v56 = v114;
  v57 = v115;
  eqdestroy___modelZsave95mongerZserialize_u455(&v56);
LABEL_139:
  popFrame_73();
  return v170;
}


/* call 0x000000014027dc0c, caller load_schematic_raw__modelZboardZschematics_u34 @ 0x000000014027c2c6 */

__int64 __fastcall load_schematic_raw__modelZboardZschematics_u34(
        __int16 a1,
        __int64 *a2,
        char a3,
        __int64 a4,
        _QWORD *a5)
{
  _QWORD *v5; // rax
  __int64 v6; // rbx
  __int64 v7; // rbx
  __int64 v8; // rbx
  __int64 v9; // rbx
  __int64 v10; // rbx
  __int64 v11; // rbx
  bool v12; // dl
  bool v13; // dl
  __int64 v14; // rbx
  __int64 v15; // rbx
  __int64 v16; // rbx
  __int64 v17; // rbx
  __int64 v19[2]; // [rsp+A0h] [rbp+20h] BYREF
  __int64 v20[2]; // [rsp+B0h] [rbp+30h] BYREF
  __int64 v21[4]; // [rsp+C0h] [rbp+40h] BYREF
  __int64 v22[4]; // [rsp+E0h] [rbp+60h] BYREF
  __int64 v23[4]; // [rsp+100h] [rbp+80h] BYREF
  __int64 v24[2]; // [rsp+120h] [rbp+A0h] BYREF
  __int64 v25; // [rsp+130h] [rbp+B0h] BYREF
  void *v26; // [rsp+138h] [rbp+B8h]
  __int64 v27; // [rsp+140h] [rbp+C0h] BYREF
  __int64 v28; // [rsp+148h] [rbp+C8h]
  __int64 v29; // [rsp+150h] [rbp+D0h]
  __int64 v30[70]; // [rsp+160h] [rbp+E0h] BYREF
  __int64 v31[37]; // [rsp+390h] [rbp+310h] BYREF
  char v32; // [rsp+4B9h] [rbp+439h]
  char v33; // [rsp+4BAh] [rbp+43Ah]
  __int64 v34; // [rsp+8F8h] [rbp+878h] BYREF
  __int64 v35; // [rsp+900h] [rbp+880h]
  __int64 v36; // [rsp+938h] [rbp+8B8h]
  __int64 v37; // [rsp+940h] [rbp+8C0h]
  __int64 v38; // [rsp+948h] [rbp+8C8h]
  __int64 v39; // [rsp+950h] [rbp+8D0h]
  __int64 clamped_word_size__modelZboardZprototype95list_u4458; // [rsp+958h] [rbp+8D8h]
  __int64 v41; // [rsp+960h] [rbp+8E0h]
  __int64 v42; // [rsp+968h] [rbp+8E8h]
  __int64 v43; // [rsp+970h] [rbp+8F0h]
  int v44; // [rsp+984h] [rbp+904h]
  __int64 started; // [rsp+988h] [rbp+908h]
  __int64 v46; // [rsp+990h] [rbp+910h]
  __int64 v47; // [rsp+998h] [rbp+918h] BYREF
  char v48[8]; // [rsp+9A0h] [rbp+920h] BYREF
  const char *v49; // [rsp+9A8h] [rbp+928h]
  __int64 v50; // [rsp+9B0h] [rbp+930h]
  const char *v51; // [rsp+9B8h] [rbp+938h]
  __int16 v52; // [rsp+9C0h] [rbp+940h]
  __int64 v53[70]; // [rsp+9D0h] [rbp+950h] BYREF
  char v54[48]; // [rsp+C00h] [rbp+B80h] BYREF
  __int64 v55; // [rsp+C30h] [rbp+BB0h] BYREF
  __int64 v56; // [rsp+C38h] [rbp+BB8h]
  __int64 v57; // [rsp+C40h] [rbp+BC0h]
  __int64 v58; // [rsp+C48h] [rbp+BC8h]
  __int64 v59; // [rsp+C50h] [rbp+BD0h]
  __int64 v60; // [rsp+C58h] [rbp+BD8h]
  __int64 v61; // [rsp+C60h] [rbp+BE0h]
  __int64 v62; // [rsp+C68h] [rbp+BE8h]
  __int64 v63; // [rsp+C70h] [rbp+BF0h]
  __int64 v64; // [rsp+C78h] [rbp+BF8h]
  __int64 v65; // [rsp+C80h] [rbp+C00h]
  _QWORD *v66; // [rsp+C88h] [rbp+C08h]
  __int64 v67; // [rsp+C90h] [rbp+C10h]
  _QWORD *v68; // [rsp+C98h] [rbp+C18h]
  __int64 v69; // [rsp+CA0h] [rbp+C20h]
  _QWORD *v70; // [rsp+CA8h] [rbp+C28h]
  __int64 v71; // [rsp+CB0h] [rbp+C30h]
  char v72; // [rsp+CBFh] [rbp+C3Fh]
  __int64 v73; // [rsp+CC0h] [rbp+C40h]
  char v74; // [rsp+CCFh] [rbp+C4Fh]
  __int64 v75; // [rsp+CD0h] [rbp+C50h]
  _QWORD *v76; // [rsp+CD8h] [rbp+C58h]
  __int64 v77; // [rsp+CE0h] [rbp+C60h]
  __int64 v78; // [rsp+CE8h] [rbp+C68h]
  __int64 v79; // [rsp+CF0h] [rbp+C70h]
  __int64 v80; // [rsp+CF8h] [rbp+C78h]
  __int64 v81; // [rsp+D00h] [rbp+C80h]
  __int64 v82; // [rsp+D08h] [rbp+C88h]
  __int64 v83; // [rsp+D10h] [rbp+C90h]
  __int64 v84; // [rsp+D18h] [rbp+C98h]
  unsigned __int8 v85; // [rsp+D27h] [rbp+CA7h]
  __int64 v86; // [rsp+D28h] [rbp+CA8h]
  _QWORD *v87; // [rsp+D30h] [rbp+CB0h]
  __int64 v88; // [rsp+D38h] [rbp+CB8h]
  _QWORD *v89; // [rsp+D40h] [rbp+CC0h]
  __int64 v90; // [rsp+D48h] [rbp+CC8h]
  char v91; // [rsp+D57h] [rbp+CD7h]
  __int64 modelZboardZschematics_u244; // [rsp+D58h] [rbp+CD8h]
  char v93; // [rsp+D67h] [rbp+CE7h]
  __int64 v94; // [rsp+D68h] [rbp+CE8h]
  __int64 v95; // [rsp+D70h] [rbp+CF0h]
  __int64 v96; // [rsp+D78h] [rbp+CF8h]
  __int64 v97; // [rsp+D80h] [rbp+D00h]
  __int64 v98; // [rsp+D88h] [rbp+D08h]
  unsigned __int8 v99; // [rsp+D94h] [rbp+D14h]
  char v100; // [rsp+D95h] [rbp+D15h]
  char v101; // [rsp+D96h] [rbp+D16h]
  unsigned __int8 v102; // [rsp+D97h] [rbp+D17h]
  __int64 v103; // [rsp+D98h] [rbp+D18h]
  __int64 v104; // [rsp+DA0h] [rbp+D20h]
  __int64 v105; // [rsp+DA8h] [rbp+D28h]
  __int64 v106; // [rsp+DB0h] [rbp+D30h]
  char v107; // [rsp+DBFh] [rbp+D3Fh]
  __int64 v108; // [rsp+DC0h] [rbp+D40h]
  __int64 v109; // [rsp+DC8h] [rbp+D48h]
  __int64 v110; // [rsp+DD0h] [rbp+D50h]
  __int16 v111; // [rsp+DDEh] [rbp+D5Eh]
  _BYTE *v112; // [rsp+DE0h] [rbp+D60h]
  __int64 v113; // [rsp+DE8h] [rbp+D68h]
  __int64 v114; // [rsp+DF0h] [rbp+D70h]
  unsigned __int8 v115; // [rsp+DFFh] [rbp+D7Fh]
  __int64 v116; // [rsp+E00h] [rbp+D80h]
  __int64 v117; // [rsp+E08h] [rbp+D88h]

  v49 = "load_schematic_raw";
  v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
  v50 = 0i64;
  v52 = 0;
  nimFrame_75(v48);
  v112 = (_BYTE *)nimErrorFlag_73();
  nimZeroMem_55(a5, 72i64);
  nimZeroMem_55(&v55, 72i64);
  v111 = 0;
  nimZeroMem_55(v54, 48i64);
  v50 = 34i64;
  v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
  nimZeroMem_55(&v55, 72i64);
  v111 = a1;
  WORD1(v61) = a1;
  v55 = 1i64;
  v56 = newSeqPayload(1i64, 560i64, 8i64);
  nimZeroMem_55(v53, 560i64);
  nimZeroMem_55(&v53[10], 80i64);
  v53[11] = 1i64;
  nimZeroMem_55(&v53[12], 8i64);
  v53[12] = 256i64;
  LOBYTE(v53[13]) = 1;
  v53[14] = 1i64;
  nimZeroMem_55(&v53[15], 8i64);
  v53[15] = 256i64;
  LOBYTE(v53[16]) = 1;
  nimZeroMem_55(&v53[60], 24i64);
  LOBYTE(v53[60]) = 0;
  qmemcpy((void *)(v56 + 8), v53, 0x230ui64);
  v50 = 35i64;
  eqcopy___modelZboardZschematics_u1632(v54, a4);
  nimZeroMem_55(v30, 104i64);
  nimZeroMem_55(&v47, 8i64);
  nimZeroMem_55(v31, 104i64);
  v110 = 0i64;
  v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v117 = 0i64;
  v50 = 183i64;
  v109 = a2[4];
  v108 = v109;
  v50 = 184i64;
  while ( v117 < v108 )
  {
    v50 = 536i64;
    v51 = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    v110 = v117;
    if ( v117 < 0 || v117 >= a2[4] )
    {
      raiseIndexError2(v117, a2[4] - 1);
      break;
    }
    v5 = (_QWORD *)(a2[5] + 104 * v117);
    v6 = v5[2];
    v31[0] = v5[1];
    v31[1] = v6;
    v7 = v5[4];
    v31[2] = v5[3];
    v31[3] = v7;
    v8 = v5[6];
    v31[4] = v5[5];
    v31[5] = v8;
    v9 = v5[8];
    v31[6] = v5[7];
    v31[7] = v9;
    v10 = v5[10];
    v31[8] = v5[9];
    v31[9] = v10;
    v11 = v5[12];
    v31[10] = v5[11];
    v31[11] = v11;
    v31[12] = v5[13];
    v47 = v110;
    v50 = 185i64;
    v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    eqcopy___modelZsave95mongerZcommon_u3692(v30, v31);
    v50 = 38i64;
    v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
    v107 = 0;
    v107 = is_tombstone__modelZsave95mongerZcommon_u4884(v30);
    if ( *v112 )
      break;
    if ( v107 != 1 )
    {
      v50 = 194i64;
      v51 = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
      v46 = bits__modelZsave95mongerZcommon_u192(1i64);
      if ( *v112 )
        break;
      v50 = 40i64;
      v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
      v27 = v30[3];
      v28 = v30[4];
      v29 = v30[5];
      v25 = v30[1];
      v26 = (void *)v30[2];
      started = board_start_wire__modelZboardZboard_u6704(
                  (unsigned int)&v55,
                  (unsigned int)&v27,
                  BYTE2(v30[0]),
                  (unsigned int)&v25,
                  *(_QWORD *)refptr_INVALID_WIRE_ID__modelZsave95mongerZcommon_u3579,
                  v46);
      if ( *v112 )
        break;
    }
    else
    {
      v50 = 39i64;
    }
    v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v117;
    v50 = 187i64;
    v106 = a2[4];
    if ( v106 != v108 )
    {
      v25 = TM__DRGBjVoeyzCuYwSWCgAUCw_3;
      v26 = &TM__DRGBjVoeyzCuYwSWCgAUCw_2;
      failedAssertImpl__stdZassertions_u234(&v25);
      if ( *v112 )
        break;
    }
  }
  v50 = 185i64;
  eqdestroy___modelZsave95mongerZcommon_u3689(v30);
  if ( *v112 )
  {
LABEL_130:
    v50 = 35i64;
    v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
    eqdestroy___modelZboardZschematics_u1629(v54);
    v50 = 173i64;
    v51 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
    eqdestroy___modelZsave95mongerZsave95monger_u2637(&v55);
    return popFrame_75();
  }
  v50 = 42i64;
  v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
  if ( a3 == 3 || a3 == 5 || a3 == 6 )
  {
    v50 = 43i64;
    WORD1(v61) = 255;
  }
  nimZeroMem_55(v30, 560i64);
  v105 = 0i64;
  v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v116 = 0i64;
  v50 = 183i64;
  v104 = *a2;
  v103 = v104;
  v50 = 184i64;
  while ( v116 < v103 )
  {
    v50 = 45i64;
    v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
    v105 = v116;
    if ( v116 < 0 || v116 >= *a2 )
    {
      raiseIndexError2(v116, *a2 - 1);
      goto LABEL_130;
    }
    qmemcpy(v30, (const void *)(560 * v116 + a2[1] + 8), sizeof(v30));
    v50 = 46i64;
    if ( LOBYTE(v30[0]) )
    {
      v102 = v30[0];
      v44 = *(_DWORD *)((char *)v30 + 2);
      v41 = v30[46];
      v42 = v30[47];
      v43 = v30[48];
      v115 = 0;
      v50 = 52i64;
      v101 = 0;
      v101 = isSome__modelZboardZschematics_u78(v54);
      if ( *v112 )
        goto LABEL_130;
      if ( v101 == 1 )
      {
        v50 = 53i64;
        if ( v102 == 78 )
        {
          nimZeroMem_55(v31, 1448i64);
          v50 = 54i64;
          v100 = 0;
          v100 = notin_custom_prototypes__modelZboardZcustom95prototype95list_u189(v30[49]);
          if ( !*v112 )
          {
            if ( v100 == 1 )
            {
              v50 = 170i64;
              v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              eqdestroy___modelZboardZprototype95list_u3239(v31);
              v50 = 55i64;
              v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
              goto LABEL_125;
            }
            v50 = 56i64;
            get_custom_prototype__modelZboardZcustom95prototype95list_u451(v30[49], v31);
            if ( !*v112 )
            {
              v50 = 57i64;
              if ( v32 == 1 )
              {
                v50 = 170i64;
                v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                eqdestroy___modelZboardZprototype95list_u3239(v31);
                v50 = 58i64;
                v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
                goto LABEL_125;
              }
              v50 = 59i64;
              if ( v33 == 1 )
              {
                v50 = 170i64;
                v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                eqdestroy___modelZboardZprototype95list_u3239(v31);
                v50 = 60i64;
                v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
                goto LABEL_125;
              }
              v99 = 0;
              v98 = 0i64;
              v50 = 2655i64;
              v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
              v97 = len__modelZboardZschematics_u131(&v34);
              if ( !*v112 )
              {
                v96 = 0i64;
                v94 = v34 - 1;
                v95 = v34 - 1;
                v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                v114 = 0i64;
                v50 = 97i64;
                while ( v114 <= v95 )
                {
                  v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                  v96 = v114;
                  v50 = 2657i64;
                  if ( v114 < 0 || v96 >= v34 )
                  {
LABEL_48:
                    raiseIndexError2(v96, v34 - 1);
                    goto LABEL_98;
                  }
                  if ( *(_QWORD *)(v35 + 16 * v96 + 16) )
                  {
                    v50 = 62i64;
                    v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
                    if ( v96 < 0 )
                      goto LABEL_48;
                    if ( v96 >= v34 )
                      goto LABEL_48;
                    v99 = *(_BYTE *)(v35 + 16 * v96 + 8);
                    if ( v96 >= v34 )
                      goto LABEL_48;
                    v98 = *(_QWORD *)(v35 + 16 * v96 + 16);
                    v50 = 63i64;
                    v93 = 0;
                    v93 = is_free_component_type__modelZscores_u1938(v99);
                    if ( *v112 )
                      goto LABEL_98;
                    if ( v93 != 1 )
                    {
                      v50 = 65i64;
                      modelZboardZschematics_u244 = 0i64;
                      modelZboardZschematics_u244 = get__modelZboardZschematics_u244(v54);
                      if ( *v112 )
                        goto LABEL_98;
                      v91 = 0;
                      v91 = contains__modelZboardZschematics_u315(modelZboardZschematics_u244, v99);
                      if ( *v112 )
                        goto LABEL_98;
                      if ( !v91 )
                      {
                        v115 = v99;
                        v50 = 67i64;
                        break;
                      }
                      v50 = 69i64;
                      v90 = 0i64;
                      v90 = get__modelZboardZschematics_u244(v54);
                      if ( *v112 )
                        goto LABEL_98;
                      v89 = 0i64;
                      v89 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v90, v99);
                      if ( *v112 )
                        goto LABEL_98;
                      if ( *v89 == -1i64 )
                      {
                        v50 = 70i64;
                      }
                      else
                      {
                        v50 = 72i64;
                        v88 = 0i64;
                        v88 = get__modelZboardZschematics_u244(v54);
                        if ( *v112 )
                          goto LABEL_98;
                        v87 = 0i64;
                        v87 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v88, v99);
                        if ( *v112 )
                          goto LABEL_98;
                        if ( v98 > *v87 )
                        {
                          v115 = v99;
                          v50 = 74i64;
                          break;
                        }
                      }
                    }
                    v50 = 2659i64;
                    v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                    v86 = 0i64;
                    v86 = len__modelZboardZschematics_u131(&v34);
                    if ( *v112 )
                      goto LABEL_98;
                    if ( v86 != v97 )
                    {
                      v25 = TM__DRGBjVoeyzCuYwSWCgAUCw_7;
                      v26 = &TM__DRGBjVoeyzCuYwSWCgAUCw_6;
                      failedAssertImpl__stdZassertions_u234(&v25);
                      if ( *v112 )
                        goto LABEL_98;
                    }
                  }
                  v50 = 102i64;
                  v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                  v39 = v114 + 1;
                  if ( __OFADD__(1i64, v114) )
                  {
LABEL_88:
                    raiseOverflow();
                    goto LABEL_98;
                  }
                  v114 = v39;
                }
                v50 = 76i64;
                v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
                if ( !v115 )
                {
                  v85 = 0;
                  v84 = 0i64;
                  v50 = 2655i64;
                  v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                  v83 = len__modelZboardZschematics_u131(&v34);
                  if ( !*v112 )
                  {
                    v82 = 0i64;
                    v80 = v34 - 1;
                    v81 = v34 - 1;
                    v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                    v113 = 0i64;
                    v50 = 97i64;
                    while ( v113 <= v81 )
                    {
                      v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                      v82 = v113;
                      v50 = 2657i64;
                      if ( v113 < 0 || v82 >= v34 )
                      {
LABEL_81:
                        raiseIndexError2(v82, v34 - 1);
                        break;
                      }
                      if ( *(_QWORD *)(v35 + 16 * v82 + 16) )
                      {
                        v50 = 77i64;
                        v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
                        if ( v82 < 0 )
                          goto LABEL_81;
                        if ( v82 >= v34 )
                          goto LABEL_81;
                        v85 = *(_BYTE *)(v35 + 16 * v82 + 8);
                        if ( v82 >= v34 )
                          goto LABEL_81;
                        v84 = *(_QWORD *)(v35 + 16 * v82 + 16);
                        v50 = 78i64;
                        v79 = 0i64;
                        v79 = get__modelZboardZschematics_u244(v54);
                        if ( *v112 )
                          break;
                        v78 = 0i64;
                        v78 = getOrDefault__modelZboardZschematics_u1095(v79, v85, -1i64);
                        if ( *v112 )
                          break;
                        if ( v78 != -1 )
                        {
                          v50 = 79i64;
                          v77 = 0i64;
                          v77 = get__modelZboardZschematics_u244(v54);
                          if ( *v112 )
                            break;
                          v76 = 0i64;
                          v76 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v77, v85);
                          if ( *v112 )
                            break;
                          v12 = __OFSUB__(*v76, v84);
                          v37 = *v76 - v84;
                          if ( v12 )
                            goto LABEL_88;
                          *v76 = v37;
                        }
                        v50 = 2659i64;
                        v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
                        v75 = 0i64;
                        v75 = len__modelZboardZschematics_u131(&v34);
                        if ( *v112 )
                          break;
                        if ( v75 != v83 )
                        {
                          v25 = TM__DRGBjVoeyzCuYwSWCgAUCw_10;
                          v26 = &TM__DRGBjVoeyzCuYwSWCgAUCw_6;
                          failedAssertImpl__stdZassertions_u234(&v25);
                          if ( *v112 )
                            break;
                        }
                      }
                      v50 = 102i64;
                      v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
                      v38 = v113 + 1;
                      if ( __OFADD__(1i64, v113) )
                        goto LABEL_88;
                      v113 = v38;
                    }
                  }
                }
              }
            }
          }
LABEL_98:
          v50 = 170i64;
          v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          eqdestroy___modelZboardZprototype95list_u3239(v31);
          if ( *v112 )
            goto LABEL_130;
        }
        else
        {
          v50 = 80i64;
          v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
          v74 = 0;
          v74 = is_free_component_type__modelZscores_u1938(v102);
          if ( *v112 )
            goto LABEL_130;
          if ( v74 != 1 )
          {
            v50 = 82i64;
            v73 = 0i64;
            v73 = get__modelZboardZschematics_u244(v54);
            if ( *v112 )
              goto LABEL_130;
            v72 = 0;
            v72 = contains__modelZboardZschematics_u315(v73, LOBYTE(v30[0]));
            if ( *v112 )
              goto LABEL_130;
            if ( v72 )
            {
              v50 = 85i64;
              v71 = 0i64;
              v71 = get__modelZboardZschematics_u244(v54);
              if ( *v112 )
                goto LABEL_130;
              v70 = 0i64;
              v70 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v71, LOBYTE(v30[0]));
              if ( *v112 )
                goto LABEL_130;
              if ( *v70 != -1i64 )
              {
                v50 = 86i64;
                v69 = 0i64;
                v69 = get__modelZboardZschematics_u244(v54);
                if ( *v112 )
                  goto LABEL_130;
                v68 = 0i64;
                v68 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v69, LOBYTE(v30[0]));
                if ( *v112 )
                  goto LABEL_130;
                if ( !*v68 )
                {
                  v50 = 87i64;
                  v115 = v30[0];
                }
                v50 = 88i64;
                v67 = 0i64;
                v67 = get__modelZboardZschematics_u244(v54);
                if ( *v112 )
                  goto LABEL_130;
                v66 = 0i64;
                v66 = (_QWORD *)X5BX5D___modelZboardZschematics_u666(v67, LOBYTE(v30[0]));
                if ( *v112 )
                  goto LABEL_130;
                v13 = __OFSUB__(*v66, -1i64);
                v36 = *v66 + 1i64;
                if ( v13 )
                {
                  raiseOverflow();
                  goto LABEL_130;
                }
                *v66 = v36;
              }
            }
            else
            {
              v50 = 83i64;
              v115 = v30[0];
            }
          }
        }
      }
      v50 = 100i64;
      clamped_word_size__modelZboardZprototype95list_u4458 = get_clamped_word_size__modelZboardZprototype95list_u4458(
                                                               v102,
                                                               v30[28],
                                                               0);
      if ( *v112 )
        goto LABEL_130;
      v50 = 90i64;
      v65 = 0i64;
      v27 = v41;
      v28 = v42;
      v29 = v43;
      v25 = v30[24];
      v26 = (void *)v30[25];
      v24[0] = v30[26];
      v24[1] = v30[27];
      v23[0] = v30[60];
      v23[1] = v30[61];
      v23[2] = v30[62];
      v22[0] = v30[50];
      v22[1] = v30[51];
      v22[2] = v30[52];
      v21[0] = v30[53];
      v21[1] = v30[54];
      v21[2] = v30[55];
      v20[0] = v30[21];
      v20[1] = v30[22];
      v19[0] = v30[30];
      v19[1] = v30[31];
      v65 = board_add_component__modelZboardZboard_u21118(
              (unsigned int)&v55,
              v102,
              (unsigned int)&v27,
              v44,
              BYTE6(v30[0]),
              v30[1],
              (__int64)&v25,
              (__int64)v24,
              v30[49],
              clamped_word_size__modelZboardZprototype95list_u4458,
              LOBYTE(v30[59]),
              (__int64)v23,
              (__int64)v22,
              0i64,
              (__int64)v21,
              (__int64)v20,
              SLOWORD(v30[23]),
              (__int64)v19,
              v115);
      if ( *v112 )
        goto LABEL_130;
    }
LABEL_125:
    v51 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v116;
    v50 = 187i64;
    v64 = *a2;
    if ( v64 != v103 )
    {
      v25 = TM__DRGBjVoeyzCuYwSWCgAUCw_13;
      v26 = &TM__DRGBjVoeyzCuYwSWCgAUCw_2;
      failedAssertImpl__stdZassertions_u234(&v25);
      if ( *v112 )
        goto LABEL_130;
    }
  }
  v14 = v56;
  *a5 = v55;
  a5[1] = v14;
  v15 = v58;
  a5[2] = v57;
  a5[3] = v15;
  v16 = v60;
  a5[4] = v59;
  a5[5] = v16;
  v17 = v62;
  a5[6] = v61;
  a5[7] = v17;
  a5[8] = v63;
  v50 = 173i64;
  v51 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
  eqwasMoved___modelZsave95mongerZsave95monger_u2634(&v55);
  v50 = 35i64;
  v51 = "D:\\TuringComplete_Phu\\model\\board\\schematics.nim";
  eqdestroy___modelZboardZschematics_u1629(v54);
  v50 = 173i64;
  v51 = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
  eqdestroy___modelZsave95mongerZsave95monger_u2637(&v55);
  return popFrame_75();
}


/* call 0x00000001402c3076, caller infer_size__modelZsimulationZpreorder_u1999 @ 0x00000001402be2ad */

__int64 __fastcall infer_size__modelZsimulationZpreorder_u1999(
        _QWORD *a1,
        __int64 *a2,
        __int64 *a3,
        __int64 a4,
        __int64 a5)
{
  __int64 v5; // rax
  __int64 v6; // rdx
  __int64 v7; // rdx
  bool v8; // al
  __int64 v9; // rcx
  __int64 v10; // rax
  __int64 v11; // rcx
  __int64 v12; // rcx
  __int64 v14[4]; // [rsp+30h] [rbp-50h] BYREF
  __int64 v15; // [rsp+50h] [rbp-30h] BYREF
  _QWORD *v16; // [rsp+58h] [rbp-28h]
  __int64 v17; // [rsp+60h] [rbp-20h] BYREF
  void *v18; // [rsp+68h] [rbp-18h]
  __int64 v19; // [rsp+70h] [rbp-10h] BYREF
  _QWORD *v20; // [rsp+78h] [rbp-8h]
  __int64 v21; // [rsp+80h] [rbp+0h]
  _QWORD *v22; // [rsp+88h] [rbp+8h]
  __int64 v23; // [rsp+90h] [rbp+10h]
  _QWORD *v24; // [rsp+98h] [rbp+18h]
  char v25[32]; // [rsp+A0h] [rbp+20h] BYREF
  __int64 (__fastcall *v26)(); // [rsp+C0h] [rbp+40h] BYREF
  _QWORD *v27; // [rsp+C8h] [rbp+48h]
  __int64 (__fastcall *v28)(); // [rsp+D0h] [rbp+50h] BYREF
  _QWORD *v29; // [rsp+D8h] [rbp+58h]
  __int64 (__fastcall *v30)(); // [rsp+E0h] [rbp+60h] BYREF
  _QWORD *v31; // [rsp+E8h] [rbp+68h]
  __int64 (__fastcall *v32)(); // [rsp+F0h] [rbp+70h] BYREF
  _QWORD *v33; // [rsp+F8h] [rbp+78h]
  __int64 (__fastcall *v34)(); // [rsp+100h] [rbp+80h] BYREF
  _QWORD *v35; // [rsp+108h] [rbp+88h]
  __int64 v36; // [rsp+118h] [rbp+98h]
  __int64 (__fastcall *v37)(); // [rsp+120h] [rbp+A0h] BYREF
  _QWORD *v38; // [rsp+128h] [rbp+A8h]
  __int64 v39; // [rsp+138h] [rbp+B8h]
  __int64 (__fastcall *v40)(); // [rsp+140h] [rbp+C0h] BYREF
  _QWORD *v41; // [rsp+148h] [rbp+C8h]
  __int64 v42; // [rsp+158h] [rbp+D8h]
  __int64 (__fastcall *v43)(); // [rsp+160h] [rbp+E0h] BYREF
  _QWORD *v44; // [rsp+168h] [rbp+E8h]
  __int64 v45; // [rsp+178h] [rbp+F8h]
  __int64 (__fastcall *v46)(); // [rsp+180h] [rbp+100h] BYREF
  _QWORD *v47; // [rsp+188h] [rbp+108h]
  __int64 v48; // [rsp+198h] [rbp+118h]
  __int64 (__fastcall *v49)(); // [rsp+1A0h] [rbp+120h] BYREF
  _QWORD *v50; // [rsp+1A8h] [rbp+128h]
  __int64 v51; // [rsp+1B8h] [rbp+138h]
  __int64 (__fastcall *v52)(); // [rsp+1C0h] [rbp+140h] BYREF
  _QWORD *v53; // [rsp+1C8h] [rbp+148h]
  __int64 v54; // [rsp+1D8h] [rbp+158h]
  __int64 (__fastcall *v55)(); // [rsp+1E0h] [rbp+160h] BYREF
  _QWORD *v56; // [rsp+1E8h] [rbp+168h]
  __int64 v57; // [rsp+1F8h] [rbp+178h]
  __int64 (__fastcall *v58)(); // [rsp+200h] [rbp+180h] BYREF
  _QWORD *v59; // [rsp+208h] [rbp+188h]
  __int64 v60; // [rsp+218h] [rbp+198h]
  __int64 (__fastcall *v61)(); // [rsp+220h] [rbp+1A0h] BYREF
  _QWORD *v62; // [rsp+228h] [rbp+1A8h]
  __int64 v63; // [rsp+238h] [rbp+1B8h]
  __int64 (__fastcall *v64)(); // [rsp+240h] [rbp+1C0h] BYREF
  _QWORD *v65; // [rsp+248h] [rbp+1C8h]
  __int64 v66; // [rsp+258h] [rbp+1D8h]
  __int64 (__fastcall *v67)(); // [rsp+260h] [rbp+1E0h] BYREF
  _QWORD *v68; // [rsp+268h] [rbp+1E8h]
  __int64 v69; // [rsp+278h] [rbp+1F8h]
  __int64 (__fastcall *v70)(); // [rsp+280h] [rbp+200h] BYREF
  _QWORD *v71; // [rsp+288h] [rbp+208h]
  __int64 v72; // [rsp+298h] [rbp+218h]
  __int64 (__fastcall *v73)(); // [rsp+2A0h] [rbp+220h] BYREF
  _QWORD *v74; // [rsp+2A8h] [rbp+228h]
  __int64 v75; // [rsp+2B8h] [rbp+238h]
  __int64 (__fastcall *v76)(); // [rsp+2C0h] [rbp+240h] BYREF
  _QWORD *v77; // [rsp+2C8h] [rbp+248h]
  __int64 v78; // [rsp+2D8h] [rbp+258h]
  __int64 (__fastcall *v79)(); // [rsp+2E0h] [rbp+260h] BYREF
  _QWORD *v80; // [rsp+2E8h] [rbp+268h]
  __int64 v81; // [rsp+2F8h] [rbp+278h]
  __int64 (__fastcall *v82)(); // [rsp+300h] [rbp+280h] BYREF
  _QWORD *v83; // [rsp+308h] [rbp+288h]
  __int64 v84; // [rsp+318h] [rbp+298h]
  __int64 (__fastcall *v85)(); // [rsp+320h] [rbp+2A0h] BYREF
  _QWORD *v86; // [rsp+328h] [rbp+2A8h]
  __int64 v87; // [rsp+338h] [rbp+2B8h]
  __int64 (__fastcall *v88)(); // [rsp+340h] [rbp+2C0h] BYREF
  _QWORD *v89; // [rsp+348h] [rbp+2C8h]
  __int64 v90; // [rsp+358h] [rbp+2D8h]
  __int64 (__fastcall *v91)(); // [rsp+360h] [rbp+2E0h] BYREF
  _QWORD *v92; // [rsp+368h] [rbp+2E8h]
  __int64 v93; // [rsp+378h] [rbp+2F8h]
  __int64 (__fastcall *v94)(); // [rsp+380h] [rbp+300h] BYREF
  _QWORD *v95; // [rsp+388h] [rbp+308h]
  __int64 (__fastcall *v96)(); // [rsp+390h] [rbp+310h] BYREF
  _QWORD *v97; // [rsp+398h] [rbp+318h]
  __int64 (__fastcall *v98)(); // [rsp+3A0h] [rbp+320h] BYREF
  _QWORD *v99; // [rsp+3A8h] [rbp+328h]
  __int64 v100; // [rsp+3B8h] [rbp+338h]
  __int64 (__fastcall *v101)(); // [rsp+3C0h] [rbp+340h] BYREF
  _QWORD *v102; // [rsp+3C8h] [rbp+348h]
  __int64 v103; // [rsp+3D8h] [rbp+358h]
  __int64 (__fastcall *v104)(); // [rsp+3E0h] [rbp+360h] BYREF
  _QWORD *v105; // [rsp+3E8h] [rbp+368h]
  __int64 v106; // [rsp+3F8h] [rbp+378h]
  __int64 (__fastcall *v107)(); // [rsp+400h] [rbp+380h] BYREF
  _QWORD *v108; // [rsp+408h] [rbp+388h]
  __int64 v109; // [rsp+418h] [rbp+398h]
  __int64 (__fastcall *v110)(); // [rsp+420h] [rbp+3A0h] BYREF
  _QWORD *v111; // [rsp+428h] [rbp+3A8h]
  __int64 v112; // [rsp+438h] [rbp+3B8h]
  __int64 (__fastcall *v113)(); // [rsp+440h] [rbp+3C0h] BYREF
  _QWORD *v114; // [rsp+448h] [rbp+3C8h]
  __int64 v115; // [rsp+458h] [rbp+3D8h]
  __int64 (__fastcall *v116)(); // [rsp+460h] [rbp+3E0h] BYREF
  _QWORD *v117; // [rsp+468h] [rbp+3E8h]
  __int64 v118; // [rsp+478h] [rbp+3F8h]
  __int64 (__fastcall *v119)(); // [rsp+480h] [rbp+400h] BYREF
  _QWORD *v120; // [rsp+488h] [rbp+408h]
  __int64 v121; // [rsp+498h] [rbp+418h]
  __int64 (__fastcall *v122)(); // [rsp+4A0h] [rbp+420h] BYREF
  _QWORD *v123; // [rsp+4A8h] [rbp+428h]
  __int64 v124; // [rsp+4B8h] [rbp+438h]
  __int64 (__fastcall *v125)(); // [rsp+4C0h] [rbp+440h] BYREF
  _QWORD *v126; // [rsp+4C8h] [rbp+448h]
  __int64 v127; // [rsp+4D8h] [rbp+458h]
  __int64 (__fastcall *v128)(); // [rsp+4E0h] [rbp+460h] BYREF
  _QWORD *v129; // [rsp+4E8h] [rbp+468h]
  __int64 v130; // [rsp+4F8h] [rbp+478h]
  __int64 (__fastcall *v131)(); // [rsp+500h] [rbp+480h] BYREF
  _QWORD *v132; // [rsp+508h] [rbp+488h]
  __int64 v133; // [rsp+518h] [rbp+498h]
  __int64 (__fastcall *v134)(); // [rsp+520h] [rbp+4A0h] BYREF
  _QWORD *v135; // [rsp+528h] [rbp+4A8h]
  __int64 v136; // [rsp+538h] [rbp+4B8h]
  __int64 (__fastcall *v137)(); // [rsp+540h] [rbp+4C0h] BYREF
  _QWORD *v138; // [rsp+548h] [rbp+4C8h]
  __int64 v139; // [rsp+558h] [rbp+4D8h]
  __int64 (__fastcall *v140)(); // [rsp+560h] [rbp+4E0h] BYREF
  _QWORD *v141; // [rsp+568h] [rbp+4E8h]
  __int64 v142; // [rsp+578h] [rbp+4F8h]
  __int64 (__fastcall *v143)(); // [rsp+580h] [rbp+500h] BYREF
  _QWORD *v144; // [rsp+588h] [rbp+508h]
  __int64 v145; // [rsp+598h] [rbp+518h]
  __int64 (__fastcall *v146)(); // [rsp+5A0h] [rbp+520h] BYREF
  _QWORD *v147; // [rsp+5A8h] [rbp+528h]
  __int64 v148; // [rsp+5B8h] [rbp+538h]
  __int64 (__fastcall *v149)(); // [rsp+5C0h] [rbp+540h] BYREF
  _QWORD *v150; // [rsp+5C8h] [rbp+548h]
  __int64 v151; // [rsp+5D8h] [rbp+558h]
  __int64 (__fastcall *v152)(); // [rsp+5E0h] [rbp+560h] BYREF
  _QWORD *v153; // [rsp+5E8h] [rbp+568h]
  __int64 (__fastcall *v154)(); // [rsp+5F0h] [rbp+570h] BYREF
  _QWORD *v155; // [rsp+5F8h] [rbp+578h]
  __int64 v156; // [rsp+600h] [rbp+580h]
  __int64 v157; // [rsp+608h] [rbp+588h]
  __int64 (__fastcall *v158)(); // [rsp+610h] [rbp+590h] BYREF
  _QWORD *v159; // [rsp+618h] [rbp+598h]
  __int64 v160; // [rsp+620h] [rbp+5A0h]
  __int64 v161; // [rsp+628h] [rbp+5A8h]
  __int64 (__fastcall *v162)(); // [rsp+630h] [rbp+5B0h] BYREF
  _QWORD *v163; // [rsp+638h] [rbp+5B8h]
  __int64 v164; // [rsp+640h] [rbp+5C0h]
  __int64 v165; // [rsp+648h] [rbp+5C8h]
  __int64 (__fastcall *v166)(); // [rsp+650h] [rbp+5D0h] BYREF
  _QWORD *v167; // [rsp+658h] [rbp+5D8h]
  __int64 v168; // [rsp+660h] [rbp+5E0h]
  __int64 v169; // [rsp+668h] [rbp+5E8h]
  __int64 v170; // [rsp+670h] [rbp+5F0h]
  __int64 v171; // [rsp+678h] [rbp+5F8h]
  __int64 (__fastcall *v172)(); // [rsp+680h] [rbp+600h] BYREF
  _QWORD *v173; // [rsp+688h] [rbp+608h]
  __int64 v174; // [rsp+698h] [rbp+618h]
  __int64 (__fastcall *v175)(); // [rsp+6A0h] [rbp+620h] BYREF
  _QWORD *v176; // [rsp+6A8h] [rbp+628h]
  __int64 v177; // [rsp+6B0h] [rbp+630h]
  __int64 v178; // [rsp+6B8h] [rbp+638h]
  __int64 (__fastcall *v179)(); // [rsp+6C0h] [rbp+640h] BYREF
  _QWORD *v180; // [rsp+6C8h] [rbp+648h]
  __int64 v181; // [rsp+6D8h] [rbp+658h]
  __int64 (__fastcall *v182)(); // [rsp+6E0h] [rbp+660h] BYREF
  _QWORD *v183; // [rsp+6E8h] [rbp+668h]
  __int64 v184; // [rsp+6F8h] [rbp+678h]
  __int64 v185; // [rsp+700h] [rbp+680h]
  __int64 v186; // [rsp+708h] [rbp+688h]
  __int64 (__fastcall *v187)(); // [rsp+710h] [rbp+690h] BYREF
  _QWORD *v188; // [rsp+718h] [rbp+698h]
  __int64 v189; // [rsp+728h] [rbp+6A8h]
  __int64 (__fastcall *v190)(); // [rsp+730h] [rbp+6B0h] BYREF
  _QWORD *v191; // [rsp+738h] [rbp+6B8h]
  __int64 v192; // [rsp+740h] [rbp+6C0h]
  __int64 v193; // [rsp+748h] [rbp+6C8h]
  __int64 (__fastcall *v194)(); // [rsp+750h] [rbp+6D0h] BYREF
  _QWORD *v195; // [rsp+758h] [rbp+6D8h]
  __int64 v196; // [rsp+768h] [rbp+6E8h]
  __int64 (__fastcall *v197)(); // [rsp+770h] [rbp+6F0h] BYREF
  _QWORD *v198; // [rsp+778h] [rbp+6F8h]
  __int64 v199; // [rsp+788h] [rbp+708h]
  __int64 v200; // [rsp+790h] [rbp+710h]
  __int64 v201; // [rsp+798h] [rbp+718h]
  __int64 (__fastcall *v202)(); // [rsp+7A0h] [rbp+720h] BYREF
  _QWORD *v203; // [rsp+7A8h] [rbp+728h]
  __int64 v204; // [rsp+7B8h] [rbp+738h]
  __int64 (__fastcall *v205)(); // [rsp+7C0h] [rbp+740h] BYREF
  _QWORD *v206; // [rsp+7C8h] [rbp+748h]
  __int64 v207; // [rsp+7D0h] [rbp+750h]
  __int64 v208; // [rsp+7D8h] [rbp+758h]
  __int64 (__fastcall *v209)(); // [rsp+7E0h] [rbp+760h] BYREF
  _QWORD *v210; // [rsp+7E8h] [rbp+768h]
  __int64 v211; // [rsp+7F8h] [rbp+778h]
  __int64 (__fastcall *v212)(); // [rsp+800h] [rbp+780h] BYREF
  _QWORD *v213; // [rsp+808h] [rbp+788h]
  __int64 v214; // [rsp+810h] [rbp+790h]
  __int64 v215; // [rsp+818h] [rbp+798h]
  __int64 (__fastcall *v216)(); // [rsp+820h] [rbp+7A0h] BYREF
  _QWORD *v217; // [rsp+828h] [rbp+7A8h]
  __int64 v218; // [rsp+838h] [rbp+7B8h]
  __int64 (__fastcall *v219)(); // [rsp+840h] [rbp+7C0h] BYREF
  _QWORD *v220; // [rsp+848h] [rbp+7C8h]
  __int64 v221; // [rsp+850h] [rbp+7D0h]
  __int64 v222; // [rsp+858h] [rbp+7D8h]
  __int64 (__fastcall *v223)(); // [rsp+860h] [rbp+7E0h] BYREF
  _QWORD *v224; // [rsp+868h] [rbp+7E8h]
  __int64 v225; // [rsp+870h] [rbp+7F0h]
  __int64 v226; // [rsp+878h] [rbp+7F8h]
  __int64 v227; // [rsp+880h] [rbp+800h]
  __int64 v228; // [rsp+888h] [rbp+808h]
  __int64 (__fastcall *v229)(); // [rsp+890h] [rbp+810h] BYREF
  _QWORD *v230; // [rsp+898h] [rbp+818h]
  __int64 v231; // [rsp+8A0h] [rbp+820h]
  __int64 v232; // [rsp+8A8h] [rbp+828h]
  __int64 v233; // [rsp+8B0h] [rbp+830h]
  __int64 v234; // [rsp+8B8h] [rbp+838h]
  __int64 (__fastcall *v235)(); // [rsp+8C0h] [rbp+840h] BYREF
  _QWORD *v236; // [rsp+8C8h] [rbp+848h]
  __int64 v237; // [rsp+8D0h] [rbp+850h]
  __int64 v238; // [rsp+8D8h] [rbp+858h]
  __int64 v239; // [rsp+8E0h] [rbp+860h]
  __int64 v240; // [rsp+8E8h] [rbp+868h]
  __int64 (__fastcall *v241)(); // [rsp+8F0h] [rbp+870h] BYREF
  _QWORD *v242; // [rsp+8F8h] [rbp+878h]
  __int64 v243; // [rsp+900h] [rbp+880h]
  __int64 v244; // [rsp+908h] [rbp+888h]
  __int64 v245; // [rsp+910h] [rbp+890h]
  __int64 v246; // [rsp+918h] [rbp+898h]
  __int64 (__fastcall *v247)(); // [rsp+920h] [rbp+8A0h] BYREF
  _QWORD *v248; // [rsp+928h] [rbp+8A8h]
  __int64 v249; // [rsp+930h] [rbp+8B0h]
  __int64 v250; // [rsp+938h] [rbp+8B8h]
  __int64 v251; // [rsp+940h] [rbp+8C0h]
  __int64 v252; // [rsp+948h] [rbp+8C8h]
  __int64 (__fastcall *v253)(); // [rsp+950h] [rbp+8D0h] BYREF
  _QWORD *v254; // [rsp+958h] [rbp+8D8h]
  __int64 v255; // [rsp+960h] [rbp+8E0h]
  __int64 v256; // [rsp+968h] [rbp+8E8h]
  __int64 v257; // [rsp+970h] [rbp+8F0h]
  __int64 v258; // [rsp+978h] [rbp+8F8h]
  __int64 (__fastcall *v259)(); // [rsp+980h] [rbp+900h] BYREF
  _QWORD *v260; // [rsp+988h] [rbp+908h]
  __int64 v261; // [rsp+998h] [rbp+918h]
  __int64 v262; // [rsp+9A0h] [rbp+920h]
  __int64 v263; // [rsp+9A8h] [rbp+928h]
  __int64 (__fastcall *v264)(); // [rsp+9B0h] [rbp+930h] BYREF
  _QWORD *v265; // [rsp+9B8h] [rbp+938h]
  __int64 v266; // [rsp+9C8h] [rbp+948h]
  __int64 v267; // [rsp+9D0h] [rbp+950h]
  __int64 v268; // [rsp+9D8h] [rbp+958h]
  __int64 (__fastcall *v269)(); // [rsp+9E0h] [rbp+960h] BYREF
  _QWORD *v270; // [rsp+9E8h] [rbp+968h]
  __int64 v271; // [rsp+9F0h] [rbp+970h]
  __int64 v272; // [rsp+9F8h] [rbp+978h]
  __int64 v273; // [rsp+A00h] [rbp+980h]
  __int64 v274; // [rsp+A08h] [rbp+988h]
  __int64 (__fastcall *v275)(); // [rsp+A10h] [rbp+990h] BYREF
  _QWORD *v276; // [rsp+A18h] [rbp+998h]
  __int64 v277; // [rsp+A20h] [rbp+9A0h]
  __int64 v278; // [rsp+A28h] [rbp+9A8h]
  __int64 v279; // [rsp+A30h] [rbp+9B0h]
  __int64 v280; // [rsp+A38h] [rbp+9B8h]
  __int64 (__fastcall *v281)(); // [rsp+A40h] [rbp+9C0h] BYREF
  _QWORD *v282; // [rsp+A48h] [rbp+9C8h]
  __int64 v283; // [rsp+A58h] [rbp+9D8h]
  __int64 v284; // [rsp+A60h] [rbp+9E0h]
  __int64 v285; // [rsp+A68h] [rbp+9E8h]
  __int64 (__fastcall *v286)(); // [rsp+A70h] [rbp+9F0h] BYREF
  _QWORD *v287; // [rsp+A78h] [rbp+9F8h]
  __int64 v288; // [rsp+A88h] [rbp+A08h]
  __int64 v289; // [rsp+A90h] [rbp+A10h]
  __int64 v290; // [rsp+A98h] [rbp+A18h]
  __int64 (__fastcall *v291)(); // [rsp+AA0h] [rbp+A20h] BYREF
  _QWORD *v292; // [rsp+AA8h] [rbp+A28h]
  __int64 v293; // [rsp+AB8h] [rbp+A38h]
  __int64 v294; // [rsp+AC0h] [rbp+A40h]
  __int64 v295; // [rsp+AC8h] [rbp+A48h]
  __int64 (__fastcall *v296)(); // [rsp+AD0h] [rbp+A50h] BYREF
  _QWORD *v297; // [rsp+AD8h] [rbp+A58h]
  __int64 v298; // [rsp+AE0h] [rbp+A60h]
  __int64 v299; // [rsp+AE8h] [rbp+A68h]
  __int64 v300; // [rsp+AF0h] [rbp+A70h]
  __int64 v301; // [rsp+AF8h] [rbp+A78h]
  __int64 (__fastcall *v302)(); // [rsp+B00h] [rbp+A80h] BYREF
  _QWORD *v303; // [rsp+B08h] [rbp+A88h]
  __int64 v304; // [rsp+B18h] [rbp+A98h]
  __int64 (__fastcall *v305)(); // [rsp+B20h] [rbp+AA0h] BYREF
  _QWORD *v306; // [rsp+B28h] [rbp+AA8h]
  __int64 v307; // [rsp+B30h] [rbp+AB0h]
  _QWORD *v308; // [rsp+B38h] [rbp+AB8h]
  __int64 v309; // [rsp+B40h] [rbp+AC0h]
  _QWORD *v310; // [rsp+B48h] [rbp+AC8h]
  __int64 v311; // [rsp+B50h] [rbp+AD0h]
  _QWORD *v312; // [rsp+B58h] [rbp+AD8h]
  __int64 v313[2]; // [rsp+B60h] [rbp+AE0h] BYREF
  __int64 v314; // [rsp+B70h] [rbp+AF0h]
  __int64 v315; // [rsp+B80h] [rbp+B00h]
  _QWORD *v316; // [rsp+B88h] [rbp+B08h]
  __int64 v317; // [rsp+B98h] [rbp+B18h]
  __int64 (__fastcall *v318)(); // [rsp+BA0h] [rbp+B20h] BYREF
  _QWORD *v319; // [rsp+BA8h] [rbp+B28h]
  __int64 v320; // [rsp+BB8h] [rbp+B38h]
  __int64 (__fastcall *v321)(); // [rsp+BC0h] [rbp+B40h] BYREF
  _QWORD *v322; // [rsp+BC8h] [rbp+B48h]
  char v323[16]; // [rsp+BD0h] [rbp+B50h] BYREF
  __int64 v324; // [rsp+BE0h] [rbp+B60h]
  __int64 v325; // [rsp+BF0h] [rbp+B70h] BYREF
  _QWORD *v326; // [rsp+BF8h] [rbp+B78h]
  __int64 v327; // [rsp+C00h] [rbp+B80h] BYREF
  _QWORD *v328; // [rsp+C08h] [rbp+B88h]
  __int64 v329; // [rsp+C10h] [rbp+B90h] BYREF
  _QWORD *v330; // [rsp+C18h] [rbp+B98h]
  __int64 v331; // [rsp+C20h] [rbp+BA0h] BYREF
  _QWORD *v332; // [rsp+C28h] [rbp+BA8h]
  __int64 v333; // [rsp+C30h] [rbp+BB0h] BYREF
  _QWORD *v334; // [rsp+C38h] [rbp+BB8h]
  __int64 v335; // [rsp+C48h] [rbp+BC8h]
  __int64 (__fastcall *v336)(); // [rsp+C50h] [rbp+BD0h] BYREF
  _QWORD *v337; // [rsp+C58h] [rbp+BD8h]
  __int64 v338; // [rsp+C68h] [rbp+BE8h]
  char v339[8]; // [rsp+C70h] [rbp+BF0h] BYREF
  const char *v340; // [rsp+C78h] [rbp+BF8h]
  __int64 v341; // [rsp+C80h] [rbp+C00h]
  const char *v342; // [rsp+C88h] [rbp+C08h]
  __int16 v343; // [rsp+C90h] [rbp+C10h]
  __int64 v344; // [rsp+CA8h] [rbp+C28h]
  unsigned __int8 v345[40]; // [rsp+CB0h] [rbp+C30h] BYREF
  __int64 v346; // [rsp+CD8h] [rbp+C58h]
  __int64 v347; // [rsp+D80h] [rbp+D00h]
  _QWORD *v348; // [rsp+D88h] [rbp+D08h]
  __int64 v349; // [rsp+D90h] [rbp+D10h]
  __int64 clamped_word_size__modelZboardZprototype95list_u4458; // [rsp+EE8h] [rbp+E68h] BYREF
  char v351; // [rsp+EF7h] [rbp+E77h]
  __int64 v352; // [rsp+EF8h] [rbp+E78h]
  _QWORD *v353; // [rsp+F00h] [rbp+E80h]
  _QWORD *v354; // [rsp+F08h] [rbp+E88h]
  char *v355; // [rsp+F10h] [rbp+E90h]
  char v356; // [rsp+F1Fh] [rbp+E9Fh]

  v5 = *a2;
  v6 = a2[1];
  v23 = v5;
  v24 = (_QWORD *)v6;
  v7 = a3[1];
  v21 = *a3;
  v22 = (_QWORD *)v7;
  v340 = "infer_size";
  v342 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v341 = 0i64;
  v343 = 0;
  nimFrame_80(v339);
  v355 = (char *)nimErrorFlag_78();
  nimZeroMem_60(&clamped_word_size__modelZboardZprototype95list_u4458, 8i64);
  v354 = 0i64;
  nimZeroMem_60(v345, 560i64);
  v341 = 74i64;
  v342 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v353 = 0i64;
  v353 = (_QWORD *)nimNewObj(48i64, 8i64);
  *v353 = &NTIv2__RCNO29bRwaiedrX59choMGCg_;
  v354 = v353;
  v341 = 73i64;
  v19 = v23;
  v20 = v24;
  eqcopy___modelZsimulationZpreorder_u2050(v353 + 3, &v19);
  v19 = v21;
  v20 = v22;
  eqcopy___modelZsimulationZpreorder_u2177(v354 + 1, &v19);
  v354[5] = a4;
  v341 = 34i64;
  v342 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
  if ( (__int64)v354[5] < 0 || v354[5] >= *a1 )
  {
    raiseIndexError2(v354[5], *a1 - 1i64);
    goto LABEL_524;
  }
  eqcopy___modelZsave95mongerZversionsZv0_u148(v345, a1[1] + 560i64 * v354[5] + 8);
  v342 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v344 = a5;
  v341 = 87i64;
  v356 = 0;
  v8 = v345[0] == 114
    || v345[0] == 115
    || v345[0] == 116
    || v345[0] == 94
    || v345[0] == 117
    || v345[0] == 50
    || v345[0] == 119
    || v345[0] == 81;
  v356 = v8;
  if ( !v8 )
    v356 = eqeq___modelZmodel95types_u853(v349, *(_QWORD *)refptr_AUTO_SIZE__modelZmodel95types_u54);
  if ( v356 != 1 )
  {
LABEL_523:
    v341 = 207i64;
    clamped_word_size__modelZboardZprototype95list_u4458 = get_clamped_word_size__modelZboardZprototype95list_u4458(
                                                             v345[0],
                                                             v344,
                                                             0);
    goto LABEL_524;
  }
  v341 = 88i64;
  switch ( v345[0] )
  {
    case 0x12u:
      v341 = 148i64;
      nimZeroMem_60(&v154, 16i64);
      v154 = input_size__modelZsimulationZpreorder_u2007;
      v155 = v354;
      if ( v354 )
        v344 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v154)(0i64, v155);
      else
        v344 = ((__int64 (__fastcall *)(_QWORD))v154)(0i64);
      if ( !*v355 )
        goto LABEL_523;
      goto LABEL_524;
    case 0x13u:
      v341 = 150i64;
      nimZeroMem_60(&v152, 16i64);
      v152 = input_size__modelZsimulationZpreorder_u2007;
      v153 = v354;
      if ( v354 )
        v151 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v152)(0i64, v153);
      else
        v151 = ((__int64 (__fastcall *)(_QWORD))v152)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v149, 16i64);
        v149 = input_size__modelZsimulationZpreorder_u2007;
        v150 = v354;
        v148 = v354
             ? ((__int64 (__fastcall *)(__int64, _QWORD *))v149)(1i64, v150)
             : ((__int64 (__fastcall *)(__int64))v149)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v151, v148);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x14u:
      v341 = 152i64;
      nimZeroMem_60(&v146, 16i64);
      v146 = input_size__modelZsimulationZpreorder_u2007;
      v147 = v354;
      if ( v354 )
        v145 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v146)(0i64, v147);
      else
        v145 = ((__int64 (__fastcall *)(_QWORD))v146)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v143, 16i64);
        v143 = input_size__modelZsimulationZpreorder_u2007;
        v144 = v354;
        v142 = v354
             ? ((__int64 (__fastcall *)(__int64, _QWORD *))v143)(1i64, v144)
             : ((__int64 (__fastcall *)(__int64))v143)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v145, v142);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x15u:
      v341 = 154i64;
      nimZeroMem_60(&v140, 16i64);
      v140 = input_size__modelZsimulationZpreorder_u2007;
      v141 = v354;
      if ( v354 )
        v139 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v140)(0i64, v141);
      else
        v139 = ((__int64 (__fastcall *)(_QWORD))v140)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v137, 16i64);
        v137 = input_size__modelZsimulationZpreorder_u2007;
        v138 = v354;
        v136 = v354
             ? ((__int64 (__fastcall *)(__int64, _QWORD *))v137)(1i64, v138)
             : ((__int64 (__fastcall *)(__int64))v137)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v139, v136);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x16u:
      v341 = 156i64;
      nimZeroMem_60(&v134, 16i64);
      v134 = input_size__modelZsimulationZpreorder_u2007;
      v135 = v354;
      if ( v354 )
        v133 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v134)(0i64, v135);
      else
        v133 = ((__int64 (__fastcall *)(_QWORD))v134)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v131, 16i64);
        v131 = input_size__modelZsimulationZpreorder_u2007;
        v132 = v354;
        v130 = v354
             ? ((__int64 (__fastcall *)(__int64, _QWORD *))v131)(1i64, v132)
             : ((__int64 (__fastcall *)(__int64))v131)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v133, v130);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x17u:
      v341 = 158i64;
      nimZeroMem_60(&v128, 16i64);
      v128 = input_size__modelZsimulationZpreorder_u2007;
      v129 = v354;
      if ( v354 )
        v127 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v128)(0i64, v129);
      else
        v127 = ((__int64 (__fastcall *)(_QWORD))v128)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v125, 16i64);
        v125 = input_size__modelZsimulationZpreorder_u2007;
        v126 = v354;
        v124 = v354
             ? ((__int64 (__fastcall *)(__int64, _QWORD *))v125)(1i64, v126)
             : ((__int64 (__fastcall *)(__int64))v125)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v127, v124);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x18u:
      v341 = 160i64;
      nimZeroMem_60(&v122, 16i64);
      v122 = input_size__modelZsimulationZpreorder_u2007;
      v123 = v354;
      if ( v354 )
        v121 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v122)(0i64, v123);
      else
        v121 = ((__int64 (__fastcall *)(_QWORD))v122)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v119, 16i64);
        v119 = input_size__modelZsimulationZpreorder_u2007;
        v120 = v354;
        v118 = v354
             ? ((__int64 (__fastcall *)(__int64, _QWORD *))v119)(1i64, v120)
             : ((__int64 (__fastcall *)(__int64))v119)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v121, v118);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x19u:
      v341 = 192i64;
      nimZeroMem_60(&v34, 16i64);
      v34 = input_size__modelZsimulationZpreorder_u2007;
      v35 = v354;
      if ( v354 )
        v344 = ((__int64 (__fastcall *)(__int64, _QWORD *))v34)(1i64, v35);
      else
        v344 = ((__int64 (__fastcall *)(__int64))v34)(1i64);
      if ( !*v355 )
        goto LABEL_523;
      goto LABEL_524;
    case 0x1Au:
      v341 = 162i64;
      nimZeroMem_60(&v116, 16i64);
      v116 = input_size__modelZsimulationZpreorder_u2007;
      v117 = v354;
      if ( v354 )
        v115 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v116)(0i64, v117);
      else
        v115 = ((__int64 (__fastcall *)(_QWORD))v116)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v113, 16i64);
        v113 = input_size__modelZsimulationZpreorder_u2007;
        v114 = v354;
        v112 = v354
             ? ((__int64 (__fastcall *)(__int64, _QWORD *))v113)(1i64, v114)
             : ((__int64 (__fastcall *)(__int64))v113)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v115, v112);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x1Bu:
      v341 = 164i64;
      nimZeroMem_60(&v110, 16i64);
      v110 = input_size__modelZsimulationZpreorder_u2007;
      v111 = v354;
      if ( v354 )
        v109 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v110)(0i64, v111);
      else
        v109 = ((__int64 (__fastcall *)(_QWORD))v110)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v107, 16i64);
        v107 = input_size__modelZsimulationZpreorder_u2007;
        v108 = v354;
        v106 = v354
             ? ((__int64 (__fastcall *)(__int64, _QWORD *))v107)(1i64, v108)
             : ((__int64 (__fastcall *)(__int64))v107)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v109, v106);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x1Cu:
      v341 = 166i64;
      nimZeroMem_60(&v104, 16i64);
      v104 = input_size__modelZsimulationZpreorder_u2007;
      v105 = v354;
      if ( v354 )
        v103 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v104)(0i64, v105);
      else
        v103 = ((__int64 (__fastcall *)(_QWORD))v104)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v101, 16i64);
        v101 = input_size__modelZsimulationZpreorder_u2007;
        v102 = v354;
        v100 = v354
             ? ((__int64 (__fastcall *)(__int64, _QWORD *))v101)(1i64, v102)
             : ((__int64 (__fastcall *)(__int64))v101)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v103, v100);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x1Du:
      v341 = 168i64;
      nimZeroMem_60(&v98, 16i64);
      v98 = input_size__modelZsimulationZpreorder_u2007;
      v99 = v354;
      if ( v354 )
        v344 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v98)(0i64, v99);
      else
        v344 = ((__int64 (__fastcall *)(_QWORD))v98)(0i64);
      if ( !*v355 )
        goto LABEL_523;
      goto LABEL_524;
    case 0x1Eu:
      v341 = 172i64;
      nimZeroMem_60(&v94, 16i64);
      v94 = input_size__modelZsimulationZpreorder_u2007;
      v95 = v354;
      if ( v354 )
        v93 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v94)(0i64, v95);
      else
        v93 = ((__int64 (__fastcall *)(_QWORD))v94)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v91, 16i64);
        v91 = input_size__modelZsimulationZpreorder_u2007;
        v92 = v354;
        v90 = v354
            ? ((__int64 (__fastcall *)(__int64, _QWORD *))v91)(1i64, v92)
            : ((__int64 (__fastcall *)(__int64))v91)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v93, v90);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x1Fu:
      v341 = 174i64;
      nimZeroMem_60(&v88, 16i64);
      v88 = input_size__modelZsimulationZpreorder_u2007;
      v89 = v354;
      if ( v354 )
        v87 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v88)(0i64, v89);
      else
        v87 = ((__int64 (__fastcall *)(_QWORD))v88)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v85, 16i64);
        v85 = input_size__modelZsimulationZpreorder_u2007;
        v86 = v354;
        v84 = v354
            ? ((__int64 (__fastcall *)(__int64, _QWORD *))v85)(1i64, v86)
            : ((__int64 (__fastcall *)(__int64))v85)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v87, v84);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x20u:
      v341 = 176i64;
      nimZeroMem_60(&v82, 16i64);
      v82 = input_size__modelZsimulationZpreorder_u2007;
      v83 = v354;
      if ( v354 )
        v81 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v82)(0i64, v83);
      else
        v81 = ((__int64 (__fastcall *)(_QWORD))v82)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v79, 16i64);
        v79 = input_size__modelZsimulationZpreorder_u2007;
        v80 = v354;
        v78 = v354
            ? ((__int64 (__fastcall *)(__int64, _QWORD *))v79)(1i64, v80)
            : ((__int64 (__fastcall *)(__int64))v79)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v81, v78);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x21u:
      v341 = 180i64;
      nimZeroMem_60(&v70, 16i64);
      v70 = input_size__modelZsimulationZpreorder_u2007;
      v71 = v354;
      if ( v354 )
        v69 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v70)(0i64, v71);
      else
        v69 = ((__int64 (__fastcall *)(_QWORD))v70)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v67, 16i64);
        v67 = input_size__modelZsimulationZpreorder_u2007;
        v68 = v354;
        v66 = v354
            ? ((__int64 (__fastcall *)(__int64, _QWORD *))v67)(1i64, v68)
            : ((__int64 (__fastcall *)(__int64))v67)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v69, v66);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x22u:
      v341 = 182i64;
      nimZeroMem_60(&v64, 16i64);
      v64 = input_size__modelZsimulationZpreorder_u2007;
      v65 = v354;
      if ( v354 )
        v63 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v64)(0i64, v65);
      else
        v63 = ((__int64 (__fastcall *)(_QWORD))v64)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v61, 16i64);
        v61 = input_size__modelZsimulationZpreorder_u2007;
        v62 = v354;
        v60 = v354
            ? ((__int64 (__fastcall *)(__int64, _QWORD *))v61)(1i64, v62)
            : ((__int64 (__fastcall *)(__int64))v61)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v63, v60);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x23u:
      v341 = 186i64;
      nimZeroMem_60(&v52, 16i64);
      v52 = input_size__modelZsimulationZpreorder_u2007;
      v53 = v354;
      if ( v354 )
        v51 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v52)(0i64, v53);
      else
        v51 = ((__int64 (__fastcall *)(_QWORD))v52)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v49, 16i64);
        v49 = input_size__modelZsimulationZpreorder_u2007;
        v50 = v354;
        v48 = v354
            ? ((__int64 (__fastcall *)(__int64, _QWORD *))v49)(1i64, v50)
            : ((__int64 (__fastcall *)(__int64))v49)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v51, v48);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x24u:
      v341 = 188i64;
      nimZeroMem_60(&v46, 16i64);
      v46 = input_size__modelZsimulationZpreorder_u2007;
      v47 = v354;
      if ( v354 )
        v45 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v46)(0i64, v47);
      else
        v45 = ((__int64 (__fastcall *)(_QWORD))v46)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v43, 16i64);
        v43 = input_size__modelZsimulationZpreorder_u2007;
        v44 = v354;
        v42 = v354
            ? ((__int64 (__fastcall *)(__int64, _QWORD *))v43)(1i64, v44)
            : ((__int64 (__fastcall *)(__int64))v43)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v45, v42);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x25u:
      v341 = 184i64;
      nimZeroMem_60(&v58, 16i64);
      v58 = input_size__modelZsimulationZpreorder_u2007;
      v59 = v354;
      if ( v354 )
        v57 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v58)(0i64, v59);
      else
        v57 = ((__int64 (__fastcall *)(_QWORD))v58)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v55, 16i64);
        v55 = input_size__modelZsimulationZpreorder_u2007;
        v56 = v354;
        v54 = v354
            ? ((__int64 (__fastcall *)(__int64, _QWORD *))v55)(1i64, v56)
            : ((__int64 (__fastcall *)(__int64))v55)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v57, v54);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x2Au:
      v341 = 190i64;
      nimZeroMem_60(&v40, 16i64);
      v40 = input_size__modelZsimulationZpreorder_u2007;
      v41 = v354;
      if ( v354 )
        v39 = ((__int64 (__fastcall *)(__int64, _QWORD *))v40)(1i64, v41);
      else
        v39 = ((__int64 (__fastcall *)(__int64))v40)(1i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v37, 16i64);
        v37 = input_size__modelZsimulationZpreorder_u2007;
        v38 = v354;
        v36 = v354
            ? ((__int64 (__fastcall *)(__int64, _QWORD *))v37)(2i64, v38)
            : ((__int64 (__fastcall *)(__int64))v37)(2i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v39, v36);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x2Fu:
      v341 = 142i64;
      nimZeroMem_60(&v166, 16i64);
      v166 = input_size__modelZsimulationZpreorder_u2007;
      v167 = v354;
      if ( v354 )
        v165 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v166)(0i64, v167);
      else
        v165 = ((__int64 (__fastcall *)(_QWORD))v166)(0i64);
      if ( !*v355 )
      {
        v164 = plus___modelZsave95mongerZcommon_u202(v165, 1i64);
        if ( !*v355 )
        {
          v344 = div__modelZsave95mongerZcommon_u217(v164, 2i64);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x30u:
      v341 = 131i64;
      nimZeroMem_60(&v219, 16i64);
      v219 = input_size__modelZsimulationZpreorder_u2007;
      v220 = v354;
      if ( v354 )
        v218 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v219)(0i64, v220);
      else
        v218 = ((__int64 (__fastcall *)(_QWORD))v219)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v216, 16i64);
        v216 = input_size__modelZsimulationZpreorder_u2007;
        v217 = v354;
        v215 = v354
             ? ((__int64 (__fastcall *)(__int64, _QWORD *))v216)(1i64, v217)
             : ((__int64 (__fastcall *)(__int64))v216)(1i64);
        if ( !*v355 )
        {
          v214 = max__modelZsave95mongerZcommon_u225(v218, v215);
          if ( !*v355 )
          {
            v344 = star___modelZsave95mongerZcommon_u213(v214, 2i64);
            if ( !*v355 )
              goto LABEL_523;
          }
        }
      }
      goto LABEL_524;
    case 0x31u:
      v341 = 194i64;
      nimZeroMem_60(&v32, 16i64);
      v32 = input_size__modelZsimulationZpreorder_u2007;
      v33 = v354;
      if ( v354 )
        v344 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v32)(0i64, v33);
      else
        v344 = ((__int64 (__fastcall *)(_QWORD))v32)(0i64);
      if ( !*v355 )
        goto LABEL_523;
      goto LABEL_524;
    case 0x32u:
    case 0x77u:
      v341 = 200i64;
      if ( v345[32] != 1 )
      {
        v341 = 203i64;
        nimZeroMem_60(&v26, 16i64);
        v26 = input_size__modelZsimulationZpreorder_u2007;
        v27 = v354;
        if ( v354 )
          v344 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v26)(0i64, v27);
        else
          v344 = ((__int64 (__fastcall *)(_QWORD))v26)(0i64);
        if ( *v355 )
          goto LABEL_524;
      }
      else
      {
        v341 = 201i64;
        if ( v346 < 0 || v346 >= *a1 )
        {
          raiseIndexError2(v346, *a1 - 1i64);
          goto LABEL_524;
        }
        v344 = *(_QWORD *)(a1[1] + 560 * v346 + 240);
      }
      goto LABEL_523;
    case 0x39u:
      v341 = 196i64;
      nimZeroMem_60(&v30, 16i64);
      v30 = input_size__modelZsimulationZpreorder_u2007;
      v31 = v354;
      if ( v354 )
        v344 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v30)(0i64, v31);
      else
        v344 = ((__int64 (__fastcall *)(_QWORD))v30)(0i64);
      if ( !*v355 )
        goto LABEL_523;
      goto LABEL_524;
    case 0x4Fu:
      v341 = 116i64;
      v344 = bits__modelZsave95mongerZcommon_u192(8i64);
      if ( !*v355 )
        goto LABEL_523;
      goto LABEL_524;
    case 0x50u:
      v341 = 198i64;
      nimZeroMem_60(&v28, 16i64);
      v28 = input_size__modelZsimulationZpreorder_u2007;
      v29 = v354;
      if ( v354 )
        v344 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v28)(0i64, v29);
      else
        v344 = ((__int64 (__fastcall *)(_QWORD))v28)(0i64);
      if ( !*v355 )
        goto LABEL_523;
      goto LABEL_524;
    case 0x51u:
    case 0x60u:
      v341 = 90i64;
      v338 = bits__modelZsave95mongerZcommon_u192(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v336, 16i64);
        v336 = input_size__modelZsimulationZpreorder_u2007;
        v337 = v354;
        v335 = v354
             ? ((__int64 (__fastcall *)(_QWORD, _QWORD *))v336)(0i64, v337)
             : ((__int64 (__fastcall *)(_QWORD))v336)(0i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v338, v335);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x55u:
      v341 = 114i64;
      v342 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      nimZeroMem_60(&v305, 16i64);
      v305 = input_size__modelZsimulationZpreorder_u2007;
      v306 = v354;
      if ( v354 )
        v344 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v305)(0i64, v306);
      else
        v344 = ((__int64 (__fastcall *)(_QWORD))v305)(0i64);
      if ( !*v355 )
        goto LABEL_523;
      goto LABEL_524;
    case 0x5Eu:
      v333 = 0i64;
      v334 = 0i64;
      v331 = 0i64;
      v332 = 0i64;
      v329 = 0i64;
      v330 = 0i64;
      v327 = 0i64;
      v328 = 0i64;
      nimZeroMem_60(v25, 32i64);
      v325 = 0i64;
      v326 = 0i64;
      nimZeroMem_60(v323, 24i64);
      v341 = 92i64;
      nimZeroMem_60(&v321, 16i64);
      v321 = input_size__modelZsimulationZpreorder_u2007;
      v322 = v354;
      if ( v354 )
        v320 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v321)(0i64, v322);
      else
        v320 = ((__int64 (__fastcall *)(_QWORD))v321)(0i64);
      if ( *v355 )
        goto LABEL_66;
      dollar___modelZsave95mongerZcommon_u260(&v331, v320);
      if ( *v355 )
        goto LABEL_66;
      v19 = v347;
      v20 = v348;
      v17 = TM__8dO79bDlK9csFzRs49cEE7wlw_73;
      v18 = &TM__8dO79bDlK9csFzRs49cEE7wlw_72;
      v15 = v331;
      v16 = v332;
      nsuReplaceStr(&v329, &v19, &v17, &v15);
      if ( *v355 )
        goto LABEL_66;
      v341 = 93i64;
      nimZeroMem_60(&v318, 16i64);
      v318 = input_size__modelZsimulationZpreorder_u2007;
      v319 = v354;
      v317 = v354
           ? ((__int64 (__fastcall *)(__int64, _QWORD *))v318)(1i64, v319)
           : ((__int64 (__fastcall *)(__int64))v318)(1i64);
      if ( *v355 )
        goto LABEL_66;
      dollar___modelZsave95mongerZcommon_u260(&v327, v317);
      if ( *v355 )
        goto LABEL_66;
      v341 = 92i64;
      v19 = v329;
      v20 = v330;
      v17 = TM__8dO79bDlK9csFzRs49cEE7wlw_76;
      v18 = &TM__8dO79bDlK9csFzRs49cEE7wlw_75;
      v15 = v327;
      v16 = v328;
      nsuReplaceStr(&v333, &v19, &v17, &v15);
      if ( *v355 )
        goto LABEL_66;
      v341 = 95i64;
      v19 = v333;
      v20 = v334;
      new_stream_slice__modelZisa95specZparse_u92(&v19, 0i64, v25);
      if ( *v355 )
        goto LABEL_66;
      v341 = 97i64;
      get_expression__modelZisa95specZexpressions_u2143(v25, &v325, v323);
      if ( *v355 )
        goto LABEL_66;
      v341 = 98i64;
      if ( !v324 )
      {
        v341 = 119i64;
        v342 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
        if ( (__int64)v354[5] < 0 || v354[5] >= *a1 )
        {
          raiseIndexError2(v354[5], *a1 - 1i64);
          goto LABEL_66;
        }
        v341 = 99i64;
        v342 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        v316 = 0i64;
        v315 = 1i64;
        v316 = (_QWORD *)newSeqPayload(1i64, 8i64, 8i64);
        v316[1] = 0i64;
        v341 = 119i64;
        v342 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
        v9 = a1[1] + 560i64 * v354[5] + 160 + 16;
        v19 = v315;
        v20 = v316;
        eqsink___modelZsave95mongerZserialize_u464(v9, &v19);
        goto LABEL_60;
      }
      nimZeroMem_60(v313, 24i64);
      v341 = 101i64;
      v342 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      v312 = 0i64;
      v311 = 0i64;
      v312 = (_QWORD *)newSeqPayload(0i64, 8i64, 8i64);
      v19 = v311;
      v20 = v312;
      eval__modelZisa95specZexpressions_u2199((unsigned int)v14, v324, (unsigned int)&v19, 0, 0i64);
      v313[0] = v14[0];
      v313[1] = v14[1];
      v314 = v14[2];
      if ( *v355 )
        goto LABEL_59;
      v341 = 102i64;
      if ( v313[0] )
      {
        if ( (__int64)v354[5] < 0 || v354[5] >= *a1 )
          goto LABEL_48;
        v341 = 111i64;
        v342 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        v308 = 0i64;
        v307 = 1i64;
        v308 = (_QWORD *)newSeqPayload(1i64, 8i64, 8i64);
        v308[1] = 0i64;
        v341 = 119i64;
        v342 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
        v12 = a1[1] + 560i64 * v354[5] + 160 + 16;
        v19 = v307;
        v20 = v308;
        eqsink___modelZsave95mongerZserialize_u464(v12, &v19);
      }
      else
      {
        v352 = 0i64;
        v341 = 119i64;
        v342 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
        if ( (__int64)v354[5] < 0 || v354[5] >= *a1 )
        {
LABEL_48:
          raiseIndexError2(v354[5], *a1 - 1i64);
          goto LABEL_59;
        }
        v341 = 104i64;
        v342 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        v310 = 0i64;
        v309 = 1i64;
        v310 = (_QWORD *)newSeqPayload(1i64, 8i64, 8i64);
        v341 = 107i64;
        if ( v314 < -2047 )
        {
          v10 = -2048i64;
        }
        else if ( v314 > 2047 )
        {
          v10 = 2048i64;
        }
        else
        {
          v10 = v314;
        }
        v352 = v10;
        v310[1] = v10;
        v341 = 119i64;
        v342 = "D:\\TuringComplete_Phu\\model\\save_monger\\serialize.nim";
        v11 = a1[1] + 560i64 * v354[5] + 160 + 16;
        v19 = v309;
        v20 = v310;
        eqsink___modelZsave95mongerZserialize_u464(v11, &v19);
      }
LABEL_59:
      v341 = 459i64;
      v342 = "D:\\TuringComplete_Phu\\model\\isa_spec\\parse.nim";
      eqdestroy___modelZisa95specZparse_u1467(v313);
      if ( *v355 )
        goto LABEL_66;
LABEL_60:
      v341 = 112i64;
      v342 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      if ( (__int64)v354[5] >= 0 && v354[5] < *a1 )
      {
        if ( *(__int64 *)(a1[1] + 560i64 * v354[5] + 176) > 0 )
          v344 = bits__modelZsave95mongerZcommon_u192(*(_QWORD *)(*(_QWORD *)(a1[1] + 560i64 * v354[5] + 184) + 8i64));
        else
          raiseIndexError2(0i64, *(_QWORD *)(a1[1] + 560i64 * v354[5] + 176) - 1i64);
      }
      else
      {
        raiseIndexError2(v354[5], *a1 - 1i64);
      }
LABEL_66:
      v351 = *v355;
      *v355 = 0;
      v341 = 336i64;
      v342 = "D:\\TuringComplete_Phu\\model\\isa_spec\\expressions.nim";
      eqdestroy___modelZisa95specZexpressions_u1546(v323);
      if ( !*v355 )
      {
        v341 = 2128i64;
        v342 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        v19 = v325;
        v20 = v326;
        eqdestroy___system_u3734(&v19);
        v341 = 71i64;
        v342 = "D:\\TuringComplete_Phu\\model\\isa_spec\\parse.nim";
        eqdestroy___modelZisa95specZparse_u272(v25);
        v341 = 394i64;
        v342 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v328 && (*v328 & 0x4000000000000000i64) == 0 )
          deallocShared(v328);
        if ( v330 && (*v330 & 0x4000000000000000i64) == 0 )
          deallocShared(v330);
        if ( v332 && (*v332 & 0x4000000000000000i64) == 0 )
          deallocShared(v332);
        if ( v334 && (*v334 & 0x4000000000000000i64) == 0 )
          deallocShared(v334);
        *v355 = v351;
        if ( !*v355 )
          goto LABEL_523;
      }
LABEL_524:
      v341 = 34i64;
      v342 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      eqdestroy___modelZsave95mongerZversionsZv0_u145(v345);
      v341 = 73i64;
      v342 = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      eqdestroy___modelZsimulationZpreorder_u32444(v354);
      popFrame_80();
      return clamped_word_size__modelZboardZprototype95list_u4458;
    case 0x61u:
      v341 = 134i64;
      nimZeroMem_60(&v212, 16i64);
      v212 = input_size__modelZsimulationZpreorder_u2007;
      v213 = v354;
      if ( v354 )
        v211 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v212)(0i64, v213);
      else
        v211 = ((__int64 (__fastcall *)(_QWORD))v212)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v209, 16i64);
        v209 = input_size__modelZsimulationZpreorder_u2007;
        v210 = v354;
        v208 = v354
             ? ((__int64 (__fastcall *)(__int64, _QWORD *))v209)(1i64, v210)
             : ((__int64 (__fastcall *)(__int64))v209)(1i64);
        if ( !*v355 )
        {
          v207 = max__modelZsave95mongerZcommon_u225(v211, v208);
          if ( !*v355 )
          {
            nimZeroMem_60(&v205, 16i64);
            v205 = input_size__modelZsimulationZpreorder_u2007;
            v206 = v354;
            v204 = v354
                 ? ((__int64 (__fastcall *)(__int64, _QWORD *))v205)(2i64, v206)
                 : ((__int64 (__fastcall *)(__int64))v205)(2i64);
            if ( !*v355 )
            {
              nimZeroMem_60(&v202, 16i64);
              v202 = input_size__modelZsimulationZpreorder_u2007;
              v203 = v354;
              v201 = v354
                   ? ((__int64 (__fastcall *)(__int64, _QWORD *))v202)(3i64, v203)
                   : ((__int64 (__fastcall *)(__int64))v202)(3i64);
              if ( !*v355 )
              {
                v200 = max__modelZsave95mongerZcommon_u225(v204, v201);
                if ( !*v355 )
                {
                  v199 = max__modelZsave95mongerZcommon_u225(v207, v200);
                  if ( !*v355 )
                  {
                    v344 = star___modelZsave95mongerZcommon_u213(v199, 4i64);
                    if ( !*v355 )
                      goto LABEL_523;
                  }
                }
              }
            }
          }
        }
      }
      goto LABEL_524;
    case 0x62u:
      v341 = 138i64;
      nimZeroMem_60(&v197, 16i64);
      v197 = input_size__modelZsimulationZpreorder_u2007;
      v198 = v354;
      if ( v354 )
        v196 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v197)(0i64, v198);
      else
        v196 = ((__int64 (__fastcall *)(_QWORD))v197)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v194, 16i64);
        v194 = input_size__modelZsimulationZpreorder_u2007;
        v195 = v354;
        v193 = v354
             ? ((__int64 (__fastcall *)(__int64, _QWORD *))v194)(1i64, v195)
             : ((__int64 (__fastcall *)(__int64))v194)(1i64);
        if ( !*v355 )
        {
          v192 = max__modelZsave95mongerZcommon_u225(v196, v193);
          if ( !*v355 )
          {
            nimZeroMem_60(&v190, 16i64);
            v190 = input_size__modelZsimulationZpreorder_u2007;
            v191 = v354;
            v189 = v354
                 ? ((__int64 (__fastcall *)(__int64, _QWORD *))v190)(2i64, v191)
                 : ((__int64 (__fastcall *)(__int64))v190)(2i64);
            if ( !*v355 )
            {
              nimZeroMem_60(&v187, 16i64);
              v187 = input_size__modelZsimulationZpreorder_u2007;
              v188 = v354;
              v186 = v354
                   ? ((__int64 (__fastcall *)(__int64, _QWORD *))v187)(3i64, v188)
                   : ((__int64 (__fastcall *)(__int64))v187)(3i64);
              if ( !*v355 )
              {
                v185 = max__modelZsave95mongerZcommon_u225(v189, v186);
                if ( !*v355 )
                {
                  v184 = max__modelZsave95mongerZcommon_u225(v192, v185);
                  if ( !*v355 )
                  {
                    v341 = 139i64;
                    nimZeroMem_60(&v182, 16i64);
                    v182 = input_size__modelZsimulationZpreorder_u2007;
                    v183 = v354;
                    v181 = v354
                         ? ((__int64 (__fastcall *)(__int64, _QWORD *))v182)(4i64, v183)
                         : ((__int64 (__fastcall *)(__int64))v182)(4i64);
                    if ( !*v355 )
                    {
                      nimZeroMem_60(&v179, 16i64);
                      v179 = input_size__modelZsimulationZpreorder_u2007;
                      v180 = v354;
                      v178 = v354
                           ? ((__int64 (__fastcall *)(__int64, _QWORD *))v179)(5i64, v180)
                           : ((__int64 (__fastcall *)(__int64))v179)(5i64);
                      if ( !*v355 )
                      {
                        v177 = max__modelZsave95mongerZcommon_u225(v181, v178);
                        if ( !*v355 )
                        {
                          nimZeroMem_60(&v175, 16i64);
                          v175 = input_size__modelZsimulationZpreorder_u2007;
                          v176 = v354;
                          v174 = v354
                               ? ((__int64 (__fastcall *)(__int64, _QWORD *))v175)(6i64, v176)
                               : ((__int64 (__fastcall *)(__int64))v175)(6i64);
                          if ( !*v355 )
                          {
                            nimZeroMem_60(&v172, 16i64);
                            v172 = input_size__modelZsimulationZpreorder_u2007;
                            v173 = v354;
                            v171 = v354
                                 ? ((__int64 (__fastcall *)(__int64, _QWORD *))v172)(7i64, v173)
                                 : ((__int64 (__fastcall *)(__int64))v172)(7i64);
                            if ( !*v355 )
                            {
                              v170 = max__modelZsave95mongerZcommon_u225(v174, v171);
                              if ( !*v355 )
                              {
                                v169 = max__modelZsave95mongerZcommon_u225(v177, v170);
                                if ( !*v355 )
                                {
                                  v341 = 137i64;
                                  v168 = max__modelZsave95mongerZcommon_u225(v184, v169);
                                  if ( !*v355 )
                                  {
                                    v341 = 140i64;
                                    v344 = star___modelZsave95mongerZcommon_u213(v168, 8i64);
                                    if ( !*v355 )
                                      goto LABEL_523;
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
      goto LABEL_524;
    case 0x63u:
      v341 = 144i64;
      nimZeroMem_60(&v162, 16i64);
      v162 = input_size__modelZsimulationZpreorder_u2007;
      v163 = v354;
      if ( v354 )
        v161 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v162)(0i64, v163);
      else
        v161 = ((__int64 (__fastcall *)(_QWORD))v162)(0i64);
      if ( !*v355 )
      {
        v160 = plus___modelZsave95mongerZcommon_u202(v161, 3i64);
        if ( !*v355 )
        {
          v344 = div__modelZsave95mongerZcommon_u217(v160, 4i64);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x64u:
      v341 = 146i64;
      nimZeroMem_60(&v158, 16i64);
      v158 = input_size__modelZsimulationZpreorder_u2007;
      v159 = v354;
      if ( v354 )
        v157 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v158)(0i64, v159);
      else
        v157 = ((__int64 (__fastcall *)(_QWORD))v158)(0i64);
      if ( !*v355 )
      {
        v156 = plus___modelZsave95mongerZcommon_u202(v157, 7i64);
        if ( !*v355 )
        {
          v344 = div__modelZsave95mongerZcommon_u217(v156, 8i64);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x68u:
      v341 = 170i64;
      nimZeroMem_60(&v96, 16i64);
      v96 = input_size__modelZsimulationZpreorder_u2007;
      v97 = v354;
      if ( v354 )
        v344 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v96)(0i64, v97);
      else
        v344 = ((__int64 (__fastcall *)(_QWORD))v96)(0i64);
      if ( !*v355 )
        goto LABEL_523;
      goto LABEL_524;
    case 0x6Cu:
      v341 = 178i64;
      nimZeroMem_60(&v76, 16i64);
      v76 = input_size__modelZsimulationZpreorder_u2007;
      v77 = v354;
      if ( v354 )
        v75 = ((__int64 (__fastcall *)(_QWORD, _QWORD *))v76)(0i64, v77);
      else
        v75 = ((__int64 (__fastcall *)(_QWORD))v76)(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v73, 16i64);
        v73 = input_size__modelZsimulationZpreorder_u2007;
        v74 = v354;
        v72 = v354
            ? ((__int64 (__fastcall *)(__int64, _QWORD *))v73)(1i64, v74)
            : ((__int64 (__fastcall *)(__int64))v73)(1i64);
        if ( !*v355 )
        {
          v344 = max__modelZsave95mongerZcommon_u225(v75, v72);
          if ( !*v355 )
            goto LABEL_523;
        }
      }
      goto LABEL_524;
    case 0x72u:
      v341 = 120i64;
      v298 = bits__modelZsave95mongerZcommon_u192(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v296, 16i64);
        v296 = input_size__modelZsimulationZpreorder_u2007;
        v297 = v354;
        v295 = v354
             ? ((__int64 (__fastcall *)(_QWORD, _QWORD *))v296)(0i64, v297)
             : ((__int64 (__fastcall *)(_QWORD))v296)(0i64);
        if ( !*v355 )
        {
          v294 = max__modelZsave95mongerZcommon_u225(v298, v295);
          if ( !*v355 )
          {
            v293 = bits__modelZsave95mongerZcommon_u192(0i64);
            if ( !*v355 )
            {
              nimZeroMem_60(&v291, 16i64);
              v291 = input_size__modelZsimulationZpreorder_u2007;
              v292 = v354;
              v290 = v354
                   ? ((__int64 (__fastcall *)(__int64, _QWORD *))v291)(1i64, v292)
                   : ((__int64 (__fastcall *)(__int64))v291)(1i64);
              if ( !*v355 )
              {
                v289 = max__modelZsave95mongerZcommon_u225(v293, v290);
                if ( !*v355 )
                {
                  v344 = plus___modelZsave95mongerZcommon_u198(v294, v289);
                  if ( !*v355 )
                    goto LABEL_523;
                }
              }
            }
          }
        }
      }
      goto LABEL_524;
    case 0x73u:
      v341 = 123i64;
      v288 = bits__modelZsave95mongerZcommon_u192(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v286, 16i64);
        v286 = input_size__modelZsimulationZpreorder_u2007;
        v287 = v354;
        v285 = v354
             ? ((__int64 (__fastcall *)(_QWORD, _QWORD *))v286)(0i64, v287)
             : ((__int64 (__fastcall *)(_QWORD))v286)(0i64);
        if ( !*v355 )
        {
          v284 = max__modelZsave95mongerZcommon_u225(v288, v285);
          if ( !*v355 )
          {
            v283 = bits__modelZsave95mongerZcommon_u192(0i64);
            if ( !*v355 )
            {
              nimZeroMem_60(&v281, 16i64);
              v281 = input_size__modelZsimulationZpreorder_u2007;
              v282 = v354;
              v280 = v354
                   ? ((__int64 (__fastcall *)(__int64, _QWORD *))v281)(1i64, v282)
                   : ((__int64 (__fastcall *)(__int64))v281)(1i64);
              if ( !*v355 )
              {
                v279 = max__modelZsave95mongerZcommon_u225(v283, v280);
                if ( !*v355 )
                {
                  v278 = plus___modelZsave95mongerZcommon_u198(v284, v279);
                  if ( !*v355 )
                  {
                    v277 = bits__modelZsave95mongerZcommon_u192(0i64);
                    if ( !*v355 )
                    {
                      nimZeroMem_60(&v275, 16i64);
                      v275 = input_size__modelZsimulationZpreorder_u2007;
                      v276 = v354;
                      v274 = v354
                           ? ((__int64 (__fastcall *)(__int64, _QWORD *))v275)(2i64, v276)
                           : ((__int64 (__fastcall *)(__int64))v275)(2i64);
                      if ( !*v355 )
                      {
                        v273 = max__modelZsave95mongerZcommon_u225(v277, v274);
                        if ( !*v355 )
                        {
                          v272 = plus___modelZsave95mongerZcommon_u198(v278, v273);
                          if ( !*v355 )
                          {
                            v341 = 124i64;
                            v271 = bits__modelZsave95mongerZcommon_u192(0i64);
                            if ( !*v355 )
                            {
                              nimZeroMem_60(&v269, 16i64);
                              v269 = input_size__modelZsimulationZpreorder_u2007;
                              v270 = v354;
                              v268 = v354
                                   ? ((__int64 (__fastcall *)(__int64, _QWORD *))v269)(3i64, v270)
                                   : ((__int64 (__fastcall *)(__int64))v269)(3i64);
                              if ( !*v355 )
                              {
                                v267 = max__modelZsave95mongerZcommon_u225(v271, v268);
                                if ( !*v355 )
                                {
                                  v341 = 123i64;
                                  v344 = plus___modelZsave95mongerZcommon_u198(v272, v267);
                                  if ( !*v355 )
                                    goto LABEL_523;
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
      goto LABEL_524;
    case 0x74u:
      v341 = 127i64;
      v266 = bits__modelZsave95mongerZcommon_u192(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v264, 16i64);
        v264 = input_size__modelZsimulationZpreorder_u2007;
        v265 = v354;
        v263 = v354
             ? ((__int64 (__fastcall *)(_QWORD, _QWORD *))v264)(0i64, v265)
             : ((__int64 (__fastcall *)(_QWORD))v264)(0i64);
        if ( !*v355 )
        {
          v262 = max__modelZsave95mongerZcommon_u225(v266, v263);
          if ( !*v355 )
          {
            v261 = bits__modelZsave95mongerZcommon_u192(0i64);
            if ( !*v355 )
            {
              nimZeroMem_60(&v259, 16i64);
              v259 = input_size__modelZsimulationZpreorder_u2007;
              v260 = v354;
              v258 = v354
                   ? ((__int64 (__fastcall *)(__int64, _QWORD *))v259)(1i64, v260)
                   : ((__int64 (__fastcall *)(__int64))v259)(1i64);
              if ( !*v355 )
              {
                v257 = max__modelZsave95mongerZcommon_u225(v261, v258);
                if ( !*v355 )
                {
                  v256 = plus___modelZsave95mongerZcommon_u198(v262, v257);
                  if ( !*v355 )
                  {
                    v255 = bits__modelZsave95mongerZcommon_u192(0i64);
                    if ( !*v355 )
                    {
                      nimZeroMem_60(&v253, 16i64);
                      v253 = input_size__modelZsimulationZpreorder_u2007;
                      v254 = v354;
                      v252 = v354
                           ? ((__int64 (__fastcall *)(__int64, _QWORD *))v253)(2i64, v254)
                           : ((__int64 (__fastcall *)(__int64))v253)(2i64);
                      if ( !*v355 )
                      {
                        v251 = max__modelZsave95mongerZcommon_u225(v255, v252);
                        if ( !*v355 )
                        {
                          v250 = plus___modelZsave95mongerZcommon_u198(v256, v251);
                          if ( !*v355 )
                          {
                            v341 = 128i64;
                            v249 = bits__modelZsave95mongerZcommon_u192(0i64);
                            if ( !*v355 )
                            {
                              nimZeroMem_60(&v247, 16i64);
                              v247 = input_size__modelZsimulationZpreorder_u2007;
                              v248 = v354;
                              v246 = v354
                                   ? ((__int64 (__fastcall *)(__int64, _QWORD *))v247)(3i64, v248)
                                   : ((__int64 (__fastcall *)(__int64))v247)(3i64);
                              if ( !*v355 )
                              {
                                v245 = max__modelZsave95mongerZcommon_u225(v249, v246);
                                if ( !*v355 )
                                {
                                  v341 = 127i64;
                                  v244 = plus___modelZsave95mongerZcommon_u198(v250, v245);
                                  if ( !*v355 )
                                  {
                                    v341 = 128i64;
                                    v243 = bits__modelZsave95mongerZcommon_u192(0i64);
                                    if ( !*v355 )
                                    {
                                      nimZeroMem_60(&v241, 16i64);
                                      v241 = input_size__modelZsimulationZpreorder_u2007;
                                      v242 = v354;
                                      v240 = v354
                                           ? ((__int64 (__fastcall *)(__int64, _QWORD *))v241)(4i64, v242)
                                           : ((__int64 (__fastcall *)(__int64))v241)(4i64);
                                      if ( !*v355 )
                                      {
                                        v239 = max__modelZsave95mongerZcommon_u225(v243, v240);
                                        if ( !*v355 )
                                        {
                                          v238 = plus___modelZsave95mongerZcommon_u198(v244, v239);
                                          if ( !*v355 )
                                          {
                                            v237 = bits__modelZsave95mongerZcommon_u192(0i64);
                                            if ( !*v355 )
                                            {
                                              nimZeroMem_60(&v235, 16i64);
                                              v235 = input_size__modelZsimulationZpreorder_u2007;
                                              v236 = v354;
                                              v234 = v354
                                                   ? ((__int64 (__fastcall *)(__int64, _QWORD *))v235)(5i64, v236)
                                                   : ((__int64 (__fastcall *)(__int64))v235)(5i64);
                                              if ( !*v355 )
                                              {
                                                v233 = max__modelZsave95mongerZcommon_u225(v237, v234);
                                                if ( !*v355 )
                                                {
                                                  v232 = plus___modelZsave95mongerZcommon_u198(v238, v233);
                                                  if ( !*v355 )
                                                  {
                                                    v341 = 129i64;
                                                    v231 = bits__modelZsave95mongerZcommon_u192(0i64);
                                                    if ( !*v355 )
                                                    {
                                                      nimZeroMem_60(&v229, 16i64);
                                                      v229 = input_size__modelZsimulationZpreorder_u2007;
                                                      v230 = v354;
                                                      v228 = v354
                                                           ? ((__int64 (__fastcall *)(__int64, _QWORD *))v229)(
                                                               6i64,
                                                               v230)
                                                           : ((__int64 (__fastcall *)(__int64))v229)(6i64);
                                                      if ( !*v355 )
                                                      {
                                                        v227 = max__modelZsave95mongerZcommon_u225(v231, v228);
                                                        if ( !*v355 )
                                                        {
                                                          v341 = 128i64;
                                                          v226 = plus___modelZsave95mongerZcommon_u198(v232, v227);
                                                          if ( !*v355 )
                                                          {
                                                            v341 = 129i64;
                                                            v225 = bits__modelZsave95mongerZcommon_u192(0i64);
                                                            if ( !*v355 )
                                                            {
                                                              nimZeroMem_60(&v223, 16i64);
                                                              v223 = input_size__modelZsimulationZpreorder_u2007;
                                                              v224 = v354;
                                                              v222 = v354
                                                                   ? ((__int64 (__fastcall *)(__int64, _QWORD *))v223)(
                                                                       7i64,
                                                                       v224)
                                                                   : ((__int64 (__fastcall *)(__int64))v223)(7i64);
                                                              if ( !*v355 )
                                                              {
                                                                v221 = max__modelZsave95mongerZcommon_u225(v225, v222);
                                                                if ( !*v355 )
                                                                {
                                                                  v344 = plus___modelZsave95mongerZcommon_u198(
                                                                           v226,
                                                                           v221);
                                                                  if ( !*v355 )
                                                                    goto LABEL_523;
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
                }
              }
            }
          }
        }
      }
      goto LABEL_524;
    case 0x75u:
      v341 = 118i64;
      v304 = bits__modelZsave95mongerZcommon_u192(0i64);
      if ( !*v355 )
      {
        nimZeroMem_60(&v302, 16i64);
        v302 = input_size__modelZsimulationZpreorder_u2007;
        v303 = v354;
        v301 = v354
             ? ((__int64 (__fastcall *)(__int64, _QWORD *))v302)(1i64, v303)
             : ((__int64 (__fastcall *)(__int64))v302)(1i64);
        if ( !*v355 )
        {
          v300 = max__modelZsave95mongerZcommon_u225(v304, v301);
          if ( !*v355 )
          {
            v299 = bits__modelZsave95mongerZcommon_u192(2048i64);
            if ( !*v355 )
            {
              v344 = min__modelZsave95mongerZcommon_u221(v300, v299);
              if ( !*v355 )
                goto LABEL_523;
            }
          }
        }
      }
      goto LABEL_524;
    default:
      goto LABEL_523;
  }
}


/* call 0x00000001402dc1ab, caller preorder__modelZsimulationZpreorder_u8738 @ 0x00000001402cb244 */

__int64 __fastcall preorder__modelZsimulationZpreorder_u8738(
        __int64 *a1,
        __int64 *a2,
        __int64 *a3,
        __int64 *a4,
        __int64 *a5,
        __int64 *a6,
        __int64 a7,
        __int64 a8)
{
  __int64 v8; // rbx
  __int64 v9; // rax
  __int64 v10; // rdx
  __int64 v11; // rdx
  __int64 v12; // rdx
  __int64 v13; // rdx
  _QWORD *v14; // r8
  __int64 v15; // rdx
  __int64 v16; // rax
  __int64 *address; // rbx
  char *v18; // rdx
  __int64 v19; // rax
  __int64 v20; // rax
  __int64 v21; // rcx
  char *v22; // rdx
  __int64 v23; // rcx
  __int64 v24; // rcx
  __int64 v25; // rcx
  __int64 v26; // rcx
  char *v27; // rdx
  __int64 v28; // rcx
  char *v29; // rdx
  __int64 v30; // rcx
  _QWORD *v31; // rax
  __int64 v32; // rbx
  __int64 v33; // rbx
  __int64 v34; // rbx
  __int64 v35; // rbx
  __int64 v36; // rdx
  __int64 v37; // rax
  __int64 v38; // rdx
  char *v39; // rdx
  __int64 v40; // rcx
  __int64 v41; // rdx
  __int64 v42; // rdx
  __int64 v43; // rcx
  __int64 v44; // rcx
  __int64 v45; // rdx
  __int64 v46; // rdx
  __int64 v47; // rdx
  __int64 v48; // rdx
  __int64 v49; // rdx
  __int64 v50; // rcx
  __int64 v51; // rax
  __int64 v52; // rdx
  __int64 v53; // rdx
  __int64 v54; // rcx
  __int64 v55; // rax
  __int64 v56; // rcx
  __int64 v57; // rdx
  __int64 v58; // rax
  char *v59; // rdx
  bool v60; // al
  __int64 v61; // rax
  __int64 v62; // rax
  char v63; // dl
  bool v64; // of
  __int64 v65; // rax
  __int64 v66; // rax
  char *v67; // rdx
  __int64 v68; // rcx
  bool v69; // al
  char *v70; // rax
  __int64 v71; // rdx
  _QWORD *v72; // rax
  __int64 v73; // rbx
  __int64 v74; // rbx
  __int64 v75; // rbx
  char *v76; // rdx
  char *v77; // rdx
  char *v78; // rax
  __int64 v79; // rdx
  __int64 v80; // rax
  char *v81; // rax
  __int64 v82; // rax
  char *v83; // rax
  char *v84; // rdx
  char *v85; // rdx
  void *v86; // rdx
  __int64 v87; // rdx
  __int64 v88; // rdx
  __int64 v89; // rdx
  __int64 v90; // rdx
  __int64 v91; // rdx
  __int64 v92; // rax
  void *v93; // rdx
  __int64 v94; // rdx
  __int64 v95; // rdx
  __int64 v96; // rdx
  _QWORD *v97; // rax
  __int64 v98; // rbx
  __int64 v99; // rbx
  __int64 v100; // rbx
  __int64 v101; // rbx
  __int64 v102; // rbx
  _QWORD *v103; // rcx
  __int64 v104; // rdx
  __int64 v105; // rdx
  _QWORD *v106; // rax
  __int64 v107; // rbx
  char *v108; // rbx
  __int64 v109; // rbx
  __int64 v110; // rbx
  __int64 v111; // rbx
  __int64 v112; // rdx
  _QWORD *v113; // rax
  __int64 v114; // rbx
  char *v115; // rbx
  __int64 v116; // rbx
  __int64 v117; // rbx
  __int64 v118; // rbx
  _QWORD *v119; // rcx
  __int64 v120; // rdx
  __int64 v121; // rdx
  _QWORD *v122; // rax
  __int64 v123; // rbx
  __int64 v124; // rbx
  __int64 v125; // rbx
  __int64 v126; // rbx
  __int64 v127; // rbx
  bool v128; // al
  bool v129; // al
  __int64 v130; // rdx
  __int64 v131; // rdx
  bool v132; // cl
  char *v133; // rdx
  __int64 v134; // rdx
  char *v135; // rdx
  __int64 v136; // rax
  __int64 v137; // r8
  __int64 v138; // rdx
  __int64 v139; // rax
  __int64 v140; // rdx
  __int64 v141; // rdx
  __int64 v142; // rax
  __int64 v143; // rdx
  __int64 v144; // rdx
  __int64 v146; // [rsp+40h] [rbp-40h] BYREF
  __int64 v147; // [rsp+48h] [rbp-38h]
  __int64 v148; // [rsp+50h] [rbp-30h]
  __int64 v149; // [rsp+60h] [rbp-20h] BYREF
  __int64 v150; // [rsp+68h] [rbp-18h]
  __int64 v151; // [rsp+70h] [rbp-10h]
  __int64 v152; // [rsp+80h] [rbp+0h] BYREF
  __int64 v153; // [rsp+88h] [rbp+8h]
  __int64 v154; // [rsp+90h] [rbp+10h]
  __int64 v155; // [rsp+A0h] [rbp+20h] BYREF
  char *v156; // [rsp+A8h] [rbp+28h]
  __int64 v157; // [rsp+B0h] [rbp+30h] BYREF
  char *v158; // [rsp+B8h] [rbp+38h]
  __int64 v159; // [rsp+C0h] [rbp+40h] BYREF
  __int64 v160; // [rsp+C8h] [rbp+48h]
  void *v161; // [rsp+D0h] [rbp+50h]
  __int64 v162; // [rsp+E0h] [rbp+60h] BYREF
  char *v163; // [rsp+E8h] [rbp+68h]
  __int64 v164; // [rsp+F0h] [rbp+70h]
  char *v165; // [rsp+F8h] [rbp+78h]
  __int64 v166; // [rsp+100h] [rbp+80h]
  char *v167; // [rsp+108h] [rbp+88h]
  __int64 v168; // [rsp+110h] [rbp+90h]
  char *v169; // [rsp+118h] [rbp+98h]
  __int64 v170; // [rsp+120h] [rbp+A0h]
  char *v171; // [rsp+128h] [rbp+A8h]
  __int64 v172; // [rsp+130h] [rbp+B0h]
  char *v173; // [rsp+138h] [rbp+B8h]
  char v174[24]; // [rsp+140h] [rbp+C0h] BYREF
  __int64 v175; // [rsp+158h] [rbp+D8h]
  __int64 v176; // [rsp+160h] [rbp+E0h]
  void *v177; // [rsp+168h] [rbp+E8h]
  char v178[560]; // [rsp+1B0h] [rbp+130h] BYREF
  __int64 v179; // [rsp+3E0h] [rbp+360h] BYREF
  __int64 v180; // [rsp+3E8h] [rbp+368h]
  __int64 v181; // [rsp+3F0h] [rbp+370h] BYREF
  char *v182; // [rsp+3F8h] [rbp+378h]
  __int64 v183; // [rsp+400h] [rbp+380h]
  __int64 v184; // [rsp+408h] [rbp+388h]
  __int64 v185; // [rsp+410h] [rbp+390h]
  __int64 v186; // [rsp+418h] [rbp+398h]
  __int64 v187; // [rsp+420h] [rbp+3A0h]
  __int64 v188; // [rsp+428h] [rbp+3A8h]
  __int64 v189; // [rsp+568h] [rbp+4E8h]
  __int64 v190[20]; // [rsp+570h] [rbp+4F0h] BYREF
  __int64 v191[70]; // [rsp+610h] [rbp+590h] BYREF
  __int64 v192[70]; // [rsp+840h] [rbp+7C0h] BYREF
  __int64 v193[182]; // [rsp+A70h] [rbp+9F0h] BYREF
  __int64 v194[182]; // [rsp+1020h] [rbp+FA0h] BYREF
  __int64 v195; // [rsp+15D0h] [rbp+1550h]
  __int64 v196; // [rsp+15D8h] [rbp+1558h]
  __int64 v197; // [rsp+15E0h] [rbp+1560h]
  __int64 v198; // [rsp+15E8h] [rbp+1568h]
  __int64 v199; // [rsp+15F0h] [rbp+1570h]
  __int64 v200; // [rsp+15F8h] [rbp+1578h]
  __int64 v201; // [rsp+1608h] [rbp+1588h]
  __int64 v202; // [rsp+1610h] [rbp+1590h] BYREF
  __int64 v203; // [rsp+1618h] [rbp+1598h]
  __int64 v204; // [rsp+1620h] [rbp+15A0h] BYREF
  char *v205; // [rsp+1628h] [rbp+15A8h]
  __int64 v206; // [rsp+1630h] [rbp+15B0h] BYREF
  char *v207; // [rsp+1638h] [rbp+15B8h]
  int v208; // [rsp+1644h] [rbp+15C4h] BYREF
  __int64 v209; // [rsp+1648h] [rbp+15C8h]
  __int64 (__fastcall *v210)(int, int, int, int, __int64); // [rsp+1650h] [rbp+15D0h] BYREF
  _QWORD *v211; // [rsp+1658h] [rbp+15D8h]
  __int64 v212; // [rsp+1668h] [rbp+15E8h]
  __int64 (__fastcall *v213)(int, int, int, int, __int64); // [rsp+1670h] [rbp+15F0h] BYREF
  _QWORD *v214; // [rsp+1678h] [rbp+15F8h]
  __int64 v215; // [rsp+1680h] [rbp+1600h] BYREF
  __int64 v216; // [rsp+1688h] [rbp+1608h]
  __int64 v217; // [rsp+1690h] [rbp+1610h]
  __int64 v218; // [rsp+1698h] [rbp+1618h]
  __int64 clamped_word_size__modelZboardZprototype95list_u4458; // [rsp+16A0h] [rbp+1620h]
  __int64 v220; // [rsp+16A8h] [rbp+1628h]
  __int64 v221[4]; // [rsp+16B0h] [rbp+1630h] BYREF
  __int64 v222[3]; // [rsp+16D0h] [rbp+1650h] BYREF
  unsigned int v223; // [rsp+16ECh] [rbp+166Ch]
  __int64 v224; // [rsp+16F0h] [rbp+1670h] BYREF
  char *v225; // [rsp+16F8h] [rbp+1678h]
  __int64 v226[3]; // [rsp+1700h] [rbp+1680h] BYREF
  unsigned int v227; // [rsp+171Ch] [rbp+169Ch]
  __int64 v228; // [rsp+1720h] [rbp+16A0h] BYREF
  char *v229; // [rsp+1728h] [rbp+16A8h]
  __int64 v230; // [rsp+1730h] [rbp+16B0h] BYREF
  __int64 v231; // [rsp+1738h] [rbp+16B8h]
  void *v232; // [rsp+1740h] [rbp+16C0h]
  __int64 v233; // [rsp+1750h] [rbp+16D0h]
  __int64 v234; // [rsp+1758h] [rbp+16D8h]
  __int64 v235; // [rsp+1760h] [rbp+16E0h]
  __int64 v236; // [rsp+1768h] [rbp+16E8h]
  __int64 v237; // [rsp+1770h] [rbp+16F0h]
  unsigned int v238; // [rsp+177Ch] [rbp+16FCh]
  __int64 v239[2]; // [rsp+1780h] [rbp+1700h] BYREF
  __int64 v240; // [rsp+1790h] [rbp+1710h] BYREF
  char *v241; // [rsp+1798h] [rbp+1718h]
  __int64 v242; // [rsp+17A0h] [rbp+1720h] BYREF
  char *v243; // [rsp+17A8h] [rbp+1728h]
  __int64 v244; // [rsp+17B0h] [rbp+1730h]
  char *v245; // [rsp+17B8h] [rbp+1738h]
  __int64 v246; // [rsp+17C8h] [rbp+1748h]
  __int64 v247; // [rsp+17D0h] [rbp+1750h]
  void *v248; // [rsp+17D8h] [rbp+1758h]
  char v249[32]; // [rsp+17E0h] [rbp+1760h] BYREF
  __int64 v250; // [rsp+1800h] [rbp+1780h] BYREF
  __int64 v251; // [rsp+1808h] [rbp+1788h]
  void *v252; // [rsp+1810h] [rbp+1790h]
  __int64 v253; // [rsp+1820h] [rbp+17A0h] BYREF
  char *v254; // [rsp+1828h] [rbp+17A8h]
  __int64 (__fastcall *v255)(); // [rsp+1830h] [rbp+17B0h] BYREF
  _QWORD *v256; // [rsp+1838h] [rbp+17B8h]
  __int64 v257; // [rsp+1840h] [rbp+17C0h] BYREF
  __int64 v258; // [rsp+1848h] [rbp+17C8h] BYREF
  __int64 v259; // [rsp+1850h] [rbp+17D0h]
  void *v260; // [rsp+1858h] [rbp+17D8h]
  char v261[32]; // [rsp+1860h] [rbp+17E0h] BYREF
  __int64 v262[4]; // [rsp+1880h] [rbp+1800h] BYREF
  __int64 v263; // [rsp+18A0h] [rbp+1820h] BYREF
  char *v264; // [rsp+18A8h] [rbp+1828h]
  __int64 v265; // [rsp+18B0h] [rbp+1830h] BYREF
  char *v266; // [rsp+18B8h] [rbp+1838h]
  __int64 v267; // [rsp+18C0h] [rbp+1840h]
  char *v268; // [rsp+18C8h] [rbp+1848h]
  __int64 v269; // [rsp+18D0h] [rbp+1850h] BYREF
  char *v270; // [rsp+18D8h] [rbp+1858h]
  __int64 v271; // [rsp+18E0h] [rbp+1860h]
  char *v272; // [rsp+18E8h] [rbp+1868h]
  __int64 v273; // [rsp+18F0h] [rbp+1870h]
  char *v274; // [rsp+18F8h] [rbp+1878h]
  __int64 v275; // [rsp+1900h] [rbp+1880h] BYREF
  char *v276; // [rsp+1908h] [rbp+1888h]
  __int64 v277; // [rsp+1910h] [rbp+1890h] BYREF
  char *v278; // [rsp+1918h] [rbp+1898h]
  __int64 v279; // [rsp+1920h] [rbp+18A0h] BYREF
  char *v280; // [rsp+1928h] [rbp+18A8h]
  __int64 v281; // [rsp+1938h] [rbp+18B8h]
  __int64 v282; // [rsp+1940h] [rbp+18C0h] BYREF
  __int64 v283; // [rsp+1948h] [rbp+18C8h]
  __int64 (__fastcall *v284)(); // [rsp+1950h] [rbp+18D0h] BYREF
  _QWORD *v285; // [rsp+1958h] [rbp+18D8h]
  __int64 v286; // [rsp+1960h] [rbp+18E0h] BYREF
  __int64 v287; // [rsp+1968h] [rbp+18E8h]
  __int64 v288; // [rsp+1970h] [rbp+18F0h] BYREF
  __int64 v289; // [rsp+1978h] [rbp+18F8h]
  __int64 v290; // [rsp+1980h] [rbp+1900h]
  __int64 v291; // [rsp+1988h] [rbp+1908h]
  __int64 v292; // [rsp+1990h] [rbp+1910h]
  __int64 v293; // [rsp+1998h] [rbp+1918h]
  __int64 (__fastcall *v294)(); // [rsp+19A0h] [rbp+1920h] BYREF
  _QWORD *v295; // [rsp+19A8h] [rbp+1928h]
  __int64 v296; // [rsp+19B0h] [rbp+1930h]
  char *v297; // [rsp+19B8h] [rbp+1938h]
  __int64 v298; // [rsp+19C8h] [rbp+1948h]
  __int64 v299; // [rsp+19D0h] [rbp+1950h] BYREF
  char *v300; // [rsp+19D8h] [rbp+1958h]
  __int64 v301; // [rsp+19E0h] [rbp+1960h] BYREF
  char *v302; // [rsp+19E8h] [rbp+1968h]
  __int64 v303; // [rsp+19F0h] [rbp+1970h]
  char *v304; // [rsp+19F8h] [rbp+1978h]
  __int64 v305; // [rsp+1A00h] [rbp+1980h] BYREF
  char *v306; // [rsp+1A08h] [rbp+1988h]
  __int64 v307[2]; // [rsp+1A10h] [rbp+1990h] BYREF
  __int64 (__fastcall *v308)(); // [rsp+1A20h] [rbp+19A0h] BYREF
  _QWORD *v309; // [rsp+1A28h] [rbp+19A8h]
  __int64 v310; // [rsp+1A30h] [rbp+19B0h] BYREF
  char *v311; // [rsp+1A38h] [rbp+19B8h]
  __int64 v312[4]; // [rsp+1A40h] [rbp+19C0h] BYREF
  __int64 v313; // [rsp+1A60h] [rbp+19E0h] BYREF
  char *v314; // [rsp+1A68h] [rbp+19E8h]
  __int64 v315; // [rsp+1A70h] [rbp+19F0h]
  __int64 v316; // [rsp+1A78h] [rbp+19F8h]
  __int64 v317; // [rsp+1A80h] [rbp+1A00h]
  __int64 v318; // [rsp+1A90h] [rbp+1A10h]
  __int64 v319; // [rsp+1A98h] [rbp+1A18h]
  __int64 v320; // [rsp+1AA0h] [rbp+1A20h]
  __int64 v321; // [rsp+1AB0h] [rbp+1A30h]
  char *v322; // [rsp+1AB8h] [rbp+1A38h]
  __int64 v323; // [rsp+1AC0h] [rbp+1A40h]
  char *v324; // [rsp+1AC8h] [rbp+1A48h]
  __int64 v325; // [rsp+1AD8h] [rbp+1A58h]
  __int64 (__fastcall *v326)(); // [rsp+1AE0h] [rbp+1A60h] BYREF
  _QWORD *v327; // [rsp+1AE8h] [rbp+1A68h]
  __int64 (__fastcall *v328)(); // [rsp+1AF0h] [rbp+1A70h] BYREF
  _QWORD *v329; // [rsp+1AF8h] [rbp+1A78h]
  __int64 v330; // [rsp+1B00h] [rbp+1A80h]
  char *v331; // [rsp+1B08h] [rbp+1A88h]
  __int64 v332; // [rsp+1B10h] [rbp+1A90h]
  char *v333; // [rsp+1B18h] [rbp+1A98h]
  __int64 v334[4]; // [rsp+1B20h] [rbp+1AA0h] BYREF
  __int64 v335; // [rsp+1B40h] [rbp+1AC0h] BYREF
  __int64 v336; // [rsp+1B48h] [rbp+1AC8h]
  __int64 v337; // [rsp+1B58h] [rbp+1AD8h]
  __int64 v338[2]; // [rsp+1B60h] [rbp+1AE0h] BYREF
  __int64 v339; // [rsp+1B70h] [rbp+1AF0h] BYREF
  char *v340; // [rsp+1B78h] [rbp+1AF8h]
  __int64 v341; // [rsp+1B80h] [rbp+1B00h]
  __int64 v342; // [rsp+1B88h] [rbp+1B08h]
  __int64 v343; // [rsp+1B90h] [rbp+1B10h]
  __int64 v344; // [rsp+1B98h] [rbp+1B18h]
  __int64 v345; // [rsp+1BA0h] [rbp+1B20h]
  char *v346; // [rsp+1BA8h] [rbp+1B28h]
  __int64 v347; // [rsp+1BB0h] [rbp+1B30h]
  char *v348; // [rsp+1BB8h] [rbp+1B38h]
  __int64 v349; // [rsp+1BC0h] [rbp+1B40h]
  char *v350; // [rsp+1BC8h] [rbp+1B48h]
  __int64 v351; // [rsp+1BD0h] [rbp+1B50h]
  char *v352; // [rsp+1BD8h] [rbp+1B58h]
  __int64 v353; // [rsp+1BE0h] [rbp+1B60h] BYREF
  char *v354; // [rsp+1BE8h] [rbp+1B68h]
  __int64 v355; // [rsp+1BF0h] [rbp+1B70h] BYREF
  char *v356; // [rsp+1BF8h] [rbp+1B78h]
  __int64 v357; // [rsp+1C00h] [rbp+1B80h] BYREF
  char *v358; // [rsp+1C08h] [rbp+1B88h]
  __int64 v359; // [rsp+1C10h] [rbp+1B90h] BYREF
  char *v360; // [rsp+1C18h] [rbp+1B98h]
  __int64 v361; // [rsp+1C20h] [rbp+1BA0h]
  __int64 v362; // [rsp+1C28h] [rbp+1BA8h]
  __int64 v363; // [rsp+1C30h] [rbp+1BB0h]
  char *v364; // [rsp+1C38h] [rbp+1BB8h]
  __int64 v365; // [rsp+1C40h] [rbp+1BC0h]
  char *v366; // [rsp+1C48h] [rbp+1BC8h]
  __int64 v367; // [rsp+1C50h] [rbp+1BD0h]
  char *v368; // [rsp+1C58h] [rbp+1BD8h]
  __int64 v369; // [rsp+1C60h] [rbp+1BE0h] BYREF
  char *v370; // [rsp+1C68h] [rbp+1BE8h]
  __int64 v371; // [rsp+1C70h] [rbp+1BF0h] BYREF
  char *v372; // [rsp+1C78h] [rbp+1BF8h]
  _QWORD v373[2]; // [rsp+1C80h] [rbp+1C00h] BYREF
  __int64 (__fastcall *v374)(__int64, __int64, __int64); // [rsp+1C90h] [rbp+1C10h] BYREF
  _QWORD *v375; // [rsp+1C98h] [rbp+1C18h]
  unsigned int v376; // [rsp+1CACh] [rbp+1C2Ch]
  __int64 (__fastcall *v377)(); // [rsp+1CB0h] [rbp+1C30h] BYREF
  _QWORD *v378; // [rsp+1CB8h] [rbp+1C38h]
  __int64 v379; // [rsp+1CC0h] [rbp+1C40h] BYREF
  char *v380; // [rsp+1CC8h] [rbp+1C48h]
  __int64 v381; // [rsp+1CD0h] [rbp+1C50h] BYREF
  char *v382; // [rsp+1CD8h] [rbp+1C58h]
  __int64 v383; // [rsp+1CE0h] [rbp+1C60h]
  char *v384; // [rsp+1CE8h] [rbp+1C68h]
  __int64 v385[3]; // [rsp+1CF0h] [rbp+1C70h] BYREF
  unsigned int v386; // [rsp+1D0Ch] [rbp+1C8Ch]
  __int64 v387[4]; // [rsp+1D10h] [rbp+1C90h] BYREF
  void *v388; // [rsp+1D30h] [rbp+1CB0h]
  unsigned int v389; // [rsp+1D3Ch] [rbp+1CBCh]
  __int64 v390[3]; // [rsp+1D40h] [rbp+1CC0h] BYREF
  __int64 v391; // [rsp+1D58h] [rbp+1CD8h] BYREF
  __int64 v392; // [rsp+1D60h] [rbp+1CE0h]
  char *v393; // [rsp+1D68h] [rbp+1CE8h]
  __int64 v394[2]; // [rsp+1D70h] [rbp+1CF0h] BYREF
  __int64 v395[2]; // [rsp+1D80h] [rbp+1D00h] BYREF
  __int64 (__fastcall *v396)(); // [rsp+1D90h] [rbp+1D10h] BYREF
  _QWORD *v397; // [rsp+1D98h] [rbp+1D18h]
  unsigned int v398; // [rsp+1DA0h] [rbp+1D20h]
  unsigned int v399; // [rsp+1DA4h] [rbp+1D24h]
  unsigned int v400; // [rsp+1DA8h] [rbp+1D28h]
  unsigned int v401; // [rsp+1DACh] [rbp+1D2Ch]
  __int64 v402[2]; // [rsp+1DB0h] [rbp+1D30h] BYREF
  void *v403; // [rsp+1DC0h] [rbp+1D40h]
  __int64 v404[4]; // [rsp+1DD0h] [rbp+1D50h] BYREF
  __int64 v405[2]; // [rsp+1DF0h] [rbp+1D70h] BYREF
  __int64 v406[3]; // [rsp+1E00h] [rbp+1D80h] BYREF
  unsigned int v407; // [rsp+1E18h] [rbp+1D98h]
  unsigned int custom_position__modelZboardZcustom95prototype_u78; // [rsp+1E1Ch] [rbp+1D9Ch]
  unsigned int v409; // [rsp+1E20h] [rbp+1DA0h]
  unsigned int position__modelZboardZcache95opps_u6; // [rsp+1E24h] [rbp+1DA4h]
  __int64 v411; // [rsp+1E28h] [rbp+1DA8h] BYREF
  __int64 v412; // [rsp+1E30h] [rbp+1DB0h] BYREF
  char *v413; // [rsp+1E38h] [rbp+1DB8h]
  __int64 v414; // [rsp+1E40h] [rbp+1DC0h] BYREF
  char *v415; // [rsp+1E48h] [rbp+1DC8h]
  __int64 v416; // [rsp+1E50h] [rbp+1DD0h]
  __int64 v417; // [rsp+1E58h] [rbp+1DD8h]
  __int64 v418[3]; // [rsp+1E60h] [rbp+1DE0h] BYREF
  unsigned int v419; // [rsp+1E7Ch] [rbp+1DFCh]
  __int64 v420[3]; // [rsp+1E80h] [rbp+1E00h] BYREF
  unsigned int v421; // [rsp+1E9Ch] [rbp+1E1Ch]
  __int64 (__fastcall *v422)(); // [rsp+1EA0h] [rbp+1E20h] BYREF
  _QWORD *v423; // [rsp+1EA8h] [rbp+1E28h]
  __int64 v424; // [rsp+1EB0h] [rbp+1E30h] BYREF
  __int64 v425; // [rsp+1EB8h] [rbp+1E38h]
  __int64 v426; // [rsp+1EC0h] [rbp+1E40h]
  char *v427; // [rsp+1EC8h] [rbp+1E48h]
  __int64 v428[2]; // [rsp+1ED0h] [rbp+1E50h] BYREF
  unsigned int v429; // [rsp+1EE4h] [rbp+1E64h]
  unsigned int v430; // [rsp+1EE8h] [rbp+1E68h]
  unsigned int v431; // [rsp+1EECh] [rbp+1E6Ch]
  __int64 v432[2]; // [rsp+1EF0h] [rbp+1E70h] BYREF
  unsigned int v433; // [rsp+1F04h] [rbp+1E84h]
  unsigned int v434; // [rsp+1F08h] [rbp+1E88h]
  unsigned int v435; // [rsp+1F0Ch] [rbp+1E8Ch]
  __int64 v436[2]; // [rsp+1F10h] [rbp+1E90h] BYREF
  unsigned int v437; // [rsp+1F24h] [rbp+1EA4h]
  unsigned int v438; // [rsp+1F28h] [rbp+1EA8h]
  unsigned int v439; // [rsp+1F2Ch] [rbp+1EACh]
  __int64 v440[2]; // [rsp+1F30h] [rbp+1EB0h] BYREF
  unsigned int v441; // [rsp+1F44h] [rbp+1EC4h]
  unsigned int v442; // [rsp+1F48h] [rbp+1EC8h]
  unsigned int v443; // [rsp+1F4Ch] [rbp+1ECCh]
  __int64 v444[2]; // [rsp+1F50h] [rbp+1ED0h] BYREF
  unsigned int v445; // [rsp+1F64h] [rbp+1EE4h]
  unsigned int v446; // [rsp+1F68h] [rbp+1EE8h]
  unsigned int v447; // [rsp+1F6Ch] [rbp+1EECh]
  __int64 v448[2]; // [rsp+1F70h] [rbp+1EF0h] BYREF
  unsigned int v449; // [rsp+1F84h] [rbp+1F04h]
  unsigned int v450; // [rsp+1F88h] [rbp+1F08h]
  unsigned int v451; // [rsp+1F8Ch] [rbp+1F0Ch]
  __int64 v452[2]; // [rsp+1F90h] [rbp+1F10h] BYREF
  unsigned int v453; // [rsp+1FA4h] [rbp+1F24h]
  unsigned int v454; // [rsp+1FA8h] [rbp+1F28h]
  unsigned int v455; // [rsp+1FACh] [rbp+1F2Ch]
  __int64 v456[3]; // [rsp+1FB0h] [rbp+1F30h] BYREF
  unsigned int v457; // [rsp+1FCCh] [rbp+1F4Ch]
  unsigned int v458; // [rsp+1FD0h] [rbp+1F50h]
  unsigned int v459; // [rsp+1FD4h] [rbp+1F54h]
  __int64 v460; // [rsp+1FD8h] [rbp+1F58h]
  __int64 v461; // [rsp+1FE0h] [rbp+1F60h] BYREF
  char *v462; // [rsp+1FE8h] [rbp+1F68h]
  __int64 v463; // [rsp+1FF8h] [rbp+1F78h]
  __int64 v464[3]; // [rsp+2000h] [rbp+1F80h] BYREF
  unsigned int finish__modelZsave95mongerZcommon_u4866; // [rsp+201Ch] [rbp+1F9Ch]
  __int64 v466[3]; // [rsp+2020h] [rbp+1FA0h] BYREF
  unsigned int start__modelZsave95mongerZcommon_u4863; // [rsp+203Ch] [rbp+1FBCh]
  __int64 (__fastcall *v468)(); // [rsp+2040h] [rbp+1FC0h] BYREF
  _QWORD *v469; // [rsp+2048h] [rbp+1FC8h]
  __int64 v470[4]; // [rsp+2050h] [rbp+1FD0h] BYREF
  char v471[8]; // [rsp+2070h] [rbp+1FF0h] BYREF
  const char *v472; // [rsp+2078h] [rbp+1FF8h]
  __int64 v473; // [rsp+2080h] [rbp+2000h]
  const char *i; // [rsp+2088h] [rbp+2008h]
  __int16 v475; // [rsp+2090h] [rbp+2010h]
  __int64 v476[7]; // [rsp+20A0h] [rbp+2020h] BYREF
  __int64 v477; // [rsp+20D8h] [rbp+2058h]
  __int64 v478; // [rsp+20E0h] [rbp+2060h]
  _QWORD *v479; // [rsp+20E8h] [rbp+2068h]
  __int64 v480; // [rsp+20F0h] [rbp+2070h] BYREF
  char *v481; // [rsp+20F8h] [rbp+2078h]
  __int64 v482; // [rsp+2100h] [rbp+2080h] BYREF
  char *v483; // [rsp+2108h] [rbp+2088h]
  __int64 v484; // [rsp+2110h] [rbp+2090h] BYREF
  __int64 v485; // [rsp+2118h] [rbp+2098h]
  void *v486; // [rsp+2120h] [rbp+20A0h]
  char v487[24]; // [rsp+2130h] [rbp+20B0h] BYREF
  __int64 v488; // [rsp+2148h] [rbp+20C8h]
  char v489; // [rsp+2157h] [rbp+20D7h]
  __int64 v490; // [rsp+2158h] [rbp+20D8h]
  __int64 v491; // [rsp+2160h] [rbp+20E0h]
  __int64 v492; // [rsp+2168h] [rbp+20E8h]
  __int64 v493; // [rsp+2170h] [rbp+20F0h]
  __int64 v494; // [rsp+2178h] [rbp+20F8h]
  __int64 v495; // [rsp+2180h] [rbp+2100h]
  __int64 v496; // [rsp+2188h] [rbp+2108h]
  __int64 v497; // [rsp+2190h] [rbp+2110h]
  __int64 v498; // [rsp+2198h] [rbp+2118h]
  char v499; // [rsp+21A6h] [rbp+2126h]
  char v500; // [rsp+21A7h] [rbp+2127h]
  __int64 v501; // [rsp+21A8h] [rbp+2128h]
  __int64 v502; // [rsp+21B0h] [rbp+2130h]
  __int64 v503; // [rsp+21B8h] [rbp+2138h]
  _QWORD *v504; // [rsp+21C0h] [rbp+2140h]
  __int64 v505; // [rsp+21C8h] [rbp+2148h]
  __int64 v506; // [rsp+21D0h] [rbp+2150h]
  __int64 v507; // [rsp+21D8h] [rbp+2158h]
  __int64 v508; // [rsp+21E0h] [rbp+2160h]
  __int64 v509; // [rsp+21E8h] [rbp+2168h]
  __int64 v510; // [rsp+21F0h] [rbp+2170h]
  __int64 gate_cost__modelZscores_u2556; // [rsp+21F8h] [rbp+2178h]
  __int64 allocation_top__modelZsave95mongerZcommon_u5497; // [rsp+2200h] [rbp+2180h]
  __int64 v513; // [rsp+2208h] [rbp+2188h]
  __int64 state_index__modelZsave95mongerZcommon_u5502; // [rsp+2210h] [rbp+2190h]
  __int64 z_state_index__modelZsave95mongerZcommon_u5499; // [rsp+2218h] [rbp+2198h]
  __int64 v516; // [rsp+2220h] [rbp+21A0h]
  __int64 *v517; // [rsp+2228h] [rbp+21A8h]
  char v518; // [rsp+2237h] [rbp+21B7h]
  __int64 v519; // [rsp+2238h] [rbp+21B8h]
  __int64 v520; // [rsp+2240h] [rbp+21C0h]
  __int64 *v521; // [rsp+2248h] [rbp+21C8h]
  char v522; // [rsp+2256h] [rbp+21D6h]
  char v523; // [rsp+2257h] [rbp+21D7h]
  __int64 v524; // [rsp+2258h] [rbp+21D8h]
  __int64 v525; // [rsp+2260h] [rbp+21E0h]
  __int64 v526; // [rsp+2268h] [rbp+21E8h]
  __int64 v527; // [rsp+2270h] [rbp+21F0h]
  __int64 v528; // [rsp+2278h] [rbp+21F8h]
  __int64 v529; // [rsp+2280h] [rbp+2200h]
  __int64 v530; // [rsp+2288h] [rbp+2208h]
  __int64 v531; // [rsp+2290h] [rbp+2210h]
  char v532; // [rsp+229Fh] [rbp+221Fh]
  __int64 v533; // [rsp+22A0h] [rbp+2220h]
  __int64 v534; // [rsp+22A8h] [rbp+2228h]
  __int64 v535; // [rsp+22B0h] [rbp+2230h]
  __int64 v536; // [rsp+22B8h] [rbp+2238h]
  __int64 *v537; // [rsp+22C0h] [rbp+2240h]
  char v538; // [rsp+22CFh] [rbp+224Fh]
  __int64 v539; // [rsp+22D0h] [rbp+2250h]
  __int64 v540; // [rsp+22D8h] [rbp+2258h]
  __int64 v541; // [rsp+22E0h] [rbp+2260h]
  __int64 v542; // [rsp+22E8h] [rbp+2268h]
  __int64 *v543; // [rsp+22F0h] [rbp+2270h]
  char v544; // [rsp+22FFh] [rbp+227Fh]
  __int64 v545; // [rsp+2300h] [rbp+2280h]
  __int64 v546; // [rsp+2308h] [rbp+2288h]
  __int64 v547; // [rsp+2310h] [rbp+2290h]
  char v548; // [rsp+231Fh] [rbp+229Fh]
  __int64 ram_pipeline_depth__modelZmodel95types_u1723; // [rsp+2320h] [rbp+22A0h]
  char v550; // [rsp+232Fh] [rbp+22AFh]
  __int64 v551; // [rsp+2330h] [rbp+22B0h]
  __int64 v552; // [rsp+2338h] [rbp+22B8h]
  __int64 v553; // [rsp+2340h] [rbp+22C0h]
  __int64 v554; // [rsp+2348h] [rbp+22C8h]
  __int64 v555; // [rsp+2350h] [rbp+22D0h]
  __int64 v556; // [rsp+2358h] [rbp+22D8h]
  __int64 v557; // [rsp+2360h] [rbp+22E0h]
  __int64 v558; // [rsp+2368h] [rbp+22E8h]
  __int64 v559; // [rsp+2370h] [rbp+22F0h]
  char *v560; // [rsp+2378h] [rbp+22F8h]
  __int64 v561; // [rsp+2380h] [rbp+2300h]
  __int64 v562; // [rsp+2388h] [rbp+2308h]
  __int64 v563; // [rsp+2390h] [rbp+2310h]
  char *v564; // [rsp+2398h] [rbp+2318h]
  __int64 v565; // [rsp+23A0h] [rbp+2320h]
  __int64 v566; // [rsp+23A8h] [rbp+2328h]
  __int64 v567; // [rsp+23B0h] [rbp+2330h]
  __int64 v568; // [rsp+23B8h] [rbp+2338h]
  char v569; // [rsp+23C7h] [rbp+2347h]
  __int64 v570; // [rsp+23C8h] [rbp+2348h]
  __int64 v571; // [rsp+23D0h] [rbp+2350h]
  __int64 v572; // [rsp+23D8h] [rbp+2358h]
  __int64 v573; // [rsp+23E0h] [rbp+2360h]
  __int64 v574; // [rsp+23E8h] [rbp+2368h]
  __int64 v575; // [rsp+23F0h] [rbp+2370h]
  __int64 v576; // [rsp+23F8h] [rbp+2378h]
  __int64 v577; // [rsp+2400h] [rbp+2380h]
  __int64 *v578; // [rsp+2408h] [rbp+2388h]
  _QWORD *v579; // [rsp+2410h] [rbp+2390h]
  __int64 v580; // [rsp+2418h] [rbp+2398h]
  __int64 v581; // [rsp+2420h] [rbp+23A0h]
  __int64 v582; // [rsp+2428h] [rbp+23A8h]
  __int64 *v583; // [rsp+2430h] [rbp+23B0h]
  _QWORD *v584; // [rsp+2438h] [rbp+23B8h]
  __int64 v585; // [rsp+2440h] [rbp+23C0h]
  __int64 v586; // [rsp+2448h] [rbp+23C8h]
  __int64 v587; // [rsp+2450h] [rbp+23D0h]
  __int64 v588; // [rsp+2458h] [rbp+23D8h]
  __int64 v589; // [rsp+2460h] [rbp+23E0h]
  __int64 v590; // [rsp+2468h] [rbp+23E8h]
  __int64 v591; // [rsp+2470h] [rbp+23F0h]
  __int64 *v592; // [rsp+2478h] [rbp+23F8h]
  _QWORD *v593; // [rsp+2480h] [rbp+2400h]
  __int64 v594; // [rsp+2488h] [rbp+2408h]
  __int64 v595; // [rsp+2490h] [rbp+2410h]
  __int64 *v596; // [rsp+2498h] [rbp+2418h]
  _QWORD *v597; // [rsp+24A0h] [rbp+2420h]
  __int64 v598; // [rsp+24A8h] [rbp+2428h]
  __int64 v599; // [rsp+24B0h] [rbp+2430h]
  char *v600; // [rsp+24B8h] [rbp+2438h]
  __int64 v601; // [rsp+24C0h] [rbp+2440h]
  __int64 v602; // [rsp+24C8h] [rbp+2448h]
  __int64 v603; // [rsp+24D0h] [rbp+2450h]
  __int64 v604; // [rsp+24D8h] [rbp+2458h]
  __int64 v605; // [rsp+24E0h] [rbp+2460h]
  __int64 v606; // [rsp+24E8h] [rbp+2468h]
  __int64 v607; // [rsp+24F0h] [rbp+2470h]
  char v608; // [rsp+24FFh] [rbp+247Fh]
  __int64 v609; // [rsp+2500h] [rbp+2480h]
  __int64 v610; // [rsp+2508h] [rbp+2488h]
  __int64 v611; // [rsp+2510h] [rbp+2490h]
  __int64 v612; // [rsp+2518h] [rbp+2498h]
  char v613; // [rsp+2527h] [rbp+24A7h]
  __int64 v614; // [rsp+2528h] [rbp+24A8h]
  __int64 v615; // [rsp+2530h] [rbp+24B0h]
  __int64 v616; // [rsp+2538h] [rbp+24B8h]
  __int64 v617; // [rsp+2540h] [rbp+24C0h]
  __int64 v618; // [rsp+2548h] [rbp+24C8h]
  __int64 v619; // [rsp+2550h] [rbp+24D0h]
  __int64 v620; // [rsp+2558h] [rbp+24D8h]
  __int64 v621; // [rsp+2560h] [rbp+24E0h]
  __int64 v622; // [rsp+2568h] [rbp+24E8h]
  bool v623; // [rsp+2577h] [rbp+24F7h]
  __int64 v624; // [rsp+2578h] [rbp+24F8h]
  bool v625; // [rsp+2587h] [rbp+2507h]
  __int64 v626; // [rsp+2588h] [rbp+2508h]
  __int64 v627; // [rsp+2590h] [rbp+2510h]
  const void *v628; // [rsp+2598h] [rbp+2518h]
  char v629; // [rsp+25A7h] [rbp+2527h]
  __int64 v630; // [rsp+25A8h] [rbp+2528h]
  __int64 v631; // [rsp+25B0h] [rbp+2530h]
  _QWORD *v632; // [rsp+25B8h] [rbp+2538h]
  __int64 v633; // [rsp+25C0h] [rbp+2540h]
  __int64 v634; // [rsp+25C8h] [rbp+2548h]
  __int64 v635; // [rsp+25D0h] [rbp+2550h]
  __int64 v636; // [rsp+25D8h] [rbp+2558h]
  _QWORD *v637; // [rsp+25E0h] [rbp+2560h]
  __int64 v638; // [rsp+25E8h] [rbp+2568h]
  __int64 v639; // [rsp+25F0h] [rbp+2570h]
  __int64 v640; // [rsp+25F8h] [rbp+2578h]
  __int64 v641; // [rsp+2600h] [rbp+2580h]
  __int64 v642; // [rsp+2608h] [rbp+2588h]
  __int64 v643; // [rsp+2610h] [rbp+2590h]
  __int64 v644; // [rsp+2618h] [rbp+2598h]
  __int64 *v645; // [rsp+2620h] [rbp+25A0h]
  _QWORD *v646; // [rsp+2628h] [rbp+25A8h]
  __int64 v647; // [rsp+2630h] [rbp+25B0h]
  __int64 v648; // [rsp+2638h] [rbp+25B8h]
  __int64 v649; // [rsp+2640h] [rbp+25C0h]
  __int64 v650; // [rsp+2648h] [rbp+25C8h]
  __int64 *v651; // [rsp+2650h] [rbp+25D0h]
  _QWORD *v652; // [rsp+2658h] [rbp+25D8h]
  __int64 v653; // [rsp+2660h] [rbp+25E0h]
  __int64 v654; // [rsp+2668h] [rbp+25E8h]
  __int64 v655; // [rsp+2670h] [rbp+25F0h]
  __int64 v656; // [rsp+2678h] [rbp+25F8h]
  __int64 v657; // [rsp+2680h] [rbp+2600h]
  __int64 v658; // [rsp+2688h] [rbp+2608h]
  __int64 v659; // [rsp+2690h] [rbp+2610h]
  __int64 v660; // [rsp+2698h] [rbp+2618h]
  __int64 v661; // [rsp+26A0h] [rbp+2620h]
  __int64 v662; // [rsp+26A8h] [rbp+2628h]
  __int64 v663; // [rsp+26B0h] [rbp+2630h]
  __int64 v664; // [rsp+26B8h] [rbp+2638h]
  __int64 v665; // [rsp+26C0h] [rbp+2640h]
  __int64 v666; // [rsp+26C8h] [rbp+2648h]
  __int64 v667; // [rsp+26D0h] [rbp+2650h]
  __int64 v668; // [rsp+26D8h] [rbp+2658h]
  __int64 v669; // [rsp+26E0h] [rbp+2660h]
  bool v670; // [rsp+26EEh] [rbp+266Eh]
  char v671; // [rsp+26EFh] [rbp+266Fh]
  __int64 v672; // [rsp+26F0h] [rbp+2670h]
  __int64 v673; // [rsp+26F8h] [rbp+2678h]
  char *v674; // [rsp+2700h] [rbp+2680h]
  __int64 v675; // [rsp+2708h] [rbp+2688h]
  __int64 v676; // [rsp+2710h] [rbp+2690h]
  __int64 *v677; // [rsp+2718h] [rbp+2698h]
  char *v678; // [rsp+2720h] [rbp+26A0h]
  __int64 v679; // [rsp+2728h] [rbp+26A8h]
  char v680; // [rsp+2737h] [rbp+26B7h]
  __int64 v681; // [rsp+2738h] [rbp+26B8h]
  __int64 v682; // [rsp+2740h] [rbp+26C0h]
  __int64 v683; // [rsp+2748h] [rbp+26C8h]
  bool v684; // [rsp+2757h] [rbp+26D7h]
  __int64 v685; // [rsp+2758h] [rbp+26D8h]
  __int64 v686; // [rsp+2760h] [rbp+26E0h]
  __int64 v687; // [rsp+2768h] [rbp+26E8h]
  __int64 v688; // [rsp+2770h] [rbp+26F0h]
  __int64 v689; // [rsp+2778h] [rbp+26F8h]
  __int64 v690; // [rsp+2780h] [rbp+2700h]
  __int64 v691; // [rsp+2788h] [rbp+2708h]
  __int64 v692; // [rsp+2790h] [rbp+2710h]
  char *v693; // [rsp+2798h] [rbp+2718h]
  __int64 v694; // [rsp+27A0h] [rbp+2720h]
  __int64 v695; // [rsp+27A8h] [rbp+2728h]
  __int64 v696; // [rsp+27B0h] [rbp+2730h]
  __int64 v697; // [rsp+27B8h] [rbp+2738h]
  __int64 v698; // [rsp+27C0h] [rbp+2740h]
  __int64 v699; // [rsp+27C8h] [rbp+2748h]
  __int64 v700; // [rsp+27D0h] [rbp+2750h]
  __int64 v701; // [rsp+27D8h] [rbp+2758h]
  __int64 v702; // [rsp+27E0h] [rbp+2760h]
  __int64 *v703; // [rsp+27E8h] [rbp+2768h]
  __int64 v704; // [rsp+27F0h] [rbp+2770h]
  __int64 v705; // [rsp+27F8h] [rbp+2778h]
  __int64 v706; // [rsp+2800h] [rbp+2780h]
  __int64 v707; // [rsp+2808h] [rbp+2788h]
  __int64 *v708; // [rsp+2810h] [rbp+2790h]
  char v709; // [rsp+281Fh] [rbp+279Fh]
  __int64 v710; // [rsp+2820h] [rbp+27A0h]
  __int64 *v711; // [rsp+2828h] [rbp+27A8h]
  char v712; // [rsp+2837h] [rbp+27B7h]
  __int64 *v713; // [rsp+2838h] [rbp+27B8h]
  __int64 v714; // [rsp+2840h] [rbp+27C0h]
  __int64 v715; // [rsp+2848h] [rbp+27C8h]
  _QWORD *v716; // [rsp+2850h] [rbp+27D0h]
  __int64 v717; // [rsp+2858h] [rbp+27D8h]
  __int64 v718; // [rsp+2860h] [rbp+27E0h]
  char v719; // [rsp+286Fh] [rbp+27EFh]
  __int64 v720; // [rsp+2870h] [rbp+27F0h]
  __int64 v721; // [rsp+2878h] [rbp+27F8h]
  __int64 v722; // [rsp+2880h] [rbp+2800h]
  __int64 *v723; // [rsp+2888h] [rbp+2808h]
  _QWORD *v724; // [rsp+2890h] [rbp+2810h]
  __int64 v725; // [rsp+2898h] [rbp+2818h]
  char v726; // [rsp+28A7h] [rbp+2827h]
  __int64 v727; // [rsp+28A8h] [rbp+2828h]
  __int64 v728; // [rsp+28B0h] [rbp+2830h]
  __int64 v729; // [rsp+28B8h] [rbp+2838h]
  __int64 *v730; // [rsp+28C0h] [rbp+2840h]
  _QWORD *v731; // [rsp+28C8h] [rbp+2848h]
  __int64 *v732; // [rsp+28D0h] [rbp+2850h]
  __int64 v733; // [rsp+28D8h] [rbp+2858h]
  __int64 v734; // [rsp+28E0h] [rbp+2860h]
  __int64 v735; // [rsp+28E8h] [rbp+2868h]
  __int64 v736; // [rsp+28F0h] [rbp+2870h]
  __int64 v737; // [rsp+28F8h] [rbp+2878h]
  char *v738; // [rsp+2900h] [rbp+2880h]
  char v739; // [rsp+290Eh] [rbp+288Eh]
  char v740; // [rsp+290Fh] [rbp+288Fh]
  __int64 v741; // [rsp+2910h] [rbp+2890h]
  __int64 v742; // [rsp+2918h] [rbp+2898h]
  __int64 v743; // [rsp+2920h] [rbp+28A0h]
  __int64 v744; // [rsp+2928h] [rbp+28A8h]
  __int64 v745; // [rsp+2930h] [rbp+28B0h]
  __int64 v746; // [rsp+2938h] [rbp+28B8h]
  __int64 v747; // [rsp+2940h] [rbp+28C0h]
  __int64 v748; // [rsp+2948h] [rbp+28C8h]
  __int64 v749; // [rsp+2950h] [rbp+28D0h]
  __int64 v750; // [rsp+2958h] [rbp+28D8h]
  __int64 v751; // [rsp+2960h] [rbp+28E0h]
  __int64 v752; // [rsp+2968h] [rbp+28E8h]
  __int64 v753; // [rsp+2970h] [rbp+28F0h]
  __int64 v754; // [rsp+2978h] [rbp+28F8h]
  __int64 v755; // [rsp+2980h] [rbp+2900h]
  __int64 v756; // [rsp+2988h] [rbp+2908h]
  __int64 v757; // [rsp+2990h] [rbp+2910h]
  __int64 v758; // [rsp+2998h] [rbp+2918h]
  __int64 v759; // [rsp+29A0h] [rbp+2920h]
  __int64 v760; // [rsp+29A8h] [rbp+2928h]
  __int64 v761; // [rsp+29B0h] [rbp+2930h]
  __int64 v762; // [rsp+29B8h] [rbp+2938h]
  __int64 v763; // [rsp+29C0h] [rbp+2940h]
  __int64 v764; // [rsp+29C8h] [rbp+2948h]
  __int64 v765; // [rsp+29D0h] [rbp+2950h]
  __int64 v766; // [rsp+29D8h] [rbp+2958h]
  __int64 v767; // [rsp+29E0h] [rbp+2960h]
  __int64 v768; // [rsp+29E8h] [rbp+2968h]
  __int64 v769; // [rsp+29F0h] [rbp+2970h]
  __int64 v770; // [rsp+29F8h] [rbp+2978h]
  __int64 v771; // [rsp+2A00h] [rbp+2980h]
  __int64 v772; // [rsp+2A08h] [rbp+2988h]
  __int64 v773; // [rsp+2A10h] [rbp+2990h]
  __int64 v774; // [rsp+2A18h] [rbp+2998h]
  __int64 v775; // [rsp+2A20h] [rbp+29A0h]
  __int64 v776; // [rsp+2A28h] [rbp+29A8h]
  __int64 v777; // [rsp+2A30h] [rbp+29B0h]
  __int64 v778; // [rsp+2A38h] [rbp+29B8h]
  __int64 v779; // [rsp+2A40h] [rbp+29C0h]
  __int64 v780; // [rsp+2A48h] [rbp+29C8h]
  __int64 v781; // [rsp+2A50h] [rbp+29D0h]
  __int64 v782; // [rsp+2A58h] [rbp+29D8h]
  __int64 v783; // [rsp+2A60h] [rbp+29E0h]
  __int64 v784; // [rsp+2A68h] [rbp+29E8h]
  __int64 v785; // [rsp+2A70h] [rbp+29F0h]
  __int64 v786; // [rsp+2A78h] [rbp+29F8h]
  __int64 v787; // [rsp+2A80h] [rbp+2A00h]
  const void *v788; // [rsp+2A88h] [rbp+2A08h]
  __int64 v789; // [rsp+2A90h] [rbp+2A10h]
  __int64 v790; // [rsp+2A98h] [rbp+2A18h]
  __int64 v791; // [rsp+2AA0h] [rbp+2A20h]
  __int64 v792; // [rsp+2AA8h] [rbp+2A28h]
  __int64 v793; // [rsp+2AB0h] [rbp+2A30h]
  __int64 v794; // [rsp+2AB8h] [rbp+2A38h]
  __int64 v795; // [rsp+2AC0h] [rbp+2A40h]
  __int64 v796; // [rsp+2AC8h] [rbp+2A48h]
  __int64 v797; // [rsp+2AD0h] [rbp+2A50h]
  char *v798; // [rsp+2AD8h] [rbp+2A58h]
  __int64 v799; // [rsp+2AE0h] [rbp+2A60h]
  __int64 *v800; // [rsp+2AE8h] [rbp+2A68h]
  __int64 v801; // [rsp+2AF0h] [rbp+2A70h]
  char v802; // [rsp+2AFFh] [rbp+2A7Fh]
  __int64 v803; // [rsp+2B00h] [rbp+2A80h]
  __int64 v804; // [rsp+2B08h] [rbp+2A88h]
  char *v805; // [rsp+2B10h] [rbp+2A90h]
  __int64 v806; // [rsp+2B18h] [rbp+2A98h]
  __int64 v807; // [rsp+2B20h] [rbp+2AA0h]
  __int64 v808; // [rsp+2B28h] [rbp+2AA8h]
  char v809; // [rsp+2B37h] [rbp+2AB7h]
  __int64 v810; // [rsp+2B38h] [rbp+2AB8h]
  __int64 v811; // [rsp+2B40h] [rbp+2AC0h]
  __int64 v812; // [rsp+2B48h] [rbp+2AC8h]
  char v813; // [rsp+2B57h] [rbp+2AD7h]
  __int64 v814; // [rsp+2B58h] [rbp+2AD8h]
  __int64 v815; // [rsp+2B60h] [rbp+2AE0h]
  char v816; // [rsp+2B6Fh] [rbp+2AEFh]
  __int64 v817; // [rsp+2B70h] [rbp+2AF0h]
  __int64 v818; // [rsp+2B78h] [rbp+2AF8h]
  __int64 v819; // [rsp+2B80h] [rbp+2B00h]
  __int64 v820; // [rsp+2B88h] [rbp+2B08h]
  __int64 v821; // [rsp+2B90h] [rbp+2B10h]
  __int64 v822; // [rsp+2B98h] [rbp+2B18h]
  __int64 v823; // [rsp+2BA0h] [rbp+2B20h]
  _QWORD *v824; // [rsp+2BA8h] [rbp+2B28h]
  _QWORD *v825; // [rsp+2BB0h] [rbp+2B30h]
  _BYTE *v826; // [rsp+2BB8h] [rbp+2B38h]
  char v827; // [rsp+2BC7h] [rbp+2B47h]
  __int64 v828; // [rsp+2BC8h] [rbp+2B48h]
  __int64 v829; // [rsp+2BD0h] [rbp+2B50h]
  bool v830; // [rsp+2BDFh] [rbp+2B5Fh]
  __int64 v831; // [rsp+2BE0h] [rbp+2B60h]
  bool v832; // [rsp+2BEEh] [rbp+2B6Eh]
  bool v833; // [rsp+2BEFh] [rbp+2B6Fh]
  __int64 v834; // [rsp+2BF0h] [rbp+2B70h]
  __int64 v835; // [rsp+2BF8h] [rbp+2B78h]
  char v836; // [rsp+2C06h] [rbp+2B86h]
  char v837; // [rsp+2C07h] [rbp+2B87h]
  __int64 v838; // [rsp+2C08h] [rbp+2B88h]
  __int64 v839; // [rsp+2C10h] [rbp+2B90h]
  __int64 v840; // [rsp+2C18h] [rbp+2B98h]
  __int64 v841; // [rsp+2C20h] [rbp+2BA0h]
  __int64 v842; // [rsp+2C28h] [rbp+2BA8h]
  __int64 v843; // [rsp+2C30h] [rbp+2BB0h]
  __int64 v844; // [rsp+2C38h] [rbp+2BB8h]
  __int64 v845; // [rsp+2C40h] [rbp+2BC0h]
  __int64 v846; // [rsp+2C48h] [rbp+2BC8h]
  __int64 v847; // [rsp+2C50h] [rbp+2BD0h]
  __int64 v848; // [rsp+2C58h] [rbp+2BD8h]
  __int64 v849; // [rsp+2C60h] [rbp+2BE0h]
  __int64 v850; // [rsp+2C68h] [rbp+2BE8h]
  __int64 v851; // [rsp+2C70h] [rbp+2BF0h]
  __int64 v852; // [rsp+2C78h] [rbp+2BF8h]
  __int64 v853; // [rsp+2C80h] [rbp+2C00h]
  __int64 v854; // [rsp+2C88h] [rbp+2C08h]
  __int64 v855; // [rsp+2C90h] [rbp+2C10h]
  __int64 v856; // [rsp+2C98h] [rbp+2C18h]
  __int64 v857; // [rsp+2CA0h] [rbp+2C20h]
  bool v858; // [rsp+2CADh] [rbp+2C2Dh]
  bool v859; // [rsp+2CAEh] [rbp+2C2Eh]
  bool v860; // [rsp+2CAFh] [rbp+2C2Fh]
  __int64 v861; // [rsp+2CB0h] [rbp+2C30h]
  __int64 v862; // [rsp+2CB8h] [rbp+2C38h]
  __int64 v863; // [rsp+2CC0h] [rbp+2C40h]
  __int64 v864; // [rsp+2CC8h] [rbp+2C48h]
  __int64 v865; // [rsp+2CD0h] [rbp+2C50h]
  __int64 v866; // [rsp+2CD8h] [rbp+2C58h]
  __int64 v867; // [rsp+2CE0h] [rbp+2C60h]
  __int64 v868; // [rsp+2CE8h] [rbp+2C68h]
  __int64 v869; // [rsp+2CF0h] [rbp+2C70h]
  __int64 v870; // [rsp+2CF8h] [rbp+2C78h]
  __int64 v871; // [rsp+2D00h] [rbp+2C80h]
  __int64 v872; // [rsp+2D08h] [rbp+2C88h]
  __int64 v873; // [rsp+2D10h] [rbp+2C90h]
  __int64 v874; // [rsp+2D18h] [rbp+2C98h]
  __int64 v875; // [rsp+2D20h] [rbp+2CA0h]
  __int64 v876; // [rsp+2D28h] [rbp+2CA8h]
  __int64 v877; // [rsp+2D30h] [rbp+2CB0h]
  __int64 v878; // [rsp+2D38h] [rbp+2CB8h]
  __int64 v879; // [rsp+2D40h] [rbp+2CC0h]
  __int64 v880; // [rsp+2D48h] [rbp+2CC8h]
  __int64 v881; // [rsp+2D50h] [rbp+2CD0h]
  __int64 v882; // [rsp+2D58h] [rbp+2CD8h]
  __int64 v883; // [rsp+2D60h] [rbp+2CE0h]
  __int64 v884; // [rsp+2D68h] [rbp+2CE8h]
  __int64 v885; // [rsp+2D70h] [rbp+2CF0h]
  __int64 v886; // [rsp+2D78h] [rbp+2CF8h]
  __int64 v887; // [rsp+2D80h] [rbp+2D00h]
  __int64 v888; // [rsp+2D88h] [rbp+2D08h]
  __int64 v889; // [rsp+2D90h] [rbp+2D10h]
  __int64 v890; // [rsp+2D98h] [rbp+2D18h]
  __int64 v891; // [rsp+2DA0h] [rbp+2D20h]
  bool v892; // [rsp+2DAFh] [rbp+2D2Fh]
  __int64 v893; // [rsp+2DB0h] [rbp+2D30h]
  __int64 v894; // [rsp+2DB8h] [rbp+2D38h]
  __int64 v895; // [rsp+2DC0h] [rbp+2D40h]
  char v896; // [rsp+2DCFh] [rbp+2D4Fh]
  __int64 v897; // [rsp+2DD0h] [rbp+2D50h]
  __int64 v898; // [rsp+2DD8h] [rbp+2D58h]
  __int64 v899; // [rsp+2DE0h] [rbp+2D60h]
  __int64 v900; // [rsp+2DE8h] [rbp+2D68h]

  v8 = a1[1];
  v172 = *a1;
  v173 = (char *)v8;
  v9 = *a2;
  v10 = a2[1];
  v170 = v9;
  v171 = (char *)v10;
  v11 = a3[1];
  v168 = *a3;
  v169 = (char *)v11;
  v12 = a5[1];
  v166 = *a5;
  v167 = (char *)v12;
  v13 = a6[1];
  v164 = *a6;
  v165 = (char *)v13;
  v472 = "preorder";
  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v473 = 0i64;
  v475 = 0;
  nimFrame_80(v471);
  v826 = (_BYTE *)nimErrorFlag_78();
  nimZeroMem_60(a8, 192i64);
  v825 = 0i64;
  nimZeroMem_60(v487, 24i64);
  nimZeroMem_60(&v484, 24i64);
  v482 = 0i64;
  v483 = 0i64;
  v480 = 0i64;
  v481 = 0i64;
  v473 = 349i64;
  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v824 = 0i64;
  v824 = (_QWORD *)nimNewObj(448i64, 8i64);
  *v824 = &NTIv2__3R39bvXexl2hRfkAk9ca9cdrQ_;
  v825 = v824;
  v473 = 72i64;
  i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
  v162 = v170;
  v163 = v171;
  eqcopy___modelZsave95mongerZversionsZv0_u1079(v824 + 12, &v162);
  v473 = 536i64;
  i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
  v162 = v168;
  v163 = v169;
  eqcopy___modelZsave95mongerZcommon_u3875(v825 + 1, &v162);
  v473 = 352i64;
  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  reset_allocation_index__modelZsave95mongerZcommon_u5428();
  if ( *v826 )
    goto LABEL_1384;
  nimZeroMem_60(v194, 104i64);
  v823 = 0i64;
  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v899 = 0i64;
  v473 = 183i64;
  v822 = v825[1];
  v821 = v822;
  v473 = 184i64;
  while ( v899 < v821 )
  {
    v823 = v899;
    v473 = 185i64;
    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    if ( v899 < 0 || v899 >= v825[1] )
    {
      raiseIndexError2(v899, v825[1] - 1i64);
      goto LABEL_1384;
    }
    eqcopy___modelZsave95mongerZcommon_u3692(v194, v825[2] + 104 * v899 + 8);
    v473 = 364i64;
    i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
    if ( v823 < 0 )
      goto LABEL_18;
    if ( v823 >= v825[1] )
      goto LABEL_18;
    *(_BYTE *)(v825[2] + 104 * v823 + 96) = 0;
    v473 = 365i64;
    if ( v823 < 0 )
      goto LABEL_18;
    if ( v823 >= v825[1] )
      goto LABEL_18;
    *(_BYTE *)(v825[2] + 104 * v823 + 97) = 0;
    v473 = 366i64;
    if ( v823 < 0
      || v823 >= v825[1]
      || (v14 = (_QWORD *)(v825[2] + 104 * v823 + 48),
          v15 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 1),
          v14[2] = *(_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435,
          v14[3] = v15,
          v14[4] = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 2),
          v473 = 367i64,
          v823 < 0)
      || v823 >= v825[1] )
    {
LABEL_18:
      raiseIndexError2(v823, v825[1] - 1i64);
      goto LABEL_1384;
    }
    *(_QWORD *)(v825[2] + 104 * v823 + 88) = 0i64;
    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v899;
    v473 = 187i64;
    v820 = v825[1];
    if ( v820 != v821 )
    {
      v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_4;
      v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
      failedAssertImpl__stdZassertions_u234(&v162);
      if ( *v826 )
        goto LABEL_1384;
    }
  }
  v473 = 185i64;
  eqdestroy___modelZsave95mongerZcommon_u3689(v194);
  nimZeroMem_60(v470, 24i64);
  nimZeroMem_60(v194, 104i64);
  v819 = 0i64;
  v897 = 0i64;
  v473 = 183i64;
  v818 = v825[1];
  v817 = v818;
  v473 = 184i64;
  while ( v897 < v817 )
  {
    v819 = v897;
    v473 = 185i64;
    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    if ( v897 < 0 || v897 >= v825[1] )
    {
      raiseIndexError2(v897, v825[1] - 1i64);
      break;
    }
    eqcopy___modelZsave95mongerZcommon_u3692(v194, v825[2] + 104 * v897 + 8);
    v473 = 385i64;
    i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
    v816 = 0;
    v816 = is_tombstone__modelZsave95mongerZcommon_u4884(v194);
    if ( *v826 )
      break;
    if ( v816 != 1 )
    {
      v473 = 387i64;
      nimZeroMem_60(&v468, 16i64);
      v468 = add_wire_pins__modelZsimulationZpreorder_u8791;
      v469 = v825;
      v159 = v194[3];
      v160 = v194[4];
      v161 = (void *)v194[5];
      start__modelZsave95mongerZcommon_u4863 = get_start__modelZsave95mongerZcommon_u4863(&v159);
      if ( *v826 )
        break;
      p3__modelZsimulationZpreorder_u1974(
        v466,
        *(_QWORD *)refptr_NO_ID__modelZsave95mongerZcommon_u3361,
        start__modelZsave95mongerZcommon_u4863);
      if ( *v826 )
        break;
      v159 = v194[3];
      v160 = v194[4];
      v161 = (void *)v194[5];
      finish__modelZsave95mongerZcommon_u4866 = get_finish__modelZsave95mongerZcommon_u4866(&v159);
      if ( *v826 )
        break;
      p3__modelZsimulationZpreorder_u1974(
        v464,
        *(_QWORD *)refptr_NO_ID__modelZsave95mongerZcommon_u3361,
        finish__modelZsave95mongerZcommon_u4866);
      if ( *v826 )
        break;
      v162 = v466[0];
      v163 = (char *)v466[1];
      v157 = v464[0];
      v158 = (char *)v464[1];
      if ( v469 )
        ((void (__fastcall *)(__int64, __int64 *, __int64 *, _QWORD *))v468)(v819, &v162, &v157, v469);
      else
        ((void (__fastcall *)(__int64, __int64 *, __int64 *))v468)(v819, &v162, &v157);
      if ( *v826 )
        break;
    }
    else
    {
      v473 = 386i64;
    }
    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    ++v897;
    v473 = 187i64;
    v815 = v825[1];
    if ( v815 != v817 )
    {
      v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_6;
      v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
      failedAssertImpl__stdZassertions_u234(&v162);
      if ( *v826 )
        break;
    }
  }
  v473 = 185i64;
  eqdestroy___modelZsave95mongerZcommon_u3689(v194);
  if ( !*v826 )
  {
    i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
    v898 = 0i64;
    v473 = 392i64;
    do
    {
      v814 = v825[12];
      if ( v898 >= v814 )
        break;
      nimZeroMem_60(v178, 560i64);
      v473 = 393i64;
      if ( v898 < 0 )
        goto LABEL_68;
      if ( v898 >= v825[12] )
        goto LABEL_68;
      setLen__modelZsave95mongerZversionsZv0_u469(v825[13] + 560 * v898 + 256 + 8, 0i64);
      v473 = 394i64;
      if ( v898 < 0 )
        goto LABEL_68;
      if ( v898 >= v825[12] )
        goto LABEL_68;
      *(_QWORD *)(v825[13] + 560 * v898 + 296) = 0i64;
      v473 = 395i64;
      if ( v898 < 0 )
        goto LABEL_68;
      if ( v898 >= v825[12] )
        goto LABEL_68;
      *(_QWORD *)(v825[13] + 560 * v898 + 288) = 0i64;
      v473 = 34i64;
      i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      if ( v898 < 0 || v898 >= v825[12] )
        goto LABEL_68;
      eqcopy___modelZsave95mongerZversionsZv0_u148(v178, v825[13] + 560 * v898 + 8);
      v473 = 399i64;
      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      v896 = v178[0] == 78;
      if ( v178[0] == 78 )
      {
        if ( v898 < 0 || v898 >= v825[12] )
          goto LABEL_68;
        v896 = eqeq___modelZsave95mongerZversionsZv7_u353(
                 *(_QWORD *)(v825[13] + 560 * v898 + 32),
                 *(_QWORD *)refptr_NO_ID__modelZsave95mongerZcommon_u3361);
      }
      if ( v896 != 1 )
        goto LABEL_69;
      v473 = 400i64;
      if ( v898 >= 0 && v898 < v825[12] )
      {
        *(_QWORD *)(v825[13] + 560 * v898 + 32) = *(_QWORD *)(v825[13] + 560 * v898 + 16);
LABEL_69:
        nimZeroMem_60(&v179, 560i64);
        nimZeroMem_60(v193, 1448i64);
        v461 = 0i64;
        v462 = 0i64;
        v473 = 34i64;
        i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        if ( v898 < 0 || v898 >= v825[12] )
        {
LABEL_71:
          raiseIndexError2(v898, v825[12] - 1i64);
          goto LABEL_257;
        }
        eqcopy___modelZsave95mongerZversionsZv0_u148(&v179, v825[13] + 560 * v898 + 8);
        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        v460 = v181;
        v473 = 405i64;
        X5BX5Deq___modelZsimulationZpreorder_u11513(v825 + 53, v180, v898);
        if ( *v826 )
          goto LABEL_257;
        v473 = 407i64;
        if ( (unsigned __int8)v179 == 118 )
        {
          v473 = 409i64;
          v459 = p__modelZmodel95types_u1460(13i64, 4294967289i64);
          if ( *v826 )
            goto LABEL_257;
          v458 = rotate__modelZsave95mongerZcommon_u4629(v459, BYTE6(v179));
          if ( *v826 )
            goto LABEL_257;
          v457 = plus___modelZsave95mongerZcommon_u4308(*(unsigned int *)((char *)&v179 + 2), v458);
          if ( *v826 )
            goto LABEL_257;
          p3__modelZsimulationZpreorder_u1974(v456, v460, v457);
          if ( *v826 )
            goto LABEL_257;
          v162 = v456[0];
          v163 = (char *)v456[1];
          X5BX5Deq___modelZsimulationZpreorder_u13002(v825 + 9, &v162, v898);
          if ( *v826 )
            goto LABEL_257;
          v473 = 410i64;
          v455 = p__modelZmodel95types_u1460(13i64, 4294967290i64);
          if ( *v826 )
            goto LABEL_257;
          v454 = rotate__modelZsave95mongerZcommon_u4629(v455, BYTE6(v179));
          if ( *v826 )
            goto LABEL_257;
          v453 = plus___modelZsave95mongerZcommon_u4308(*(unsigned int *)((char *)&v179 + 2), v454);
          if ( *v826 )
            goto LABEL_257;
          p3__modelZsimulationZpreorder_u1974(v452, v460, v453);
          if ( *v826 )
            goto LABEL_257;
          v162 = v452[0];
          v163 = (char *)v452[1];
          X5BX5Deq___modelZsimulationZpreorder_u13002(v825 + 9, &v162, v898);
          if ( *v826 )
            goto LABEL_257;
          v473 = 411i64;
          v451 = p__modelZmodel95types_u1460(13i64, 4294967291i64);
          if ( *v826 )
            goto LABEL_257;
          v450 = rotate__modelZsave95mongerZcommon_u4629(v451, BYTE6(v179));
          if ( *v826 )
            goto LABEL_257;
          v449 = plus___modelZsave95mongerZcommon_u4308(*(unsigned int *)((char *)&v179 + 2), v450);
          if ( *v826 )
            goto LABEL_257;
          p3__modelZsimulationZpreorder_u1974(v448, v460, v449);
          if ( *v826 )
            goto LABEL_257;
          v162 = v448[0];
          v163 = (char *)v448[1];
          X5BX5Deq___modelZsimulationZpreorder_u13002(v825 + 9, &v162, v898);
          if ( *v826 )
            goto LABEL_257;
        }
        else
        {
          if ( (unsigned __int8)v179 > 0x76u )
            goto LABEL_120;
          if ( (unsigned __int8)v179 != 54 )
          {
            if ( (unsigned __int8)v179 != 56 )
              goto LABEL_120;
            v473 = 416i64;
            v439 = p__modelZmodel95types_u1460(13i64, 0i64);
            if ( !*v826 )
            {
              v438 = rotate__modelZsave95mongerZcommon_u4629(v439, BYTE6(v179));
              if ( !*v826 )
              {
                v437 = plus___modelZsave95mongerZcommon_u4308(*(unsigned int *)((char *)&v179 + 2), v438);
                if ( !*v826 )
                {
                  p3__modelZsimulationZpreorder_u1974(v436, v460, v437);
                  if ( !*v826 )
                  {
                    v162 = v436[0];
                    v163 = (char *)v436[1];
                    X5BX5Deq___modelZsimulationZpreorder_u13002(v825 + 9, &v162, v898);
                    if ( !*v826 )
                    {
                      v473 = 417i64;
                      v435 = p__modelZmodel95types_u1460(13i64, 1i64);
                      if ( !*v826 )
                      {
                        v434 = rotate__modelZsave95mongerZcommon_u4629(v435, BYTE6(v179));
                        if ( !*v826 )
                        {
                          v433 = plus___modelZsave95mongerZcommon_u4308(*(unsigned int *)((char *)&v179 + 2), v434);
                          if ( !*v826 )
                          {
                            p3__modelZsimulationZpreorder_u1974(v432, v460, v433);
                            if ( !*v826 )
                            {
                              v162 = v432[0];
                              v163 = (char *)v432[1];
                              X5BX5Deq___modelZsimulationZpreorder_u13002(v825 + 9, &v162, v898);
                              if ( !*v826 )
                              {
                                v473 = 418i64;
                                v431 = p__modelZmodel95types_u1460(13i64, 2i64);
                                if ( !*v826 )
                                {
                                  v430 = rotate__modelZsave95mongerZcommon_u4629(v431, BYTE6(v179));
                                  if ( !*v826 )
                                  {
                                    v429 = plus___modelZsave95mongerZcommon_u4308(
                                             *(unsigned int *)((char *)&v179 + 2),
                                             v430);
                                    if ( !*v826 )
                                    {
                                      p3__modelZsimulationZpreorder_u1974(v428, v460, v429);
                                      if ( !*v826 )
                                      {
                                        v162 = v428[0];
                                        v163 = (char *)v428[1];
                                        X5BX5Deq___modelZsimulationZpreorder_u13002(v825 + 9, &v162, v898);
                                        if ( !*v826 )
                                          goto LABEL_120;
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
            goto LABEL_257;
          }
          v473 = 413i64;
          v447 = p__modelZmodel95types_u1460(13i64, 0i64);
          if ( *v826 )
            goto LABEL_257;
          v446 = rotate__modelZsave95mongerZcommon_u4629(v447, BYTE6(v179));
          if ( *v826 )
            goto LABEL_257;
          v445 = plus___modelZsave95mongerZcommon_u4308(*(unsigned int *)((char *)&v179 + 2), v446);
          if ( *v826 )
            goto LABEL_257;
          p3__modelZsimulationZpreorder_u1974(v444, v460, v445);
          if ( *v826 )
            goto LABEL_257;
          v162 = v444[0];
          v163 = (char *)v444[1];
          X5BX5Deq___modelZsimulationZpreorder_u13002(v825 + 9, &v162, v898);
          if ( *v826 )
            goto LABEL_257;
          v473 = 414i64;
          v443 = p__modelZmodel95types_u1460(13i64, 1i64);
          if ( *v826 )
            goto LABEL_257;
          v442 = rotate__modelZsave95mongerZcommon_u4629(v443, BYTE6(v179));
          if ( *v826 )
            goto LABEL_257;
          v441 = plus___modelZsave95mongerZcommon_u4308(*(unsigned int *)((char *)&v179 + 2), v442);
          if ( *v826 )
            goto LABEL_257;
          p3__modelZsimulationZpreorder_u1974(v440, v460, v441);
          if ( *v826 )
            goto LABEL_257;
          v162 = v440[0];
          v163 = (char *)v440[1];
          X5BX5Deq___modelZsimulationZpreorder_u13002(v825 + 9, &v162, v898);
          if ( *v826 )
            goto LABEL_257;
        }
LABEL_120:
        v473 = 422i64;
        if ( (_BYTE)v179 == 78 )
        {
          nimZeroMem_60(v194, 1448i64);
          v426 = 0i64;
          v427 = 0i64;
          v473 = 423i64;
          v813 = 0;
          v159 = v470[0];
          v160 = v470[1];
          v161 = (void *)v470[2];
          v813 = contains__modelZsave95mongerZsave95monger_u1046(&v159, v180);
          if ( *v826 )
            goto LABEL_218;
          if ( v813 == 1 )
          {
            v473 = 424i64;
            if ( !*(_QWORD *)(a8 + 184) )
            {
              v473 = 425i64;
              *(_QWORD *)(a8 + 184) = v898;
            }
            v473 = 72i64;
            i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
            v162 = v426;
            v163 = v427;
            eqdestroy___modelZsave95mongerZversionsZv0_u1076(&v162);
            v473 = 170i64;
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            eqdestroy___modelZboardZprototype95list_u3239(v194);
            v473 = 934i64;
            v162 = v461;
            v163 = v462;
            eqdestroy___modelZboardZprototype95list_u1711(&v162);
            v473 = 34i64;
            i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
            eqdestroy___modelZsave95mongerZversionsZv0_u145(&v179);
            v473 = 426i64;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
LABEL_258:
            v473 = 563i64;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v463 = v898 + 1;
            if ( __OFADD__(1i64, v898) )
              raiseOverflow();
            else
              v898 = v463;
            goto LABEL_261;
          }
          v473 = 427i64;
          incl__modelZsave95mongerZsave95monger_u1438(v470, v180);
          if ( !*v826 )
          {
            v473 = 429i64;
            get_custom_prototype__modelZboardZcustom95prototype95list_u451(v189, v194);
            if ( !*v826 )
            {
              v473 = 431i64;
              v425 = v180;
              nimZeroMem_60(v174, 104i64);
              nimZeroMem_60(&v424, 8i64);
              v473 = 433i64;
              nimZeroMem_60(v174, 104i64);
              nimZeroMem_60(v191, 104i64);
              v812 = 0i64;
              v473 = 536i64;
              i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
              nimZeroMem_60(v191, 104i64);
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              v895 = 0i64;
              v811 = v194[32];
              v810 = v194[32];
              v473 = 184i64;
              while ( v895 < v810 )
              {
                v812 = v895;
                v473 = 185i64;
                i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                if ( v895 < 0 || v895 >= v194[32] )
                {
                  raiseIndexError2(v895, v194[32] - 1);
                  break;
                }
                eqcopy___modelZsave95mongerZcommon_u3692(v191, v194[33] + 104 * v895 + 8);
                v424 = v812;
                v473 = 185i64;
                i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                eqsink___modelZsave95mongerZcommon_u3698(v174, v191);
                eqwasMoved___modelZsave95mongerZcommon_u3686(v191);
                nimZeroMem_60(v192, 104i64);
                v473 = 434i64;
                i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                v809 = 0;
                v809 = is_tombstone__modelZsave95mongerZcommon_u4884(v174);
                if ( *v826 )
                  break;
                if ( v809 != 1 )
                {
                  v473 = 185i64;
                  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                  eqdup___modelZsave95mongerZcommon_u3695(v174, v192);
                  v473 = 436i64;
                  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                  add__modelZsave95mongerZcommon_u4119(v825 + 1, v192);
                  v473 = 437i64;
                  v808 = 0i64;
                  if ( v825[2] )
                    v16 = v825[2] + 8i64;
                  else
                    v16 = 0i64;
                  v808 = X5BX5D___modelZsimulationZpreorder_u14837(v16, v825[1], 1i64);
                  if ( *v826 )
                    break;
                  if ( v898 < 0 || v898 >= v825[12] )
                  {
                    raiseIndexError2(v898, v825[12] - 1i64);
                    break;
                  }
                  *(_QWORD *)(v808 + 96) = *(_QWORD *)(v825[13] + 560 * v898 + 32);
                  v473 = 438i64;
                  nimZeroMem_60(&v422, 16i64);
                  v422 = add_wire_pins__modelZsimulationZpreorder_u8791;
                  v423 = v825;
                  v473 = 439i64;
                  v807 = v825[1] - 1i64;
                  v473 = 440i64;
                  v159 = v175;
                  v160 = v176;
                  v161 = v177;
                  v421 = get_start__modelZsave95mongerZcommon_u4863(&v159);
                  if ( *v826 )
                    break;
                  p3__modelZsimulationZpreorder_u1974(v420, v425, v421);
                  if ( *v826 )
                    break;
                  v473 = 441i64;
                  v159 = v175;
                  v160 = v176;
                  v161 = v177;
                  v419 = get_finish__modelZsave95mongerZcommon_u4866(&v159);
                  if ( *v826 )
                    break;
                  p3__modelZsimulationZpreorder_u1974(v418, v425, v419);
                  if ( *v826 )
                    break;
                  v162 = v420[0];
                  v163 = (char *)v420[1];
                  v157 = v418[0];
                  v158 = (char *)v418[1];
                  if ( v423 )
                    ((void (__fastcall *)(__int64, __int64 *, __int64 *, _QWORD *))v422)(v807, &v162, &v157, v423);
                  else
                    ((void (__fastcall *)(__int64, __int64 *, __int64 *))v422)(v807, &v162, &v157);
                  if ( *v826 )
                    break;
                }
                else
                {
                  v473 = 435i64;
                }
                i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                ++v895;
                v473 = 187i64;
                v806 = v194[32];
                if ( v194[32] != v810 )
                {
                  v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_9;
                  v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                  failedAssertImpl__stdZassertions_u234(&v162);
                  if ( *v826 )
                    break;
                }
              }
              v473 = 185i64;
              eqdestroy___modelZsave95mongerZcommon_u3689(v191);
              eqdestroy___modelZsave95mongerZcommon_u3689(v174);
              if ( !*v826 )
              {
                v473 = 444i64;
                i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                X5BX5Deq___modelZsimulationZpreorder_u11513(v487, v425, v898);
                if ( !*v826 )
                {
                  v426 = v194[28];
                  v427 = (char *)v194[29];
                  v473 = 72i64;
                  i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                  eqwasMoved___modelZsave95mongerZversionsZv0_u1073(&v194[28]);
                  v805 = 0i64;
                  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                  v894 = 0i64;
                  v804 = v426;
                  v803 = v426;
                  v473 = 260i64;
                  while ( v894 < v803 )
                  {
                    v473 = 448i64;
                    i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                    if ( v894 < 0 || v894 >= v426 )
                    {
                      raiseIndexError2(v894, v426 - 1);
                      goto LABEL_218;
                    }
                    v805 = &v427[560 * v894 + 8];
                    v473 = 449i64;
                    if ( *v805 == 90 )
                    {
                      v473 = 452i64;
                      v802 = 0;
                      v159 = v190[0];
                      v160 = v190[1];
                      v161 = (void *)v190[2];
                      v802 = contains__modelZsimulationZpreorder_u14968(&v159, *((_QWORD *)v805 + 1));
                      if ( *v826 )
                        goto LABEL_218;
                      if ( v802 == 1 )
                      {
                        v801 = 0i64;
                        v473 = 454i64;
                        v800 = 0i64;
                        v800 = (__int64 *)X5BX5D___modelZsimulationZpreorder_u15055(v190, *((_QWORD *)v805 + 1));
                        if ( *v826 )
                          goto LABEL_218;
                        v417 = *v800;
                        v801 = v417;
                        v473 = 453i64;
                        add__modelZsave95mongerZserialize_u151(v805 + 168, v417);
                      }
                    }
                    else
                    {
                      v473 = 450i64;
                    }
                    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                    ++v894;
                    v473 = 263i64;
                    v799 = v426;
                    if ( v426 != v803 )
                    {
                      v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_11;
                      v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_10;
                      failedAssertImpl__stdZassertions_u234(&v162);
                      if ( *v826 )
                        goto LABEL_218;
                    }
                  }
                  v798 = 0i64;
                  v893 = 0i64;
                  v797 = v426;
                  v796 = v426;
                  v473 = 251i64;
                  while ( 2 )
                  {
                    if ( v893 >= v796 )
                    {
                      v473 = 72i64;
                      i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                      v162 = v426;
                      v163 = v427;
                      eqdestroy___modelZsave95mongerZversionsZv0_u1076(&v162);
                      v473 = 170i64;
                      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                      eqdestroy___modelZboardZprototype95list_u3239(v194);
                      v473 = 934i64;
                      v162 = v461;
                      v163 = v462;
                      eqdestroy___modelZboardZprototype95list_u1711(&v162);
                      v473 = 34i64;
                      i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                      eqdestroy___modelZsave95mongerZversionsZv0_u145(&v179);
                      v473 = 519i64;
                      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                      goto LABEL_258;
                    }
                    v473 = 459i64;
                    i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                    if ( v893 < 0 || v893 >= v426 )
                    {
                      raiseIndexError2(v893, v426 - 1);
                      break;
                    }
                    v798 = &v427[560 * v893 + 8];
                    nimZeroMem_60(v191, 560i64);
                    v473 = 460i64;
                    if ( !*v798 )
                    {
                      v473 = 34i64;
                      i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                      eqdestroy___modelZsave95mongerZversionsZv0_u145(v191);
                      v473 = 461i64;
                      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                      goto LABEL_213;
                    }
                    v473 = 34i64;
                    i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                    eqcopy___modelZsave95mongerZversionsZv0_u148(v191, v798);
                    v473 = 464i64;
                    i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                    v416 = mix__modelZsave95mongerZcommon_u3384(v425, v191[1]);
                    if ( !*v826 )
                    {
                      v473 = 466i64;
                      if ( LOBYTE(v191[0]) != 118 )
                        goto LABEL_185;
                      v414 = 0i64;
                      v415 = 0i64;
                      v473 = 467i64;
                      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                      v412 = 0i64;
                      v413 = 0i64;
                      dollar___modelZsave95mongerZcommon_u3396(&v414, v191[1]);
                      if ( !*v826 )
                      {
                        address = (__int64 *)_emutls_get_address(refptr___emutls_v_global_save_base_path__modelZmodel95types_u77);
                        rawNewString(&v162, v194[2] + *address + v414 + 25);
                        v412 = v162;
                        v413 = v163;
                        v18 = (char *)address[1];
                        v162 = *address;
                        v163 = v18;
                        appendString_25(&v412, &v162);
                        v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_14;
                        v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_13;
                        appendString_25(&v412, &v162);
                        v162 = v194[2];
                        v163 = (char *)v194[3];
                        appendString_25(&v412, &v162);
                        v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_16;
                        v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_15;
                        appendString_25(&v412, &v162);
                        v162 = v414;
                        v163 = v415;
                        appendString_25(&v412, &v162);
                        v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_18;
                        v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_17;
                        appendString_25(&v412, &v162);
                        v473 = 1699i64;
                        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                        v162 = v412;
                        v163 = v413;
                        eqsink___system_u2667(&v191[63], &v162);
                        v473 = 394i64;
                        if ( v415 && (*(_QWORD *)v415 & 0x4000000000000000i64) == 0 )
                          deallocShared(v415);
LABEL_185:
                        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                        v191[1] = v416;
                        v191[2] = v425;
                        v191[3] = (__int64)v182;
                        v473 = 473i64;
                        if ( LOBYTE(v191[0]) == 79 )
                        {
                          nimZeroMem_60(&v411, 8i64);
                          v473 = 477i64;
                          v792 = 0i64;
                          v792 = X5BX5D___modelZboardZprototype95list_u4239(
                                   refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
                                   79i64);
                          if ( !*v826 )
                          {
                            if ( *(__int64 *)(v792 + 128) > 0 )
                            {
                              v473 = 475i64;
                              position__modelZboardZcache95opps_u6 = get_position__modelZboardZcache95opps_u6(
                                                                       *(unsigned int *)((char *)v191 + 2),
                                                                       *(_QWORD *)(v792 + 136) + 8i64,
                                                                       BYTE6(v191[0]));
                              if ( !*v826 )
                              {
                                v473 = 481i64;
                                custom_position__modelZboardZcustom95prototype_u78 = get_custom_position__modelZboardZcustom95prototype_u78(*(unsigned int *)((char *)v191 + 2));
                                if ( !*v826 )
                                {
                                  v407 = rotate__modelZsave95mongerZcommon_u4629(
                                           custom_position__modelZboardZcustom95prototype_u78,
                                           BYTE6(v179));
                                  if ( !*v826 )
                                  {
                                    v409 = plus___modelZsave95mongerZcommon_u4308(
                                             v407,
                                             *(unsigned int *)((char *)&v179 + 2));
                                    if ( !*v826 )
                                    {
                                      v473 = 484i64;
                                      v791 = v825[12];
                                      v790 = v791;
                                      v473 = 485i64;
                                      nimZeroMem_60(v192, 560i64);
                                      LOBYTE(v192[0]) = 80;
                                      v192[28] = v191[28];
                                      v473 = 294i64;
                                      i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
                                      v411 = eqdup___modelZsave95mongerZcommon_u3374(v182);
                                      v192[3] = v411;
                                      nimZeroMem_60(&v192[10], 80i64);
                                      v192[11] = 1i64;
                                      nimZeroMem_60(&v192[12], 8i64);
                                      v192[12] = 256i64;
                                      LOBYTE(v192[13]) = 1;
                                      v192[14] = 1i64;
                                      nimZeroMem_60(&v192[15], 8i64);
                                      v192[15] = 256i64;
                                      LOBYTE(v192[16]) = 1;
                                      nimZeroMem_60(&v192[60], 24i64);
                                      LOBYTE(v192[60]) = 0;
                                      v473 = 485i64;
                                      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                                      add__modelZsave95mongerZversionsZv0_u1028(v825 + 12, v192);
                                      v473 = 493i64;
                                      p3__modelZsimulationZpreorder_u1974(
                                        v406,
                                        v425,
                                        position__modelZboardZcache95opps_u6);
                                      if ( !*v826 )
                                      {
                                        v473 = 494i64;
                                        p3__modelZsimulationZpreorder_u1974(v405, v460, v409);
                                        if ( !*v826 )
                                        {
                                          v473 = 496i64;
                                          nimZeroMem_60(v404, 24i64);
                                          v404[0] = v790;
                                          v162 = v406[0];
                                          v163 = (char *)v406[1];
                                          v159 = v790;
                                          v160 = v404[1];
                                          v161 = (void *)v404[2];
                                          X5BX5Deq___modelZsimulationZpreorder_u15268(v825 + 17, &v162, &v159);
                                          if ( !*v826 )
                                          {
                                            v473 = 498i64;
                                            nimZeroMem_60(v402, 24i64);
                                            v402[0] = v790;
                                            LOBYTE(v403) = 1;
                                            v162 = v405[0];
                                            v163 = (char *)v405[1];
                                            v159 = v790;
                                            v160 = v402[1];
                                            v161 = v403;
                                            X5BX5Deq___modelZsimulationZpreorder_u15268(v825 + 17, &v162, &v159);
                                          }
                                        }
                                      }
                                    }
                                  }
                                }
                              }
                            }
                            else
                            {
                              raiseIndexError2(0i64, *(_QWORD *)(v792 + 128) - 1i64);
                            }
                          }
                        }
                        else if ( LOBYTE(v191[0]) == 81 )
                        {
                          v473 = 502i64;
                          v795 = 0i64;
                          v795 = X5BX5D___modelZboardZprototype95list_u4239(
                                   refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
                                   81i64);
                          if ( !*v826 )
                          {
                            if ( *(__int64 *)(v795 + 96) > 0 )
                            {
                              v473 = 500i64;
                              v401 = get_position__modelZboardZcache95opps_u6(
                                       *(unsigned int *)((char *)v191 + 2),
                                       *(_QWORD *)(v795 + 104) + 8i64,
                                       BYTE6(v191[0]));
                              if ( !*v826 )
                              {
                                v473 = 506i64;
                                v399 = get_custom_position__modelZboardZcustom95prototype_u78(*(unsigned int *)((char *)v191 + 2));
                                if ( !*v826 )
                                {
                                  v398 = rotate__modelZsave95mongerZcommon_u4629(v399, BYTE6(v179));
                                  if ( !*v826 )
                                  {
                                    v400 = plus___modelZsave95mongerZcommon_u4308(
                                             v398,
                                             *(unsigned int *)((char *)&v179 + 2));
                                    if ( !*v826 )
                                    {
                                      v473 = 509i64;
                                      v794 = v825[1];
                                      v793 = v794;
                                      v473 = 510i64;
                                      nimZeroMem_60(v192, 104i64);
                                      teleport_path__modelZsave95mongerZcommon_u5069(&v159, v401, v400);
                                      v192[3] = v159;
                                      v192[4] = v160;
                                      v192[5] = (__int64)v161;
                                      if ( !*v826 )
                                      {
                                        v192[7] = 1i64;
                                        nimZeroMem_60(&v192[8], 8i64);
                                        v192[8] = 256i64;
                                        LOBYTE(v192[9]) = 1;
                                        add__modelZsave95mongerZcommon_u4119(v825 + 1, v192);
                                        v473 = 511i64;
                                        nimZeroMem_60(&v396, 16i64);
                                        v396 = add_wire_pins__modelZsimulationZpreorder_u8791;
                                        v397 = v825;
                                        v473 = 513i64;
                                        p3__modelZsimulationZpreorder_u1974(v395, v425, v401);
                                        if ( !*v826 )
                                        {
                                          v473 = 514i64;
                                          p3__modelZsimulationZpreorder_u1974(v394, v460, v400);
                                          if ( !*v826 )
                                          {
                                            v162 = v395[0];
                                            v163 = (char *)v395[1];
                                            v157 = v394[0];
                                            v158 = (char *)v394[1];
                                            if ( v397 )
                                              ((void (__fastcall *)(__int64, __int64 *, __int64 *, _QWORD *))v396)(
                                                v793,
                                                &v162,
                                                &v157,
                                                v397);
                                            else
                                              ((void (__fastcall *)(__int64, __int64 *, __int64 *))v396)(
                                                v793,
                                                &v162,
                                                &v157);
                                          }
                                        }
                                      }
                                    }
                                  }
                                }
                              }
                            }
                            else
                            {
                              raiseIndexError2(0i64, *(_QWORD *)(v795 + 96) - 1i64);
                            }
                          }
                        }
                        else
                        {
                          v473 = 517i64;
                          nimZeroMem_60(v192, 560i64);
                          qmemcpy(v192, v191, sizeof(v192));
                          v473 = 34i64;
                          i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                          eqwasMoved___modelZsave95mongerZversionsZv0_u142(v191, v191);
                          v473 = 517i64;
                          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                          add__modelZsave95mongerZversionsZv0_u1028(v825 + 12, v192);
                        }
                      }
                    }
                    v473 = 34i64;
                    i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                    eqdestroy___modelZsave95mongerZversionsZv0_u145(v191);
                    if ( *v826 )
                      break;
LABEL_213:
                    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                    ++v893;
                    v473 = 254i64;
                    v789 = v426;
                    if ( v426 != v796 )
                    {
                      v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_21;
                      v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
                      failedAssertImpl__stdZassertions_u234(&v162);
                      if ( *v826 )
                        break;
                    }
                    continue;
                  }
                }
              }
            }
          }
LABEL_218:
          v473 = 72i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
          v162 = v426;
          v163 = v427;
          eqdestroy___modelZsave95mongerZversionsZv0_u1076(&v162);
          v473 = 170i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          eqdestroy___modelZboardZprototype95list_u3239(v194);
          if ( *v826 )
            goto LABEL_257;
        }
        v473 = 521i64;
        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        v788 = 0i64;
        v788 = (const void *)X5BX5D___modelZboardZprototype95list_u4239(
                               refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
                               (unsigned __int8)v179);
        if ( *v826 )
          goto LABEL_257;
        qmemcpy(v193, v788, 0x5A8ui64);
        v473 = 523i64;
        v892 = (unsigned __int8)v183 == 0;
        if ( !(_BYTE)v183 )
        {
          v787 = v193[14];
          v892 = v193[14] > 0;
        }
        if ( v892 )
        {
          nimZeroMem_60(v192, 560i64);
          v473 = 34i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
          eqcopy___modelZsave95mongerZversionsZv0_u148(v192, &v179);
          v473 = 525i64;
          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          v786 = v825[12];
          v785 = v786;
          LOBYTE(v192[4]) = 1;
          v192[5] = v898;
          v473 = 34i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
          v393 = 0i64;
          v392 = 0i64;
          v393 = (char *)newSeqPayload(0i64, 80i64, 8i64);
          v162 = v392;
          v163 = v393;
          eqsink___modelZsave95mongerZversionsZv0_u181(&v192[8], &v162);
          v473 = 529i64;
          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          nimZeroMem_60(&v391, 8i64);
          v391 = inverse__modelZsave95mongerZcommon_u3393(v192[1]);
          if ( *v826 )
            goto LABEL_257;
          v192[1] = v391;
          v473 = 531i64;
          nimZeroMem_60(v194, 560i64);
          qmemcpy(v194, v192, 0x230ui64);
          add__modelZsave95mongerZversionsZv0_u1028(v825 + 12, v194);
          v473 = 532i64;
          if ( v898 < 0 || v898 >= v825[12] )
            goto LABEL_71;
          *(_QWORD *)(v825[13] + 560 * v898 + 48) = v785;
        }
        v461 = 0i64;
        v462 = 0i64;
        v473 = 536i64;
        if ( (_BYTE)v183 )
        {
          v162 = v193[14];
          v163 = (char *)v193[15];
        }
        else
        {
          v473 = 934i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          v162 = v193[12];
          v163 = (char *)v193[13];
        }
        eqcopy___modelZboardZprototype95list_u1714(&v461, &v162);
        nimZeroMem_60(v194, 56i64);
        v784 = 0i64;
        v473 = 541i64;
        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        nimZeroMem_60(v194, 56i64);
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v891 = 0i64;
        v783 = v461;
        v782 = v461;
        v473 = 184i64;
        while ( v891 < v782 )
        {
          v784 = v891;
          v473 = 934i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v891 < 0 || v891 >= v461 )
          {
            raiseIndexError2(v891, v461 - 1);
            goto LABEL_257;
          }
          eqcopy___modelZboardZprototype95list_u1780(v194, &v462[56 * v891 + 8]);
          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          v473 = 543i64;
          v389 = get_position__modelZboardZcache95opps_u6(*(unsigned int *)((char *)&v179 + 2), v194, BYTE6(v179));
          if ( !*v826 )
          {
            v473 = 542i64;
            p3__modelZsimulationZpreorder_u1974(v390, v460, v389);
            if ( !*v826 )
            {
              v387[2] = v898;
              LOBYTE(v388) = 1;
              v387[3] = v784;
              v473 = 549i64;
              v162 = v390[0];
              v163 = (char *)v390[1];
              v159 = v898;
              v160 = v784;
              v161 = v388;
              X5BX5Deq___modelZsimulationZpreorder_u15268(v825 + 17, &v162, &v159);
              if ( !*v826 )
              {
                i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                ++v891;
                v473 = 187i64;
                v781 = v461;
                if ( v461 == v782 )
                  continue;
                v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_22;
                v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                failedAssertImpl__stdZassertions_u234(&v162);
                if ( !*v826 )
                  continue;
              }
            }
          }
          goto LABEL_257;
        }
        v473 = 934i64;
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        eqdestroy___modelZboardZprototype95list_u1777(v194);
        v473 = 551i64;
        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        if ( !(_BYTE)v183 )
        {
          nimZeroMem_60(v194, 56i64);
          v780 = 0i64;
          v473 = 552i64;
          nimZeroMem_60(v194, 56i64);
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          v890 = 0i64;
          v779 = v193[16];
          v778 = v193[16];
          v473 = 184i64;
          while ( v890 < v778 )
          {
            v780 = v890;
            v473 = 934i64;
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            if ( v890 < 0 || v890 >= v193[16] )
            {
              raiseIndexError2(v890, v193[16] - 1);
              goto LABEL_257;
            }
            eqcopy___modelZboardZprototype95list_u1780(v194, v193[17] + 56 * v890 + 8);
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v473 = 555i64;
            v386 = get_position__modelZboardZcache95opps_u6(*(unsigned int *)((char *)&v179 + 2), v194, BYTE6(v179));
            if ( !*v826 )
            {
              v473 = 553i64;
              p3__modelZsimulationZpreorder_u1974(v387, v460, v386);
              if ( !*v826 )
              {
                v473 = 558i64;
                nimZeroMem_60(v385, 24i64);
                v385[0] = v898;
                v385[1] = v780;
                v473 = 561i64;
                v162 = v387[0];
                v163 = (char *)v387[1];
                v159 = v898;
                v160 = v780;
                v161 = (void *)v385[2];
                X5BX5Deq___modelZsimulationZpreorder_u15268(v825 + 17, &v162, &v159);
                if ( !*v826 )
                {
                  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                  ++v890;
                  v473 = 187i64;
                  v777 = v193[16];
                  if ( v193[16] == v778 )
                    continue;
                  v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_23;
                  v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                  failedAssertImpl__stdZassertions_u234(&v162);
                  if ( !*v826 )
                    continue;
                }
              }
            }
            goto LABEL_257;
          }
          v473 = 934i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          eqdestroy___modelZboardZprototype95list_u1777(v194);
        }
LABEL_257:
        v162 = v461;
        v163 = v462;
        eqdestroy___modelZboardZprototype95list_u1711(&v162);
        v473 = 34i64;
        i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        eqdestroy___modelZsave95mongerZversionsZv0_u145(&v179);
        if ( !*v826 )
          goto LABEL_258;
        goto LABEL_261;
      }
LABEL_68:
      raiseIndexError2(v898, v825[12] - 1i64);
LABEL_261:
      v473 = 34i64;
      i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      eqdestroy___modelZsave95mongerZversionsZv0_u145(v178);
    }
    while ( !*v826 );
  }
  v473 = 160i64;
  i = "D:\\TuringComplete_Phu\\model\\save_monger\\save_monger.nim";
  eqdestroy___modelZsave95mongerZsave95monger_u2597(v470);
  if ( *v826 )
    goto LABEL_1384;
  v473 = 565i64;
  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  if ( v164 )
  {
    v383 = 0i64;
    v384 = 0i64;
    v473 = 567i64;
    v381 = 0i64;
    v382 = 0i64;
    rawNewString(&v162, v172 + v164 + 1);
    v381 = v162;
    v382 = v163;
    v162 = v172;
    v163 = v173;
    appendString_25(&v381, &v162);
    v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_25;
    v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_15;
    appendString_25(&v381, &v162);
    v162 = v164;
    v163 = v165;
    appendString_25(&v381, &v162);
    v383 = v381;
    v384 = v382;
    v162 = v166;
    v163 = v167;
    v157 = v381;
    v158 = v382;
    v155 = v164;
    v156 = v165;
    create_missing_buffers__modelZboardZmemory95manager_u2550(a4, v825 + 12, &v162, &v157, &v155, a7);
    v473 = 394i64;
    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v384 && (*(_QWORD *)v384 & 0x4000000000000000i64) == 0 )
      deallocShared(v384);
    if ( *v826 )
      goto LABEL_1384;
  }
  v473 = 668i64;
  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v776 = v825[12];
  if ( v776 < 0 )
  {
    raiseRangeErrorI(v776, 0i64, 0x7FFFFFFFFFFFFFFFi64);
    goto LABEL_1384;
  }
  setLen__modelZsimulationZpreorder_u2068(v825 + 33, v776);
  v473 = 669i64;
  v775 = v825[12];
  if ( v775 < 0 )
  {
    raiseRangeErrorI(v775, 0i64, 0x7FFFFFFFFFFFFFFFi64);
    goto LABEL_1384;
  }
  setLen__modelZsimulationZpreorder_u2068(v825 + 49, v775);
  nimZeroMem_60(v193, 560i64);
  v774 = 0i64;
  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v889 = 0i64;
  v473 = 183i64;
  v773 = v825[12];
  v772 = v773;
  v473 = 184i64;
  while ( v889 < v772 )
  {
    nimZeroMem_60(v194, 1448i64);
    v774 = v889;
    v473 = 34i64;
    i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    if ( v889 >= 0 && v889 < v825[12] )
    {
      eqcopy___modelZsave95mongerZversionsZv0_u148(v193, v825[13] + 560 * v889 + 8);
      v473 = 672i64;
      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      if ( LOBYTE(v193[0]) == 118 )
      {
        v379 = 0i64;
        v380 = 0i64;
        v473 = 673i64;
        if ( v774 >= 0 && v774 < v825[12] )
        {
          setLen__modelZsave95mongerZversionsZv0_u901(v825[13] + 560 * v774 + 448 + 8, 0i64);
          v379 = 0i64;
          v380 = 0i64;
          v473 = 676i64;
          nimZeroMem_60(&v377, 16i64);
          v377 = get_component_at_offset__modelZsimulationZpreorder_u16736;
          v378 = v825;
          v376 = p__modelZmodel95types_u1460(13i64, 4294967288i64);
          if ( !*v826 )
          {
            v19 = v378
                ? ((__int64 (__fastcall *)(__int64 *, _QWORD, _QWORD *))v377)(v193, v376, v378)
                : ((__int64 (__fastcall *)(__int64 *, _QWORD))v377)(v193, v376);
            v771 = v19;
            if ( !*v826 )
            {
              v473 = 677i64;
              nimZeroMem_60(&v374, 16i64);
              v374 = find_top_port__modelZsimulationZpreorder_u18852;
              v375 = v825;
              if ( v825 )
                v374(v771, (__int64)&v379, (__int64)v375);
              else
                ((void (__fastcall *)(__int64, __int64 *))v374)(v771, &v379);
              if ( !*v826 )
              {
                v473 = 679i64;
                v20 = v380 ? (__int64)(v380 + 8) : 0i64;
                reverse__modelZsimulationZpreorder_u18912(v20, v379);
                if ( !*v826 )
                {
                  v473 = 681i64;
                  get_cost__modelZscores_u2321(v373, (__int64)v193);
                  if ( !*v826 )
                  {
                    v770 = v373[1];
                    v769 = 0i64;
                    v768 = 0i64;
                    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                    v888 = 0i64;
                    v767 = v379;
                    v766 = v379;
                    v473 = 184i64;
                    while ( v888 < v766 )
                    {
                      v473 = 683i64;
                      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                      v769 = v888;
                      if ( v888 < 0 || v888 >= v379 )
                      {
                        raiseIndexError2(v888, v379 - 1);
                        break;
                      }
                      v768 = *(_QWORD *)&v380[8 * v888 + 8];
                      v473 = 684i64;
                      if ( v768 < 0
                        || v768 >= v825[12]
                        || (*(_QWORD *)(v825[13] + 560 * v768 + 472) = v769, v473 = 685i64, v768 < 0)
                        || v768 >= v825[12]
                        || (*(_QWORD *)(v825[13] + 560 * v768 + 304) = v774, v473 = 686i64, v768 < 0)
                        || v768 >= v825[12]
                        || (*(_QWORD *)(v825[13] + 560 * v768 + 288) = v193[39], v473 = 687i64, v768 < 0)
                        || v768 >= v825[12] )
                      {
LABEL_314:
                        raiseIndexError2(v768, v825[12] - 1i64);
                        break;
                      }
                      if ( *(_BYTE *)(v825[13] + 560 * v768 + 8) == 54 )
                      {
                        v473 = 688i64;
                        if ( v768 >= v825[12] )
                          goto LABEL_314;
                        *(_QWORD *)(v825[13] + 560 * v768 + 296) = v770;
                      }
                      v473 = 689i64;
                      if ( v774 < 0 || v774 >= v825[12] )
                        goto LABEL_280;
                      nimZeroMem_60(v192, 48i64);
                      v192[0] = v768;
                      add__modelZsimulationZpreorder_u18969(v825[13] + 560 * v774 + 448 + 8, v192);
                      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                      ++v888;
                      v473 = 187i64;
                      v765 = v379;
                      if ( v379 != v766 )
                      {
                        v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_36;
                        v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                        failedAssertImpl__stdZassertions_u234(&v162);
                        if ( *v826 )
                          break;
                      }
                    }
                  }
                }
              }
            }
          }
        }
        else
        {
LABEL_280:
          raiseIndexError2(v774, v825[12] - 1i64);
        }
        v473 = 982i64;
        i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
        v162 = v379;
        v163 = v380;
        eqdestroy___modelZsave95mongerZcommon_u5612(&v162);
        if ( *v826 )
          goto LABEL_412;
      }
      v473 = 693i64;
      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      nimZeroMem_60(v194, 1448i64);
      v473 = 694i64;
      if ( LOBYTE(v193[0]) == 78 )
      {
        v473 = 695i64;
        get_custom_prototype__modelZboardZcustom95prototype95list_u451(v193[49], v194);
        if ( *v826 )
          goto LABEL_412;
      }
      else
      {
        v473 = 697i64;
        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        v764 = 0i64;
        v764 = X5BX5D___modelZboardZprototype95list_u4239(
                 refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
                 LOBYTE(v193[0]));
        if ( *v826 )
          goto LABEL_412;
        v473 = 170i64;
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        eqcopy___modelZboardZprototype95list_u3242(v194, v764);
      }
      v473 = 699i64;
      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      if ( LOBYTE(v193[4]) != 1 )
      {
        v359 = 0i64;
        v360 = 0i64;
        v357 = 0i64;
        v358 = 0i64;
        v355 = 0i64;
        v356 = 0i64;
        v353 = 0i64;
        v354 = 0i64;
        v757 = v194[12];
        v756 = v194[12];
        v473 = 1175i64;
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
        if ( v194[12] < 0 )
        {
          raiseRangeErrorI(v756, 0i64, 0x7FFFFFFFFFFFFFFFi64);
          goto LABEL_412;
        }
        newSeqUninit__modelZsimulationZpreorder_u19074(&v162, v756);
        v359 = v162;
        v360 = v163;
        v755 = 0i64;
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
        v885 = 0i64;
        v473 = 129i64;
        while ( v885 < v756 )
        {
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
          v755 = v885;
          v473 = 1179i64;
          if ( v885 < 0 || v755 >= v359 )
          {
            raiseIndexError2(v755, v359 - 1);
            goto LABEL_412;
          }
          *(_QWORD *)&v360[8 * v755 + 8] = 0i64;
          v473 = 131i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v344 = v885 + 1;
          if ( __OFADD__(1i64, v885) )
          {
LABEL_404:
            raiseOverflow();
            goto LABEL_412;
          }
          v885 = v344;
        }
        v473 = 982i64;
        i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
        if ( v774 >= 0 && v774 < v825[33] )
        {
          v473 = 705i64;
          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          v351 = v359;
          v352 = v360;
          eqwasMoved___modelZsave95mongerZcommon_u5609(&v359);
          v473 = 982i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
          v25 = v825[34] + 16 * v774 + 8;
          v162 = v351;
          v163 = v352;
          eqsink___modelZsave95mongerZcommon_u5621(v25, &v162);
          v754 = v194[16];
          v753 = v194[16];
          v473 = 1175i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
          if ( v194[16] < 0 )
          {
            raiseRangeErrorI(v753, 0i64, 0x7FFFFFFFFFFFFFFFi64);
            goto LABEL_412;
          }
          newSeqUninit__modelZsimulationZpreorder_u19074(&v162, v753);
          v357 = v162;
          v358 = v163;
          v752 = 0i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v884 = 0i64;
          v473 = 129i64;
          while ( v884 < v753 )
          {
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
            v752 = v884;
            v473 = 1179i64;
            if ( v884 < 0 || v752 >= v357 )
            {
              raiseIndexError2(v752, v357 - 1);
              goto LABEL_412;
            }
            *(_QWORD *)&v358[8 * v752 + 8] = 0i64;
            v473 = 131i64;
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
            v343 = v884 + 1;
            if ( __OFADD__(1i64, v884) )
              goto LABEL_404;
            v884 = v343;
          }
          v473 = 982i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
          if ( v774 < 0 || v774 >= v825[49] )
          {
            raiseIndexError2(v774, v825[49] - 1i64);
            goto LABEL_412;
          }
          v473 = 706i64;
          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          v349 = v357;
          v350 = v358;
          eqwasMoved___modelZsave95mongerZcommon_u5609(&v357);
          v473 = 982i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
          v26 = v825[50] + 16 * v774 + 8;
          v162 = v349;
          v163 = v350;
          eqsink___modelZsave95mongerZcommon_u5621(v26, &v162);
          v751 = v194[12];
          v750 = v194[12];
          v473 = 1175i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
          if ( v194[12] < 0 )
          {
            raiseRangeErrorI(v750, 0i64, 0x7FFFFFFFFFFFFFFFi64);
            goto LABEL_412;
          }
          newSeqUninit__modelZboardZboard_u21887(&v162, v750);
          v355 = v162;
          v356 = v163;
          v749 = 0i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v883 = 0i64;
          v473 = 129i64;
          while ( v883 < v750 )
          {
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
            v749 = v883;
            v473 = 1179i64;
            if ( v883 < 0 || v749 >= v355 )
            {
              raiseIndexError2(v749, v355 - 1);
              goto LABEL_412;
            }
            v27 = v356;
            v356[80 * v749 + 8] = 0;
            *(_QWORD *)&v27[80 * v749 + 16] = 1i64;
            *(_QWORD *)&v27[80 * v749 + 24] = 256i64;
            v27[80 * v749 + 32] = 1;
            *(_QWORD *)&v27[80 * v749 + 40] = 1i64;
            *(_QWORD *)&v27[80 * v749 + 48] = 256i64;
            v27[80 * v749 + 56] = 1;
            *(_QWORD *)&v27[80 * v749 + 64] = 0i64;
            *(_WORD *)&v27[80 * v749 + 72] = 0;
            *(_WORD *)&v27[80 * v749 + 74] = 0;
            *(_QWORD *)&v27[80 * v749 + 80] = 0i64;
            v473 = 131i64;
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
            v342 = v883 + 1;
            if ( __OFADD__(1i64, v883) )
              goto LABEL_404;
            v883 = v342;
          }
          v473 = 34i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
          if ( v774 >= 0 && v774 < v825[12] )
          {
            v473 = 708i64;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v347 = v355;
            v348 = v356;
            eqwasMoved___modelZsave95mongerZversionsZv0_u169(&v355);
            v473 = 34i64;
            i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
            v28 = v825[13] + 560 * v774 + 48 + 8;
            v162 = v347;
            v163 = v348;
            eqsink___modelZsave95mongerZversionsZv0_u181(v28, &v162);
            v748 = v194[16];
            v747 = v194[16];
            v473 = 1175i64;
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
            if ( v194[16] < 0 )
            {
              raiseRangeErrorI(v747, 0i64, 0x7FFFFFFFFFFFFFFFi64);
              goto LABEL_412;
            }
            newSeqUninit__modelZboardZboard_u21887(&v162, v747);
            v353 = v162;
            v354 = v163;
            v746 = 0i64;
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
            v882 = 0i64;
            v473 = 129i64;
            while ( v882 < v747 )
            {
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
              v746 = v882;
              v473 = 1179i64;
              if ( v882 < 0 || v746 >= v353 )
              {
                raiseIndexError2(v746, v353 - 1);
                goto LABEL_412;
              }
              v29 = v354;
              v354[80 * v746 + 8] = 0;
              *(_QWORD *)&v29[80 * v746 + 16] = 1i64;
              *(_QWORD *)&v29[80 * v746 + 24] = 256i64;
              v29[80 * v746 + 32] = 1;
              *(_QWORD *)&v29[80 * v746 + 40] = 1i64;
              *(_QWORD *)&v29[80 * v746 + 48] = 256i64;
              v29[80 * v746 + 56] = 1;
              *(_QWORD *)&v29[80 * v746 + 64] = 0i64;
              *(_WORD *)&v29[80 * v746 + 72] = 0;
              *(_WORD *)&v29[80 * v746 + 74] = 0;
              *(_QWORD *)&v29[80 * v746 + 80] = 0i64;
              v473 = 131i64;
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
              v341 = v882 + 1;
              if ( __OFADD__(1i64, v882) )
                goto LABEL_404;
              v882 = v341;
            }
            v473 = 34i64;
            i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
            if ( v774 >= 0 && v774 < v825[12] )
            {
              v473 = 710i64;
              i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
              v345 = v353;
              v346 = v354;
              eqwasMoved___modelZsave95mongerZversionsZv0_u169(&v353);
              v473 = 34i64;
              i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
              v30 = v825[13] + 560 * v774 + 64 + 8;
              v162 = v345;
              v163 = v346;
              eqsink___modelZsave95mongerZversionsZv0_u181(v30, &v162);
              v162 = v353;
              v163 = v354;
              eqdestroy___modelZsave95mongerZversionsZv0_u172(&v162);
              v162 = v355;
              v163 = v356;
              eqdestroy___modelZsave95mongerZversionsZv0_u172(&v162);
              v473 = 982i64;
              i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
              v162 = v357;
              v163 = v358;
              eqdestroy___modelZsave95mongerZcommon_u5612(&v162);
              v162 = v359;
              v163 = v360;
              eqdestroy___modelZsave95mongerZcommon_u5612(&v162);
LABEL_410:
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v889;
              v473 = 187i64;
              v745 = v825[12];
              if ( v745 != v772 )
              {
                v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_43;
                v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                failedAssertImpl__stdZassertions_u234(&v162);
              }
              goto LABEL_412;
            }
          }
          goto LABEL_408;
        }
LABEL_342:
        raiseIndexError2(v774, v825[33] - 1i64);
        goto LABEL_412;
      }
      v371 = 0i64;
      v372 = 0i64;
      v369 = 0i64;
      v370 = 0i64;
      v763 = v194[14];
      v762 = v194[14];
      v473 = 1175i64;
      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
      if ( v194[14] >= 0 )
      {
        newSeqUninit__modelZsimulationZpreorder_u19074(&v162, v762);
        v371 = v162;
        v372 = v163;
        v761 = 0i64;
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
        v887 = 0i64;
        v473 = 129i64;
        while ( v887 < v762 )
        {
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
          v761 = v887;
          v473 = 1179i64;
          if ( v887 < 0 || v761 >= v371 )
          {
            raiseIndexError2(v761, v371 - 1);
            goto LABEL_412;
          }
          *(_QWORD *)&v372[8 * v761 + 8] = 0i64;
          v473 = 131i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v362 = v887 + 1;
          if ( __OFADD__(1i64, v887) )
            goto LABEL_404;
          v887 = v362;
        }
        v473 = 982i64;
        i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
        if ( v774 < 0 || v774 >= v825[33] )
          goto LABEL_342;
        v473 = 700i64;
        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        v367 = v371;
        v368 = v372;
        eqwasMoved___modelZsave95mongerZcommon_u5609(&v371);
        v473 = 982i64;
        i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
        v21 = v825[34] + 16 * v774 + 8;
        v162 = v367;
        v163 = v368;
        eqsink___modelZsave95mongerZcommon_u5621(v21, &v162);
        v760 = v194[14];
        v759 = v194[14];
        v473 = 1175i64;
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
        if ( v194[14] >= 0 )
        {
          newSeqUninit__modelZboardZboard_u21887(&v162, v759);
          v369 = v162;
          v370 = v163;
          v758 = 0i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
          v886 = 0i64;
          v473 = 129i64;
          while ( v886 < v759 )
          {
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sequtils.nim";
            v758 = v886;
            v473 = 1179i64;
            if ( v886 < 0 || v758 >= v369 )
            {
              raiseIndexError2(v758, v369 - 1);
              goto LABEL_412;
            }
            v22 = v370;
            v370[80 * v758 + 8] = 0;
            *(_QWORD *)&v22[80 * v758 + 16] = 1i64;
            *(_QWORD *)&v22[80 * v758 + 24] = 256i64;
            v22[80 * v758 + 32] = 1;
            *(_QWORD *)&v22[80 * v758 + 40] = 1i64;
            *(_QWORD *)&v22[80 * v758 + 48] = 256i64;
            v22[80 * v758 + 56] = 1;
            *(_QWORD *)&v22[80 * v758 + 64] = 0i64;
            *(_WORD *)&v22[80 * v758 + 72] = 0;
            *(_WORD *)&v22[80 * v758 + 74] = 0;
            *(_QWORD *)&v22[80 * v758 + 80] = 0i64;
            v473 = 131i64;
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
            v361 = v886 + 1;
            if ( __OFADD__(1i64, v886) )
              goto LABEL_404;
            v886 = v361;
          }
          v473 = 34i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
          if ( v774 >= 0 && v774 < v825[12] )
          {
            v473 = 702i64;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v365 = v369;
            v366 = v370;
            eqwasMoved___modelZsave95mongerZversionsZv0_u169(&v369);
            v473 = 34i64;
            i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
            v23 = v825[13] + 560 * v774 + 48 + 8;
            v162 = v365;
            v163 = v366;
            eqsink___modelZsave95mongerZversionsZv0_u181(v23, &v162);
            if ( v774 >= 0 && v774 < v825[12] )
            {
              v364 = 0i64;
              v363 = 0i64;
              v364 = (char *)newSeqPayload(0i64, 80i64, 8i64);
              v24 = v825[13] + 560 * v774 + 64 + 8;
              v162 = v363;
              v163 = v364;
              eqsink___modelZsave95mongerZversionsZv0_u181(v24, &v162);
              v162 = v369;
              v163 = v370;
              eqdestroy___modelZsave95mongerZversionsZv0_u172(&v162);
              v473 = 982i64;
              i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
              v162 = v371;
              v163 = v372;
              eqdestroy___modelZsave95mongerZcommon_u5612(&v162);
              goto LABEL_410;
            }
          }
LABEL_408:
          raiseIndexError2(v774, v825[12] - 1i64);
          goto LABEL_412;
        }
        raiseRangeErrorI(v759, 0i64, 0x7FFFFFFFFFFFFFFFi64);
      }
      else
      {
        raiseRangeErrorI(v762, 0i64, 0x7FFFFFFFFFFFFFFFi64);
      }
    }
    else
    {
      raiseIndexError2(v889, v825[12] - 1i64);
    }
LABEL_412:
    v473 = 170i64;
    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    eqdestroy___modelZboardZprototype95list_u3239(v194);
    if ( *v826 )
      break;
  }
  v473 = 34i64;
  i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
  eqdestroy___modelZsave95mongerZversionsZv0_u145(v193);
  if ( *v826 )
    goto LABEL_1384;
  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v473 = 712i64;
  v479 = 0i64;
  v478 = 1i64;
  v479 = (_QWORD *)newSeqPayload(1i64, 64i64, 8i64);
  nimZeroMem_60(v476, 64i64);
  v477 = -1i64;
  v31 = v479;
  v32 = v476[1];
  v479[1] = v476[0];
  v31[2] = v32;
  v33 = v476[3];
  v31[3] = v476[2];
  v31[4] = v33;
  v34 = v476[5];
  v31[5] = v476[4];
  v31[6] = v34;
  v35 = v477;
  v31[7] = v476[6];
  v31[8] = v35;
  v473 = 73i64;
  v162 = v478;
  v163 = (char *)v479;
  eqsink___modelZsimulationZpreorder_u2183(v825 + 37, &v162);
  v339 = 0i64;
  v340 = 0i64;
  nimZeroMem_60(v338, 16i64);
  v473 = 767i64;
  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
  v36 = v825[7];
  v159 = v825[6];
  v160 = v36;
  v161 = (void *)v825[8];
  v744 = len__modelZsimulationZpreorder_u19351(&v159);
  if ( !*v826 )
  {
    v743 = 0i64;
    v742 = 0i64;
    v473 = 768i64;
    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
    v741 = v825[6] - 1i64;
    v742 = v741;
    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
    v881 = 0i64;
    v473 = 97i64;
    while ( v881 <= v742 )
    {
      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
      v743 = v881;
      v473 = 769i64;
      if ( v881 < 0 || v743 >= v825[6] )
      {
LABEL_426:
        raiseIndexError2(v743, v825[6] - 1i64);
        break;
      }
      v740 = 0;
      v740 = isFilled__pureZcollectionsZtables_u31_5(*(_QWORD *)(v825[7] + 40 * v743 + 8));
      if ( *v826 )
        break;
      if ( v740 == 1 )
      {
        v473 = 715i64;
        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        if ( v743 < 0 )
          goto LABEL_426;
        if ( v743 >= v825[6] )
          goto LABEL_426;
        v37 = v825[7] + 40 * v743;
        v38 = *(_QWORD *)(v37 + 24);
        v338[0] = *(_QWORD *)(v37 + 16);
        v338[1] = v38;
        v473 = 982i64;
        i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
        if ( v743 >= v825[6] )
          goto LABEL_426;
        v39 = *(char **)(v825[7] + 40 * v743 + 40);
        v162 = *(_QWORD *)(v825[7] + 40 * v743 + 32);
        v163 = v39;
        eqcopy___modelZsave95mongerZcommon_u5615(&v339, &v162);
        v335 = 0i64;
        v336 = 0i64;
        v473 = 716i64;
        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        if ( v339 <= 0 )
        {
          raiseIndexError2(0i64, v339 - 1);
          break;
        }
        v739 = 0;
        v40 = *((_QWORD *)v340 + 1);
        v159 = v484;
        v160 = v485;
        v161 = v486;
        v739 = contains__modelZboardZboard_u12534(&v159, v40);
        if ( *v826 )
          break;
        if ( v739 != 1 )
        {
          v473 = 718i64;
          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          nimZeroMem_60(v334, 24i64);
          v473 = 441i64;
          i = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
          v159 = v334[0];
          v160 = v334[1];
          v161 = (void *)v334[2];
          eqsink___modelZboardZboard_u15254(v825 + 20, &v159);
          v473 = 934i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          nimZeroMem_60(v192, 64i64);
          v473 = 982i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
          v162 = v339;
          v163 = v340;
          eqdup___modelZsave95mongerZcommon_u5618(&v335, &v162);
          v192[0] = v335;
          v192[1] = v336;
          v192[7] = -1i64;
          v473 = 934i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          eqsink___modelZsimulationZpreorder_u2353(v825 + 23, v192);
          v738 = 0i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          v880 = 0i64;
          v737 = v339;
          v736 = v339;
          v473 = 251i64;
          while ( v880 < v736 )
          {
            v473 = 722i64;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            if ( v880 < 0 || v880 >= v339 )
            {
              raiseIndexError2(v880, v339 - 1);
              goto LABEL_576;
            }
            v738 = &v340[8 * v880 + 8];
            v473 = 723i64;
            incl__modelZboardZboard_u11061(&v484, *(_QWORD *)v738);
            if ( !*v826 )
            {
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v880;
              v473 = 254i64;
              v735 = v339;
              if ( v339 == v736 )
                continue;
              v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_44;
              v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
              failedAssertImpl__stdZassertions_u234(&v162);
              if ( !*v826 )
                continue;
            }
            goto LABEL_576;
          }
          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          v879 = 0i64;
          v473 = 728i64;
          while ( 1 )
          {
            v734 = v825[23];
            if ( v879 >= v734 )
              break;
            v473 = 729i64;
            if ( v879 < 0 || v879 >= v825[23] )
            {
              raiseIndexError2(v879, v825[23] - 1i64);
              goto LABEL_576;
            }
            v733 = *(_QWORD *)(v825[24] + 8 * v879 + 8);
            nimZeroMem_60(v194, 32i64);
            v473 = 730i64;
            v732 = 0i64;
            v732 = (__int64 *)X5BX5D___modelZsimulationZpreorder_u19751(v825 + 3, v733);
            if ( *v826 )
              goto LABEL_576;
            v41 = v732[1];
            v194[0] = *v732;
            v194[1] = v41;
            v42 = v732[3];
            v194[2] = v732[2];
            v194[3] = v42;
            v332 = v194[0];
            v333 = (char *)v194[1];
            v330 = v194[2];
            v331 = (char *)v42;
            v473 = 743i64;
            nimZeroMem_60(&v328, 16i64);
            v328 = connect__modelZsimulationZpreorder_u19843;
            v329 = v825;
            v162 = v332;
            v163 = v333;
            if ( v825 )
              ((void (__fastcall *)(__int64 *, _QWORD *))v328)(&v162, v329);
            else
              ((void (__fastcall *)(__int64 *))v328)(&v162);
            if ( *v826 )
              goto LABEL_576;
            v473 = 744i64;
            nimZeroMem_60(&v326, 16i64);
            v326 = connect__modelZsimulationZpreorder_u19843;
            v327 = v825;
            v162 = v330;
            v163 = v331;
            if ( v825 )
              ((void (__fastcall *)(__int64 *, _QWORD *))v326)(&v162, v327);
            else
              ((void (__fastcall *)(__int64 *))v326)(&v162);
            if ( *v826 )
              goto LABEL_576;
            v731 = 0i64;
            v730 = 0i64;
            v473 = 746i64;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v162 = v332;
            v163 = v333;
            v730 = (__int64 *)X5BX5D___modelZsimulationZpreorder_u11211(v825 + 6, &v162);
            if ( *v826 )
              goto LABEL_576;
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            v878 = 0i64;
            v473 = 250i64;
            v729 = *v730;
            v728 = v729;
            v473 = 251i64;
            while ( v878 < v728 )
            {
              v473 = 746i64;
              i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
              if ( v878 < 0 || v878 >= *v730 )
              {
                raiseIndexError2(v878, *v730 - 1);
                goto LABEL_576;
              }
              v731 = (_QWORD *)(v730[1] + 8 * v878 + 8);
              v727 = 0i64;
              v473 = 747i64;
              v726 = 0;
              v43 = *v731;
              v159 = v484;
              v160 = v485;
              v161 = v486;
              v726 = contains__modelZboardZboard_u12534(&v159, v43);
              if ( *v826 )
                goto LABEL_576;
              if ( v726 != 1 )
              {
                v473 = 749i64;
                incl__modelZboardZboard_u11061(&v484, *v731);
                if ( *v826 )
                  goto LABEL_576;
                v473 = 751i64;
                v727 = *v731;
                add__modelZsave95mongerZcommon_u5717(v825 + 23, v727);
              }
              else
              {
                v473 = 748i64;
              }
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v878;
              v473 = 254i64;
              v725 = *v730;
              if ( v725 != v728 )
              {
                v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_48;
                v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
                failedAssertImpl__stdZassertions_u234(&v162);
                if ( *v826 )
                  goto LABEL_576;
              }
            }
            v724 = 0i64;
            v723 = 0i64;
            v473 = 753i64;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v162 = v330;
            v163 = v331;
            v723 = (__int64 *)X5BX5D___modelZsimulationZpreorder_u11211(v825 + 6, &v162);
            if ( *v826 )
              goto LABEL_576;
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            v877 = 0i64;
            v473 = 250i64;
            v722 = *v723;
            v721 = v722;
            v473 = 251i64;
            while ( v877 < v721 )
            {
              v473 = 753i64;
              i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
              if ( v877 < 0 || v877 >= *v723 )
              {
                raiseIndexError2(v877, *v723 - 1);
                goto LABEL_576;
              }
              v724 = (_QWORD *)(v723[1] + 8 * v877 + 8);
              v720 = 0i64;
              v473 = 754i64;
              v719 = 0;
              v44 = *v724;
              v159 = v484;
              v160 = v485;
              v161 = v486;
              v719 = contains__modelZboardZboard_u12534(&v159, v44);
              if ( *v826 )
                goto LABEL_576;
              if ( v719 != 1 )
              {
                v473 = 756i64;
                incl__modelZboardZboard_u11061(&v484, *v724);
                if ( *v826 )
                  goto LABEL_576;
                v473 = 758i64;
                v720 = *v724;
                add__modelZsave95mongerZcommon_u5717(v825 + 23, v720);
              }
              else
              {
                v473 = 755i64;
              }
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v877;
              v473 = 254i64;
              v718 = *v723;
              if ( v718 != v721 )
              {
                v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_49;
                v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
                failedAssertImpl__stdZassertions_u234(&v162);
                if ( *v826 )
                  goto LABEL_576;
              }
            }
            v473 = 760i64;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v325 = v879 + 1;
            if ( __OFADD__(1i64, v879) )
              goto LABEL_487;
            v879 = v325;
          }
          v473 = 762i64;
          v717 = 0i64;
          v45 = v825[21];
          v159 = v825[20];
          v160 = v45;
          v161 = (void *)v825[22];
          v717 = len__modelZboardZboard_u15042(&v159);
          if ( *v826 )
            break;
          if ( v717 < -32768 || v717 > 0x7FFF )
          {
            raiseRangeErrorI(v717, -32768i64, 0x7FFFi64);
            break;
          }
          *((_WORD *)v825 + 100) = v717;
          v473 = 764i64;
          if ( *((_WORD *)v825 + 100) )
          {
            nimZeroMem_60(v193, 64i64);
            v473 = 777i64;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v705 = v825[37];
            v704 = v705;
            v703 = 0i64;
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            v875 = 0i64;
            v473 = 250i64;
            v702 = v825[26];
            v701 = v702;
            v473 = 251i64;
            while ( v875 < v701 )
            {
              v473 = 779i64;
              i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
              if ( v875 < 0 || v875 >= v825[26] )
              {
                raiseIndexError2(v875, v825[26] - 1i64);
                goto LABEL_576;
              }
              v56 = v825[27];
              v703 = (__int64 *)(v56 + 24 * v875 + 8);
              v473 = 780i64;
              v700 = *v703;
              v473 = 782i64;
              if ( *(_BYTE *)(v56 + 24 * v875 + 24) != 1 )
              {
                v473 = 785i64;
                if ( v700 < 0 || v700 >= v825[49] )
                {
                  raiseIndexError2(v700, v825[49] - 1i64);
                  goto LABEL_576;
                }
                if ( v703[1] < 0 || v703[1] >= *(_QWORD *)(v825[50] + 16 * v700 + 8) )
                {
                  raiseIndexError2(v703[1], *(_QWORD *)(v825[50] + 16 * v700 + 8) - 1i64);
                  goto LABEL_576;
                }
                *(_QWORD *)(*(_QWORD *)(v825[50] + 16 * v700 + 16) + 8 * v703[1] + 8) = v704;
              }
              else
              {
                v473 = 783i64;
                if ( v700 < 0 || v700 >= v825[33] )
                {
                  raiseIndexError2(v700, v825[33] - 1i64);
                  goto LABEL_576;
                }
                if ( v703[1] < 0 || v703[1] >= *(_QWORD *)(v825[34] + 16 * v700 + 8) )
                {
                  raiseIndexError2(v703[1], *(_QWORD *)(v825[34] + 16 * v700 + 8) - 1i64);
                  goto LABEL_576;
                }
                *(_QWORD *)(*(_QWORD *)(v825[34] + 16 * v700 + 16) + 8 * v703[1] + 8) = v704;
              }
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v875;
              v473 = 254i64;
              v699 = v825[26];
              if ( v699 != v701 )
              {
                v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_52;
                v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
                failedAssertImpl__stdZassertions_u234(&v162);
                if ( *v826 )
                  goto LABEL_576;
              }
            }
            v473 = 934i64;
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            nimZeroMem_60(v194, 64i64);
            eqdup___modelZsimulationZpreorder_u2350(v825 + 23, v194);
            v193[0] = v194[0];
            v193[1] = v194[1];
            v193[2] = v194[2];
            v193[3] = v194[3];
            v193[4] = v194[4];
            v193[5] = v194[5];
            v193[6] = v194[6];
            v193[7] = v194[7];
            v473 = 787i64;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            add__modelZsimulationZpreorder_u20806(v825 + 37, v193);
          }
          else
          {
            v716 = 0i64;
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            v876 = 0i64;
            v473 = 250i64;
            v715 = v825[23];
            v714 = v715;
            v473 = 251i64;
            while ( v876 < v714 )
            {
              v473 = 765i64;
              i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
              if ( v876 < 0 || v876 >= v825[23] )
              {
                raiseIndexError2(v876, v825[23] - 1i64);
                goto LABEL_576;
              }
              v716 = (_QWORD *)(v825[24] + 8 * v876 + 8);
              nimZeroMem_60(v194, 32i64);
              v473 = 766i64;
              v713 = 0i64;
              v713 = (__int64 *)X5BX5D___modelZsimulationZpreorder_u19751(v825 + 3, *v716);
              if ( *v826 )
                goto LABEL_576;
              v46 = v713[1];
              v194[0] = *v713;
              v194[1] = v46;
              v47 = v713[3];
              v194[2] = v713[2];
              v194[3] = v47;
              v323 = v194[0];
              v324 = (char *)v194[1];
              v321 = v194[2];
              v322 = (char *)v47;
              v473 = 768i64;
              v712 = 0;
              v48 = v825[18];
              v159 = v825[17];
              v160 = v48;
              v161 = (void *)v825[19];
              v162 = v194[0];
              v163 = (char *)v194[1];
              v712 = contains__modelZsimulationZpreorder_u2519(&v159, &v162);
              if ( *v826 )
                goto LABEL_576;
              if ( v712 == 1 )
              {
                v473 = 769i64;
                v711 = 0i64;
                v162 = v323;
                v163 = v324;
                v711 = (__int64 *)X5BX5D___modelZsimulationZpreorder_u19952(v825 + 17, &v162);
                if ( *v826 )
                  goto LABEL_576;
                v49 = v711[1];
                v318 = *v711;
                v319 = v49;
                v320 = v711[2];
                v710 = v318;
                v473 = 771i64;
                if ( v318 < 0 || v710 >= v825[12] )
                {
                  raiseIndexError2(v710, v825[12] - 1i64);
                  goto LABEL_576;
                }
                if ( v319 < 0 || v319 >= *(_QWORD *)(v825[13] + 560 * v710 + 56) )
                {
                  raiseIndexError2(v319, *(_QWORD *)(v825[13] + 560 * v710 + 56) - 1i64);
                  goto LABEL_576;
                }
                v50 = *(_QWORD *)(v825[13] + 560 * v710 + 64);
                v51 = v319;
                *(_BYTE *)(v50 + 80 * v319 + 8) = 0;
                *(_QWORD *)(v50 + 80 * v51 + 16) = 1i64;
                *(_QWORD *)(v50 + 80 * v51 + 24) = 256i64;
                *(_BYTE *)(v50 + 80 * v51 + 32) = 1;
                *(_QWORD *)(v50 + 80 * v51 + 40) = 1i64;
                *(_QWORD *)(v50 + 80 * v51 + 48) = 256i64;
                *(_BYTE *)(v50 + 80 * v51 + 56) = 1;
                *(_QWORD *)(v50 + 80 * v51 + 64) = 0i64;
                *(_WORD *)(v50 + 80 * v51 + 72) = 0;
                *(_WORD *)(v50 + 80 * v51 + 74) = 0;
                *(_QWORD *)(v50 + 80 * v51 + 80) = 0i64;
              }
              v473 = 772i64;
              v709 = 0;
              v52 = v825[18];
              v159 = v825[17];
              v160 = v52;
              v161 = (void *)v825[19];
              v162 = v321;
              v163 = v322;
              v709 = contains__modelZsimulationZpreorder_u2519(&v159, &v162);
              if ( *v826 )
                goto LABEL_576;
              if ( v709 == 1 )
              {
                v473 = 773i64;
                v708 = 0i64;
                v162 = v321;
                v163 = v322;
                v708 = (__int64 *)X5BX5D___modelZsimulationZpreorder_u19952(v825 + 17, &v162);
                if ( *v826 )
                  goto LABEL_576;
                v53 = v708[1];
                v315 = *v708;
                v316 = v53;
                v317 = v708[2];
                v707 = v315;
                v473 = 775i64;
                if ( v315 < 0 || v707 >= v825[12] )
                {
                  raiseIndexError2(v707, v825[12] - 1i64);
                  goto LABEL_576;
                }
                if ( v316 < 0 || v316 >= *(_QWORD *)(v825[13] + 560 * v707 + 56) )
                {
                  raiseIndexError2(v316, *(_QWORD *)(v825[13] + 560 * v707 + 56) - 1i64);
                  goto LABEL_576;
                }
                v54 = *(_QWORD *)(v825[13] + 560 * v707 + 64);
                v55 = v316;
                *(_BYTE *)(v54 + 80 * v316 + 8) = 0;
                *(_QWORD *)(v54 + 80 * v55 + 16) = 1i64;
                *(_QWORD *)(v54 + 80 * v55 + 24) = 256i64;
                *(_BYTE *)(v54 + 80 * v55 + 32) = 1;
                *(_QWORD *)(v54 + 80 * v55 + 40) = 1i64;
                *(_QWORD *)(v54 + 80 * v55 + 48) = 256i64;
                *(_BYTE *)(v54 + 80 * v55 + 56) = 1;
                *(_QWORD *)(v54 + 80 * v55 + 64) = 0i64;
                *(_WORD *)(v54 + 80 * v55 + 72) = 0;
                *(_WORD *)(v54 + 80 * v55 + 74) = 0;
                *(_QWORD *)(v54 + 80 * v55 + 80) = 0i64;
              }
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v876;
              v473 = 254i64;
              v706 = v825[23];
              if ( v706 != v714 )
              {
                v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_51;
                v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
                failedAssertImpl__stdZassertions_u234(&v162);
                if ( *v826 )
                  goto LABEL_576;
              }
            }
          }
        }
        else
        {
          v473 = 717i64;
        }
        v473 = 771i64;
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\tables.nim";
        v698 = 0i64;
        v57 = v825[7];
        v159 = v825[6];
        v160 = v57;
        v161 = (void *)v825[8];
        v698 = len__modelZsimulationZpreorder_u19351(&v159);
        if ( *v826 )
          break;
        if ( v698 != v744 )
        {
          v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_54;
          v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_53;
          failedAssertImpl__stdZassertions_u234(&v162);
          if ( *v826 )
            break;
        }
      }
      v473 = 102i64;
      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v337 = v881 + 1;
      if ( __OFADD__(1i64, v881) )
      {
LABEL_487:
        raiseOverflow();
        break;
      }
      v881 = v337;
    }
  }
LABEL_576:
  v473 = 982i64;
  i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
  v162 = v339;
  v163 = v340;
  eqdestroy___modelZsave95mongerZcommon_u5612(&v162);
  if ( *v826 )
    goto LABEL_1384;
  v473 = 790i64;
  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v697 = v825[37];
  if ( v697 < 0 )
  {
    raiseRangeErrorI(v697, 0i64, 0x7FFFFFFFFFFFFFFFi64);
    goto LABEL_1384;
  }
  setLen__modelZsimulationZpreorder_u2068(v825 + 51, v697);
  v313 = 0i64;
  v314 = 0i64;
  v696 = 0i64;
  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v874 = 0i64;
  v473 = 183i64;
  v695 = v825[33];
  v694 = v695;
  v473 = 184i64;
  while ( v874 < v694 )
  {
    v696 = v874;
    v473 = 982i64;
    i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
    if ( v874 < 0 || v874 >= v825[33] )
    {
      raiseIndexError2(v874, v825[33] - 1i64);
      break;
    }
    v58 = v825[34] + 16 * v874;
    v59 = *(char **)(v58 + 16);
    v162 = *(_QWORD *)(v58 + 8);
    v163 = v59;
    eqcopy___modelZsave95mongerZcommon_u5615(&v313, &v162);
    v693 = 0i64;
    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    v873 = 0i64;
    v692 = v313;
    v691 = v313;
    v473 = 251i64;
    while ( v873 < v691 )
    {
      v473 = 793i64;
      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      if ( v873 < 0 || v873 >= v313 )
      {
        raiseIndexError2(v873, v313 - 1);
        goto LABEL_603;
      }
      v693 = &v314[8 * v873 + 8];
      v473 = 794i64;
      if ( *(_QWORD *)v693 )
      {
        v473 = 796i64;
        if ( *(__int64 *)v693 < 0 || *(_QWORD *)v693 >= v825[51] )
        {
          raiseIndexError2(*(_QWORD *)v693, v825[51] - 1i64);
          goto LABEL_603;
        }
        add__modelZsave95mongerZcommon_u5717(v825[52] + 16i64 * *(_QWORD *)v693 + 8, v696);
      }
      else
      {
        v473 = 795i64;
      }
      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      ++v873;
      v473 = 254i64;
      v690 = v313;
      if ( v313 != v691 )
      {
        v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_56;
        v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
        failedAssertImpl__stdZassertions_u234(&v162);
        if ( *v826 )
          goto LABEL_603;
      }
    }
    ++v874;
    v473 = 187i64;
    v689 = v825[33];
    if ( v689 != v694 )
    {
      v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_57;
      v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
      failedAssertImpl__stdZassertions_u234(&v162);
      if ( *v826 )
        break;
    }
  }
LABEL_603:
  v473 = 982i64;
  i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
  v162 = v313;
  v163 = v314;
  eqdestroy___modelZsave95mongerZcommon_u5612(&v162);
  if ( *v826 )
    goto LABEL_1384;
  nimZeroMem_60(v312, 24i64);
  v310 = 0i64;
  v311 = 0i64;
  v473 = 809i64;
  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v688 = v825[37];
  if ( v688 < 0 )
  {
    raiseRangeErrorI(v688, 0i64, 0x7FFFFFFFFFFFFFFFi64);
    goto LABEL_690;
  }
  setLen__modelZsave95mongerZcommon_u5632(v825 + 35, v688);
  nimZeroMem_60(v194, 560i64);
  v687 = 0i64;
  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v872 = 0i64;
  v473 = 183i64;
  v686 = v825[12];
  v685 = v686;
  v473 = 184i64;
  while ( 2 )
  {
    if ( v872 >= v685 )
    {
      v473 = 34i64;
      i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
      eqdestroy___modelZsave95mongerZversionsZv0_u145(v194);
      v473 = 837i64;
      for ( i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            ;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim" )
      {
        while ( 1 )
        {
          v682 = v310;
          if ( v310 <= 0 )
            goto LABEL_690;
          nimZeroMem_60(v194, 560i64);
          v473 = 839i64;
          v681 = pop__modelZsimulationZpreorder_u21011(&v310);
          v473 = 841i64;
          nimZeroMem_60(v307, 16i64);
          v307[1] = v681;
          v162 = v307[0];
          v163 = (char *)v681;
          add__modelZsimulationZpreorder_u21027(&v482, &v162);
          v473 = 34i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
          if ( v681 >= 0 && v681 < v825[12] )
            break;
          raiseIndexError2(v681, v825[12] - 1i64);
LABEL_689:
          v473 = 34i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
          eqdestroy___modelZsave95mongerZversionsZv0_u145(v194);
          if ( *v826 )
            goto LABEL_690;
        }
        eqcopy___modelZsave95mongerZversionsZv0_u148(v194, v825[13] + 560 * v681 + 8);
        v473 = 845i64;
        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        v680 = 0;
        if ( v825[32] )
          v61 = v825[32] + 8i64;
        else
          v61 = 0i64;
        v680 = contains__modelZtranslations_u2303_5(v61, v825[31], v681);
        if ( v680 == 1 )
        {
          v305 = 0i64;
          v306 = 0i64;
          v303 = 0i64;
          v304 = 0i64;
          v301 = 0i64;
          v302 = 0i64;
          dollar___systemZdollars_u14(&v305, v681);
          if ( *v826 )
            goto LABEL_689;
          rawNewString(&v162, v305 + 101);
          v301 = v162;
          v302 = v163;
          v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_64;
          v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_63;
          appendString_25(&v301, &v162);
          v162 = v305;
          v163 = v306;
          appendString_25(&v301, &v162);
          v303 = v301;
          v304 = v302;
          v162 = v301;
          v163 = v302;
          failedAssertImpl__stdZassertions_u234(&v162);
          if ( *v826 )
            goto LABEL_689;
          v473 = 394i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( v304 && (*(_QWORD *)v304 & 0x4000000000000000i64) == 0 )
            deallocShared(v304);
          if ( v306 && (*(_QWORD *)v306 & 0x4000000000000000i64) == 0 )
            deallocShared(v306);
        }
        v473 = 846i64;
        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        add__modelZsave95mongerZcommon_u5717(v825 + 31, v681);
        v473 = 848i64;
        if ( LOBYTE(v194[0]) != 78 )
          break;
        v473 = 34i64;
        i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        eqdestroy___modelZsave95mongerZversionsZv0_u145(v194);
        v473 = 849i64;
      }
      v679 = 0i64;
      v678 = 0i64;
      v677 = 0i64;
      v473 = 180i64;
      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      if ( v681 < 0 || v681 >= v825[49] )
      {
        raiseIndexError2(v681, v825[49] - 1i64);
        goto LABEL_689;
      }
      v677 = (__int64 *)(v825[50] + 16 * v681 + 8);
      v871 = 0i64;
      v473 = 183i64;
      v676 = *v677;
      v675 = v676;
      v473 = 184i64;
      while ( 1 )
      {
        if ( v871 >= v675 )
          goto LABEL_689;
        nimZeroMem_60(v193, 64i64);
        v299 = 0i64;
        v300 = 0i64;
        v473 = 851i64;
        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        v679 = v871;
        if ( v871 >= 0 && v871 < *v677 )
        {
          v678 = *(char **)(v677[1] + 8 * v871 + 8);
          v473 = 934i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          if ( (__int64)v678 >= 0 && (__int64)v678 < v825[37] )
          {
            eqcopy___modelZsimulationZpreorder_u2347(v193, v825[38] + ((_QWORD)v678 << 6) + 8i64);
            v473 = 854i64;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            if ( (__int64)v678 >= 0 && (__int64)v678 < v825[35] )
            {
              v62 = *(_QWORD *)(v825[36] + 8i64 * (_QWORD)v678 + 8);
              v63 = 0;
              v64 = __OFADD__(1i64, v62);
              v65 = v62 + 1;
              if ( v64 )
                v63 = 1;
              v298 = v65;
              if ( (v63 & 1) != 0 )
              {
                raiseOverflow();
                goto LABEL_688;
              }
              *(_QWORD *)(v825[36] + 8i64 * (_QWORD)v678 + 8) = v298;
              v473 = 856i64;
              if ( (__int64)v678 >= 0 && (__int64)v678 < v825[35] )
              {
                if ( SLOWORD(v193[2]) == *(_QWORD *)(v825[36] + 8i64 * (_QWORD)v678 + 8) )
                {
                  v473 = 857i64;
                  LOBYTE(v296) = 1;
                  v297 = v678;
                  v162 = v296;
                  v163 = v678;
                  add__modelZsimulationZpreorder_u21027(&v482, &v162);
                }
                v473 = 982i64;
                i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
                if ( (__int64)v678 >= 0 && (__int64)v678 < v825[51] )
                {
                  v66 = v825[52] + 16i64 * (_QWORD)v678;
                  v67 = *(char **)(v66 + 16);
                  v162 = *(_QWORD *)(v66 + 8);
                  v163 = v67;
                  eqcopy___modelZsave95mongerZcommon_u5615(&v299, &v162);
                  v473 = 861i64;
                  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                  if ( v194[5] )
                  {
                    v473 = 862i64;
                    add__modelZsave95mongerZcommon_u5717(&v299, v194[5]);
                  }
                  v674 = 0i64;
                  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                  v870 = 0i64;
                  v673 = v299;
                  v672 = v299;
                  v473 = 251i64;
                  while ( v870 < v672 )
                  {
                    v473 = 864i64;
                    i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                    if ( v870 < 0 || v870 >= v299 )
                    {
                      raiseIndexError2(v870, v299 - 1);
                      goto LABEL_688;
                    }
                    v674 = &v300[8 * v870 + 8];
                    v473 = 865i64;
                    v671 = 0;
                    v68 = *(_QWORD *)v674;
                    v159 = v312[0];
                    v160 = v312[1];
                    v161 = (void *)v312[2];
                    v671 = contains__modelZboardZboard_u12534(&v159, v68);
                    if ( *v826 )
                      goto LABEL_688;
                    if ( v671 != 1 )
                    {
                      v473 = 867i64;
                      nimZeroMem_60(&v294, 16i64);
                      v294 = is_ready__modelZsimulationZpreorder_u20904;
                      v295 = v825;
                      v670 = 0;
                      if ( v825 )
                        v69 = ((unsigned __int8 (__fastcall *)(_QWORD, _QWORD *))v294)(*(_QWORD *)v674, v295) != 0;
                      else
                        v69 = ((unsigned __int8 (__fastcall *)(_QWORD))v294)(*(_QWORD *)v674) != 0;
                      v670 = v69;
                      if ( *v826 )
                        goto LABEL_688;
                      if ( v670 )
                      {
                        v669 = 0i64;
                        v473 = 868i64;
                        v669 = *(_QWORD *)v674;
                        add__modelZsave95mongerZcommon_u5717(&v310, v669);
                        v473 = 869i64;
                        incl__modelZboardZboard_u11061(v312, *(_QWORD *)v674);
                        if ( *v826 )
                          goto LABEL_688;
                      }
                    }
                    else
                    {
                      v473 = 866i64;
                    }
                    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                    ++v870;
                    v473 = 254i64;
                    v668 = v299;
                    if ( v299 != v672 )
                    {
                      v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_67;
                      v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
                      failedAssertImpl__stdZassertions_u234(&v162);
                      if ( *v826 )
                        goto LABEL_688;
                    }
                  }
                  ++v871;
                  v473 = 187i64;
                  v667 = *v677;
                  if ( v667 != v675 )
                  {
                    v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_68;
                    v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                    failedAssertImpl__stdZassertions_u234(&v162);
                  }
                }
                else
                {
                  raiseIndexError2(v678, v825[51] - 1i64);
                }
                goto LABEL_688;
              }
            }
            raiseIndexError2(v678, v825[35] - 1i64);
          }
          else
          {
            raiseIndexError2(v678, v825[37] - 1i64);
          }
        }
        else
        {
          raiseIndexError2(v871, *v677 - 1);
        }
LABEL_688:
        v473 = 982i64;
        i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
        v162 = v299;
        v163 = v300;
        eqdestroy___modelZsave95mongerZcommon_u5612(&v162);
        v473 = 934i64;
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        eqdestroy___modelZsimulationZpreorder_u2344(v193);
        if ( *v826 )
          goto LABEL_689;
      }
    }
    v687 = v872;
    v473 = 34i64;
    i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    if ( v872 >= 0 && v872 < v825[12] )
    {
      eqcopy___modelZsave95mongerZversionsZv0_u148(v194, v825[13] + 560 * v872 + 8);
      v473 = 833i64;
      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      nimZeroMem_60(&v308, 16i64);
      v308 = is_ready__modelZsimulationZpreorder_u20904;
      v309 = v825;
      v684 = 0;
      if ( v825 )
        v60 = ((unsigned __int8 (__fastcall *)(__int64, _QWORD *))v308)(v687, v309) != 0;
      else
        v60 = ((unsigned __int8 (__fastcall *)(__int64))v308)(v687) != 0;
      v684 = v60;
      if ( *v826 )
        goto LABEL_690;
      if ( v684 )
      {
        v473 = 834i64;
        add__modelZsave95mongerZcommon_u5717(&v310, v687);
        v473 = 835i64;
        incl__modelZboardZboard_u11061(v312, v687);
        if ( *v826 )
          goto LABEL_690;
      }
      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      ++v872;
      v473 = 187i64;
      v683 = v825[12];
      if ( v683 != v685 )
      {
        v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_61;
        v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
        failedAssertImpl__stdZassertions_u234(&v162);
        if ( *v826 )
          goto LABEL_690;
      }
      continue;
    }
    break;
  }
  raiseIndexError2(v872, v825[12] - 1i64);
LABEL_690:
  v473 = 982i64;
  i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
  v162 = v310;
  v163 = v311;
  eqdestroy___modelZsave95mongerZcommon_u5612(&v162);
  v473 = 441i64;
  i = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  eqdestroy___modelZboardZboard_u15245(v312);
  if ( *v826 )
    goto LABEL_1384;
  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  *((_BYTE *)v825 + 336) = 0;
  v900 = 0i64;
  v869 = 0i64;
  v473 = 1014i64;
  while ( 2 )
  {
    v666 = v482;
    if ( v869 < v482 )
    {
      v473 = 1015i64;
      if ( v869 < 0 || v869 >= v482 )
      {
        raiseIndexError2(v869, v482 - 1);
        goto LABEL_1384;
      }
      v70 = &v483[16 * v869];
      v71 = *((_QWORD *)v70 + 2);
      v292 = *((_QWORD *)v70 + 1);
      v293 = v71;
      v473 = 1017i64;
      if ( (unsigned __int8)v292 != 1 )
      {
        nimZeroMem_60(v194, 560i64);
        v657 = v293;
        v473 = 34i64;
        i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        if ( v293 >= 0
          && v657 < v825[12]
          && (eqcopy___modelZsave95mongerZversionsZv0_u148(v194, v825[13] + 560 * v657 + 8),
              v473 = 1039i64,
              i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim",
              v657 >= 0)
          && v657 < v825[12] )
        {
          nimZeroMem_60(&v288, 8i64);
          v76 = (char *)v825[34];
          v162 = v825[33];
          v163 = v76;
          v77 = (char *)v825[38];
          v157 = v825[37];
          v158 = v77;
          v288 = infer_size__modelZsimulationZpreorder_u1999(
                   (int)v825 + 96,
                   (unsigned int)&v162,
                   (unsigned int)&v157,
                   v657,
                   v194[28]);
          if ( !*v826 )
            *(_QWORD *)(v825[13] + 560 * v657 + 240) = v288;
        }
        else
        {
          raiseIndexError2(v657, v825[12] - 1i64);
        }
        v473 = 34i64;
        i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        eqdestroy___modelZsave95mongerZversionsZv0_u145(v194);
        if ( *v826 )
          goto LABEL_1384;
      }
      else
      {
        nimZeroMem_60(v192, 64i64);
        v665 = v293;
        v473 = 934i64;
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        if ( v293 < 0 || v665 >= v825[37] )
          goto LABEL_699;
        eqcopy___modelZsimulationZpreorder_u2347(v192, v825[38] + (v665 << 6) + 8);
        v473 = 1021i64;
        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        v290 = bits__modelZsave95mongerZcommon_u192(0x8000000000000000ui64);
        if ( !*v826 )
        {
          v664 = 0i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          v868 = 0i64;
          v663 = v192[3];
          v662 = v192[3];
          v473 = 251i64;
          while ( v868 < v662 )
          {
            v473 = 1022i64;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            if ( v868 < 0 || v868 >= v192[3] )
            {
              raiseIndexError2(v868, v192[3] - 1);
              goto LABEL_728;
            }
            v664 = v192[4] + 24 * v868 + 8;
            nimZeroMem_60(v193, 560i64);
            nimZeroMem_60(v194, 1448i64);
            nimZeroMem_60(v191, 56i64);
            v473 = 1023i64;
            if ( *(_BYTE *)(v664 + 16) != 1 )
            {
              v473 = 1025i64;
              v661 = *(_QWORD *)v664;
              v473 = 34i64;
              i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
              if ( v661 >= 0 && v661 < v825[12] )
              {
                eqcopy___modelZsave95mongerZversionsZv0_u148(v193, v825[13] + 560 * v661 + 8);
                v473 = 1028i64;
                i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                v660 = 0i64;
                v660 = X5BX5D___modelZboardZprototype95list_u4239(
                         refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
                         LOBYTE(v193[0]));
                if ( !*v826 )
                {
                  v473 = 170i64;
                  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                  eqcopy___modelZboardZprototype95list_u3242(v194, v660);
                  v473 = 1029i64;
                  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                  v659 = *(_QWORD *)(v664 + 8);
                  if ( v659 < 0 )
                    goto LABEL_716;
                  if ( v659 >= v194[16] )
                    goto LABEL_716;
                  v72 = (_QWORD *)(v194[17] + 56 * v659);
                  v73 = v72[2];
                  v191[0] = v72[1];
                  v191[1] = v73;
                  v74 = v72[4];
                  v191[2] = v72[3];
                  v191[3] = v74;
                  v75 = v72[6];
                  v191[4] = v72[5];
                  v191[5] = v75;
                  v191[6] = v72[7];
                  v473 = 934i64;
                  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                  if ( v659 < v194[16] )
                  {
                    eqwasMoved___modelZboardZprototype95list_u1774(v194[17] + 56 * v659 + 8);
                    v473 = 1030i64;
                    i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                    v162 = v193[21];
                    v163 = (char *)v193[22];
                    v289 = proto_word_size__modelZboardZprototype95list_u4422(v191, v193[29], &v162);
                    if ( !*v826 )
                    {
                      v473 = 1032i64;
                      v290 = max__modelZsave95mongerZcommon_u225(v290, v289);
                    }
                  }
                  else
                  {
LABEL_716:
                    raiseIndexError2(v659, v194[16] - 1);
                  }
                }
              }
              else
              {
                raiseIndexError2(v661, v825[12] - 1i64);
              }
              v473 = 934i64;
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              eqdestroy___modelZboardZprototype95list_u1777(v191);
              v473 = 170i64;
              eqdestroy___modelZboardZprototype95list_u3239(v194);
              v473 = 34i64;
              i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
              eqdestroy___modelZsave95mongerZversionsZv0_u145(v193);
              if ( *v826 )
                goto LABEL_728;
            }
            else
            {
              v473 = 934i64;
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              eqdestroy___modelZboardZprototype95list_u1777(v191);
              v473 = 170i64;
              eqdestroy___modelZboardZprototype95list_u3239(v194);
              v473 = 34i64;
              i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
              eqdestroy___modelZsave95mongerZversionsZv0_u145(v193);
              v473 = 1024i64;
              i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            }
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v868;
            v473 = 254i64;
            v658 = v192[3];
            if ( v192[3] != v662 )
            {
              v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_69;
              v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
              failedAssertImpl__stdZassertions_u234(&v162);
              if ( *v826 )
                goto LABEL_728;
            }
          }
          v473 = 1034i64;
          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          if ( v665 >= 0 && v665 < v825[37] )
            *(_QWORD *)(v825[38] + (v665 << 6) + 48) = v290;
          else
LABEL_699:
            raiseIndexError2(v665, v825[37] - 1i64);
        }
LABEL_728:
        v473 = 934i64;
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
        eqdestroy___modelZsimulationZpreorder_u2344(v192);
        if ( *v826 )
          goto LABEL_1384;
      }
      v473 = 1041i64;
      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      v291 = v869 + 1;
      if ( __OFADD__(1i64, v869) )
      {
LABEL_740:
        raiseOverflow();
        goto LABEL_1384;
      }
      v869 = v291;
      continue;
    }
    break;
  }
  v656 = 0i64;
  nimZeroMem_60(&v286, 16i64);
  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
  v867 = 0i64;
  v655 = v482;
  v654 = v482;
  v473 = 184i64;
  while ( v867 < v654 )
  {
    v473 = 1043i64;
    i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
    v656 = v867;
    if ( v867 < 0 || v867 >= v482 )
    {
      raiseIndexError2(v867, v482 - 1);
      goto LABEL_1384;
    }
    v78 = &v483[16 * v867];
    v79 = *((_QWORD *)v78 + 2);
    v286 = *((_QWORD *)v78 + 1);
    v287 = v79;
    v473 = 1044i64;
    if ( (unsigned __int8)v286 != 1 )
    {
      v653 = v287;
      v473 = 1048i64;
      if ( v287 < 0 || v653 >= v825[12] || v653 < 0 || v653 >= v825[12] )
        goto LABEL_782;
      *(_QWORD *)(v825[13] + 560 * v653 + 232) = *(_QWORD *)(v825[13] + 560 * v653 + 240);
      v866 = 0i64;
      v652 = 0i64;
      v651 = 0i64;
      v473 = 247i64;
      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      if ( v653 < 0 || v653 >= v825[33] )
      {
        raiseIndexError2(v653, v825[33] - 1i64);
        goto LABEL_1384;
      }
      v651 = (__int64 *)(v825[34] + 16 * v653 + 8);
      v865 = 0i64;
      v473 = 250i64;
      v650 = *v651;
      v649 = v650;
      v473 = 251i64;
      while ( v865 < v649 )
      {
        v473 = 1050i64;
        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        if ( v865 < 0 || v865 >= *v651 )
        {
          raiseIndexError2(v865, *v651 - 1);
          goto LABEL_1384;
        }
        v652 = (_QWORD *)(v651[1] + 8 * v865 + 8);
        v473 = 1051i64;
        if ( *v652 )
        {
          v473 = 1052i64;
          if ( (__int64)*v652 < 0 || *v652 >= v825[37] )
          {
            raiseIndexError2(*v652, v825[37] - 1i64);
            goto LABEL_1384;
          }
          v80 = *(_QWORD *)(v825[38] + (*v652 << 6) + 56i64);
          if ( v866 >= v80 )
            v80 = v866;
          v866 = v80;
        }
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v865;
        v473 = 254i64;
        v648 = *v651;
        if ( v648 != v649 )
        {
          v157 = TM__8dO79bDlK9csFzRs49cEE7wlw_173;
          v158 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
          failedAssertImpl__stdZassertions_u234(&v157);
          if ( *v826 )
            goto LABEL_1384;
        }
      }
      v473 = 1053i64;
      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      if ( v866 > *(_QWORD *)(a8 + 32) )
      {
        *(_QWORD *)(a8 + 32) = v866;
        v473 = 1055i64;
        v900 = v653;
      }
      v473 = 1056i64;
      if ( v653 < 0 || v653 >= v825[12] )
      {
LABEL_782:
        raiseIndexError2(v653, v825[12] - 1i64);
        goto LABEL_1384;
      }
      get_cost__modelZscores_u2321(&v282, v825[13] + 560 * v653 + 8);
      if ( *v826 )
        goto LABEL_1384;
      v281 = v283 + v866;
      if ( __OFADD__(v283, v866) )
        goto LABEL_740;
      v647 = v281;
      v646 = 0i64;
      v645 = 0i64;
      v473 = 247i64;
      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      if ( v653 < 0 || v653 >= v825[49] )
      {
        raiseIndexError2(v653, v825[49] - 1i64);
        goto LABEL_1384;
      }
      v645 = (__int64 *)(v825[50] + 16 * v653 + 8);
      v864 = 0i64;
      v473 = 250i64;
      v644 = *v645;
      v643 = v644;
      v473 = 251i64;
      while ( v864 < v643 )
      {
        v473 = 1057i64;
        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        if ( v864 < 0 || v864 >= *v645 )
        {
          raiseIndexError2(v864, *v645 - 1);
          goto LABEL_1384;
        }
        v646 = (_QWORD *)(v645[1] + 8 * v864 + 8);
        v473 = 1058i64;
        if ( *v646 )
        {
          v473 = 1059i64;
          if ( (__int64)*v646 < 0 || *v646 >= v825[37] )
          {
LABEL_803:
            raiseIndexError2(*v646, v825[37] - 1i64);
            goto LABEL_1384;
          }
          if ( v647 > *(_QWORD *)(v825[38] + (*v646 << 6) + 56i64) )
          {
            v473 = 1060i64;
            if ( (__int64)*v646 < 0 )
              goto LABEL_803;
            if ( *v646 >= v825[37] )
              goto LABEL_803;
            *(_QWORD *)(v825[38] + (*v646 << 6) + 56i64) = v647;
            v473 = 1061i64;
            if ( (__int64)*v646 < 0 || *v646 >= v825[37] )
              goto LABEL_803;
            *(_QWORD *)(v825[38] + (*v646 << 6) + 64i64) = v653;
          }
        }
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        ++v864;
        v473 = 254i64;
        v642 = *v645;
        if ( v642 != v643 )
        {
          v157 = TM__8dO79bDlK9csFzRs49cEE7wlw_175;
          v158 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
          failedAssertImpl__stdZassertions_u234(&v157);
          if ( *v826 )
            goto LABEL_1384;
        }
      }
    }
    else
    {
      v473 = 1045i64;
      nimZeroMem_60(&v284, 16i64);
      v284 = handle_cluster__modelZsimulationZpreorder_u21176;
      v285 = v825;
      if ( v825 )
        ((void (__fastcall *)(__int64, _QWORD *))v284)(v287, v285);
      else
        ((void (__fastcall *)(__int64))v284)(v287);
      if ( *v826 )
        goto LABEL_1384;
    }
    ++v867;
    v473 = 187i64;
    v641 = v482;
    if ( v482 != v654 )
    {
      v157 = TM__8dO79bDlK9csFzRs49cEE7wlw_176;
      v158 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
      failedAssertImpl__stdZassertions_u234(&v157);
      if ( *v826 )
        goto LABEL_1384;
    }
  }
  nimZeroMem_60(v194, 64i64);
  v640 = 0i64;
  v863 = 0i64;
  v473 = 183i64;
  v639 = v825[37];
  v638 = v639;
  v473 = 184i64;
  while ( 1 )
  {
    if ( v863 >= v638 )
    {
      v473 = 934i64;
      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
      eqdestroy___modelZsimulationZpreorder_u2344(v194);
      v279 = 0i64;
      v280 = 0i64;
      v277 = 0i64;
      v278 = 0i64;
      v275 = 0i64;
      v276 = 0i64;
      v632 = 0i64;
      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      v861 = 0i64;
      v473 = 250i64;
      v631 = v825[31];
      v630 = v631;
      v473 = 251i64;
      while ( v861 < v630 )
      {
        nimZeroMem_60(v193, 560i64);
        nimZeroMem_60(v194, 1448i64);
        v473 = 1074i64;
        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
        if ( v861 >= 0 && v861 < v825[31] )
        {
          v632 = (_QWORD *)(v825[32] + 8 * v861 + 8);
          v473 = 34i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
          if ( (__int64)*v632 >= 0 && *v632 < v825[12] )
          {
            eqcopy___modelZsave95mongerZversionsZv0_u148(v193, v825[13] + 560i64 * *v632 + 8);
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v629 = v193[0];
            v473 = 1077i64;
            v628 = 0i64;
            v628 = (const void *)X5BX5D___modelZboardZprototype95list_u4239(
                                   refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
                                   LOBYTE(v193[0]));
            if ( !*v826 )
            {
              qmemcpy(v194, v628, 0x5A8ui64);
              v473 = 1078i64;
              v860 = 0;
              v859 = WORD1(v194[8]) != 0;
              if ( WORD1(v194[8]) )
              {
                v627 = v194[12];
                v859 = v194[12] == 0;
              }
              v860 = v859;
              if ( v859 )
              {
                v626 = v194[14];
                v860 = v194[14] == 0;
              }
              v625 = v860;
              v473 = 1079i64;
              v858 = WORD2(v194[8]) != 0;
              if ( WORD2(v194[8]) )
              {
                v624 = v194[16];
                v858 = v194[16] == 0;
              }
              v623 = v858;
              v473 = 1081i64;
              if ( !v625 )
              {
                if ( !v623 )
                {
                  v620 = 0i64;
                  v473 = 1086i64;
                  v620 = *v632;
                  add__modelZsave95mongerZcommon_u5717(&v277, v620);
                }
                else
                {
                  v621 = 0i64;
                  v473 = 1084i64;
                  v621 = *v632;
                  add__modelZsave95mongerZcommon_u5717(&v275, v621);
                }
              }
              else
              {
                v622 = 0i64;
                v473 = 1082i64;
                v622 = *v632;
                add__modelZsave95mongerZcommon_u5717(&v279, v622);
              }
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v861;
              v473 = 254i64;
              v619 = v825[31];
              if ( v619 != v630 )
              {
                v157 = TM__8dO79bDlK9csFzRs49cEE7wlw_179;
                v158 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
                failedAssertImpl__stdZassertions_u234(&v157);
              }
            }
          }
          else
          {
            raiseIndexError2(*v632, v825[12] - 1i64);
          }
        }
        else
        {
          raiseIndexError2(v861, v825[31] - 1i64);
        }
        v473 = 34i64;
        i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
        eqdestroy___modelZsave95mongerZversionsZv0_u145(v193);
        if ( *v826 )
          goto LABEL_870;
      }
      v473 = 1088i64;
      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      if ( v280 )
        v81 = v280 + 8;
      else
        v81 = 0i64;
      sort__modelZsimulationZpreorder_u27209(v81, v279, 1i64);
      if ( !*v826 )
      {
        v473 = 1089i64;
        v82 = v276 ? (__int64)(v276 + 8) : 0i64;
        sort__modelZsimulationZpreorder_u27209(v82, v275, 1i64);
        if ( !*v826 )
        {
          v273 = v279;
          v274 = v280;
          v473 = 982i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
          eqwasMoved___modelZsave95mongerZcommon_u5609(&v279);
          v271 = v277;
          v272 = v278;
          v473 = 982i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
          eqwasMoved___modelZsave95mongerZcommon_u5609(&v277);
          v473 = 1091i64;
          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          v269 = 0i64;
          v270 = 0i64;
          v157 = v273;
          v158 = v274;
          v162 = v271;
          v163 = v272;
          amp___modelZsimulationZpreorder_u27374(&v269, &v157, &v162);
          v267 = v275;
          v268 = v276;
          v473 = 982i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
          eqwasMoved___modelZsave95mongerZcommon_u5609(&v275);
          v473 = 1091i64;
          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          v162 = v269;
          v163 = v270;
          v155 = v267;
          v156 = v268;
          amp___modelZsimulationZpreorder_u27374(&v157, &v162, &v155);
          v480 = v157;
          v481 = v158;
        }
      }
LABEL_870:
      v473 = 982i64;
      i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
      v157 = v275;
      v158 = v276;
      eqdestroy___modelZsave95mongerZcommon_u5612(&v157);
      v157 = v277;
      v158 = v278;
      eqdestroy___modelZsave95mongerZcommon_u5612(&v157);
      v157 = v279;
      v158 = v280;
      eqdestroy___modelZsave95mongerZcommon_u5612(&v157);
      if ( *v826 )
        break;
      v473 = 1094i64;
      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      v618 = v480;
      v617 = v825[12];
      if ( v480 != v617 )
      {
        v265 = 0i64;
        v266 = 0i64;
        v263 = 0i64;
        v264 = 0i64;
        nimZeroMem_60(v262, 24i64);
        nimZeroMem_60(v261, 24i64);
        nimZeroMem_60(v194, 560i64);
        v616 = 0i64;
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
        v857 = 0i64;
        v473 = 183i64;
        v615 = v825[12];
        v614 = v615;
        v473 = 184i64;
        while ( 1 )
        {
          if ( v857 >= v614 )
            goto LABEL_894;
          v616 = v857;
          v473 = 34i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
          if ( v857 < 0 || v857 >= v825[12] )
          {
            raiseIndexError2(v857, v825[12] - 1i64);
            goto LABEL_894;
          }
          eqcopy___modelZsave95mongerZversionsZv0_u148(v194, v825[13] + 560 * v857 + 8);
          v473 = 1098i64;
          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          v613 = 0;
          if ( v481 )
            v83 = v481 + 8;
          else
            v83 = 0i64;
          v613 = contains__modelZtranslations_u2303_5(v83, v480, v616);
          if ( !v613 )
          {
            v473 = 1099i64;
            if ( v616 < 0 || v616 >= v825[12] )
              goto LABEL_889;
            nimZeroMem_60(&v258, 8i64);
            v84 = (char *)v825[34];
            v157 = v825[33];
            v158 = v84;
            v85 = (char *)v825[38];
            v162 = v825[37];
            v163 = v85;
            v258 = infer_size__modelZsimulationZpreorder_u1999(
                     (int)v825 + 96,
                     (unsigned int)&v157,
                     (unsigned int)&v162,
                     v616,
                     v194[28]);
            if ( *v826 )
              goto LABEL_894;
            *(_QWORD *)(v825[13] + 560 * v616 + 240) = v258;
            v473 = 1100i64;
            if ( v616 < 0 || v616 >= v825[12] )
            {
LABEL_889:
              raiseIndexError2(v616, v825[12] - 1i64);
LABEL_894:
              v473 = 34i64;
              i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
              eqdestroy___modelZsave95mongerZversionsZv0_u145(v194);
              if ( !*v826 )
              {
                v473 = 1102i64;
                i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                *((_BYTE *)v825 + 336) = 1;
                nimZeroMem_60(v194, 560i64);
                v611 = 0i64;
                i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                v856 = 0i64;
                v473 = 183i64;
                v610 = v825[12];
                v609 = v610;
                v473 = 184i64;
                while ( v856 < v609 )
                {
                  v611 = v856;
                  v473 = 34i64;
                  i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                  if ( v856 < 0 || v856 >= v825[12] )
                  {
                    raiseIndexError2(v856, v825[12] - 1i64);
                    goto LABEL_965;
                  }
                  eqcopy___modelZsave95mongerZversionsZv0_u148(v194, v825[13] + 560 * v856 + 8);
                  v473 = 1105i64;
                  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                  v608 = 0;
                  v608 = eqeq___modelZmodel95types_u853(v194[28], *(_QWORD *)refptr_AUTO_SIZE__modelZmodel95types_u54);
                  if ( v608 == 1 )
                  {
                    v473 = 1106i64;
                    if ( v611 < 0 || v611 >= v825[12] )
                    {
                      raiseIndexError2(v611, v825[12] - 1i64);
                      goto LABEL_965;
                    }
                    nimZeroMem_60(&v257, 8i64);
                    v257 = bits__modelZsave95mongerZcommon_u192(8i64);
                    if ( *v826 )
                      goto LABEL_965;
                    *(_QWORD *)(v825[13] + 560 * v611 + 232) = v257;
                  }
                  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                  ++v856;
                  v473 = 187i64;
                  v607 = v825[12];
                  if ( v607 != v609 )
                  {
                    v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_181;
                    v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                    failedAssertImpl__stdZassertions_u234(&v162);
                    if ( *v826 )
                      goto LABEL_965;
                  }
                }
                v473 = 34i64;
                i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                eqdestroy___modelZsave95mongerZversionsZv0_u145(v194);
                nimZeroMem_60(v194, 560i64);
                v606 = 0i64;
                i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                v855 = 0i64;
                v473 = 183i64;
                v605 = v825[12];
                v604 = v605;
                v473 = 184i64;
                while ( 1 )
                {
                  if ( v855 >= v604 )
                    goto LABEL_928;
                  v606 = v855;
                  v473 = 34i64;
                  i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                  if ( v855 < 0 || v855 >= v825[12] )
                    break;
                  eqcopy___modelZsave95mongerZversionsZv0_u148(v194, v825[13] + 560 * v855 + 8);
                  v473 = 1131i64;
                  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                  v603 = v263;
                  if ( v263 )
                  {
                    v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_183;
                    v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_182;
                    failedAssertImpl__stdZassertions_u234(&v162);
                    if ( *v826 )
                      goto LABEL_928;
                  }
                  v473 = 1132i64;
                  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                  nimZeroMem_60(&v255, 16i64);
                  v255 = find_circular_path__modelZsimulationZpreorder_u27451;
                  v256 = v825;
                  v253 = 0i64;
                  v254 = 0i64;
                  if ( v825 )
                  {
                    ((void (__fastcall *)(__int64 *, __int64 *, __int64, _QWORD *))v255)(&v253, &v263, v606, v256);
                  }
                  else
                  {
                    ((void (__fastcall *)(__int64 *, __int64 *, __int64))v255)(&v162, &v263, v606);
                    v253 = v162;
                    v254 = v163;
                  }
                  if ( *v826 )
                    goto LABEL_928;
                  v473 = 982i64;
                  i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
                  v162 = v253;
                  v163 = v254;
                  eqsink___modelZsave95mongerZcommon_u5621(&v265, &v162);
                  v473 = 1133i64;
                  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                  v602 = v265;
                  if ( v265 > 0 )
                  {
                    v473 = 34i64;
                    i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                    eqdestroy___modelZsave95mongerZversionsZv0_u145(v194);
                    v473 = 1134i64;
                    i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                    goto LABEL_929;
                  }
                  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                  ++v855;
                  v473 = 187i64;
                  v601 = v825[12];
                  if ( v601 != v604 )
                  {
                    v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_190;
                    v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                    failedAssertImpl__stdZassertions_u234(&v162);
                    if ( *v826 )
                      goto LABEL_928;
                  }
                }
                raiseIndexError2(v855, v825[12] - 1i64);
LABEL_928:
                v473 = 34i64;
                i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                eqdestroy___modelZsave95mongerZversionsZv0_u145(v194);
                if ( !*v826 )
                {
LABEL_929:
                  v600 = 0i64;
                  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                  v854 = 0i64;
                  v599 = v265;
                  v598 = v265;
                  v473 = 251i64;
                  while ( 1 )
                  {
                    if ( v854 >= v598 )
                    {
                      v473 = 1145i64;
                      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                      v259 = 0i64;
                      v260 = 0i64;
                      v86 = (void *)v825[13];
                      v259 = v825[12];
                      v260 = v86;
                      v586 = 0i64;
                      v159 = v262[0];
                      v160 = v262[1];
                      v161 = (void *)v262[2];
                      v162 = v259;
                      v163 = (char *)v86;
                      v87 = v825[18];
                      v152 = v825[17];
                      v153 = v87;
                      v154 = v825[19];
                      v88 = v825[7];
                      v149 = v825[6];
                      v150 = v88;
                      v151 = v825[8];
                      v89 = v825[4];
                      v146 = v825[3];
                      v147 = v89;
                      v148 = v825[5];
                      v586 = set_critical_path__modelZsimulationZpreorder_u2428(
                               (unsigned int)&v159,
                               (unsigned int)v261,
                               (unsigned int)&v162,
                               (int)v825 + 8,
                               (__int64)&v152,
                               (__int64)&v149,
                               (__int64)&v146,
                               1);
                      goto LABEL_965;
                    }
                    v473 = 1139i64;
                    i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                    if ( v854 < 0 || v854 >= v265 )
                      break;
                    v600 = &v266[8 * v854 + 8];
                    v473 = 1140i64;
                    incl__modelZboardZboard_u11061(v262, *(_QWORD *)v600);
                    if ( *v826 )
                      goto LABEL_965;
                    v597 = 0i64;
                    v596 = 0i64;
                    v473 = 247i64;
                    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                    if ( *(__int64 *)v600 < 0 || *(_QWORD *)v600 >= v825[49] )
                    {
                      raiseIndexError2(*(_QWORD *)v600, v825[49] - 1i64);
                      goto LABEL_965;
                    }
                    v596 = (__int64 *)(v825[50] + 16i64 * *(_QWORD *)v600 + 8);
                    v853 = 0i64;
                    v473 = 250i64;
                    v595 = *v596;
                    v594 = v595;
                    v473 = 251i64;
                    while ( v853 < v594 )
                    {
                      v473 = 1141i64;
                      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                      if ( v853 < 0 || v853 >= *v596 )
                      {
                        raiseIndexError2(v853, *v596 - 1);
                        goto LABEL_965;
                      }
                      v597 = (_QWORD *)(v596[1] + 8 * v853 + 8);
                      v593 = 0i64;
                      v592 = 0i64;
                      v473 = 247i64;
                      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                      if ( (__int64)*v597 < 0 || *v597 >= v825[37] )
                      {
                        raiseIndexError2(*v597, v825[37] - 1i64);
                        goto LABEL_965;
                      }
                      v592 = (__int64 *)(v825[38] + (*v597 << 6) + 8i64);
                      v852 = 0i64;
                      v473 = 250i64;
                      v591 = *v592;
                      v590 = v591;
                      v473 = 251i64;
                      while ( v852 < v590 )
                      {
                        v473 = 1142i64;
                        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                        if ( v852 < 0 || v852 >= *v592 )
                        {
                          raiseIndexError2(v852, *v592 - 1);
                          goto LABEL_965;
                        }
                        v593 = (_QWORD *)(v592[1] + 8 * v852 + 8);
                        v473 = 1143i64;
                        incl__modelZboardZboard_u11061(v261, *v593);
                        if ( !*v826 )
                        {
                          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                          ++v852;
                          v473 = 254i64;
                          v589 = *v592;
                          if ( v589 == v590 )
                            continue;
                          v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_191;
                          v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
                          failedAssertImpl__stdZassertions_u234(&v162);
                          if ( !*v826 )
                            continue;
                        }
                        goto LABEL_965;
                      }
                      ++v853;
                      v473 = 254i64;
                      v588 = *v596;
                      if ( v588 != v594 )
                      {
                        v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_192;
                        v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
                        failedAssertImpl__stdZassertions_u234(&v162);
                        if ( *v826 )
                          goto LABEL_965;
                      }
                    }
                    ++v854;
                    v473 = 254i64;
                    v587 = v265;
                    if ( v265 != v598 )
                    {
                      v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_193;
                      v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
                      failedAssertImpl__stdZassertions_u234(&v162);
                      if ( *v826 )
                        goto LABEL_965;
                    }
                  }
                  raiseIndexError2(v854, v265 - 1);
                }
              }
LABEL_965:
              v473 = 441i64;
              i = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
              eqdestroy___modelZboardZboard_u15245(v261);
              eqdestroy___modelZboardZboard_u15245(v262);
              v473 = 982i64;
              i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
              v162 = v263;
              v163 = v264;
              eqdestroy___modelZsave95mongerZcommon_u5612(&v162);
              v162 = v265;
              v163 = v266;
              eqdestroy___modelZsave95mongerZcommon_u5612(&v162);
              if ( *v826 )
                goto LABEL_1384;
LABEL_1084:
              v473 = 982i64;
              i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
              v162 = v480;
              v163 = v481;
              eqsink___modelZsave95mongerZcommon_u5621(a8, &v162);
              eqwasMoved___modelZsave95mongerZcommon_u5609(&v480);
              nimZeroMem_60(v192, 560i64);
              v554 = 0i64;
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              v841 = 0i64;
              v473 = 183i64;
              v553 = v825[12];
              v552 = v553;
              v473 = 184i64;
              while ( 2 )
              {
                if ( v841 >= v552 )
                {
LABEL_1221:
                  v473 = 34i64;
                  i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                  eqdestroy___modelZsave95mongerZversionsZv0_u145(v192);
                  if ( *v826 )
                    goto LABEL_1384;
                  nimZeroMem_60(v194, 560i64);
                  v529 = 0i64;
                  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                  v835 = 0i64;
                  v473 = 183i64;
                  v528 = v825[12];
                  v527 = v528;
                  v473 = 184i64;
                  while ( 2 )
                  {
                    if ( v835 < v527 )
                    {
                      v529 = v835;
                      v473 = 34i64;
                      i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                      if ( v835 < 0 || v835 >= v825[12] )
                      {
                        raiseIndexError2(v835, v825[12] - 1i64);
                        break;
                      }
                      eqcopy___modelZsave95mongerZversionsZv0_u148(v194, v825[13] + 560 * v835 + 8);
                      nimZeroMem_60(&v179, 48i64);
                      v526 = 0i64;
                      v473 = 1388i64;
                      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                      nimZeroMem_60(&v179, 48i64);
                      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                      v834 = 0i64;
                      v525 = v194[30];
                      v524 = v194[30];
                      v473 = 184i64;
LABEL_1228:
                      if ( v834 >= v524 )
                      {
LABEL_1263:
                        eqdestroy___modelZsave95mongerZversionsZv0_u362(&v179);
                        if ( *v826 )
                          break;
                        v473 = 1420i64;
                        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                        v832 = 0;
                        v129 = LOBYTE(v194[0]) == 84 || LOBYTE(v194[0]) == 85;
                        v832 = v129;
                        if ( v129 )
                        {
                          v473 = 1421i64;
                          v518 = 0;
                          v518 = eqeq___modelZsave95mongerZversionsZv7_u353(
                                   v194[2],
                                   *(_QWORD *)refptr_NO_ID__modelZsave95mongerZcommon_u3361);
                          v832 = v518 == 0;
                        }
                        if ( v832 )
                        {
                          nimZeroMem_60(v192, 72i64);
                          v206 = 0i64;
                          v207 = 0i64;
                          v204 = 0i64;
                          v205 = 0i64;
                          v473 = 1423i64;
                          v517 = 0i64;
                          v517 = (__int64 *)X5BX5D___modelZsimulationZpreorder_u28460(v487, v194[2]);
                          if ( !*v826 )
                          {
                            v516 = *v517;
                            v473 = 1425i64;
                            nimZeroMem_60(v192, 72i64);
                            v473 = 1426i64;
                            v202 = 0i64;
                            v203 = 0i64;
                            if ( v194[6] <= 0 )
                              goto LABEL_1283;
                            dollar___modelZsave95mongerZcommon_u260(&v206, *(_QWORD *)(v194[7] + 64));
                            if ( !*v826 )
                            {
                              if ( v194[6] <= 0 )
                              {
LABEL_1283:
                                raiseIndexError2(0i64, v194[6] - 1);
                              }
                              else
                              {
                                z_state_index__modelZsave95mongerZcommon_u5499 = 0i64;
                                v130 = *(_QWORD *)(v194[7] + 24);
                                v159 = *(_QWORD *)(v194[7] + 16);
                                v160 = v130;
                                v161 = *(void **)(v194[7] + 32);
                                z_state_index__modelZsave95mongerZcommon_u5499 = get_z_state_index__modelZsave95mongerZcommon_u5499(&v159);
                                if ( !*v826 )
                                {
                                  dollar___systemZdollars_u14(&v204, z_state_index__modelZsave95mongerZcommon_u5499);
                                  if ( !*v826 )
                                  {
                                    rawNewString(&v162, v206 + v204 + 11);
                                    v202 = v162;
                                    v203 = (__int64)v163;
                                    v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_251;
                                    v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_220;
                                    appendString_25(&v202, &v162);
                                    v162 = v206;
                                    v163 = v207;
                                    appendString_25(&v202, &v162);
                                    v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_253;
                                    v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_252;
                                    appendString_25(&v202, &v162);
                                    v162 = v204;
                                    v163 = v205;
                                    appendString_25(&v202, &v162);
                                    v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_254;
                                    v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_224;
                                    appendString_25(&v202, &v162);
                                    v192[4] = v202;
                                    v192[5] = v203;
                                    v473 = 1427i64;
                                    if ( v194[6] <= 0 )
                                      goto LABEL_1283;
                                    state_index__modelZsave95mongerZcommon_u5502 = 0i64;
                                    v131 = *(_QWORD *)(v194[7] + 24);
                                    v159 = *(_QWORD *)(v194[7] + 16);
                                    v160 = v131;
                                    v161 = *(void **)(v194[7] + 32);
                                    state_index__modelZsave95mongerZcommon_u5502 = get_state_index__modelZsave95mongerZcommon_u5502(
                                                                                     &v159,
                                                                                     0i64);
                                    if ( !*v826 )
                                    {
                                      v132 = __OFADD__(
                                               *refptr_simulation_state__modelZsimulator95types_u81,
                                               state_index__modelZsave95mongerZcommon_u5502);
                                      v201 = *refptr_simulation_state__modelZsimulator95types_u81
                                           + state_index__modelZsave95mongerZcommon_u5502;
                                      if ( v132 )
                                      {
                                        raiseOverflow();
                                      }
                                      else
                                      {
                                        v192[2] = v201;
                                        if ( v194[6] <= 0 )
                                          goto LABEL_1283;
                                        v192[3] = *(_QWORD *)(v194[7] + 64);
                                        v473 = 1429i64;
                                        LODWORD(v192[7]) = get_custom_position__modelZboardZcustom95prototype_u78(*(unsigned int *)((char *)v194 + 2));
                                        if ( !*v826 )
                                        {
                                          BYTE4(v192[7]) = LOBYTE(v194[0]) == 84;
                                          v192[8] = v194[1];
                                          v473 = 1433i64;
                                          if ( v516 >= 0 && v516 < v825[12] )
                                          {
                                            nimZeroMem_60(v193, 72i64);
                                            v193[0] = v192[0];
                                            v193[1] = v192[1];
                                            v193[2] = v192[2];
                                            v193[3] = v192[3];
                                            v193[4] = v192[4];
                                            v193[5] = v192[5];
                                            v193[6] = v192[6];
                                            v193[7] = v192[7];
                                            v193[8] = v192[8];
                                            v473 = 934i64;
                                            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                                            eqwasMoved___modelZsave95mongerZversionsZv0_u511(v192);
                                            v473 = 1433i64;
                                            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                                            add__modelZsimulationZpreorder_u28615(v825[13] + 560 * v516 + 256 + 8, v193);
                                          }
                                          else
                                          {
                                            raiseIndexError2(v516, v825[12] - 1i64);
                                          }
                                        }
                                      }
                                    }
                                  }
                                }
                              }
                            }
                          }
                          v473 = 394i64;
                          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                          if ( v205 && (*(_QWORD *)v205 & 0x4000000000000000i64) == 0 )
                            deallocShared(v205);
                          if ( v207 && (*(_QWORD *)v207 & 0x4000000000000000i64) == 0 )
                            deallocShared(v207);
                          v473 = 934i64;
                          eqdestroy___modelZsave95mongerZversionsZv0_u514(v192);
                          if ( *v826 )
                            break;
                        }
                        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                        ++v835;
                        v473 = 187i64;
                        v513 = v825[12];
                        if ( v513 != v527 )
                        {
                          v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_256;
                          v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                          failedAssertImpl__stdZassertions_u234(&v162);
                          if ( *v826 )
                            break;
                        }
                        continue;
                      }
                      nimZeroMem_60(v191, 72i64);
                      nimZeroMem_60(v192, 72i64);
                      v526 = v834;
                      v473 = 934i64;
                      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                      if ( v834 < 0 || v834 >= v194[30] )
                      {
                        raiseIndexError2(v834, v194[30] - 1);
                        goto LABEL_1262;
                      }
                      eqcopy___modelZsave95mongerZversionsZv0_u365(&v179, v194[31] + 48 * v834 + 8);
                      v473 = 1389i64;
                      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                      nimZeroMem_60(v191, 72i64);
                      v473 = 1391i64;
                      v523 = 0;
                      v523 = eqeq___modelZsave95mongerZversionsZv7_u353(
                               v180,
                               *(_QWORD *)refptr_NO_ID__modelZsave95mongerZcommon_u3361);
                      if ( v523 != 1 )
                      {
                        v473 = 1398i64;
                        nimZeroMem_60(&v210, 16i64);
                        v210 = get_linked_index__modelZsimulationZpreorder_u28319;
                        v211 = v825;
                        v473 = 1399i64;
                        v209 = mix__modelZsave95mongerZcommon_u3388(v194[2], v179, v180);
                        if ( !*v826 )
                        {
                          if ( v211 )
                            v210(v209, v183, v184, (int)v191, (__int64)v211);
                          else
                            ((void (__fastcall *)(__int64, __int64, __int64, __int64 *))v210)(v209, v183, v184, v191);
                          if ( !*v826 )
                            goto LABEL_1244;
                        }
                      }
                      else
                      {
                        v473 = 1392i64;
                        nimZeroMem_60(&v213, 16i64);
                        v213 = get_linked_index__modelZsimulationZpreorder_u28319;
                        v214 = v825;
                        v473 = 1393i64;
                        v212 = mix__modelZsave95mongerZcommon_u3384(v194[2], v179);
                        if ( *v826 )
                          goto LABEL_1262;
                        if ( v214 )
                          v213(v212, v183, v184, (int)v191, (__int64)v214);
                        else
                          ((void (__fastcall *)(__int64, __int64, __int64, __int64 *))v213)(v212, v183, v184, v191);
                        if ( *v826 )
                          goto LABEL_1262;
LABEL_1244:
                        v473 = 1699i64;
                        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                        v162 = v181;
                        v163 = v182;
                        eqsink___system_u2667(v191, &v162);
                        eqwasMoved___system_u2658(&v181);
                        v473 = 1409i64;
                        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                        if ( v529 < 0 || v529 >= v825[12] )
                        {
                          raiseIndexError2(v529, v825[12] - 1i64);
                          goto LABEL_1262;
                        }
                        v473 = 934i64;
                        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                        eqdup___modelZsave95mongerZversionsZv0_u520(v191, v192);
                        v473 = 1409i64;
                        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                        add__modelZsimulationZpreorder_u28615(v825[13] + 560 * v529 + 256 + 8, v192);
                        v473 = 1411i64;
                        v833 = 0;
                        v128 = LOBYTE(v194[0]) == 82 || LOBYTE(v194[0]) == 83;
                        v833 = v128;
                        if ( v128 )
                        {
                          v473 = 1412i64;
                          v522 = 0;
                          v522 = eqeq___modelZsave95mongerZversionsZv7_u353(
                                   v194[2],
                                   *(_QWORD *)refptr_NO_ID__modelZsave95mongerZcommon_u3361);
                          v833 = v522 == 0;
                        }
                        if ( v833 )
                        {
                          v473 = 1414i64;
                          v521 = 0i64;
                          v521 = (__int64 *)X5BX5D___modelZsimulationZpreorder_u28460(v487, v194[2]);
                          if ( *v826 )
                            goto LABEL_1262;
                          v520 = *v521;
                          v473 = 1415i64;
                          nimZeroMem_60(&v208, 4i64);
                          v208 = get_custom_position__modelZboardZcustom95prototype_u78(*(unsigned int *)((char *)v194 + 2));
                          if ( *v826 )
                            goto LABEL_1262;
                          LODWORD(v191[7]) = v208;
                          BYTE4(v191[7]) = LOBYTE(v194[0]) == 82;
                          v191[8] = v194[1];
                          v473 = 1418i64;
                          if ( v520 < 0 || v520 >= v825[12] )
                          {
                            raiseIndexError2(v520, v825[12] - 1i64);
                            goto LABEL_1262;
                          }
                          nimZeroMem_60(v193, 72i64);
                          v193[0] = v191[0];
                          v193[1] = v191[1];
                          v193[2] = v191[2];
                          v193[3] = v191[3];
                          v193[4] = v191[4];
                          v193[5] = v191[5];
                          v193[6] = v191[6];
                          v193[7] = v191[7];
                          v193[8] = v191[8];
                          v473 = 934i64;
                          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                          eqwasMoved___modelZsave95mongerZversionsZv0_u511(v191);
                          v473 = 1418i64;
                          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                          add__modelZsimulationZpreorder_u28615(v825[13] + 560 * v520 + 256 + 8, v193);
                        }
                        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                        ++v834;
                        v473 = 187i64;
                        v519 = v194[30];
                        if ( v194[30] != v524 )
                        {
                          v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_250;
                          v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                          failedAssertImpl__stdZassertions_u234(&v162);
                        }
                      }
LABEL_1262:
                      v473 = 934i64;
                      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                      eqdestroy___modelZsave95mongerZversionsZv0_u514(v191);
                      if ( *v826 )
                        goto LABEL_1263;
                      goto LABEL_1228;
                    }
                    break;
                  }
                  v473 = 34i64;
                  i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                  eqdestroy___modelZsave95mongerZversionsZv0_u145(v194);
                  if ( !*v826 )
                  {
                    v473 = 1435i64;
                    i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                    *(_BYTE *)(a8 + 40) = *((_BYTE *)v825 + 336);
                    v473 = 72i64;
                    i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                    v133 = (char *)v825[13];
                    v162 = v825[12];
                    v163 = v133;
                    eqcopy___modelZsave95mongerZversionsZv0_u1079(a8 + 128, &v162);
                    v473 = 1437i64;
                    i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                    allocation_top__modelZsave95mongerZcommon_u5497 = 0i64;
                    allocation_top__modelZsave95mongerZcommon_u5497 = get_allocation_top__modelZsave95mongerZcommon_u5497();
                    if ( !*v826 )
                    {
                      *(_QWORD *)(a8 + 16) = allocation_top__modelZsave95mongerZcommon_u5497;
                      v473 = 357i64;
                      v134 = v825[44];
                      v159 = v825[43];
                      v160 = v134;
                      v161 = (void *)v825[45];
                      eqcopy___modelZsimulationZpreorder_u30618(a8 + 104, &v159);
                      v473 = 1439i64;
                      gate_cost__modelZscores_u2556 = 0i64;
                      v135 = (char *)v825[13];
                      v162 = v825[12];
                      v163 = v135;
                      gate_cost__modelZscores_u2556 = get_gate_cost__modelZscores_u2556(&v162, 1i64);
                      if ( !*v826 )
                      {
                        *(_QWORD *)(a8 + 24) = gate_cost__modelZscores_u2556;
                        nimZeroMem_60(v193, 560i64);
                        v510 = 0i64;
                        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                        v831 = 0i64;
                        v473 = 183i64;
                        v509 = v825[12];
                        v508 = v509;
                        v473 = 184i64;
                        while ( v831 < v508 )
                        {
                          v510 = v831;
                          v473 = 34i64;
                          i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                          if ( v831 < 0 || v831 >= v825[12] )
                          {
                            raiseIndexError2(v831, v825[12] - 1i64);
                            break;
                          }
                          eqcopy___modelZsave95mongerZversionsZv0_u148(v193, v825[13] + 560 * v831 + 8);
                          v473 = 1442i64;
                          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                          v830 = LOBYTE(v193[4]) == 0;
                          if ( !LOBYTE(v193[4]) )
                          {
                            v507 = 0i64;
                            v507 = X5BX5D___modelZboardZprototype95list_u4239(
                                     refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
                                     LOBYTE(v193[0]));
                            if ( *v826 )
                              break;
                            v830 = *(_QWORD *)(v507 + 56) != 0i64;
                          }
                          if ( v830 )
                          {
                            nimZeroMem_60(v194, 80i64);
                            v473 = 436i64;
                            i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
                            eqdup___modelZsave95mongerZversionsZv0_u75(&v193[10], v194);
                            v473 = 1443i64;
                            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                            X5BX5Deq___modelZsimulationZpreorder_u28887(a8 + 64, v193[1], v194);
                            if ( *v826 )
                              break;
                          }
                          v473 = 1445i64;
                          v506 = v170 - 1;
                          if ( v170 - 1 >= v510 )
                          {
                            v473 = 1448i64;
                            if ( LOBYTE(v193[4]) == 1 )
                            {
                              v473 = 1449i64;
                              if ( v193[5] < 0 || v193[5] >= *(_QWORD *)(a8 + 48) )
                              {
                                raiseIndexError2(v193[5], *(_QWORD *)(a8 + 48) - 1i64);
                                break;
                              }
                              if ( v193[7] )
                                v136 = v193[7] + 8;
                              else
                                v136 = 0i64;
                              add__modelZsimulationZpreorder_u30243(
                                *(_QWORD *)(a8 + 56) + 232 * v193[5] + 8,
                                v136,
                                v193[6]);
                            }
                            v473 = 1451i64;
                            nimZeroMem_60(v192, 232i64);
                            v199 = v193[6];
                            v200 = v193[7];
                            v473 = 34i64;
                            i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                            eqwasMoved___modelZsave95mongerZversionsZv0_u169(&v193[6]);
                            v192[0] = v199;
                            v192[1] = v200;
                            v197 = v193[8];
                            v198 = v193[9];
                            v473 = 34i64;
                            i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                            eqwasMoved___modelZsave95mongerZversionsZv0_u169(&v193[8]);
                            v192[2] = v197;
                            v192[3] = v198;
                            v192[4] = v193[10];
                            v192[5] = v193[11];
                            v192[6] = v193[12];
                            v192[7] = v193[13];
                            v192[8] = v193[14];
                            v192[9] = v193[15];
                            v192[10] = v193[16];
                            v192[11] = v193[17];
                            v192[12] = v193[18];
                            v192[13] = v193[19];
                            v195 = v193[32];
                            v196 = v193[33];
                            v473 = 34i64;
                            i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                            eqwasMoved___modelZsave95mongerZversionsZv0_u445(&v193[32]);
                            v192[14] = v195;
                            v192[15] = v196;
                            v192[16] = v193[28];
                            v192[19] = v193[58];
                            v192[27] = v193[35];
                            v192[28] = v193[36];
                            v473 = 1451i64;
                            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                            add__modelZsimulationZpreorder_u30267(a8 + 48, v192);
                            v473 = 1464i64;
                            v505 = v825[1];
                            if ( v505 > 0 )
                            {
                              v504 = 0i64;
                              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                              v829 = 0i64;
                              v503 = v193[56];
                              v502 = v193[56];
                              v473 = 251i64;
                              while ( v829 < v502 )
                              {
                                nimZeroMem_60(v194, 560i64);
                                v501 = 0i64;
                                v500 = 0;
                                v499 = 0;
                                v473 = 1465i64;
                                i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                                if ( v829 < 0 || v829 >= v193[56] )
                                {
                                  raiseIndexError2(v829, v193[56] - 1);
                                  goto LABEL_1368;
                                }
                                v504 = (_QWORD *)(v193[57] + 48 * v829 + 8);
                                v473 = 34i64;
                                i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                                if ( (__int64)*v504 < 0 || *v504 >= v825[12] )
                                {
                                  raiseIndexError2(*v504, v825[12] - 1i64);
                                  goto LABEL_1368;
                                }
                                eqcopy___modelZsave95mongerZversionsZv0_u148(v194, v825[13] + 560i64 * *v504 + 8);
                                v473 = 1467i64;
                                i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                                v137 = *v504;
                                v138 = v825[15];
                                v159 = v825[14];
                                v160 = v138;
                                v161 = (void *)v825[16];
                                v498 = getOrDefault__modelZsimulationZpreorder_u30380(&v159, v137);
                                if ( *v826 )
                                  goto LABEL_1368;
                                v473 = 1469i64;
                                v497 = 0i64;
                                v139 = *(_QWORD *)(a8 + 56) ? *(_QWORD *)(a8 + 56) + 8i64 : 0i64;
                                v497 = X5BX5D___modelZsimulationZpreorder_u30454(v139, *(_QWORD *)(a8 + 48), 1i64);
                                if ( *v826 )
                                  goto LABEL_1368;
                                v473 = 1471i64;
                                v501 = *v504;
                                v191[0] = v501;
                                v473 = 1472i64;
                                if ( v194[6] <= 0 )
                                {
                                  raiseIndexError2(0i64, v194[6] - 1);
                                  goto LABEL_1368;
                                }
                                LOBYTE(v191[5]) = *(_BYTE *)(v194[7] + 8) == 1;
                                v473 = 1473i64;
                                v140 = *(_QWORD *)(v194[7] + 48);
                                v159 = *(_QWORD *)(v194[7] + 40);
                                v160 = v140;
                                v161 = *(void **)(v194[7] + 56);
                                v191[1] = get_state_index__modelZsave95mongerZcommon_u5502(&v159, 0i64);
                                if ( *v826 )
                                  goto LABEL_1368;
                                v473 = 1474i64;
                                if ( v194[6] <= 1 )
                                  goto LABEL_1341;
                                v141 = *(_QWORD *)(v194[7] + 128);
                                v159 = *(_QWORD *)(v194[7] + 120);
                                v160 = v141;
                                v161 = *(void **)(v194[7] + 136);
                                v191[2] = get_state_index__modelZsave95mongerZcommon_u5502(&v159, 0i64);
                                if ( *v826 )
                                  goto LABEL_1368;
                                v191[4] = v194[28];
                                if ( v194[6] <= 1 )
                                {
LABEL_1341:
                                  raiseIndexError2(1i64, v194[6] - 1);
                                  goto LABEL_1368;
                                }
                                v191[3] = *(_QWORD *)(v194[7] + 144);
                                BYTE1(v191[5]) = LOBYTE(v194[0]) == 54;
                                v473 = 1478i64;
                                if ( v498 < 0
                                  || v498 >= v825[1]
                                  || (v500 = *(_BYTE *)(v825[2] + 104 * v498 + 96),
                                      BYTE2(v191[5]) = v500,
                                      v473 = 1479i64,
                                      v498 >= v825[1]) )
                                {
                                  raiseIndexError2(v498, v825[1] - 1i64);
                                  goto LABEL_1368;
                                }
                                v499 = *(_BYTE *)(v825[2] + 104 * v498 + 96);
                                BYTE3(v191[5]) = v499;
                                v473 = 1469i64;
                                add__modelZsimulationZpreorder_u18969(v497 + 136, v191);
                                i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                                ++v829;
                                v473 = 254i64;
                                v496 = v193[56];
                                if ( v193[56] != v502 )
                                {
                                  v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_258;
                                  v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
                                  failedAssertImpl__stdZassertions_u234(&v162);
                                  if ( *v826 )
                                    goto LABEL_1368;
                                }
                                v473 = 34i64;
                                i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                                eqdestroy___modelZsave95mongerZversionsZv0_u145(v194);
                              }
                            }
                            v473 = 1483i64;
                            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                            if ( v193[5] )
                            {
                              v473 = 1484i64;
                              v495 = 0i64;
                              if ( *(_QWORD *)(a8 + 56) )
                                v142 = *(_QWORD *)(a8 + 56) + 8i64;
                              else
                                v142 = 0i64;
                              v495 = X5BX5D___modelZsimulationZpreorder_u30454(v142, *(_QWORD *)(a8 + 48), 1i64);
                              if ( *v826 )
                                break;
                              if ( v193[5] < 0 || v193[5] >= v825[12] )
                              {
                                raiseIndexError2(v193[5], v825[12] - 1i64);
                                break;
                              }
                              if ( *(_QWORD *)(v825[13] + 560 * v193[5] + 64) )
                                v143 = *(_QWORD *)(v825[13] + 560 * v193[5] + 64) + 8i64;
                              else
                                v143 = 0i64;
                              add__modelZsimulationZpreorder_u30243(
                                v495,
                                v143,
                                *(_QWORD *)(v825[13] + 560 * v193[5] + 56));
                            }
                          }
                          else
                          {
                            v473 = 1446i64;
                          }
                          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                          ++v831;
                          v473 = 187i64;
                          v494 = v825[12];
                          if ( v494 != v508 )
                          {
                            v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_259;
                            v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                            failedAssertImpl__stdZassertions_u234(&v162);
                            if ( *v826 )
                              break;
                          }
                        }
LABEL_1368:
                        v473 = 34i64;
                        i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                        eqdestroy___modelZsave95mongerZversionsZv0_u145(v193);
                        if ( !*v826 )
                        {
                          nimZeroMem_60(v194, 104i64);
                          v493 = 0i64;
                          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                          v828 = 0i64;
                          v473 = 183i64;
                          v492 = v825[1];
                          v491 = v492;
                          v473 = 184i64;
                          while ( v828 < v491 )
                          {
                            v493 = v828;
                            v473 = 185i64;
                            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                            if ( v828 < 0 || v828 >= v825[1] )
                            {
                              raiseIndexError2(v828, v825[1] - 1i64);
                              break;
                            }
                            eqcopy___modelZsave95mongerZcommon_u3692(v194, v825[2] + 104 * v828 + 8);
                            v473 = 1489i64;
                            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                            v490 = v168 - 1;
                            if ( v168 - 1 < v493 )
                            {
                              v473 = 185i64;
                              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                              eqdestroy___modelZsave95mongerZcommon_u3689(v194);
                              v473 = 1490i64;
                              i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                              goto LABEL_1384;
                            }
                            v827 = v194[0];
                            v473 = 1493i64;
                            v489 = 0;
                            v144 = v825[40];
                            v159 = v825[39];
                            v160 = v144;
                            v161 = (void *)v825[41];
                            v489 = contains__modelZboardZboard_u12534(&v159, v493);
                            if ( !*v826 )
                            {
                              if ( !v489 )
                              {
                                v473 = 1494i64;
                                v827 = 1;
                              }
                              v473 = 1496i64;
                              v193[1] = v194[6];
                              LOBYTE(v193[0]) = v827;
                              v193[2] = v194[7];
                              v193[3] = v194[8];
                              v193[4] = v194[9];
                              v193[5] = v194[10];
                              LOWORD(v193[6]) = v194[11];
                              BYTE2(v193[6]) = BYTE2(v194[11]);
                              add__modelZsimulationZpreorder_u30566(a8 + 88, v193);
                              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                              ++v828;
                              v473 = 187i64;
                              v488 = v825[1];
                              if ( v488 == v491 )
                                continue;
                              v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_260;
                              v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                              failedAssertImpl__stdZassertions_u234(&v162);
                              if ( !*v826 )
                                continue;
                            }
                            break;
                          }
                          v473 = 185i64;
                          eqdestroy___modelZsave95mongerZcommon_u3689(v194);
                        }
                      }
                    }
                  }
                  goto LABEL_1384;
                }
                v554 = v841;
                v473 = 34i64;
                i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
                if ( v841 < 0 || v841 >= v825[12] )
                {
                  raiseIndexError2(v841, v825[12] - 1i64);
                  goto LABEL_1221;
                }
                eqcopy___modelZsave95mongerZversionsZv0_u148(v192, v825[13] + 560 * v841 + 8);
                nimZeroMem_60(v193, 1448i64);
                v473 = 1222i64;
                i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                v551 = 0i64;
                v551 = X5BX5D___modelZboardZprototype95list_u4239(
                         refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
                         LOBYTE(v192[0]));
                if ( *v826 )
                {
LABEL_1216:
                  v473 = 170i64;
                  eqdestroy___modelZboardZprototype95list_u3239(v193);
                  if ( *v826 )
                    goto LABEL_1221;
                }
                else
                {
                  v473 = 170i64;
                  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                  eqcopy___modelZboardZprototype95list_u3242(v193, v551);
                  v473 = 1224i64;
                  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                  if ( !LOBYTE(v192[4]) )
                  {
                    v237 = v193[7];
                    v473 = 1227i64;
                    v550 = 0;
                    v550 = eqeq___modelZboardZmemory95manager_u146(
                             v193[7],
                             *(_QWORD *)refptr_MEM_VARIABLE_WIDTH__modelZmodel95types_u18);
                    if ( v550 == 1 )
                    {
                      v473 = 1228i64;
                      v237 = to_bytes__modelZsave95mongerZcommon_u148(v192[28]);
                      if ( *v826 )
                        goto LABEL_1216;
                    }
                    v473 = 1230i64;
                    if ( LOBYTE(v192[0]) == 54 )
                    {
                      v473 = 1231i64;
                      if ( v192[37] < 0 || v192[37] >= v825[12] )
                      {
                        raiseIndexError2(v192[37], v825[12] - 1i64);
                        goto LABEL_1216;
                      }
                      ram_pipeline_depth__modelZmodel95types_u1723 = get_ram_pipeline_depth__modelZmodel95types_u1723(v825[13] + 560 * v192[37] + 8);
                      if ( *v826 )
                        goto LABEL_1216;
                      v473 = 1232i64;
                      if ( ram_pipeline_depth__modelZmodel95types_u1723 > 0 )
                      {
                        v473 = 1233i64;
                        v236 = bytes__modelZsave95mongerZcommon_u195(1i64);
                        if ( *v826 )
                          goto LABEL_1216;
                        v235 = to_bytes__modelZsave95mongerZcommon_u148(v192[28]);
                        if ( *v826 )
                          goto LABEL_1216;
                        v234 = plus___modelZsave95mongerZcommon_u233(v236, v235);
                        if ( *v826 )
                          goto LABEL_1216;
                        v233 = ram_pipeline_depth__modelZmodel95types_u1723 + 1;
                        if ( __OFADD__(1i64, ram_pipeline_depth__modelZmodel95types_u1723) )
                        {
                          raiseOverflow();
                          goto LABEL_1216;
                        }
                        v237 = star___modelZsave95mongerZcommon_u248(v234, v233);
                        if ( *v826 )
                          goto LABEL_1216;
                      }
                    }
                    v473 = 1235i64;
                    if ( v237 > 0 )
                    {
                      v473 = 1237i64;
                      if ( v554 < 0 || v554 >= v825[12] )
                        goto LABEL_1111;
                      nimZeroMem_60(v194, 80i64);
                      allocate_memory__modelZsave95mongerZcommon_u5437(&v159, v237, 0i64);
                      v194[1] = v159;
                      v194[2] = v160;
                      v194[3] = (__int64)v161;
                      if ( *v826 )
                        goto LABEL_1216;
                      v194[7] = to_bits__modelZsave95mongerZcommon_u170(v237);
                      if ( *v826 )
                        goto LABEL_1216;
                      v194[4] = 1i64;
                      nimZeroMem_60(&v194[5], 8i64);
                      v194[5] = 256i64;
                      LOBYTE(v194[6]) = 1;
                      v97 = (_QWORD *)(v825[13] + 560 * v554 + 80);
                      v98 = v194[1];
                      v97[1] = v194[0];
                      v97[2] = v98;
                      v99 = v194[3];
                      v97[3] = v194[2];
                      v97[4] = v99;
                      v100 = v194[5];
                      v97[5] = v194[4];
                      v97[6] = v100;
                      v101 = v194[7];
                      v97[7] = v194[6];
                      v97[8] = v101;
                      v102 = v194[9];
                      v97[9] = v194[8];
                      v97[10] = v102;
                      v473 = 1238i64;
                      if ( v554 < 0 || v554 >= v825[12] )
                      {
LABEL_1111:
                        raiseIndexError2(v554, v825[12] - 1i64);
                        goto LABEL_1216;
                      }
                      nimZeroMem_60(&v230, 24i64);
                      allocate_memory__modelZsave95mongerZcommon_u5437(&v159, v237, 0i64);
                      v230 = v159;
                      v231 = v160;
                      v232 = v161;
                      if ( *v826 )
                        goto LABEL_1216;
                      v103 = (_QWORD *)(v825[13] + 560 * v554 + 112);
                      v104 = v231;
                      v103[1] = v230;
                      v103[2] = v104;
                      v103[3] = v232;
                    }
                  }
                  v473 = 1240i64;
                  if ( LOBYTE(v192[4]) != 1 )
                  {
                    v473 = 1242i64;
                    if ( LOBYTE(v192[0]) != 78 )
                    {
                      nimZeroMem_60(v191, 56i64);
                      v535 = 0i64;
                      v473 = 1270i64;
                      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                      nimZeroMem_60(v191, 56i64);
                      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                      v838 = 0i64;
                      v534 = v193[16];
                      v533 = v193[16];
                      v473 = 184i64;
                      while ( v838 < v533 )
                      {
                        v535 = v838;
                        v473 = 934i64;
                        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                        if ( v838 < 0 || v838 >= v193[16] )
                        {
                          raiseIndexError2(v838, v193[16] - 1);
                          break;
                        }
                        eqcopy___modelZboardZprototype95list_u1780(v191, v193[17] + 56 * v838 + 8);
                        nimZeroMem_60(v221, 24i64);
                        v473 = 1271i64;
                        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                        if ( v535 < 0 || v535 >= v192[8] )
                        {
                          raiseIndexError2(v535, v192[8] - 1);
                          break;
                        }
                        v532 = 0;
                        v119 = (_QWORD *)(80 * v535 + v192[9]);
                        v120 = v119[3];
                        v159 = v119[2];
                        v160 = v120;
                        v161 = (void *)v119[4];
                        v121 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 1);
                        v146 = *(_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435;
                        v147 = v121;
                        v148 = *((_QWORD *)refptr_NO_ALLOC__modelZsave95mongerZcommon_u3435 + 2);
                        v532 = eqeq___modelZsimulationZcontroller_u106(&v159, &v146);
                        if ( v532 )
                        {
                          v220 = v192[28];
                          v473 = 1275i64;
                          v836 = 0;
                          v836 = eqeq___modelZmodel95types_u853(
                                   v192[28],
                                   *(_QWORD *)refptr_AUTO_SIZE__modelZmodel95types_u54);
                          if ( !v836 )
                            v836 = v192[28] <= 0;
                          if ( v836 == 1 )
                          {
                            v473 = 1276i64;
                            v220 = bits__modelZsave95mongerZcommon_u192(8i64);
                            if ( *v826 )
                              break;
                          }
                          v473 = 1278i64;
                          v162 = v192[21];
                          v163 = (char *)v192[22];
                          clamped_word_size__modelZboardZprototype95list_u4458 = proto_word_size__modelZboardZprototype95list_u4422(
                                                                                   v191,
                                                                                   v220,
                                                                                   &v162);
                          if ( *v826 )
                            break;
                          v473 = 1279i64;
                          clamped_word_size__modelZboardZprototype95list_u4458 = get_clamped_word_size__modelZboardZprototype95list_u4458(
                                                                                   LOBYTE(v192[0]),
                                                                                   clamped_word_size__modelZboardZprototype95list_u4458,
                                                                                   1i64);
                          if ( *v826 )
                            break;
                          v473 = 1280i64;
                          v218 = to_bytes__modelZsave95mongerZcommon_u148(clamped_word_size__modelZboardZprototype95list_u4458);
                          if ( *v826 )
                            break;
                          v473 = 1282i64;
                          allocate_memory__modelZsave95mongerZcommon_u5437(&v215, v218, LOBYTE(v191[0]) == 3);
                          if ( *v826 )
                            break;
                          v837 = 0;
                          v473 = 1285i64;
                          if ( LOBYTE(v191[0]) == 3 )
                          {
                            v473 = 1286i64;
                            v837 = 1;
                          }
                          v473 = 1288i64;
                          if ( v554 < 0 || v554 >= v825[12] )
                          {
                            raiseIndexError2(v554, v825[12] - 1i64);
                            break;
                          }
                          if ( v535 < 0 || v535 >= *(_QWORD *)(v825[13] + 560 * v554 + 72) )
                          {
                            raiseIndexError2(v535, *(_QWORD *)(v825[13] + 560 * v554 + 72) - 1i64);
                            break;
                          }
                          nimZeroMem_60(v194, 80i64);
                          LOBYTE(v194[0]) = v837;
                          v473 = 506i64;
                          i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
                          v146 = v215;
                          v147 = v216;
                          v148 = v217;
                          eqdup___modelZsave95mongerZcommon_u3943(&v159, &v146);
                          v221[0] = v159;
                          v221[1] = v160;
                          v221[2] = (__int64)v161;
                          v194[1] = v159;
                          v194[2] = v160;
                          v194[3] = (__int64)v161;
                          v194[4] = v215;
                          v194[5] = v216;
                          v194[6] = v217;
                          v194[7] = clamped_word_size__modelZboardZprototype95list_u4458;
                          LOWORD(v194[8]) = 1;
                          v122 = (_QWORD *)(*(_QWORD *)(v825[13] + 560 * v554 + 80) + 80 * v535);
                          v123 = v159;
                          v122[1] = v194[0];
                          v122[2] = v123;
                          v124 = v194[3];
                          v122[3] = v194[2];
                          v122[4] = v124;
                          v125 = v194[5];
                          v122[5] = v194[4];
                          v122[6] = v125;
                          v126 = v194[7];
                          v122[7] = v194[6];
                          v122[8] = v126;
                          v127 = v194[9];
                          v122[9] = v194[8];
                          v122[10] = v127;
                        }
                        else
                        {
                          v473 = 1272i64;
                        }
                        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                        ++v838;
                        v473 = 187i64;
                        v531 = v193[16];
                        if ( v193[16] != v533 )
                        {
                          v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_216;
                          v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                          failedAssertImpl__stdZassertions_u234(&v162);
                          if ( *v826 )
                            break;
                        }
                      }
                      v473 = 934i64;
                      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                      eqdestroy___modelZboardZprototype95list_u1777(v191);
                      goto LABEL_1216;
                    }
                    v473 = 1243i64;
                    v548 = 0;
                    v548 = eqeq___modelZsave95mongerZversionsZv7_u353(
                             v192[2],
                             *(_QWORD *)refptr_NO_ID__modelZsave95mongerZcommon_u3361);
                    if ( v548 )
                    {
                      v473 = 1245i64;
                      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                      nimZeroMem_60(v194, 1448i64);
                      get_custom_prototype__modelZboardZcustom95prototype95list_u451(v192[49], v194);
                      if ( !*v826 )
                      {
                        v473 = 170i64;
                        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                        eqsink___modelZboardZprototype95list_u3248(v193, v194);
                        nimZeroMem_60(v178, 56i64);
                        v547 = 0i64;
                        v473 = 1246i64;
                        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                        nimZeroMem_60(v178, 56i64);
                        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                        v840 = 0i64;
                        v546 = v193[12];
                        v545 = v193[12];
                        v473 = 184i64;
                        while ( v840 < v545 )
                        {
                          v547 = v840;
                          v473 = 934i64;
                          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                          if ( v840 < 0 || v840 >= v193[12] )
                          {
                            raiseIndexError2(v840, v193[12] - 1);
                            break;
                          }
                          eqcopy___modelZboardZprototype95list_u1780(v178, v193[13] + 56 * v840 + 8);
                          v473 = 1247i64;
                          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                          v227 = get_position__modelZboardZcache95opps_u6(
                                   *(unsigned int *)((char *)v192 + 2),
                                   v178,
                                   BYTE6(v192[0]));
                          if ( !*v826 )
                          {
                            p3__modelZsimulationZpreorder_u1974(
                              &v228,
                              *(_QWORD *)refptr_NO_ID__modelZsave95mongerZcommon_u3361,
                              v227);
                            if ( !*v826 )
                            {
                              v473 = 1248i64;
                              v544 = 0;
                              v105 = v825[7];
                              v159 = v825[6];
                              v160 = v105;
                              v161 = (void *)v825[8];
                              v162 = v228;
                              v163 = v229;
                              v544 = contains__modelZsimulationZpreorder_u9980(&v159, &v162);
                              if ( !*v826 )
                              {
                                if ( v544 != 1 )
                                  goto LABEL_1151;
                                nimZeroMem_60(v191, 104i64);
                                nimZeroMem_60(v226, 24i64);
                                v473 = 1249i64;
                                i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                                v543 = 0i64;
                                v162 = v228;
                                v163 = v229;
                                v543 = (__int64 *)X5BX5D___modelZsimulationZpreorder_u11211(v825 + 6, &v162);
                                if ( !*v826 )
                                {
                                  if ( *v543 > 0 )
                                  {
                                    if ( *(__int64 *)(v543[1] + 8) >= 0 && *(_QWORD *)(v543[1] + 8) < v825[1] )
                                    {
                                      v473 = 185i64;
                                      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                                      eqcopy___modelZsave95mongerZcommon_u3692(
                                        v191,
                                        v825[2] + 104i64 * *(_QWORD *)(v543[1] + 8) + 8);
                                      v473 = 1250i64;
                                      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                                      if ( v554 >= 0 && v554 < v825[12] )
                                      {
                                        if ( v547 >= 0 && v547 < *(_QWORD *)(v825[13] + 560 * v554 + 56) )
                                        {
                                          nimZeroMem_60(&v179, 80i64);
                                          LOBYTE(v179) = v191[0];
                                          v473 = 506i64;
                                          i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
                                          v146 = v191[7];
                                          v147 = v191[8];
                                          v148 = v191[9];
                                          eqdup___modelZsave95mongerZcommon_u3943(&v159, &v146);
                                          v226[0] = v159;
                                          v226[1] = v160;
                                          v226[2] = (__int64)v161;
                                          v180 = v159;
                                          v181 = v160;
                                          v182 = (char *)v161;
                                          v183 = v191[7];
                                          v184 = v191[8];
                                          v185 = v191[9];
                                          v186 = v191[6];
                                          LOWORD(v187) = 1;
                                          v106 = (_QWORD *)(*(_QWORD *)(v825[13] + 560 * v554 + 64) + 80 * v547);
                                          v107 = v159;
                                          v106[1] = v179;
                                          v106[2] = v107;
                                          v108 = v182;
                                          v106[3] = v181;
                                          v106[4] = v108;
                                          v109 = v184;
                                          v106[5] = v183;
                                          v106[6] = v109;
                                          v110 = v186;
                                          v106[7] = v185;
                                          v106[8] = v110;
                                          v111 = v188;
                                          v106[9] = v187;
                                          v106[10] = v111;
                                        }
                                        else
                                        {
                                          raiseIndexError2(v547, *(_QWORD *)(v825[13] + 560 * v554 + 56) - 1i64);
                                        }
                                      }
                                      else
                                      {
                                        raiseIndexError2(v554, v825[12] - 1i64);
                                      }
                                    }
                                    else
                                    {
                                      raiseIndexError2(*(_QWORD *)(v543[1] + 8), v825[1] - 1i64);
                                    }
                                  }
                                  else
                                  {
                                    raiseIndexError2(0i64, *v543 - 1);
                                  }
                                }
                                v473 = 185i64;
                                i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                                eqdestroy___modelZsave95mongerZcommon_u3689(v191);
                                if ( !*v826 )
                                {
LABEL_1151:
                                  ++v840;
                                  v473 = 187i64;
                                  v542 = v193[12];
                                  if ( v193[12] == v545 )
                                    continue;
                                  v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_214;
                                  v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                                  failedAssertImpl__stdZassertions_u234(&v162);
                                  if ( !*v826 )
                                    continue;
                                }
                              }
                            }
                          }
                          break;
                        }
                        v473 = 934i64;
                        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                        eqdestroy___modelZboardZprototype95list_u1777(v178);
                        if ( !*v826 )
                        {
                          nimZeroMem_60(v178, 56i64);
                          v541 = 0i64;
                          v473 = 1258i64;
                          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                          nimZeroMem_60(v178, 56i64);
                          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                          v839 = 0i64;
                          v540 = v193[16];
                          v539 = v193[16];
                          v473 = 184i64;
                          while ( v839 < v539 )
                          {
                            v541 = v839;
                            v473 = 934i64;
                            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                            if ( v839 < 0 || v839 >= v193[16] )
                            {
                              raiseIndexError2(v839, v193[16] - 1);
                              break;
                            }
                            eqcopy___modelZboardZprototype95list_u1780(v178, v193[17] + 56 * v839 + 8);
                            v473 = 1259i64;
                            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                            v223 = get_position__modelZboardZcache95opps_u6(
                                     *(unsigned int *)((char *)v192 + 2),
                                     v178,
                                     BYTE6(v192[0]));
                            if ( !*v826 )
                            {
                              p3__modelZsimulationZpreorder_u1974(
                                &v224,
                                *(_QWORD *)refptr_NO_ID__modelZsave95mongerZcommon_u3361,
                                v223);
                              if ( !*v826 )
                              {
                                v473 = 1260i64;
                                v538 = 0;
                                v112 = v825[7];
                                v159 = v825[6];
                                v160 = v112;
                                v161 = (void *)v825[8];
                                v162 = v224;
                                v163 = v225;
                                v538 = contains__modelZsimulationZpreorder_u9980(&v159, &v162);
                                if ( !*v826 )
                                {
                                  if ( v538 != 1 )
                                    goto LABEL_1179;
                                  nimZeroMem_60(v191, 104i64);
                                  nimZeroMem_60(v222, 24i64);
                                  v473 = 1261i64;
                                  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                                  v537 = 0i64;
                                  v162 = v224;
                                  v163 = v225;
                                  v537 = (__int64 *)X5BX5D___modelZsimulationZpreorder_u11211(v825 + 6, &v162);
                                  if ( !*v826 )
                                  {
                                    if ( *v537 > 0 )
                                    {
                                      if ( *(__int64 *)(v537[1] + 8) >= 0 && *(_QWORD *)(v537[1] + 8) < v825[1] )
                                      {
                                        v473 = 185i64;
                                        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                                        eqcopy___modelZsave95mongerZcommon_u3692(
                                          v191,
                                          v825[2] + 104i64 * *(_QWORD *)(v537[1] + 8) + 8);
                                        v473 = 1262i64;
                                        i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                                        if ( v554 >= 0 && v554 < v825[12] )
                                        {
                                          if ( v541 >= 0 && v541 < *(_QWORD *)(v825[13] + 560 * v554 + 72) )
                                          {
                                            nimZeroMem_60(&v179, 80i64);
                                            LOBYTE(v179) = v191[0];
                                            v473 = 506i64;
                                            i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
                                            v146 = v191[7];
                                            v147 = v191[8];
                                            v148 = v191[9];
                                            eqdup___modelZsave95mongerZcommon_u3943(&v159, &v146);
                                            v222[0] = v159;
                                            v222[1] = v160;
                                            v222[2] = (__int64)v161;
                                            v180 = v159;
                                            v181 = v160;
                                            v182 = (char *)v161;
                                            v183 = v191[7];
                                            v184 = v191[8];
                                            v185 = v191[9];
                                            v186 = v191[6];
                                            LOWORD(v187) = 1;
                                            v113 = (_QWORD *)(*(_QWORD *)(v825[13] + 560 * v554 + 80) + 80 * v541);
                                            v114 = v159;
                                            v113[1] = v179;
                                            v113[2] = v114;
                                            v115 = v182;
                                            v113[3] = v181;
                                            v113[4] = v115;
                                            v116 = v184;
                                            v113[5] = v183;
                                            v113[6] = v116;
                                            v117 = v186;
                                            v113[7] = v185;
                                            v113[8] = v117;
                                            v118 = v188;
                                            v113[9] = v187;
                                            v113[10] = v118;
                                          }
                                          else
                                          {
                                            raiseIndexError2(v541, *(_QWORD *)(v825[13] + 560 * v554 + 72) - 1i64);
                                          }
                                        }
                                        else
                                        {
                                          raiseIndexError2(v554, v825[12] - 1i64);
                                        }
                                      }
                                      else
                                      {
                                        raiseIndexError2(*(_QWORD *)(v537[1] + 8), v825[1] - 1i64);
                                      }
                                    }
                                    else
                                    {
                                      raiseIndexError2(0i64, *v537 - 1);
                                    }
                                  }
                                  v473 = 185i64;
                                  i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                                  eqdestroy___modelZsave95mongerZcommon_u3689(v191);
                                  if ( !*v826 )
                                  {
LABEL_1179:
                                    ++v839;
                                    v473 = 187i64;
                                    v536 = v193[16];
                                    if ( v193[16] == v539 )
                                      continue;
                                    v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_215;
                                    v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                                    failedAssertImpl__stdZassertions_u234(&v162);
                                    if ( !*v826 )
                                      continue;
                                  }
                                }
                              }
                            }
                            break;
                          }
                          v473 = 934i64;
                          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                          eqdestroy___modelZboardZprototype95list_u1777(v178);
                        }
                      }
                      goto LABEL_1216;
                    }
                    v473 = 170i64;
                    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                    eqdestroy___modelZboardZprototype95list_u3239(v193);
                    v473 = 1244i64;
                    i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                  }
                  else
                  {
                    v473 = 170i64;
                    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
                    eqdestroy___modelZboardZprototype95list_u3239(v193);
                    v473 = 1241i64;
                    i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                  }
                }
                i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                ++v841;
                v473 = 187i64;
                v530 = v825[12];
                if ( v530 != v552 )
                {
                  v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_217;
                  v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                  failedAssertImpl__stdZassertions_u234(&v162);
                  if ( *v826 )
                    goto LABEL_1221;
                }
                continue;
              }
            }
            *(_QWORD *)(v825[13] + 560 * v616 + 232) = *(_QWORD *)(v825[13] + 560 * v616 + 240);
          }
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          ++v857;
          v473 = 187i64;
          v612 = v825[12];
          if ( v612 != v614 )
          {
            v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_180;
            v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
            failedAssertImpl__stdZassertions_u234(&v162);
            if ( *v826 )
              goto LABEL_894;
          }
        }
      }
      v473 = 1151i64;
      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      v585 = v480;
      if ( v480 <= 0 )
        goto LABEL_1084;
      nimZeroMem_60(&v250, 24i64);
      nimZeroMem_60(v249, 24i64);
      v473 = 1156i64;
      if ( v900 )
      {
        v851 = v900;
        v473 = 1159i64;
        while ( 1 )
        {
          v473 = 1160i64;
          incl__modelZboardZboard_u11061(&v250, v851);
          if ( *v826 )
            goto LABEL_1083;
          v850 = 0x8000000000000000ui64;
          v849 = -1i64;
          v584 = 0i64;
          v583 = 0i64;
          v473 = 247i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          if ( v851 < 0 || v851 >= v825[33] )
          {
            raiseIndexError2(v851, v825[33] - 1i64);
            goto LABEL_1083;
          }
          v583 = (__int64 *)(v825[34] + 16 * v851 + 8);
          v848 = 0i64;
          v473 = 250i64;
          v582 = *v583;
          v581 = v582;
          v473 = 251i64;
          while ( v848 < v581 )
          {
            v473 = 1164i64;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            if ( v848 < 0 || v848 >= *v583 )
            {
              raiseIndexError2(v848, *v583 - 1);
              goto LABEL_1083;
            }
            v584 = (_QWORD *)(v583[1] + 8 * v848 + 8);
            nimZeroMem_60(v194, 64i64);
            v473 = 1165i64;
            if ( *v584 )
            {
              v473 = 934i64;
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              if ( (__int64)*v584 >= 0 && *v584 < v825[37] )
              {
                eqcopy___modelZsimulationZpreorder_u2347(v194, v825[38] + (*v584 << 6) + 8i64);
                v473 = 1167i64;
                i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
                if ( v850 < v194[6] )
                {
                  v850 = v194[6];
                  v473 = 1169i64;
                  v849 = *v584;
                }
              }
              else
              {
                raiseIndexError2(*v584, v825[37] - 1i64);
              }
              v473 = 934i64;
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              eqdestroy___modelZsimulationZpreorder_u2344(v194);
              if ( *v826 )
                goto LABEL_1083;
            }
            else
            {
              v473 = 934i64;
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              eqdestroy___modelZsimulationZpreorder_u2344(v194);
              v473 = 1165i64;
              i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            }
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            ++v848;
            v473 = 254i64;
            v580 = *v583;
            if ( v580 != v581 )
            {
              v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_206;
              v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
              failedAssertImpl__stdZassertions_u234(&v162);
              if ( *v826 )
                goto LABEL_1083;
            }
          }
          v473 = 1171i64;
          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          if ( v849 == -1 )
          {
            v473 = 1172i64;
            goto LABEL_1011;
          }
          v473 = 1174i64;
          if ( v849 < 0 || v849 >= v825[37] )
          {
LABEL_999:
            raiseIndexError2(v849, v825[37] - 1i64);
            goto LABEL_1083;
          }
          v851 = *(_QWORD *)(v825[38] + (v849 << 6) + 64);
          v473 = 1176i64;
          if ( v851 == -1 )
            break;
          v579 = 0i64;
          v578 = 0i64;
          v473 = 247i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
          if ( v849 >= v825[37] )
            goto LABEL_999;
          v578 = (__int64 *)(v825[38] + (v849 << 6) + 8);
          v847 = 0i64;
          v473 = 250i64;
          v577 = *v578;
          v576 = v577;
          v473 = 251i64;
          while ( v847 < v576 )
          {
            v473 = 1179i64;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            if ( v847 < 0 || v847 >= *v578 )
            {
              raiseIndexError2(v847, *v578 - 1);
              goto LABEL_1083;
            }
            v579 = (_QWORD *)(v578[1] + 8 * v847 + 8);
            v473 = 1180i64;
            incl__modelZboardZboard_u11061(v249, *v579);
            if ( !*v826 )
            {
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v847;
              v473 = 254i64;
              v575 = *v578;
              if ( v575 == v576 )
                continue;
              v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_207;
              v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
              failedAssertImpl__stdZassertions_u234(&v162);
              if ( !*v826 )
                continue;
            }
            goto LABEL_1083;
          }
        }
        v473 = 1177i64;
      }
LABEL_1011:
      v574 = 0i64;
      v473 = 268i64;
      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sets.nim";
      v159 = v250;
      v160 = v251;
      v161 = v252;
      v573 = len__modelZboardZboard_u15042(&v159);
      if ( *v826 )
        goto LABEL_1083;
      v572 = 0i64;
      v570 = v250 - 1;
      v571 = v250 - 1;
      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
      v846 = 0i64;
      v473 = 97i64;
      while ( v846 <= v571 )
      {
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sets.nim";
        v572 = v846;
        v473 = 270i64;
        if ( v846 < 0 || v572 >= v250 )
        {
          raiseIndexError2(v572, v250 - 1);
          goto LABEL_1083;
        }
        v569 = 0;
        v569 = isFilled__pureZcollectionsZsets_u39_2(*(_QWORD *)(v251 + 16 * v572 + 8));
        if ( *v826 )
          goto LABEL_1083;
        if ( v569 == 1 )
        {
          nimZeroMem_60(v193, 560i64);
          nimZeroMem_60(v194, 1448i64);
          v244 = 0i64;
          v245 = 0i64;
          v242 = 0i64;
          v243 = 0i64;
          v473 = 1182i64;
          i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
          if ( v572 < 0 || v572 >= v250 )
          {
            raiseIndexError2(v572, v250 - 1);
            goto LABEL_1077;
          }
          v574 = *(_QWORD *)(v251 + 16 * v572 + 16);
          v473 = 34i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
          if ( v574 < 0
            || v574 >= v825[12]
            || (eqcopy___modelZsave95mongerZversionsZv0_u148(v193, v825[13] + 560 * v574 + 8),
                v473 = 1187i64,
                i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim",
                v574 < 0)
            || v574 >= v825[12] )
          {
            raiseIndexError2(v574, v825[12] - 1i64);
            goto LABEL_1077;
          }
          get_prototype__modelZboardZcustom95prototype95list_u502(v825[13] + 560 * v574 + 8, v194);
          if ( !*v826 )
          {
            v244 = 0i64;
            v245 = 0i64;
            v473 = 1191i64;
            if ( LOBYTE(v193[4]) )
            {
              v244 = v194[14];
              v245 = (char *)v194[15];
              v473 = 934i64;
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              eqwasMoved___modelZboardZprototype95list_u1708(&v194[14]);
            }
            else
            {
              v244 = v194[12];
              v245 = (char *)v194[13];
              v473 = 934i64;
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              eqwasMoved___modelZboardZprototype95list_u1708(&v194[12]);
            }
            v473 = 1196i64;
            i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
            v242 = 0i64;
            v243 = 0i64;
            nimZeroMem_60(v192, 56i64);
            v568 = 0i64;
            v473 = 1197i64;
            nimZeroMem_60(v192, 56i64);
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            v844 = 0i64;
            v567 = v244;
            v566 = v244;
            v473 = 184i64;
            while ( v844 < v566 )
            {
              v240 = 0i64;
              v241 = 0i64;
              v568 = v844;
              v473 = 934i64;
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
              if ( v844 < 0 || v844 >= v244 )
              {
                raiseIndexError2(v844, v244 - 1);
                goto LABEL_1077;
              }
              eqcopy___modelZboardZprototype95list_u1780(v192, &v245[56 * v844 + 8]);
              i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
              v473 = 1200i64;
              v238 = get_position__modelZboardZcache95opps_u6(*(unsigned int *)((char *)v193 + 2), v192, BYTE6(v193[0]));
              if ( *v826 )
                goto LABEL_1077;
              v473 = 1198i64;
              p3__modelZsimulationZpreorder_u1974(v239, v193[2], v238);
              if ( *v826 )
                goto LABEL_1077;
              v473 = 1202i64;
              v90 = v825[7];
              v159 = v825[6];
              v160 = v90;
              v161 = (void *)v825[8];
              v162 = v239[0];
              v163 = (char *)v239[1];
              getOrDefault__modelZsimulationZpreorder_u27825(&v240, &v159, &v162);
              if ( *v826 )
                goto LABEL_1077;
              v91 = v241 ? (__int64)(v241 + 8) : 0i64;
              add__modelZsimulationZpreorder_u27898(&v242, v91, v240);
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v844;
              v473 = 187i64;
              v565 = v244;
              if ( v244 != v566 )
              {
                v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_208;
                v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
                failedAssertImpl__stdZassertions_u234(&v162);
                if ( *v826 )
                  goto LABEL_1077;
              }
              v473 = 982i64;
              i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
              v162 = v240;
              v163 = v241;
              eqdestroy___modelZsave95mongerZcommon_u5612(&v162);
            }
            v473 = 934i64;
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
            eqdestroy___modelZboardZprototype95list_u1777(v192);
            v845 = 0i64;
            v564 = 0i64;
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
            v843 = 0i64;
            v563 = v242;
            v562 = v242;
            v473 = 251i64;
            while ( v843 < v562 )
            {
              v473 = 1205i64;
              i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
              if ( v843 < 0 || v843 >= v242 )
              {
                raiseIndexError2(v843, v242 - 1);
                goto LABEL_1077;
              }
              v564 = &v243[8 * v843 + 8];
              v473 = 1206i64;
              if ( *(__int64 *)v564 < 0 || *(_QWORD *)v564 >= v825[1] )
              {
                raiseIndexError2(*(_QWORD *)v564, v825[1] - 1i64);
                goto LABEL_1077;
              }
              v92 = *(_QWORD *)(v825[2] + 104i64 * *(_QWORD *)v564 + 88);
              if ( v845 >= v92 )
                v92 = v845;
              v845 = v92;
              i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
              ++v843;
              v473 = 254i64;
              v561 = v242;
              if ( v242 != v562 )
              {
                v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_209;
                v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
                failedAssertImpl__stdZassertions_u234(&v162);
                if ( *v826 )
                  goto LABEL_1077;
              }
            }
            v560 = 0i64;
            v842 = 0i64;
            v559 = v242;
            v558 = v242;
            v473 = 251i64;
            while ( v842 < v558 )
            {
              v473 = 1208i64;
              i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
              if ( v842 < 0 || v842 >= v242 )
              {
                raiseIndexError2(v842, v242 - 1);
                goto LABEL_1077;
              }
              v560 = &v243[8 * v842 + 8];
              v473 = 1209i64;
              if ( *(__int64 *)v560 < 0 || *(_QWORD *)v560 >= v825[1] )
              {
                raiseIndexError2(*(_QWORD *)v560, v825[1] - 1i64);
                goto LABEL_1077;
              }
              if ( v845 == *(_QWORD *)(v825[2] + 104i64 * *(_QWORD *)v560 + 88)
                || (v473 = 1210i64, excl__modelZsimulationZpreorder_u27945(v249, *(_QWORD *)v560), !*v826) )
              {
                i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
                ++v842;
                v473 = 254i64;
                v557 = v242;
                if ( v242 == v558 )
                  continue;
                v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_210;
                v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
                failedAssertImpl__stdZassertions_u234(&v162);
                if ( !*v826 )
                  continue;
              }
              goto LABEL_1077;
            }
            v473 = 272i64;
            i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\pure\\collections\\sets.nim";
            v556 = 0i64;
            v159 = v250;
            v160 = v251;
            v161 = v252;
            v556 = len__modelZboardZboard_u15042(&v159);
            if ( !*v826 && v556 != v573 )
            {
              v162 = TM__8dO79bDlK9csFzRs49cEE7wlw_211;
              v163 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_198;
              failedAssertImpl__stdZassertions_u234(&v162);
            }
          }
LABEL_1077:
          v473 = 982i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
          v162 = v242;
          v163 = v243;
          eqdestroy___modelZsave95mongerZcommon_u5612(&v162);
          v473 = 934i64;
          i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
          v162 = v244;
          v163 = v245;
          eqdestroy___modelZboardZprototype95list_u1711(&v162);
          v473 = 170i64;
          eqdestroy___modelZboardZprototype95list_u3239(v194);
          v473 = 34i64;
          i = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
          eqdestroy___modelZsave95mongerZversionsZv0_u145(v193);
          if ( *v826 )
            goto LABEL_1083;
        }
        v473 = 102i64;
        i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators_1.nim";
        v246 = v846 + 1;
        if ( __OFADD__(1i64, v846) )
        {
          raiseOverflow();
          goto LABEL_1083;
        }
        v846 = v246;
      }
      v473 = 1212i64;
      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      v247 = 0i64;
      v248 = 0i64;
      v93 = (void *)v825[13];
      v247 = v825[12];
      v248 = v93;
      v555 = 0i64;
      v159 = v250;
      v160 = v251;
      v161 = v252;
      v162 = v247;
      v163 = (char *)v93;
      v94 = v825[18];
      v146 = v825[17];
      v147 = v94;
      v148 = v825[19];
      v95 = v825[7];
      v149 = v825[6];
      v150 = v95;
      v151 = v825[8];
      v96 = v825[4];
      v152 = v825[3];
      v153 = v96;
      v154 = v825[5];
      v555 = set_critical_path__modelZsimulationZpreorder_u2428(
               (unsigned int)&v159,
               (unsigned int)v249,
               (unsigned int)&v162,
               (int)v825 + 8,
               (__int64)&v146,
               (__int64)&v149,
               (__int64)&v152,
               0);
      if ( !*v826 )
        *(_QWORD *)(a8 + 176) = v555;
LABEL_1083:
      v473 = 441i64;
      i = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
      eqdestroy___modelZboardZboard_u15245(v249);
      eqdestroy___modelZboardZboard_u15245(&v250);
      if ( *v826 )
        break;
      goto LABEL_1084;
    }
    v640 = v863;
    v473 = 934i64;
    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    if ( v863 < 0 || v863 >= v825[37] )
    {
      raiseIndexError2(v863, v825[37] - 1i64);
      break;
    }
    eqcopy___modelZsimulationZpreorder_u2347(v194, v825[38] + (v863 << 6) + 8);
    v637 = 0i64;
    i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
    v862 = 0i64;
    v636 = v194[0];
    v635 = v194[0];
    v473 = 251i64;
    while ( v862 < v635 )
    {
      v473 = 1064i64;
      i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
      if ( v862 < 0 || v862 >= v194[0] )
      {
        raiseIndexError2(v862, v194[0] - 1);
        goto LABEL_1384;
      }
      v637 = (_QWORD *)(v194[1] + 8 * v862 + 8);
      v473 = 1065i64;
      if ( (__int64)*v637 < 0 || *v637 >= v825[1] )
      {
        raiseIndexError2(*v637, v825[1] - 1i64);
        goto LABEL_1384;
      }
      *(_QWORD *)(v825[2] + 104i64 * *v637 + 88) = v194[6];
      i = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\iterators.nim";
      ++v862;
      v473 = 254i64;
      v634 = v194[0];
      if ( v194[0] != v635 )
      {
        v157 = TM__8dO79bDlK9csFzRs49cEE7wlw_177;
        v158 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_20;
        failedAssertImpl__stdZassertions_u234(&v157);
        if ( *v826 )
          goto LABEL_1384;
      }
    }
    ++v863;
    v473 = 187i64;
    v633 = v825[37];
    if ( v633 != v638 )
    {
      v157 = TM__8dO79bDlK9csFzRs49cEE7wlw_178;
      v158 = (char *)&TM__8dO79bDlK9csFzRs49cEE7wlw_3;
      failedAssertImpl__stdZassertions_u234(&v157);
      if ( *v826 )
        break;
    }
  }
LABEL_1384:
  v473 = 982i64;
  i = "D:\\TuringComplete_Phu\\model\\save_monger\\common.nim";
  v162 = v480;
  v163 = v481;
  eqdestroy___modelZsave95mongerZcommon_u5612(&v162);
  v473 = 804i64;
  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  v162 = v482;
  v163 = v483;
  eqdestroy___modelZsimulationZpreorder_u30809(&v162);
  v473 = 441i64;
  i = "D:\\TuringComplete_Phu\\model\\board\\board.nim";
  eqdestroy___modelZboardZboard_u15245(&v484);
  v473 = 358i64;
  i = "D:\\TuringComplete_Phu\\model\\simulation\\preorder.nim";
  eqdestroy___modelZsimulationZpreorder_u30636(v487);
  v473 = 340i64;
  eqdestroy___modelZsimulationZpreorder_u32000(v825);
  return popFrame_80();
}


/* call 0x00000001405af092, caller set_component_size__modelZutilities_u98 @ 0x00000001405aebbd */

__int64 __fastcall set_component_size__modelZutilities_u98(__int64 a1, __int64 a2, __int64 *a3)
{
  __int64 v3; // rdx
  __int64 v5; // [rsp+0h] [rbp-80h] BYREF
  __int64 v6; // [rsp+20h] [rbp-60h] BYREF
  __int64 v7; // [rsp+28h] [rbp-58h]
  __int64 v8; // [rsp+30h] [rbp-50h]
  __int64 v9; // [rsp+38h] [rbp-48h]
  const char *v10; // [rsp+48h] [rbp-38h]
  __int64 v11; // [rsp+50h] [rbp-30h]
  const char *v12; // [rsp+58h] [rbp-28h]
  __int16 v13; // [rsp+60h] [rbp-20h]
  char v14[560]; // [rsp+70h] [rbp-10h] BYREF
  __int64 v15[145]; // [rsp+2A0h] [rbp+220h] BYREF
  __int64 clamped_word_size__modelZboardZprototype95list_u4458; // [rsp+728h] [rbp+6A8h]
  char v17[560]; // [rsp+730h] [rbp+6B0h] BYREF
  __int64 v18; // [rsp+960h] [rbp+8E0h] BYREF
  __int64 v19; // [rsp+968h] [rbp+8E8h]
  char v20[560]; // [rsp+970h] [rbp+8F0h] BYREF
  char v21[1456]; // [rsp+BA0h] [rbp+B20h] BYREF
  unsigned __int8 v22[568]; // [rsp+1150h] [rbp+10D0h] BYREF
  const void *v23; // [rsp+1388h] [rbp+1308h]
  __int64 v24; // [rsp+1390h] [rbp+1310h]
  __int64 v25; // [rsp+1398h] [rbp+1318h]
  _BYTE *v26; // [rsp+13A0h] [rbp+1320h]
  unsigned __int8 v27; // [rsp+13AEh] [rbp+132Eh]
  unsigned __int8 v28; // [rsp+13AFh] [rbp+132Fh]

  v3 = a3[1];
  v8 = *a3;
  v9 = v3;
  v10 = "set_component_size";
  v12 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  v11 = 0i64;
  v13 = 0;
  nimFrame_145(&v5 + 8);
  v26 = (_BYTE *)nimErrorFlag_141();
  v28 = 0;
  nimZeroMem_118(v22, 560i64);
  nimZeroMem_118(v21, 1448i64);
  nimZeroMem_118(v20, 560i64);
  v18 = 0i64;
  v19 = 0i64;
  v25 = 0i64;
  v24 = 0i64;
  nimZeroMem_118(v17, 560i64);
  v11 = 34i64;
  v12 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
  if ( a2 < 0 || a2 >= *(_QWORD *)(a1 + 152) )
    goto LABEL_28;
  eqcopy___modelZsave95mongerZversionsZv0_u148(v22, *(_QWORD *)(a1 + 160) + 560 * a2 + 8);
  v11 = 73i64;
  v12 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
  v23 = 0i64;
  v23 = (const void *)X5BX5D___modelZboardZprototype95list_u4239(
                        refptr_PROTOTYPES__modelZboardZprototype95list_u3752,
                        v22[0]);
  if ( *v26 )
  {
LABEL_31:
    v11 = 934i64;
    v12 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v6 = v18;
    v7 = v19;
    eqdestroy___modelZboardZboard_u17903(&v6);
    v11 = 34i64;
    v12 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    eqdestroy___modelZsave95mongerZversionsZv0_u145(v20);
    eqdestroy___modelZsave95mongerZversionsZv0_u145(v22);
    goto LABEL_32;
  }
  qmemcpy(v21, v23, 0x5A8ui64);
  v11 = 75i64;
  if ( v22[0] == 90 || v22[0] == 94 )
  {
    v11 = 76i64;
    if ( a2 < 0 || a2 >= *(_QWORD *)(a1 + 152) )
    {
LABEL_28:
      raiseIndexError2(a2, *(_QWORD *)(a1 + 152) - 1i64);
      goto LABEL_31;
    }
    *(_QWORD *)(*(_QWORD *)(a1 + 160) + 560 * a2 + 232) = *refptr_current_word_size__modelZmodel95types_u728;
    v28 = 1;
    v11 = 934i64;
    v12 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v6 = v18;
    v7 = v19;
    eqdestroy___modelZboardZboard_u17903(&v6);
    v11 = 34i64;
    v12 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    eqdestroy___modelZsave95mongerZversionsZv0_u145(v20);
    eqdestroy___modelZsave95mongerZversionsZv0_u145(v22);
  }
  else
  {
    v11 = 79i64;
    v12 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
    if ( v21[0] >= 2u )
      goto LABEL_31;
    v11 = 81i64;
    v12 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
    v27 = 0;
    v27 = *(_BYTE *)refptr_dev_mode__modelZmodel95types_u727 == 0;
    v27 &= 1u;
    if ( v27 == 1 )
      v27 = v22[472];
    if ( v27 == 1 )
      goto LABEL_31;
    v11 = 84i64;
    v12 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
    clamped_word_size__modelZboardZprototype95list_u4458 = get_clamped_word_size__modelZboardZprototype95list_u4458(
                                                             v22[0],
                                                             *refptr_current_word_size__modelZmodel95types_u728,
                                                             0);
    if ( *v26 )
      goto LABEL_31;
    v11 = 34i64;
    v12 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    if ( a2 < 0 )
      goto LABEL_28;
    if ( a2 >= *(_QWORD *)(a1 + 152) )
      goto LABEL_28;
    eqcopy___modelZsave95mongerZversionsZv0_u148(v20, *(_QWORD *)(a1 + 160) + 560 * a2 + 8);
    v11 = 86i64;
    v12 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
    if ( a2 < 0 )
      goto LABEL_28;
    if ( a2 >= *(_QWORD *)(a1 + 152) )
      goto LABEL_28;
    *(_QWORD *)(*(_QWORD *)(a1 + 160) + 560 * a2 + 232) = clamped_word_size__modelZboardZprototype95list_u4458;
    v11 = 87i64;
    if ( a2 < 0 )
      goto LABEL_28;
    if ( a2 >= *(_QWORD *)(a1 + 152) )
      goto LABEL_28;
    *(_QWORD *)(*(_QWORD *)(a1 + 160) + 560 * a2 + 240) = clamped_word_size__modelZboardZprototype95list_u4458;
    v11 = 90i64;
    v18 = 1i64;
    v19 = newSeqPayload(1i64, 1152i64, 8i64);
    nimZeroMem_118(v15, 1152i64);
    LOBYTE(v15[1]) = 0;
    v25 = a2;
    v15[2] = a2;
    v11 = 94i64;
    v24 = a2;
    v15[73] = a2;
    nimZeroMem_118(v14, 560i64);
    qmemcpy(v14, v20, sizeof(v14));
    v11 = 34i64;
    v12 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    eqwasMoved___modelZsave95mongerZversionsZv0_u142(v20, v20);
    qmemcpy(&v15[3], v14, 0x230ui64);
    v11 = 34i64;
    v12 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    if ( a2 < 0 || a2 >= *(_QWORD *)(a1 + 152) )
      goto LABEL_28;
    eqdup___modelZsave95mongerZversionsZv0_u151(*(_QWORD *)(a1 + 160) + 560 * a2 + 8, v17);
    qmemcpy(&v15[74], v17, 0x230ui64);
    qmemcpy((void *)(v19 + 8), v15, 0x480ui64);
    v11 = 100i64;
    v12 = "D:\\TuringComplete_Phu\\model\\utilities.nim";
    add_undo_changes__modelZboardZboard_u17728(&v18);
    if ( *v26 )
      goto LABEL_31;
    v28 = 1;
    v11 = 934i64;
    v12 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
    v6 = v18;
    v7 = v19;
    eqdestroy___modelZboardZboard_u17903(&v6);
    v11 = 34i64;
    v12 = "D:\\TuringComplete_Phu\\model\\save_monger\\versions\\v0.nim";
    eqdestroy___modelZsave95mongerZversionsZv0_u145(v20);
    eqdestroy___modelZsave95mongerZversionsZv0_u145(v22);
  }
LABEL_32:
  popFrame_145();
  return v28;
}


/* call 0x00000001405daa8d, caller add_component__presenterZutilitiesZhelper95functions_u5957 @ 0x00000001405da5f4 */

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


/* call 0x00000001405debbc, caller save_static_value__presenterZutilitiesZhelper95functions_u3331 @ 0x00000001405deabd */

__int64 __fastcall save_static_value__presenterZutilitiesZhelper95functions_u3331(__int64 a1, __int64 *a2, __int64 a3)
{
  __int64 v3; // rax
  __int64 v4; // rdx
  __int64 v6; // [rsp+0h] [rbp-90h] BYREF
  __int64 v7; // [rsp+20h] [rbp-70h]
  __int64 v8; // [rsp+28h] [rbp-68h]
  const char *v9; // [rsp+38h] [rbp-58h]
  __int64 v10; // [rsp+40h] [rbp-50h]
  const char *v11; // [rsp+48h] [rbp-48h]
  __int16 v12; // [rsp+50h] [rbp-40h]
  __int64 v13; // [rsp+68h] [rbp-28h]
  __int64 clamped_word_size__modelZboardZprototype95list_u4458; // [rsp+70h] [rbp-20h]
  unsigned __int8 v15; // [rsp+7Fh] [rbp-11h]
  __int64 v16; // [rsp+80h] [rbp-10h]
  _BYTE *v17; // [rsp+88h] [rbp-8h]

  v3 = *a2;
  v4 = a2[1];
  v7 = v3;
  v8 = v4;
  v9 = "save_static_value";
  v11 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
  v10 = 0i64;
  v12 = 0;
  nimFrame_149(&v6 + 6);
  v17 = (_BYTE *)nimErrorFlag_144();
  v10 = 443i64;
  v11 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
  if ( v7 >= 0 && v7 < *(_QWORD *)(a1 + 152) )
  {
    v16 = *(_QWORD *)(a1 + 160) + 560 * v7 + 8;
    v10 = 444i64;
    v15 = *(_BYTE *)v16;
    v10 = 445i64;
    clamped_word_size__modelZboardZprototype95list_u4458 = get_clamped_word_size__modelZboardZprototype95list_u4458(
                                                             v15,
                                                             a3,
                                                             0);
    if ( !*v17 )
    {
      v13 = v8;
      v10 = 447i64;
      if ( v8 )
      {
        v10 = 450i64;
        X5BX5Deq___modelZsave95mongerZversionsZv7_u70(
          v16 + 400,
          v13,
          clamped_word_size__modelZboardZprototype95list_u4458);
      }
      else
      {
        v10 = 448i64;
        *(_QWORD *)(v16 + 224) = clamped_word_size__modelZboardZprototype95list_u4458;
      }
    }
  }
  else
  {
    raiseIndexError2(v7, *(_QWORD *)(a1 + 152) - 1i64);
  }
  return popFrame_149();
}


/* call 0x00000001405ef259, caller get_static_value_string__presenterZutilitiesZhelper95functions_u3188 @ 0x00000001405ef04e */

_QWORD *__fastcall get_static_value_string__presenterZutilitiesZhelper95functions_u3188(
        _QWORD *a1,
        __int64 a2,
        __int64 *a3)
{
  __int64 v3; // rdx
  void *v4; // rdx
  __int64 v6[2]; // [rsp+20h] [rbp-60h] BYREF
  __int64 v7[4]; // [rsp+30h] [rbp-50h] BYREF
  __int64 v8; // [rsp+50h] [rbp-30h]
  __int64 v9; // [rsp+58h] [rbp-28h]
  __int64 v10; // [rsp+60h] [rbp-20h]
  __int64 clamped_word_size__modelZboardZprototype95list_u4458; // [rsp+68h] [rbp-18h]
  __int64 v12; // [rsp+70h] [rbp-10h]
  __int64 v13; // [rsp+78h] [rbp-8h]
  _QWORD v14[2]; // [rsp+80h] [rbp+0h] BYREF
  __int64 v15; // [rsp+90h] [rbp+10h]
  const char *v16; // [rsp+98h] [rbp+18h]
  __int16 v17; // [rsp+A0h] [rbp+20h]
  __int64 v18; // [rsp+B0h] [rbp+30h]
  __int64 v19; // [rsp+B8h] [rbp+38h]
  __int64 v20; // [rsp+C8h] [rbp+48h]
  __int64 v21[70]; // [rsp+D0h] [rbp+50h] BYREF
  __int64 v22; // [rsp+300h] [rbp+280h] BYREF
  void *v23; // [rsp+308h] [rbp+288h]
  char v24; // [rsp+316h] [rbp+296h]
  unsigned __int8 v25; // [rsp+317h] [rbp+297h]
  _BYTE *v26; // [rsp+318h] [rbp+298h]

  v3 = a3[1];
  v8 = *a3;
  v9 = v3;
  v14[1] = "get_static_value_string";
  v16 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
  v15 = 0i64;
  v17 = 0;
  nimFrame_149(v14);
  v26 = (_BYTE *)nimErrorFlag_144();
  v22 = 0i64;
  v23 = 0i64;
  nimZeroMem_121(v21, 560i64);
  v15 = 428i64;
  v16 = "D:\\TuringComplete_Phu\\presenter\\utilities\\helper_functions.nim";
  if ( v8 >= 0 && v8 < *(_QWORD *)(a2 + 152) )
  {
    qmemcpy(v21, (const void *)(560 * v8 + *(_QWORD *)(a2 + 160) + 8), sizeof(v21));
    v25 = v21[0];
    v20 = v9;
    v18 = 0i64;
    v19 = 0i64;
    v15 = 431i64;
    if ( v9 )
    {
      v15 = 433i64;
      v13 = bits__modelZsave95mongerZcommon_u192(8i64);
      if ( !*v26 )
      {
        v7[0] = v21[50];
        v7[1] = v21[51];
        v7[2] = v21[52];
        v12 = getOrDefault__presenterZutilitiesZhelper95functions_u3257(v7, v20, v13);
        if ( !*v26 )
        {
          v15 = 432i64;
          clamped_word_size__modelZboardZprototype95list_u4458 = get_clamped_word_size__modelZboardZprototype95list_u4458(
                                                                   v25,
                                                                   v12,
                                                                   0);
          if ( !*v26 )
            dollar___systemZdollars_u14(&v22, clamped_word_size__modelZboardZprototype95list_u4458);
        }
      }
    }
    else
    {
      v15 = 435i64;
      v24 = 0;
      v24 = eqeq___modelZmodel95types_u853(v21[28], *(_QWORD *)refptr_AUTO_SIZE__modelZmodel95types_u54);
      if ( v24 != 1 )
      {
        v15 = 438i64;
        v10 = get_clamped_word_size__modelZboardZprototype95list_u4458(v25, v21[28], 0);
        if ( !*v26 )
        {
          dollar___systemZdollars_u14(v6, v10);
          v22 = v6[0];
          v23 = (void *)v6[1];
        }
      }
      else
      {
        v15 = 436i64;
        v22 = 0i64;
        v23 = &TM__xlEKrMnRGXqvDRNJ4JVzrQ_46;
      }
    }
  }
  else
  {
    raiseIndexError2(v8, *(_QWORD *)(a2 + 152) - 1i64);
  }
  popFrame_149();
  v4 = v23;
  *a1 = v22;
  a1[1] = v4;
  return a1;
}


/* call 0x00000001405ef330, caller get_static_value_string__presenterZutilitiesZhelper95functions_u3188 @ 0x00000001405ef04e */

/* data/non-function xref from 0x0000000140beffa4 */

/* data/non-function xref from 0x0000000140beffb0 */

/* XREFS TO proto_word_size @ 0x00000001402378b1 */

/* call 0x00000001402d5cb5, caller preorder__modelZsimulationZpreorder_u8738 @ 0x00000001402cb244 */

/* call 0x00000001402dc166, caller preorder__modelZsimulationZpreorder_u8738 @ 0x00000001402cb244 */

/* data/non-function xref from 0x0000000140beffbc */

/* data/non-function xref from 0x0000000140beffc8 */
