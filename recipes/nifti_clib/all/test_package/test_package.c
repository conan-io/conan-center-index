#include "nifticdf.h"

// taken from nifti_clib/real_easy/minimal_example_of_downstream_usage
int main(void) {
    double input= 7.0;
    const double output = alnrel(&input);

    return (output > 0.0) ? EXIT_SUCCESS: EXIT_FAILURE ;
}
