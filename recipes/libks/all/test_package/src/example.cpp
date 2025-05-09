#include <libks/ks.h>

int main() {
  ks_json_t *json = ks_json_create_object();
  const char *value;

  ks_init();

  value = ks_json_get_object_string(json, "key", "value");
  int result = strcmp(value, "value");

  ks_shutdown();
  return result;
}
