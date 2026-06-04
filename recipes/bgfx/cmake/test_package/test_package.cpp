#include <bx/math.h>
#include <stdio.h>
#include <stdlib.h>


int main() {
	float tLerp = bx::lerp(0.0f, 10.0f, 0.5f);
	printf("bx::lerp(0.0f, 10.0f, 0.5f) = %f\n", tLerp);
    return EXIT_SUCCESS;
}
