cmake_minimum_required(VERSION 3.1.2)
project(test_package)

find_package(OpenSceneGraph REQUIRED)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "bin")

include_directories(${OPENSCENEGRAPH_INCLUDE_DIRS})
link_libraries(${OPENSCENEGRAPH_LIBRARIES})
add_compile_definitions(${OPENSCENEGRAPH_COMPILE_DEFINITIONS})

add_compile_definitions(
	WITH_PNG=${WITH_PNG}
	WITH_DCMTK=${WITH_DCMTK}
)

add_executable(${PROJECT_NAME} test_package.cpp)
