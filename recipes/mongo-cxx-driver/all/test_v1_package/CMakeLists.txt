cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(mongocxx REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)

if(${MONGO-CXX-DRIVER_POLYFILL} STREQUAL "std")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
elseif(${MONGO-CXX-DRIVER_POLYFILL} STREQUAL "experimental")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
endif()

if(TARGET mongo::mongocxx_shared)
  target_link_libraries(${PROJECT_NAME} PRIVATE mongo::mongocxx_shared mongo::bsoncxx_shared)
else()
  target_link_libraries(${PROJECT_NAME} PRIVATE mongo::mongocxx_static mongo::bsoncxx_static)
endif()
