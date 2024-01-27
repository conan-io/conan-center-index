cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(wxWidgets REQUIRED core base stc xml CONFIG)

if(MSVC)
  add_definitions("-DUNICODE")
  add_definitions("-D_UNICODE")
  add_definitions("-D_CRT_SECURE_NO_WARNINGS")
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
# don't link to ${CONAN_LIBS} or CONAN_PKG::package

target_link_libraries(${PROJECT_NAME} ${wxwidgets_LIBRARIES})
