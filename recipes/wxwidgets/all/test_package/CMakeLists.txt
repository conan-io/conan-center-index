cmake_minimum_required(VERSION 3.1)
project(test_package)

find_package(wxWidgets REQUIRED)

if(MSVC)
  add_definitions("-DUNICODE")
  add_definitions("-D_UNICODE")
  add_definitions("-D_CRT_SECURE_NO_WARNINGS")
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} wxWidgets::wxWidgets)
