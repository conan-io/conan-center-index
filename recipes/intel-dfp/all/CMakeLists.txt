cmake_minimum_required(VERSION 3.12)

project(intel-dfp LANGUAGES C)
enable_testing()

option(CALL_BY_REF "Pass function arguments and return values by reference")
option(GLOBAL_RND "Store the value of the rounding mode in a global variable")
option(GLOBAL_EXC "Store the value of the exception status flags in a global variable")

file(GLOB_RECURSE MAIN_SOURCES LIBRARY/src/*.c)
set(FLOAT128_SOURCES
    LIBRARY/float128/dpml_exception.c
    LIBRARY/float128/dpml_four_over_pi.c
    LIBRARY/float128/dpml_ux_bessel.c
    LIBRARY/float128/dpml_ux_bid.c
    LIBRARY/float128/dpml_ux_cbrt.c
    LIBRARY/float128/dpml_ux_erf.c
    LIBRARY/float128/dpml_ux_exp.c
    LIBRARY/float128/dpml_ux_int.c
    LIBRARY/float128/dpml_ux_inv_hyper.c
    LIBRARY/float128/dpml_ux_inv_trig.c
    LIBRARY/float128/dpml_ux_lgamma.c
    LIBRARY/float128/dpml_ux_log.c
    LIBRARY/float128/dpml_ux_mod.c
    LIBRARY/float128/dpml_ux_ops.c
    LIBRARY/float128/dpml_ux_ops_64.c
    LIBRARY/float128/dpml_ux_pow.c
    LIBRARY/float128/dpml_ux_powi.c
    LIBRARY/float128/dpml_ux_sqrt.c
    LIBRARY/float128/dpml_ux_trig.c
    LIBRARY/float128/sqrt_tab_t.c
)

# Compiler definitions that are common for all files
add_library(common_definitions INTERFACE)
target_compile_definitions(common_definitions INTERFACE
    DECIMAL_CALL_BY_REFERENCE=$<BOOL:${CALL_BY_REF}>
    DECIMAL_GLOBAL_ROUNDING=$<BOOL:${GLOBAL_RND}>
    DECIMAL_GLOBAL_EXCEPTION_FLAGS=$<BOOL:${GLOBAL_EXC}>
    $<UPPER_CASE:${CMAKE_SYSTEM_NAME}>
    efi2
)

# Main library files
add_library(main OBJECT ${MAIN_SOURCES})
target_compile_definitions(main PRIVATE
    USE_COMPILER_F128_TYPE=0
    USE_COMPILER_F80_TYPE=0
)
target_link_libraries(main PRIVATE common_definitions)

# Files from the "float128" directory
add_library(float128 OBJECT ${FLOAT128_SOURCES})
target_compile_definitions(float128 PRIVATE
    USE_NATIVE_QUAD_TYPE=0
    $<LOWER_CASE:${CMAKE_C_COMPILER_ID}>
)
target_link_libraries(float128 PRIVATE common_definitions)

# Output static library
add_library(intel_dfp
    $<TARGET_OBJECTS:main>
    $<TARGET_OBJECTS:float128>
)

include(GNUInstallDirs)

set(HEADERS_TO_INSTALL
    LIBRARY/src/bid_conf.h
    LIBRARY/src/bid_functions.h
)
set(HEADERS_DEST ${CMAKE_INSTALL_INCLUDEDIR})

install(TARGETS intel_dfp)
install(
    FILES ${HEADERS_TO_INSTALL}
    DESTINATION ${HEADERS_DEST}
)

# Test targets
add_executable(readtest TESTS/readtest.c)
target_compile_definitions(readtest PRIVATE
    __intptr_t_defined
    $<UPPER_CASE:${CMAKE_SYSTEM_NAME}>
    DECIMAL_CALL_BY_REFERENCE=$<BOOL:${CALL_BY_REF}>
    DECIMAL_GLOBAL_ROUNDING=$<BOOL:${GLOBAL_RND}>
    DECIMAL_GLOBAL_EXCEPTION_FLAGS=$<BOOL:${GLOBAL_EXC}>
)
target_link_libraries(readtest PRIVATE intel_dfp m)

set(TEST_ENTRIES ${PROJECT_SOURCE_DIR}/TESTS/readtest.in)
add_test(NAME sanity COMMAND sh -c "$<TARGET_FILE:readtest> < ${TEST_ENTRIES}")
