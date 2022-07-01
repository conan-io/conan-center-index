cmake_minimum_required(VERSION 3.8)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

# Note: This must appear before adding the Abseil source subdirectory because
# Abseil's minimum CMake version is 3.5 so it may cause the definition of
# check_cxx_source_compiles() to have CMP0067 unset
include(CheckCXXSourceCompiles)

if(MSVC)
    add_definitions("-D_HAS_DEPRECATED_RESULT_OF")
endif()

if(NOT CMAKE_SYSTEM_PROCESSOR)
    set(CMAKE_SYSTEM_PROCESSOR ${CONAN_ABSEIL_SYSTEM_PROCESSOR})
endif()

add_subdirectory(source_subfolder)

get_target_property(ABSL_INCLUDES absl::config INTERFACE_INCLUDE_DIRECTORIES)
set(CMAKE_REQUIRED_INCLUDES ${ABSL_INCLUDES})

check_cxx_source_compiles("
#include\"absl/base/config.h\"
#if defined(ABSL_HAVE_STD_STRING_VIEW) && ABSL_HAVE_STD_STRING_VIEW == 1
int main() {}
#else
#error \"no std::string_view\"
#endif
"
USE_STD_STRING_VIEW)

check_cxx_source_compiles("
#include\"absl/base/config.h\"
#if defined(ABSL_HAVE_STD_ANY) && ABSL_HAVE_STD_ANY == 1
int main() {}
#else
#error \"no std::any\"
#endif
"
USE_STD_ANY)

check_cxx_source_compiles("
#include\"absl/base/config.h\"
#if defined(ABSL_HAVE_STD_OPTIONAL) && ABSL_HAVE_STD_OPTIONAL == 1
int main() {}
#else
#error \"no std::optional\"
#endif
"
USE_STD_OPTIONAL)

check_cxx_source_compiles("
#include\"absl/base/config.h\"
#if defined(ABSL_HAVE_STD_VARIANT) && ABSL_HAVE_STD_VARIANT == 1
int main() {}
#else
#error \"no std::variant\"
#endif
"
USE_STD_VARIANT)

configure_file(${CMAKE_CURRENT_SOURCE_DIR}/abi.h.in ${CMAKE_CURRENT_SOURCE_DIR}/abi.h)
