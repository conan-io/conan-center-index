#include <glad/gl.h>
#include <GLFW/glfw3.h>

#include <stdio.h>

int main() {
    GLFWwindow* window;

    #ifdef __APPLE__
    if (!glfwInit()) {
        return -1;
    }
    #endif

    window = glfwCreateWindow(1, 1, "Hello World", NULL, NULL);

    int version = gladLoaderLoadGL();
    printf("GL %d.%d\n", GLAD_VERSION_MAJOR(version), GLAD_VERSION_MINOR(version));
    gladLoaderUnloadGL();

    glfwTerminate();

    return 0;
}
