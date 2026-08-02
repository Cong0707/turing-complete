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
