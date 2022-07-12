#include <s2let/s2let.h>

int main(int argc, char *argv[])
{
  complex double *buffer;
  s2let_allocate_lm(&buffer, 5);
  free(buffer);
  return 0;
}
