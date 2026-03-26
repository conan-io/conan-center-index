cmake_minimum_required(VERSION 3.15)
# Disable vcpkg MSBuild integration (auto-injected via vcpkg.path.txt)
# to prevent system-installed vcpkg packages from shadowing Conan packages.
set(CMAKE_VS_GLOBALS "VcpkgEnabled=false")
project(test_dtoa_milo CXX)

find_package(dtoa-milo REQUIRED CONFIG)

add_executable(test_dtoa_milo test_dtoa_milo.cpp)
target_link_libraries(test_dtoa_milo PRIVATE dtoa-milo::dtoa-milo)
target_compile_features(test_dtoa_milo PRIVATE cxx_std_11)
