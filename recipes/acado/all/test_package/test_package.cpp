#include <acado_auxiliary_functions.h>
#include <acado_common.h>
#include <cstdlib>

ACADOvariables acadoVariables;
ACADOworkspace acadoWorkspace;

int main()
{
    acado_initializeSolver();

    acado_preparationStep();

    for (std::size_t iter{0}; iter < 10U; ++iter)
    {
        // Perform the feedback step
        acado_feedbackStep();

        // Prepare for the next step
        acado_preparationStep();
    }

    return EXIT_SUCCESS;
}
