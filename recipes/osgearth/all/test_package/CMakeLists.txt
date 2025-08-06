cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(osgearth REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)

target_link_libraries(
    ${PROJECT_NAME}

    PRIVATE
        osgearth::osgearth
)

target_compile_features(
    ${PROJECT_NAME}

    PRIVATE
        cxx_std_14
)
