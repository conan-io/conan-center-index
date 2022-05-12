#include <cglm/cglm.h>
#include <stdio.h>

int main() {
    mat4 matrix = {
        { 0.20138f, 0.82993f, 0.28319, 0.29518f },
        { 0.99043f, 0.88820f, 0.62279, 0.33396f },
        { 0.48144f, 0.36351f, 0.70723, 0.65915f },
        { 0.64711f, 0.69593f, 0.80561, 0.62619f },
    };
    vec4 vector = { 0.023048f, 0.243715f, 0.125258f, 0.699470 };
    vec4 result;

    float det = glm_mat4_det(matrix);
    glm_mat4_mulv(matrix, vector, result);

    printf("determinant is %f\n", det);
    printf("result of multiplication is: { %f, %f, %f, %f }\n", result[0], result[1], result[2], result[3]);

    return 0;
}
