cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(wt REQUIRED Wt HTTP CONFIG)
if(WITH_DBO)
  find_package(wt REQUIRED Dbo CONFIG)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
target_link_libraries(${PROJECT_NAME} Wt::Wt Wt::HTTP)
if(WITH_DBO)
  target_link_libraries(${PROJECT_NAME} Wt::Dbo)
  target_compile_definitions(${PROJECT_NAME} PRIVATE "WITH_DBO")
endif()
