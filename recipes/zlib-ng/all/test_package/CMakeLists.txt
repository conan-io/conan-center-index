cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C)

if (ZLIB_COMPAT)
  find_package(ZLIB 1.3.1 EXACT REQUIRED CONFIG)
  set(zlib_name ZLIB)
else()
  find_package(zlib-ng REQUIRED CONFIG)
  set(zlib_name zlib-ng)
endif()



add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE ${zlib_name}::${zlib_name})
target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)
