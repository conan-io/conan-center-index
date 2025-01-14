cmake_minimum_required(VERSION 3.15)

project(test_devil LANGUAGES CXX)

find_package(DevIL REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
# don't link to ${CONAN_LIBS} or CONAN_PKG::package
target_link_libraries(${PROJECT_NAME} PRIVATE DevIL::IL DevIL::ILU DevIL::ILUT DevIL::DevIL)
