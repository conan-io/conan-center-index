cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(astro-informatics-so3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} example.c)
target_compile_features(${PROJECT_NAME} PUBLIC c_std_99)
target_link_libraries(${PROJECT_NAME}
                      astro-informatics-so3::astro-informatics-so3)
