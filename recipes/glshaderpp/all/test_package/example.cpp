#include <iostream>
#include <GL/glew.h>
#include <GLShaderPP/ShaderProgram.h>
#include <GLShaderPP/Shader.h>
#include <GLShaderPP/ShaderException.h>

int main() {
    GLShaderPP::CShaderException e("If you read this, GLShaderPP is happy :)", GLShaderPP::CShaderException::ExceptionType::LinkError);
    std::cout << e.what() << '\n';
    return EXIT_SUCCESS;
}
