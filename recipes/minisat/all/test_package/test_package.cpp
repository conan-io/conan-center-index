// example from https://accu.org/journals/overload/27/150/horenovsky_2640/
#include <minisat/core/Solver.h>
#include <iostream>

using namespace Minisat;

int main() {
  Solver solver;
  // Create variables
  Var A = solver.newVar();
  Var B = solver.newVar();
  Var C = solver.newVar();
  // Create the clauses
  solver.addClause( mkLit(A),  mkLit(B),  mkLit(C));
  solver.addClause(~mkLit(A),  mkLit(B),  mkLit(C));
  solver.addClause( mkLit(A), ~mkLit(B),  mkLit(C));
  solver.addClause( mkLit(A),  mkLit(B), ~mkLit(C));
  // Check for solution and retrieve model if found
  bool sat = solver.solve();
  if (sat) {
    std::clog << "SAT\n"
              << "Model found:\n";
    std::clog << "A := "
              << (solver.modelValue(A) == l_True)
              << '\n';
    std::clog << "B := "
              << (solver.modelValue(B) == l_True)
              << '\n';
    std::clog << "C := "
              << (solver.modelValue(C) == l_True)
              << '\n';
    return 0;
  } else {
    std::clog << "UNSAT\n";
    return 1;
  }
}
