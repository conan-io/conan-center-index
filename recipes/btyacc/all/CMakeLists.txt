cmake_minimum_required(VERSION 3.1)

project(btyacc C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

# ---- btyacc executable ----

set(src "${PROJECT_SOURCE_DIR}")
set(bin "${PROJECT_BINARY_DIR}")
add_custom_command(
    OUTPUT skeleton.c
    COMMAND "${CMAKE_COMMAND}"
    "-Dinput=${src}/btyaccpa.ske"
    "-Doutput=${bin}/skeleton.c.tmp"
    "-P${src}/cmake/skel2c.cmake"
    COMMAND "${CMAKE_COMMAND}" -E copy_if_different
    "${bin}/skeleton.c.tmp"
    "${bin}/skeleton.c"
    COMMAND "${CMAKE_COMMAND}" -E remove "${bin}/skeleton.c.tmp"
    MAIN_DEPENDENCY btyaccpa.ske
    DEPENDS cmake/skel2c.cmake
    COMMENT "skel2c [btyaccpa.ske -> skeleton.c]"
    VERBATIM
)

add_executable(
    btyacc
    closure.c
    dtor.c
    error.c
    lalr.c
    lr0.c
    main.c
    mkpar.c
    output.c
    mstring.c
    reader.c
    readskel.c
    skeleton.c
    symtab.c
    verbose.c
    warshall.c
    "${bin}/skeleton.c"
)

target_include_directories(btyacc PRIVATE "${src}")

# ---- Install rules ----

include(GNUInstallDirs)
install(TARGETS btyacc RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}")
