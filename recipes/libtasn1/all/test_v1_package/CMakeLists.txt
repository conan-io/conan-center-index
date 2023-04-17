cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

# Note: See https://github.com/conan-io/conan/issues/12237
# `NO_CMAKE_PATH` is added to avoid searching in `CMAKE_PREFIX_PATH`
# it should find the correct executable by falling back on the `PATH`
# environment variable defined by Conan during the test_package run.
find_program(ASN1_PARSER NAMES asn1Parser NO_CMAKE_PATH)
if(NOT ASN1_PARSER)
    message(FATAL_ERROR "asn1Parser not found")
endif()
find_package(libtasn1 REQUIRED CONFIG)

set(PKIX_ASN1_TAB_C "${CMAKE_CURRENT_BINARY_DIR}/pkix_asn1_tab.c")
set(PKIX_ASN_IN "${CMAKE_CURRENT_SOURCE_DIR}/../test_package/pkix.asn")
add_custom_command(
    COMMAND ${ASN1_PARSER} -o ${PKIX_ASN1_TAB_C} ${PKIX_ASN_IN}
    OUTPUT ${PKIX_ASN1_TAB_C}
    DEPENDS ${PKIX_ASN_IN}
)
add_custom_target(pkix_asn DEPENDS ${PKIX_ASN1_TAB_C})

add_executable(${PROJECT_NAME} ../test_package/test_package.c ${PKIX_ASN1_TAB_C})
target_link_libraries(${PROJECT_NAME} PRIVATE libtasn1::libtasn1)
add_dependencies(${PROJECT_NAME} pkix_asn)
