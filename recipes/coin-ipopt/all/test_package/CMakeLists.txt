cmake_minimum_required(VERSION 3.15)
project(test_package)

include(FindPkgConfig)
pkg_check_modules(Ipopt REQUIRED IMPORTED_TARGET coin-ipopt)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::Ipopt)
