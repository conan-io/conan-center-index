cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

find_package(assert REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
# don't link to ${CONAN_LIBS} or CONAN_PKG::package
target_link_libraries(${PROJECT_NAME} PRIVATE assert::assert)
# In case the target project need a specific C++ standard
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
