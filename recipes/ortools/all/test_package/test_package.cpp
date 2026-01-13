#include <cstdlib>
#include <memory>

// because there are compile errors without this
#define OR_PROTO_DLL

#include "absl/base/log_severity.h"
#include "absl/log/globals.h"
#include "ortools/base/init_google.h"
#include "ortools/glop/lp_solver.h"
#include "ortools/linear_solver/linear_solver.h"


int main(int argc, char* argv[]) {
    absl::SetStderrThreshold(absl::LogSeverityAtLeast::kInfo);
    InitGoogle(argv[0], &argc, &argv, true);
    std::unique_ptr<operations_research::MPSolver> solver(operations_research::MPSolver::CreateSolver("GLOP"));
    if (!solver) {
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
