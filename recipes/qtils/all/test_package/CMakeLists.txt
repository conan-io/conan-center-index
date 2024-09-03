CMAKE_MINIMUM_REQUIRED(VERSION 3.15)

PROJECT(demo)

find_package(qtils  REQUIRED)

add_executable(${PROJECT_NAME}
        main.cpp
)

target_link_libraries(${PROJECT_NAME}
        qtils::qtils
)
