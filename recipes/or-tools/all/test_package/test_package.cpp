#include <iostream>
#include "ortools/base/version.h"
#include "ortools/glop/lp_solver.h"


int main() {
    operations_research::glop::LPSolver solver;
    std::cout << "Google OR-Tools version: "
              << operations_research::OrToolsMajorVersion() << "."
              << operations_research::OrToolsMinorVersion() << "."
              << operations_research::OrToolsPatchVersion() << std::endl;
    std::cout << "GLOP version: " << operations_research::glop::LPSolver::GlopVersion() << std::endl;
    return EXIT_SUCCESS;
}