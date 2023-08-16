#include <svm/svm.h>

#include <stdio.h>
#include <stdlib.h>

struct svm_parameter param;

int main(int argc, char **argv)
{
    param.svm_type = C_SVC;
    param.kernel_type = PRECOMPUTED;

    //Allocate some dummy data
    param.weight = (double*)malloc(10 * sizeof(double));
    svm_destroy_param(&param);

    printf("libsvm version %d test_package OK \n", LIBSVM_VERSION);
    return 0;
}
