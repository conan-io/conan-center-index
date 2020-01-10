#include "glad/glad.h"

#include <stdio.h>

int main() {
  if(!gladLoadGL()) {
    printf("Failed to initialize OpenGL context, expected since no context has been initialized\n");
  } else {
    printf("OpenGL %d.%d\n", GLVersion.major, GLVersion.minor);
  }

  return 0;
}
