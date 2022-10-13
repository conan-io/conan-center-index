get_target_property(ABSL_INCLUDES absl::config INTERFACE_INCLUDE_DIRECTORIES)
set(CMAKE_REQUIRED_INCLUDES ${ABSL_INCLUDES})

check_cxx_source_compiles("
#include \"absl/base/config.h\"
#if defined(ABSL_HAVE_STD_STRING_VIEW) && ABSL_HAVE_STD_STRING_VIEW == 1
int main() {}
#else
#error \"no std::string_view\"
#endif
"
USE_STD_STRING_VIEW)

check_cxx_source_compiles("
#include \"absl/base/config.h\"
#if defined(ABSL_HAVE_STD_ANY) && ABSL_HAVE_STD_ANY == 1
int main() {}
#else
#error \"no std::any\"
#endif
"
USE_STD_ANY)

check_cxx_source_compiles("
#include \"absl/base/config.h\"
#if defined(ABSL_HAVE_STD_OPTIONAL) && ABSL_HAVE_STD_OPTIONAL == 1
int main() {}
#else
#error \"no std::optional\"
#endif
"
USE_STD_OPTIONAL)

check_cxx_source_compiles("
#include \"absl/base/config.h\"
#if defined(ABSL_HAVE_STD_VARIANT) && ABSL_HAVE_STD_VARIANT == 1
int main() {}
#else
#error \"no std::variant\"
#endif
"
USE_STD_VARIANT)

configure_file(${CMAKE_CURRENT_LIST_DIR}/abi.h.in ${PROJECT_BINARY_DIR}/abi.h)
