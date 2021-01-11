#include "atspi/atspi.h"
#include "assert.h"

int main()
{
  atspi_init ();
  assert(atspi_get_desktop_count() > 0);
  return atspi_exit();
}
