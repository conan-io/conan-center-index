cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

# Note: testing with RenderingFreeType to check autoinit is working
# TODO make test different depending on what modules were enabled. ie don't test with this if not built!
find_package (VTK COMPONENTS CommonCore RenderingFreeType REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

target_link_libraries(${PROJECT_NAME} VTK::VTK)
