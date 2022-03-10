cmake_minimum_required(VERSION 3.12)

project(enchant VERSION "${CONAN_enchant_VERSION}" LANGUAGES C)

set(root "${PROJECT_SOURCE_DIR}/source_subfolder")
set(src "${root}/src")
set(bin "${PROJECT_BINARY_DIR}")

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS KEEP_RPATHS)

# ---- Config headers ----

include(compile-checks.cmake)

set_directory_properties(PROPERTIES CMAKE_CONFIGURE_DEPENDS config.h.in)
file(READ "${root}/config.h.in" content)
string(REGEX REPLACE "#[ \t]*undef ([^\r\n ]+)" "#cmakedefine \\1 @\\1@" content "${content}")
string(CONFIGURE "${content}" content @ONLY)
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

# ---- Setup ----

find_package(glib REQUIRED CONFIG)

include(GenerateExportHeader)

function(target_set_visibility target)
  set_target_properties(
      "${target}" PROPERTIES
      C_VISIBILITY_PRESET hidden
      CXX_VISIBILITY_PRESET hidden
      VISIBILITY_INLINES_HIDDEN YES
  )
endfunction()

set(providers "")
macro(add_provider target)
  add_library("${target}" MODULE ${ARGN})
  if(NOT providers)
    generate_export_header("${target}" BASE_NAME enchant_module)
  endif()
  list(APPEND providers "${target}")
  target_set_visibility("${target}")
  set_property(TARGET "${target}" PROPERTY DEFINE_SYMBOL enchant_module_EXPORTS)
  target_link_libraries("${target}" PRIVATE enchant)
endmacro()

if(MSVC)
  add_compile_options(/wd4996)
endif()

# ---- Library ----

add_library(
    enchant SHARED
    "${root}/lib/relocatable.c"
    "${src}/lib.c"
    "${src}/libenchant.rc"
    "${src}/pwl.c"
)

target_compile_definitions(enchant PRIVATE NO_XMALLOC=1 PIC=1 ENABLE_COSTLY_RELOCATABLE=1)
target_include_directories(enchant PUBLIC "${bin}" "${src}" "${root}/lib")
target_link_libraries(enchant PRIVATE glib::glib-2.0 glib::gmodule-2.0)

generate_export_header(enchant)
target_set_visibility(enchant)
set_target_properties(
    enchant PROPERTIES
    VERSION "${PROJECT_VERSION}"
    SOVERSION "${PROJECT_VERSION_MAJOR}"
)

# ---- Providers ----

# There is only this provider in CCI for now
enable_language(CXX)
add_provider(enchant_hunspell "${root}/providers/enchant_hunspell.cpp")

find_package(hunspell REQUIRED CONFIG)
target_link_libraries(enchant_hunspell PRIVATE hunspell::hunspell glib::glib-2.0)

# ---- Install rules ----

include(GNUInstallDirs)

install(
    TARGETS enchant
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
)

if(NOT providers STREQUAL "")
  install(
      TARGETS ${providers}
      LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}/enchant-${PROJECT_VERSION_MAJOR}"
  )
endif()

install(
    FILES
    "${src}/enchant++.h"
    "${src}/enchant.h"
    "${bin}/enchant_export.h"
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)
