cmake_minimum_required(VERSION 2.8)
project(tinkerforge_bindings)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

file(GLOB SOURCES ${CMAKE_SOURCE_DIR}/source_subfolder/source/*.c)
file(GLOB HEADERS ${CMAKE_SOURCE_DIR}/source_subfolder/source/*.h)

add_library(${PROJECT_NAME} ${SOURCES})
set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER "${HEADERS}")
install(TARGETS ${PROJECT_NAME}
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin
        PUBLIC_HEADER DESTINATION include
)
