# Switch 103/5 A 完整逻辑 DAG

本表由 v15 端点网络直接恢复。`rN` 是物理逻辑网络编号；多 Switch 输出先合并为一个 BUS owner。
Maker/Splitter 为 `0 gate / 0 delay`，单列在末尾，不隐藏任何付费元件。

## 付费逻辑

| 元件 | arrival | cost | 输出 | 公式 |
|---:|---:|---:|---|---|
| c0 AND | 1 | 1 | r14<G3> | `AND(r6<B3>, r111<A3>)` |
| c1 NAND | 1 | 1 | r3<nG3> | `NAND(r6<B3>, r111<A3>)` |
| c2 OR | 1 | 1 | r188<V2> | `OR(r1<B2>, r124<A2>)` |
| c3 NAND | 2 | 1 | r21<X3=nP3> | `NAND(r13<V3>, r3<nG3>)` |
| BUS r174 | 2 | 4 | r174<D23=G23|P23> | SW(c4, r14<G3>, r13<V3>); SW(c9, r188<V2>, r13<V3>) |
| c5 NAND | 1 | 1 | r306<nG2> | `NAND(r1<B2>, r124<A2>)` |
| c6 OR | 1 | 1 | r13<V3> | `OR(r6<B3>, r111<A3>)` |
| c7 NOR | 4 | 1 | r18<P3*nC4> | `NOR(r21<X3=nP3>, r83<C4>)` |
| BUS r142 | 5 | 4 | r142<S3> | SW(c8, r21<X3=nP3>, r11<C3>); SW(c10, r18<P3*nC4>, r18<P3*nC4>) |
| c11 OR | 1 | 1 | r171<V1> | `OR(r37<B1>, r114<A1>)` |
| BUS r36 | 1 | 4 | r36<T0=Cin*V0> | SW(c12, r38<B0>, r30<Cin>); SW(c13, r43<A0>, r30<Cin>) |
| c14 OR | 1 | 1 | r51<V0> | `OR(r38<B0>, r43<A0>)` |
| c15 OR | 2 | 1 | r56<C1> | `OR(r34<G0>, r36<T0=Cin*V0>)` |
| c16 NOR | 2 | 1 | r54<Q0*nCin> | `NOR(r51<V0>, r30<Cin>)` |
| c17 AND | 1 | 1 | r72<G1> | `AND(r37<B1>, r114<A1>)` |
| c18 NOR | 3 | 1 | r44 | `NOR(r56<C1>, r54<Q0*nCin>)` |
| c19 OR | 4 | 1 | r41<S0> | `OR(r44, r45<G0*Cin>)` |
| c20 AND | 2 | 1 | r45<G0*Cin> | `AND(r30<Cin>, r34<G0>)` |
| c21 AND | 3 | 1 | r60<G1*C1> | `AND(r56<C1>, r72<G1>)` |
| c22 NOR | 4 | 1 | r61 | `NOR(r177<C2>, r63<Q1*nC1>)` |
| c23 OR | 5 | 1 | r138<S1> | `OR(r61, r60<G1*C1>)` |
| c24 NOR | 3 | 1 | r63<Q1*nC1> | `NOR(r171<V1>, r56<C1>)` |
| BUS r177 | 2 | 6 | r177<C2> | SW(c25, r72<G1>, r171<V1>); SW(c26, r34<G0>, r171<V1>); SW(c40, r36<T0=Cin*V0>, r171<V1>) |
| c27 AND | 4 | 1 | r79<C4*P4> | `AND(r83<C4>, r82<P4>)` |
| c28 AND | 2 | 1 | r82<P4> | `AND(r89<V4>, r85<nG4>)` |
| c29 NAND | 1 | 1 | r85<nG4> | `NAND(r78<B4>, r103<A4>)` |
| c30 OR | 1 | 1 | r89<V4> | `OR(r78<B4>, r103<A4>)` |
| c31 NOR | 4 | 1 | r152<nC4*nP4> | `NOR(r83<C4>, r82<P4>)` |
| c35 NOR | 5 | 1 | r144<S4> | `NOR(r152<nC4*nP4>, r79<C4*P4>)` |
| c36 NAND | 1 | 1 | r335<nG5> | `NAND(r84<B5>, r105<A5>)` |
| c37 OR | 1 | 1 | r163<V5> | `OR(r84<B5>, r105<A5>)` |
| c38 AND | 2 | 1 | r319<P5> | `AND(r163<V5>, r335<nG5>)` |
| c39 AND | 1 | 1 | r34<G0> | `AND(r38<B0>, r43<A0>)` |
| BUS r83 | 3 | 4 | r83<C4> | SW(c41, r191<R23=G2|G3>, r174<D23=G23|P23>); SW(c42, r177<C2>, r174<D23=G23|P23>) |
| c43 NAND | 2 | 1 | r191<R23=G2|G3> | `NAND(r306<nG2>, r3<nG3>)` |
| c44 AND | 2 | 1 | r307<P2> | `AND(r188<V2>, r306<nG2>)` |
| c45 NAND | 3 | 1 | r29<N2=~(C2*P2)> | `NAND(r177<C2>, r307<P2>)` |
| c46 OR | 3 | 1 | r197<O2=C2|P2> | `OR(r177<C2>, r307<P2>)` |
| c47 NOR | 1 | 1 | r257<Q6> | `NOR(r92<B6>, r108<A6>)` |
| c48 AND | 1 | 1 | r275<G6> | `AND(r92<B6>, r108<A6>)` |
| c49 NOR | 1 | 1 | r215<Q7> | `NOR(r94<B7>, r125<A7>)` |
| c50 AND | 1 | 1 | r218<G7> | `AND(r94<B7>, r125<A7>)` |
| c51 NOR | 2 | 1 | r233<P6> | `NOR(r257<Q6>, r275<G6>)` |
| BUS r210 | 5 | 4 | r210<C8> | SW(c52, r223<E67=G6|X7>, r213<D67=G67|P67>); SW(c53, r337<C6>, r213<D67=G67|P67>) |
| c54 OR | 4 | 1 | r213<D67=G67|P67> | `OR(r214<P7*nQ6>, r218<G7>)` |
| c56 OR | 2 | 1 | r276<X7=nP7> | `OR(r215<Q7>, r218<G7>)` |
| BUS r237 | 5 | 6 | r237<S6> | SW(c58, r356<K54>, r233<P6>); SW(c59, r234<R45=P5*nG4*nC4>, r233<P6>); SW(c60, r337<C6>, r240<X6=nP6>) |
| c61 OR | 2 | 1 | r240<X6=nP6> | `OR(r257<Q6>, r275<G6>)` |
| BUS r245 | 5 | 6 | r245<S7> | SW(c62, r356<K54>, r281<L7=G6 xor P7>); SW(c63, r337<C6>, r270<F7=XNOR(Q6,P7)>); SW(c64, r234<R45=P5*nG4*nC4>, r281<L7=G6 xor P7>) |
| c65 NOR | 3 | 1 | r214<P7*nQ6> | `NOR(r276<X7=nP7>, r257<Q6>)` |
| c66 NOR | 4 | 1 | r270<F7=XNOR(Q6,P7)> | `NOR(r267<X7*Q6>, r214<P7*nQ6>)` |
| c67 AND | 3 | 1 | r267<X7*Q6> | `AND(r276<X7=nP7>, r257<Q6>)` |
| c68 OR | 3 | 1 | r223<E67=G6|X7> | `OR(r275<G6>, r276<X7=nP7>)` |
| c69 NAND | 3 | 1 | r282<N67=~(G6*X7)> | `NAND(r275<G6>, r276<X7=nP7>)` |
| c70 NAND | 4 | 1 | r281<L7=G6 xor P7> | `NAND(r282<N67=~(G6*X7)>, r223<E67=G6|X7>)` |
| c71 AND | 4 | 1 | r140<S2> | `AND(r197<O2=C2|P2>, r29<N2=~(C2*P2)>)` |
| c72 NAND | 4 | 1 | r11<C3> | `NAND(r29<N2=~(C2*P2)>, r306<nG2>)` |
| c73 NAND | 4 | 1 | r325<n(C4*P4)> | `NAND(r83<C4>, r82<P4>)` |
| c74 NAND | 3 | 1 | r352<E45=G4|nP5> | `NAND(r85<nG4>, r319<P5>)` |
| c75 NAND | 4 | 1 | r334<L5=G4 xor P5> | `NAND(r203<F45=nG4|P5>, r352<E45=G4|nP5>)` |
| c76 OR | 3 | 1 | r203<F45=nG4|P5> | `OR(r85<nG4>, r319<P5>)` |
| BUS r332 | 5 | 4 | r332<S5> | SW(c77, r325<n(C4*P4)>, r334<L5=G4 xor P5>); SW(c78, r79<C4*P4>, r352<E45=G4|nP5>) |
| BUS r337 | 4 | 4 | r337<C6> | SW(c79, r352<E45=G4|nP5>, r347<D45=G54|P54>); SW(c80, r83<C4>, r347<D45=G54|P54>) |
| c81 NAND | 2 | 1 | r351<N45=~(V4*V5)> | `NAND(r89<V4>, r163<V5>)` |
| c82 NAND | 3 | 1 | r347<D45=G54|P54> | `NAND(r351<N45=~(V4*V5)>, r335<nG5>)` |
| c83 NOR | 4 | 1 | r234<R45=P5*nG4*nC4> | `NOR(r352<E45=G4|nP5>, r83<C4>)` |
| c84 AND | 3 | 1 | r356<K54> | `AND(r351<N45=~(V4*V5)>, r335<nG5>)` |

## 免费边界与位序

```text
A(U8) -> c33 SPLITTER8 -> A0..A7
B(U8) -> c32 SPLITTER8 -> B0..B7
S0..S7 -> c34 MAKER8 -> Output(U8)
C8 -> c57 MAKER2.in1; MAKER2.in0=Z -> c55 SPLITTER2.out1 -> Carry out
```

## 九输出 arrival

| 输出 | 网络 | arrival | mismatch |
|---|---:|---:|---:|
| S0 | r41 | 4 | 0 |
| S1 | r138 | 5 | 0 |
| S2 | r140 | 4 | 0 |
| S3 | r142 | 5 | 0 |
| S4 | r144 | 5 | 0 |
| S5 | r332 | 5 | 0 |
| S6 | r237 | 5 | 0 |
| S7 | r245 | 5 | 0 |
| C8 | r278 | 5 | 0 |
