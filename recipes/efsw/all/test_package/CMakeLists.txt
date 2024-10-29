cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX) # if the project uses c++

find_package(efsw REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
# don't link to ${CONAN_LIBS} or CONAN_PKG::package
target_link_libraries(${PROJECT_NAME} PRIVATE efsw::efsw)
# In case the target project need a specific C++ standard
