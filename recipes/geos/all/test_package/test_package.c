#include <geos_c.h>

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>

void notice(const char *fmt, ...) {
  va_list ap;

  fprintf(stdout, "NOTICE: ");

  va_start(ap, fmt);
  vfprintf(stdout, fmt, ap);
  va_end(ap);
  fprintf(stdout, "\n");
}

void log_and_exit(const char *fmt, ...) {
  va_list ap;

  fprintf(stdout, "ERROR: ");

  va_start(ap, fmt);
  vfprintf(stdout, fmt, ap);
  va_end(ap);
  fprintf(stdout, "\n");
  exit(1);
}

int main() {
  initGEOS(notice, log_and_exit);
  printf("GEOS version %s\n", GEOSversion());

  finishGEOS();

  return EXIT_SUCCESS;
}
