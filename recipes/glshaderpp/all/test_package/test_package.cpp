#include <GL/glew.h>
#include <GLShaderPP/Shader.h>
#include <GLShaderPP/ShaderException.h>
#include <GLShaderPP/ShaderProgram.h>

#include <iostream>

int main() {
    GLShaderPP::CShaderException e("If you read this, GLShaderPP is happy :)",
                                   GLShaderPP::CShaderException::ExceptionType::LinkError);
    std::cout << e.what() << '\n';
    return EXIT_SUCCESS;
}
