#include <iostream>
#include <GL/gl.h>

int main()
{    
    
    glBegin(GL_TRIANGLES);
    if(const auto err = glGetError())
        std::cout << "error: " << err << std::endl;
        glVertex2f(20.0f, 10.0f);
    if(const auto err = glGetError())
        std::cout << "error: " << err << std::endl;
        glVertex2f(10.0f, 30.0f);
    if(const auto err = glGetError())
        std::cout << "error: " << err << std::endl;
        glVertex2f(20.0f, 50.0f);
    if(const auto err = glGetError())
        std::cout << "error: " << err << std::endl;
    glEnd();
    if(const auto err = glGetError())
        std::cout << "error: " << err << std::endl;
        
    return 0;
}
