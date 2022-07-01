cmake_minimum_required(VERSION 3.4)
project(tinkerforge_bindings)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

file(GLOB SOURCES ${CMAKE_SOURCE_DIR}/source_subfolder/source/*.c)
file(GLOB HEADERS ${CMAKE_SOURCE_DIR}/source_subfolder/source/*.h)

if(WIN32 AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

add_library(${PROJECT_NAME} ${SOURCES})

if(MSVC)
        target_link_libraries(${PROJECT_NAME} PRIVATE ws2_32 advapi32)
endif()

set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER "${HEADERS}")
install(TARGETS ${PROJECT_NAME}
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin
        PUBLIC_HEADER DESTINATION include
)
