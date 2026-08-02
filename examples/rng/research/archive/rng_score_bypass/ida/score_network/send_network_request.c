__int64 __fastcall send_network_request__modelZnetworkingZclient_u1848(__int64 a1)
{
  _QWORD v2[6]; // [rsp+0h] [rbp-80h] BYREF
  __int64 v3; // [rsp+30h] [rbp-50h]
  const char *v4; // [rsp+38h] [rbp-48h]
  __int16 v5; // [rsp+40h] [rbp-40h]
  char v6[208]; // [rsp+50h] [rbp-30h] BYREF

  v2[5] = "send_network_request";
  v4 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
  v3 = 0i64;
  v5 = 0;
  nimFrame_91(&v2[4]);
  nimZeroMem_69(v6, 200i64);
  v3 = 368i64;
  v4 = "C:\\Users\\Admin\\.choosenim\\toolchains\\nim-2.2.6\\lib\\system\\channels_builtin.nim";
  eqdup___modelZnetworkingZclient_u1888(a1, v6);
  v3 = 211i64;
  v4 = "D:\\TuringComplete_Phu\\model\\networking\\client.nim";
  send__modelZnetworkingZclient_u1850(&network_request_channel__modelZnetworkingZclient_u1837, v6);
  return popFrame_91();
}
