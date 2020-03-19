#include <iostream>
#include <GL/glu.h>

int main()
{
	if(const GLubyte* str = gluGetString(GLU_VERSION))
	{
		std::cout << "Glu version; " << str << std::endl;
	}
    return 0;
}
