cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C)

if (ZLIB_COMPAT)
  set(zlib_name ZLIB)
else()
  set(zlib_name zlib-ng)
endif()

find_package(${zlib_name} REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE ${zlib_name}::${zlib_name})
target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)
