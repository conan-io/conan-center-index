cmake_minimum_required(VERSION 3.1)
project(conanSociTest CXX)

set(TEST_NAME soci.tests)
add_executable(${TEST_NAME} test_package.cpp)
target_compile_features(${TEST_NAME} PRIVATE cxx_std_11)

#message("soci empty?: ${SOCI_EMPTY}")
#if (SOCI_EMPTY)
#  target_compile_definitions(${TEST_NAME} PUBLIC SOCI_EMPTY)
#endif ()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
conan_target_link_libraries(${TEST_NAME} ${CONAN_LIBS}) # CONAN_PKG::soci_core CONAN_PKG::soci_empty
#message("Conan libs: ${CONAN_LIBS}")
