cmake_minimum_required(VERSION 3.1)

project(qdbm_wrapper VERSION "${CONAN_qdbm_VERSION}" LANGUAGES C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS KEEP_RPATHS)

# ---- Dependencies ----

option(THREADS_PREFER_PTHREAD_FLAG "" ON)

macro(find_package_if condition name)
  option("${condition}" "Enable ${condition}" OFF)
  if(${condition})
    find_package("${name}" REQUIRED ${ARGN})
    link_libraries("${name}::${name}")
    add_definitions("-D${condition}")
  endif()
endmacro()

find_package_if(MYICONV Iconv CONFIG)
find_package_if(MYZLIB ZLIB CONFIG)
find_package_if(MYPTHREAD Threads)

# ---- Library ----

add_library(
    qdbm
    depot.c
    curia.c
    relic.c
    hovel.c
    cabin.c
    villa.c
    vista.c
    odeum.c
    myconf.c
)

if(WIN32)
  target_sources(qdbm PRIVATE qdbm.def)
endif()

# Too noisy
if(MSVC)
  target_compile_definitions(
      qdbm PRIVATE
      _CRT_SECURE_NO_WARNINGS
      _CRT_SECURE_NO_DEPRECATE
  )
  target_compile_options(qdbm PRIVATE /wd4267 /wd4996 /wd4244)
endif()

target_include_directories(qdbm PRIVATE "${PROJECT_SOURCE_DIR}")

set_target_properties(
    qdbm PROPERTIES
    VERSION "${PROJECT_VERSION}"
    SOVERSION "${PROJECT_VERSION_MAJOR}"
)

# ---- Install ----

include(GNUInstallDirs)

install(
    TARGETS qdbm
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
)

install(
    FILES
    cabin.h
    curia.h
    depot.h
    odeum.h
    relic.h
    villa.h
    vista.h
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/qdbm"
)
