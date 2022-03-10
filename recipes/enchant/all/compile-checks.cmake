# ---- Autotools style compile checks ----

set(ENABLE_RELOCATABLE 1)

# Shortcircuit logic for Windows
if(WIN32)
  return()
endif()

include(CheckFunctionExists)
include(CheckTypeSize)

macro(to_define name)
  string(MAKE_C_IDENTIFIER "${name}" to_define_result)
  string(TOUPPER "${to_define_result}" to_define_result)
endmacro()

macro(check_function function)
  to_define("${function}")
  check_function_exists("${function}" "HAVE_${to_define_result}")
endmacro()

check_function(flock)

check_type_size(ssize_t SSIZE_T_TYPE)
if(HAVE_SSIZE_T_TYPE)
  return()
endif()

check_type_size(size_t SIZE_T_TYPE)

# Find the first built-in signed integer type that's as big as size_t
foreach(type signed\ char short int long long\ long)
  to_define("${type}")
  check_type_size("${type}" "${to_define_result}_TYPE" BUILTIN_TYPES_ONLY)
  if("${HAVE_${to_define_result}_TYPE}" AND SIZE_T_TYPE EQUAL "${${to_define_result}_TYPE}")
    set(ssize_t "${type}")
    break()
  endif()
endforeach()
