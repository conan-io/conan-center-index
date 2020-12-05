#include <glbinding/glbinding.h>

#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>

int main() {
#if defined(__APPLE__) && defined(__MACH__)
    glfwInitHint(GLFW_COCOA_MENUBAR, GLFW_FALSE);
#endif
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
