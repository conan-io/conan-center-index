#include <cstdlib>
#include <pj_base/number_parse.hpp>

#ifdef PJ_TEST_WITH_HOST
#include <pj_plugins/host/plugin_catalog.hpp>
#endif

// parseNumber<double> dispatches to PJ::detail::parseDoubleImpl, which is
// compiled out-of-line into libpj_base.a. Calling it therefore verifies that
// the static archive is actually linked through the plugin_sdk component, not
// merely that the headers are on the include path.
int main() {
  const auto value = PJ::parseNumber<double>("1.5");
  if (!value || *value != 1.5) {
    return EXIT_FAILURE;
  }

#ifdef PJ_TEST_WITH_HOST
  // Scanning a (non-existent) directory forces the plugin_host archives — and the
  // dlopen-backed loader, hence libdl — onto the link line, validating the
  // plugin_host component's lib list and system_libs wiring.
  const auto scan = PJ::scanPluginDsos("/nonexistent/plotjuggler_sdk_test_package");
  (void)scan;
#endif

  return EXIT_SUCCESS;
}
