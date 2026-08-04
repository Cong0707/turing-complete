# Byte Adder 80/7: C3/n80 no-BUS55 dual-solver closure

## Conclusion

The exact weighted-cost-5 domain for ranked case `56-80__no_55` is closed as `10/10 UNSAT` across CaDiCaL 1.9.5 and Glucose 4.2.

- source shell: the complete retained-frontier ancestor closure, minus cut `{56,80}` and exactly private `BUS55`;
- exact packed partition: `128` rows derived from all `131072` U8/U8/U1 assignments;
- projected score at the rejected bound: `76/7/532`;
- positive worker regression: current expanded-shell `g5/n3/s2/x0` is SAT and passes full replay;
- both solvers cover the same five weighted compositions, with identical variables/clauses for every pair;
- all ten result hashes, both summary hashes, source/ranking/worker/runner hashes, and empty stderr logs were checked.

## CNF Pairs

| ordinary | components | switches | xors | variables | clauses | CaDiCaL | Glucose |
|---:|---:|---:|---:|---:|---:|:---:|:---:|
| 0 | 2 | 1 | 1 | 4678 | 47690 | UNSAT | UNSAT |
| 1 | 3 | 2 | 0 | 7542 | 73335 | UNSAT | UNSAT |
| 2 | 3 | 0 | 1 | 7542 | 73335 | UNSAT | UNSAT |
| 3 | 4 | 1 | 0 | 11029 | 103100 | UNSAT | UNSAT |
| 5 | 5 | 0 | 0 | 15140 | 137041 | UNSAT | UNSAT |

## Scope

This is a complete closure only for the recorded no-private source shell and weighted-cost-5 primitive domain. It is not a lower bound for any different source shell, cut, primitive contract, or projected gate cost.
