#include <cstdlib>
#include <cstdarg>
#include <iostream>

#include "GL/freeglut.h"


void error_handler(const char *fmt, va_list ap) {
    std::cout << fmt << std::endl;
}

void renderScene(void) {

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

	glBegin(GL_TRIANGLES);
		glVertex3f(-0.5,-0.5,0.0);
		glVertex3f(0.5,0.0,0.0);
		glVertex3f(0.0,0.5,0.0);
	glEnd();

        glutSwapBuffers();
}

int main(int argc, char **argv) {
    glutInitErrorFunc(error_handler);
    std::cout << std::endl << "FreeGLUT version:" << std::endl;
    std::cout << glutGet(GLUT_VERSION);
    std::cout << std::endl;

    /*
    glutInit(&argc,argv);
    glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA);
	glutInitWindowPosition(100,100);
	glutInitWindowSize(320,320);
	glutCreateWindow("Lighthouse3D - GLUT Tutorial");

	// register callbacks
	glutDisplayFunc(renderScene);

	// enter GLUT event processing cycle
	glutMainLoop();*/
    return EXIT_SUCCESS;
}
