# see https://github.com/conan-io/cmake-conan/issues/249#issuecomment-737011732
cmake_minimum_required(VERSION 3.17)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

# conanfile.py source() method extracts to source_subfolder
# nmos-cpp top-level CMakeLists.txt is in Development
add_subdirectory("source_subfolder/Development")
