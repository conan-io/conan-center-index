#include <glbinding/glbinding.h>

#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>

int main() {
    GLFWmonitor *monitor = glfwGetPrimaryMonitor();
    GLFWwindow *window = glfwCreateWindow(640, 480, "Window name", monitor, NULL);

    glbinding::initialize(glfwGetProcAddress, false);

    glfwDestroyWindow(window);
    glfwTerminate();

    return 0;
}
