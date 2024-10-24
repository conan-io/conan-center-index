cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(blis REQUIRED CONFIG)
add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE blis::blis)
target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)

find_package(BLAS REQUIRED MODULE)
add_executable(${PROJECT_NAME}_blas test_package_blas.c)
target_link_libraries(${PROJECT_NAME}_blas PRIVATE BLAS::BLAS)
target_compile_features(${PROJECT_NAME}_blas PRIVATE c_std_99)
