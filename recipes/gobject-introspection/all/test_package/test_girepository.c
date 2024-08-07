#include "girepository.h"

int main() {
  GIRepository *repository;
  GError *error = NULL;
  GIBaseInfo *base_info;
  GIArgument in_args[1];
  GIArgument retval;

  repository = g_irepository_get_default();
  g_irepository_require(repository, "GLib", "2.0", 0, &error);
  if (error) {
    g_error("ERROR: %s\n", error->message);
    return 1;
  }

  base_info = g_irepository_find_by_name(repository, "GLib", "log_set_debug_enabled");
  if (!base_info) {
    g_error("ERROR: %s\n", "Could not find GLib.log_set_debug_enabled");
    return 1;
  }

  // Call GLib.log_set_debug_enabled(true)
  in_args[0].v_boolean = 1;
  if (!g_function_info_invoke((GIFunctionInfo *) base_info,
                              (const GIArgument *) &in_args, 1, // input args
                              NULL, 0, // output args
                              &retval, &error)) {
    g_error("ERROR: %s\n", error->message);
    return 1;
  }

  g_base_info_unref(base_info);
}
