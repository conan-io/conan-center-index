#include <cstdlib>
#include <executorch/extension/tensor/tensor.h>


int main(void) {

    float input[1 * 3 * 224 * 224];
    auto tensor = executorch::extension::from_blob(input, {1, 3, 224, 224});

    return EXIT_SUCCESS;
}
