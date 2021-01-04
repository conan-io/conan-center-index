#include <GLFW/glfw3.h>

int main (void)
{
    GLFWwindow* window;
    GLFWmonitor* monitor = NULL;

    monitor = glfwGetPrimaryMonitor();

    window = glfwCreateWindow(640, 480, "Window name", monitor, NULL);

    glfwDestroyWindow(window);
    glfwTerminate();

    return 0;
}
