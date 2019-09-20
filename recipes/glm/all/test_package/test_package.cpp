#include <cstdlib>
#include "glm/glm.hpp"

int main (int argc, char * argv[]) {
    glm::vec4 position = glm::vec4(glm::vec3(0.0), 1.0);
    glm::mat4 model = glm::mat4(1.0);
    model[4] = glm::vec4(1.0, 1.0, 0.0, 1.0);
    glm::vec4 transformed = model * position;

    return EXIT_SUCCESS;
}
