cmake_minimum_required(VERSION 3.15)

project(test_package CXX)


add_executable(${PROJECT_NAME} test_package.cpp)

if(LIBASSERT2)
  find_package(libassert REQUIRED CONFIG)
  target_link_libraries(${PROJECT_NAME} PRIVATE libassert::assert)
  target_compile_definitions(${PROJECT_NAME} PRIVATE LIBASSERT2)
else()
  find_package(assert REQUIRED CONFIG)
  target_link_libraries(${PROJECT_NAME} PRIVATE assert::assert)
endif()


target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
