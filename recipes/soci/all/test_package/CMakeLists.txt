cmake_minimum_required(VERSION 3.1)

project(conanSociTest CXX)

option(ENABLE_CONAN "Enable conan" True)

set(TEST_NAME soci.tests)

message("** SOCI shared: ${SOCI_SHARED}")
#if (SOCI_SHARED)
#    add_executable(${TEST_NAME} shared.test.cpp)
#else ()
    add_executable(${TEST_NAME} static.test.cpp)
#endif ()

target_compile_features(${TEST_NAME} PRIVATE cxx_std_11)

if (ENABLE_CONAN)
  include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
  conan_basic_setup(TARGETS)
  conan_target_link_libraries(${TEST_NAME} ${CONAN_LIBS})
  message("** Conan SOCI libs: ${CONAN_LIBS}")
endif ()

enable_testing()
add_test(NAME ${TEST_NAME}
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}
    COMMAND ${TEST_NAME})
