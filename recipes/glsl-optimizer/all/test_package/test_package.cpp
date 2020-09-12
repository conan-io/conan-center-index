#include <glsl_optimizer.h>

int main() {
	glslopt_ctx* ctx = glslopt_initialize(kGlslTargetOpenGL);
	glslopt_cleanup(ctx);
    return 0;
}

