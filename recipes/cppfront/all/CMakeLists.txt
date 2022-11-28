cmake_minimum_required(VERSION 3.8)
project(cppfront CXX)

add_executable(${PROJECT_NAME} ${CMAKE_CURRENT_SOURCE_DIR}/source/cppfront.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)

install(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_BINDIR})

