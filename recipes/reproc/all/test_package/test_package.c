#include <reproc/reproc.h>
#include <stdio.h>

int main()
{
  reproc_t *process = reproc_new();
  if (!process) {
    fprintf(stderr, "Failed to create reproc process.\n");
    return 1;
  }
  printf("reproc setup successful. Process object created.\n");
  reproc_destroy(process);
  return 0;
}
