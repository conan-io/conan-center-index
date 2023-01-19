cmake_minimum_required(VERSION 3.8)
project(test_package)

find_package(tinyspline REQUIRED CONFIG)

if(tinyspline_VERSION VERSION_GREATER_EQUAL "0.3.0")
    add_definitions(-DTINYSPLINE_API_0_3)
endif()

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c PRIVATE tinyspline::tinyspline)

if(TINYSPLINE_CXX)
    # FIXME: we should have to call find_package(tinysplinecxx REQUIRED CONFIG)
    add_executable(${PROJECT_NAME}_cpp test_package.cpp)
    target_link_libraries(${PROJECT_NAME}_cpp PRIVATE tinysplinecxx::tinysplinecxx)
    if(tinyspline_VERSION VERSION_GREATER_EQUAL "0.4.0")
        target_compile_features(${PROJECT_NAME}_cpp PRIVATE cxx_std_11)
    endif()
endif()
