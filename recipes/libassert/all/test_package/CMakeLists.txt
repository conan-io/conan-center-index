cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

option(LIBASSERT2 "" Off)

if(LIBASSERT2)
  find_package(libassert REQUIRED CONFIG)
else()
  find_package(assert REQUIRED CONFIG)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
# don't link to ${CONAN_LIBS} or CONAN_PKG::package
if(${assert_VERSION} VERSION_GREATER_EQUAL "2.0.0")
  target_link_libraries(${PROJECT_NAME} PRIVATE libassert::assert)
  target_compile_definitions(${PROJECT_NAME} PRIVATE LIBASSERT2)
else()
  target_link_libraries(${PROJECT_NAME} PRIVATE assert::assert)
endif()
# In case the target project need a specific C++ standard
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
