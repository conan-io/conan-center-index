cmake_minimum_required(VERSION 3.8)

project(test_spix CXX)

find_package(spix REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_spix.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE spix::spix)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
