cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if(TINYSPLINE_API_0_3)
  add_definitions(-DTINYSPLINE_API_0_3)
endif()
add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c ${CONAN_LIBS})

if(TINYSPLINE_CXX)
  add_executable(${PROJECT_NAME}_cpp test_package.cpp)
  target_link_libraries(${PROJECT_NAME}_cpp ${CONAN_LIBS})
endif()
