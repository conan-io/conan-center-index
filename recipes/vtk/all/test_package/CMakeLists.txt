cmake_minimum_required(VERSION 3.1.3) # 3.1.3 is first fully functional cross-platform version with Targets
project(test_vtk)

set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

# From oryginal recipe
# if(APPLE)
#     # Workaround for rpath error
#     set(CMAKE_SKIP_RPATH 0)
# endif(APPLE)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} CONAN_PKG::VTK)
#set_target_properties(test_zlib PROPERTIES OUTPUT_NAME "test")

# From oryginal recipe
# target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS} ${CMAKE_DL_LIBS})
# if(UNIX AND NOT APPLE)
#     TARGET_LINK_LIBRARIES(${PROJECT_NAME} m)
# endif()
