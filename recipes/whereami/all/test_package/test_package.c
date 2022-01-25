#include <whereami.h>
#include <stdio.h>
#include <stdlib.h>

int main() {

  int length = wai_getExecutablePath(NULL, 0, NULL);

  if (length > 0) {
    char* path = (char*)malloc(length + 1);
    if (!path) {
      abort();
    }
    int dirname_length = 0;
    wai_getExecutablePath(path, length, &dirname_length);
    path[length] = '\0';

    printf("Executable path: %s\n", path);
    path[dirname_length] = '\0';
    printf("  dirname: %s\n", path);
    printf("  basename: %s\n", path + dirname_length + 1);

    free(path);
  }

  printf("\n");

  length = wai_getModulePath(NULL, 0, NULL);
  if (length > 0) {
    char* path = (char*)malloc(length + 1);
    if (!path) {
      abort();
    }
    int dirname_length = 0;
    wai_getModulePath(path, length, &dirname_length);
    path[length] = '\0';

    printf("module path: %s\n", path);
    path[dirname_length] = '\0';
    printf("  dirname: %s\n", path);
    printf("  basename: %s\n", path + dirname_length + 1);
    free(path);
  }

  return 0;
}
