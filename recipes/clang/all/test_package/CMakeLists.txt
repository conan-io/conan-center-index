cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX)
set(CMAKE_VERBOSE_MAKEFILE ON)

find_package(Clang REQUIRED CONFIG COMPONENTS clangTooling)
add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE clangTooling)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

# See https://clang.llvm.org/docs/LibTooling.html#builtin-includes for explanation of the following
string(REGEX MATCH "^([0-9]+)\\.([0-9]+)\\.([0-9]+)" clang_version_match ${Clang_VERSION})
set(clang_version_major ${CMAKE_MATCH_1})
set(clang_include_path "lib/clang/${clang_version_major}/include")
set(clang_include_src_path "${Clang_INCLUDE_DIR}/../${clang_include_path}/")
set(clang_include_dest_path "$<TARGET_FILE_DIR:test_package>/../${clang_include_path}")

add_custom_command(
    TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory ${clang_include_src_path} ${clang_include_dest_path}
)
