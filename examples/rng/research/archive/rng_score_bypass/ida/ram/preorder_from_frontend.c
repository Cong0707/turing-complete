__int64 __fastcall preorder_from_frontend__presenterZutilities_u17125(__int64 a1, __int64 a2)
{
  _QWORD *v2; // rdx
  __int64 v4[2]; // [rsp+20h] [rbp-70h] BYREF
  __int64 v5; // [rsp+30h] [rbp-60h] BYREF
  _QWORD *v6; // [rsp+38h] [rbp-58h]
  char v7[8]; // [rsp+40h] [rbp-50h] BYREF
  const char *v8; // [rsp+48h] [rbp-48h]
  __int64 v9; // [rsp+50h] [rbp-40h]
  const char *v10; // [rsp+58h] [rbp-38h]
  __int16 v11; // [rsp+60h] [rbp-30h]
  __int64 v12; // [rsp+70h] [rbp-20h] BYREF
  _QWORD *v13; // [rsp+78h] [rbp-18h]
  char v14; // [rsp+87h] [rbp-9h]
  _BYTE *v15; // [rsp+88h] [rbp-8h]

  v8 = "preorder_from_frontend";
  v10 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
  v9 = 0i64;
  v11 = 0;
  nimFrame_162(v7);
  v15 = (_BYTE *)nimErrorFlag_157();
  v12 = 0i64;
  v13 = 0i64;
  v9 = 1431i64;
  v10 = "D:\\TuringComplete_Phu\\presenter\\utilities.nim";
  sim_stop_and_refresh__modelZsimulationZcompile95thread_u3763(a1);
  if ( !*v15 )
  {
    v9 = 1432i64;
    v2 = (_QWORD *)refptr_loaded_level__modelZmodel95types_u830[1];
    v5 = *refptr_loaded_level__modelZmodel95types_u830;
    v6 = v2;
    v4[0] = TM__8FyyixzftvDEeBWCL79bP9aA_219;
    v4[1] = (__int64)&TM__8FyyixzftvDEeBWCL79bP9aA_43_0;
    if ( (unsigned __int8)eqStrings_25(&v5, v4)
      || (v9 = 1433i64, set_command_setting__modelZsimulator95types_u130(6i64, 0i64), !*v15)
      && (v9 = 1434i64, reset_ui__modelZutilities_u6022(a1), !*v15) )
    {
      v9 = 1437i64;
      get_progress_string__modelZsave_u1680(&v12, 8u);
      if ( !*v15 )
      {
        v9 = 1438i64;
        v14 = 0;
        v14 = is_using_level_solution_schematic__presenterZutilities_u6348(a2);
        if ( !*v15 )
        {
          v9 = 1435i64;
          v5 = v12;
          v6 = v13;
          preorder__modelZsimulationZcompile95thread_u4293(a1, &v5, v14);
        }
      }
    }
  }
  v9 = 394i64;
  v10 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system.nim";
  if ( v13 && (*v13 & 0x4000000000000000i64) == 0 )
    deallocShared(v13);
  return popFrame_162();
}
