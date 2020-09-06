#include <glsl_optimizer.h>

int main() {
    // Simple way to referencing the function to make sure stuff are linked correctly
    glslopt_ctx*(*ptr)(glslopt_target) = glslopt_initialize;
    return 0;
}

