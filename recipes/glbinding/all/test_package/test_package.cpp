#include <glbinding/glbinding.h>

#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>

#include <stdio.h>

int main() {
#if defined(__APPLE__) && defined(__MACH__)
    glfwInitHint(GLFW_COCOA_MENUBAR, GLFW_FALSE);
#endif
    if (!glfwInit()) {
        printf("glfwInit() failed. Ignoring because this is not testing glfw.\n");
        return 0;
    }

    glfwDefaultWindowHints();
    glfwWindowHint(GLFW_VISIBLE, GLFW_FALSE);

    GLFWwindow *window = glfwCreateWindow(320, 240, "", nullptr, nullptr);
    if (!window) {
        glfwTerminate();
        printf("glfwCreateWindow failed. Ignoring because this is not testing glfw.\n");
        return 0;
    }

    glfwMakeContextCurrent(window);

    glbinding::initialize(glfwGetProcAddress, false);

    glfwDestroyWindow(window);
    glfwTerminate();

    return 0;
}
