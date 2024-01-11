cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(matplotlib_cpp REQUIRED CONFIG)
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(Python3 COMPONENTS NumPy)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE matplotlib_cpp::matplotlib_cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

target_link_libraries(${PROJECT_NAME} PRIVATE
  Python3::Python
  Python3::Module
)
if(Python3_NumPy_FOUND)
  target_link_libraries(${PROJECT_NAME} PRIVATE
    Python3::NumPy
  )
else()
  target_compile_definitions(${PROJECT_NAME} PRIVATE WITHOUT_NUMPY)
endif()
