cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX)

find_package(dispenso REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
# don't link to ${CONAN_LIBS} or CONAN_PKG::package
target_link_libraries(${PROJECT_NAME} PRIVATE Dispenso::dispenso)
# In case the target project need a specific C++ standard
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
