#include "gtk/gtk.h"
#include <stdio.h>

int main (int argc, char **argv)
{
  printf("gtk version %d.%d.%d\n", gtk_get_major_version(), gtk_get_minor_version(), gtk_get_micro_version());
  printf("binary age: %d\n", gtk_get_binary_age());
  printf("interface age: %d\n", gtk_get_interface_age());
  return 0;
}
