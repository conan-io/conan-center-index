cmake_minimum_required(VERSION 3.1)

project(qdbm_wrapper VERSION "${CONAN_qdbm_VERSION}" LANGUAGES C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS KEEP_RPATHS)

set(QDBM_SRC_DIR ${PROJECT_SOURCE_DIR}/source_subfolder)

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

find_package_if(MYICONV Iconv)
find_package_if(MYZLIB ZLIB)
find_package_if(MYPTHREAD Threads)

# ---- Library ----

add_library(
    qdbm
    ${QDBM_SRC_DIR}/depot.c
    ${QDBM_SRC_DIR}/curia.c
    ${QDBM_SRC_DIR}/relic.c
    ${QDBM_SRC_DIR}/hovel.c
    ${QDBM_SRC_DIR}/cabin.c
    ${QDBM_SRC_DIR}/villa.c
    ${QDBM_SRC_DIR}/vista.c
    ${QDBM_SRC_DIR}/odeum.c
    ${QDBM_SRC_DIR}/myconf.c
)

if(WIN32)
  target_sources(qdbm PRIVATE ${QDBM_SRC_DIR}/qdbm.def)
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

target_include_directories(qdbm PRIVATE "${QDBM_SRC_DIR}")

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
    ${QDBM_SRC_DIR}/cabin.h
    ${QDBM_SRC_DIR}/curia.h
    ${QDBM_SRC_DIR}/depot.h
    ${QDBM_SRC_DIR}/odeum.h
    ${QDBM_SRC_DIR}/relic.h
    ${QDBM_SRC_DIR}/villa.h
    ${QDBM_SRC_DIR}/vista.h
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/qdbm"
)
