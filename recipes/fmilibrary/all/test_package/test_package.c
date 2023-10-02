#include <fmilib.h>

int main() {
  fmi_import_context_t* c = fmi_import_allocate_context(jm_get_default_callbacks());
  int e = (c == NULL) ? 1 : 0;
  fmi_import_free_context(c);
  return e;
}
