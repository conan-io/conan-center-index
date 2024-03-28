cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(Ruby REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        CXX_STANDARD 11
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
)

target_link_libraries(${PROJECT_NAME} Ruby::Ruby)
if (RUBY_STATIC_RUBY)
  target_compile_definitions(${PROJECT_NAME} PRIVATE RUBY_STATIC_RUBY)
endif()
if (RUBY_STATIC_LINKED_EXT)
  target_compile_definitions(${PROJECT_NAME} PRIVATE RUBY_STATIC_LINKED_EXT)
endif()
