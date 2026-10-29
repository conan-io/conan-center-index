#include <cstdlib>
#include <iostream>
#include "glm/glm.hpp"

int main (void) {
    glm::vec4 position = glm::vec4(glm::vec3(0.0), 1.0);
    glm::mat4 model = glm::mat4(1.0);
    model[3] = glm::vec4(1.0, 1.0, 0.0, 1.0);
    glm::vec4 transformed = model * position;
    std::cout << "GLM Test Package: (" << transformed.x << ", " << transformed.y << ", " << transformed.z << ", " << transformed.w << ")" << std::endl;
    return EXIT_SUCCESS;
}
