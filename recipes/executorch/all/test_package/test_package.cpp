#include <cstdlib>
#include <executorch/extension/tensor/tensor.h>


int main(void) {
    /*
     * TODO: Remove this comment before pushing the testing code;
     *
     * Create a minimal usage for the target project here;
     * Avoid upstream full examples, or code bigger than 15 lines;
     * Avoid networking connections;
     * Avoid background apps or servers;
     * Avoid GUI apps;
     * Avoid extra files like images, sounds and other binaries;
     * The propose is testing the generated artifacts ONLY;
    */

    float input[1 * 3 * 224 * 224];
    auto tensor = from_blob(input, {1, 3, 224, 224});

    return EXIT_SUCCESS;
}
