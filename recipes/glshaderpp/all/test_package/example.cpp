#include <iostream>
#include <string>
#include <GL/glew.h>
#include <GLShaderPP/ShaderProgram.h>

int main() {

    std::string strVertex = R"SHADER(
#version 330 core
  
layout(location = 0) in vec2 position;
layout(location = 1) in vec3 inputcolor;

out vec3 color;

void main()
{
    gl_Position = vec4(position, 0.0f, 1.0f);
	color = inputcolor;
}
)SHADER";
    std::string strFragment = R"SHADER(
#version 330 core

in vec3 color; 
out vec4 fragColor;

void main()
{
	fragColor = vec4(color, 1.0f);
}
)SHADER";
    try{

        GLShaderPP::CShaderProgram program{ 
            GLShaderPP::CShader{ GL_VERTEX_SHADER, strVertex },
            GLShaderPP::CShader{ GL_FRAGMENT_SHADER, strFragment }
        };
    }
    catch(const GLShaderPP::CShaderException&)
    {
        //It must fail since we tried to create a shader without any OpenGL context
        std::cout << "It works!\n";
        return EXIT_SUCCESS;
    }
    std::cout << "It doesn't work!\n";
    return EXIT_FAILURE;
}
