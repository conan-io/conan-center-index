cmake_minimum_required(VERSION 3.1)

project(hunspell VERSION "${CONAN_hunspell_VERSION}" LANGUAGES CXX)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS KEEP_RPATHS)
set(src src/hunspell)

# ---- Configure hunvisapi.h ----

include(CheckCXXCompilerFlag)
check_cxx_compiler_flag(-fvisibility=hidden HAVE_VISIBILITY)
configure_file("${src}/hunvisapi.h.in" hunvisapi.h @ONLY)

# ---- Library target ----

add_library(
    hunspell
    "${src}/affentry.cxx"
    "${src}/affixmgr.cxx"
    "${src}/csutil.cxx"
    "${src}/filemgr.cxx"
    "${src}/hashmgr.cxx"
    "${src}/hunspell.cxx"
    "${src}/hunzip.cxx"
    "${src}/phonet.cxx"
    "${src}/replist.cxx"
    "${src}/suggestmgr.cxx"
)

if(MSVC)
  target_compile_options(hunspell PRIVATE /wd4267 /wd4996)
endif()

if(NOT BUILD_SHARED_LIBS)
  target_compile_definitions(hunspell PRIVATE HUNSPELL_STATIC)
endif()
target_compile_definitions(hunspell PRIVATE BUILDING_LIBHUNSPELL)

target_include_directories(hunspell PRIVATE "${src}" "${PROJECT_BINARY_DIR}")

set_target_properties(
    hunspell PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN YES
    VERSION "${PROJECT_VERSION}"
    SOVERSION "${PROJECT_VERSION_MAJOR}"
)

# ---- Install ----

include(GNUInstallDirs)

install(
    TARGETS hunspell
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
)

install(
    FILES
    "${src}/hunspell.hxx"
    "${src}/hunspell.h"
    "${src}/w_char.hxx"
    "${src}/atypes.hxx"
    "${PROJECT_BINARY_DIR}/hunvisapi.h"
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/hunspell"
)
