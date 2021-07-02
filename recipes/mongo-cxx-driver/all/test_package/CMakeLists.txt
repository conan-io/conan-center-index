cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(mongocxx REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

if(${MONGO-CXX-DRIVER_POLYFILL} STREQUAL "std")
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
elseif(${MONGO-CXX-DRIVER_POLYFILL} STREQUAL "experimental")
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 14)
else()
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
endif()

if(MONGO-CXX-DRIVER_SHARED)
  target_link_libraries(${PROJECT_NAME} mongo::mongocxx_shared mongo::bsoncxx_shared)
else()
  target_link_libraries(${PROJECT_NAME} mongo::mongocxx_static mongo::bsoncxx_static)
endif()
