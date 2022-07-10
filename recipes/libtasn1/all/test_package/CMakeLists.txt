cmake_minimum_required(VERSION 3.1)
project(test_package C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

add_custom_command(OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/pkix_asn1_tab.c"
    COMMAND asn1Parser -o "${CMAKE_CURRENT_BINARY_DIR}/pkix_asn1_tab.c" "${CMAKE_CURRENT_SOURCE_DIR}/pkix.asn"
    DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/pkix.asn")

add_executable(${PROJECT_NAME} test_package.c "${CMAKE_CURRENT_BINARY_DIR}/pkix_asn1_tab.c")
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
