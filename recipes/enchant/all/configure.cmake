# ---- Autotools style compile checks ----

set(DLADDR_LIBRARIES "")
set(ENABLE_RELOCATABLE 1)

if(NOT WIN32)
  include(CheckFunctionExists)
  include(CheckLibraryExists)

  check_library_exists(dl dladdr "" HAVE_DLADDR_IN_DL)
  if(HAVE_DLADDR_IN_DL)
    set(HAVE_DLADDR 1)
    set(DLADDR_LIBRARIES dl)
  else()
    check_function_exists(dladdr HAVE_DLADDR)
  endif()

  check_function_exists(flock HAVE_FLOCK)
endif()

# ---- Write config headers ----

set_directory_properties(PROPERTIES CMAKE_CONFIGURE_DEPENDS config.h.in)
file(READ "${root}/config.h.in" content)
string(REGEX REPLACE "#[ \t]*undef ([^\r\n ]+)" "#cmakedefine \\1 @\\1@" content "${content}")
string(CONFIGURE "${content}
#cmakedefine HAVE_DLADDR @HAVE_DLADDR@
" content @ONLY)
file(
    WRITE "${bin}/config.h.tmp" "${content}"
    "#define ENCHANT_MAJOR_VERSION \"${PROJECT_VERSION_MAJOR}\"\n"
    "#define ENCHANT_VERSION_STRING \"${PROJECT_VERSION}\"\n"
)

configure_file(configmake.h configmake.h COPYONLY)
execute_process(
    COMMAND "${CMAKE_COMMAND}" -E copy_if_different "${bin}/config.h.tmp" "${bin}/config.h"
    RESULT_VARIABLE result
)
if(NOT result STREQUAL "0")
  message(FATAL_ERROR "Copy failed: ${result}")
endif()
