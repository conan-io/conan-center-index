cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(intel-ipsec-mb REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE intel-ipsec-mb::intel-ipsec-mb)
target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)
