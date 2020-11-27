#include <GLFW/glfw3.h>
#include <glbinding/glbinding.h>

int main() {
    if (!glfwInit()) return 1;

    glfwDefaultWindowHints();
    glfwWindowHint(GLFW_VISIBLE, GLFW_FALSE);

    GLFWwindow *window = glfwCreateWindow(320, 240, "", nullptr, nullptr);
    if (!window) {
        glfwTerminate();
        return -1;
    }

    glfwMakeContextCurrent(window);

    glbinding::initialize(glfwGetProcAddress, false);

    glfwDestroyWindow(window);
    glfwTerminate();

    return 0;
}
