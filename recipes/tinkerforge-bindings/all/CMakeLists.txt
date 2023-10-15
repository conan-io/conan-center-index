cmake_minimum_required(VERSION 3.4)
project(tinkerforge_bindings)

set(SOURCES_DIR ${CMAKE_CURRENT_LIST_DIR}/src)

file(GLOB SOURCES ${SOURCES_DIR}/source/*.c)
file(GLOB HEADERS ${SOURCES_DIR}/source/*.h)

if(WIN32 AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

add_library(${PROJECT_NAME} ${SOURCES})

if(MSVC)
        target_link_libraries(${PROJECT_NAME} PRIVATE ws2_32 advapi32)
endif()

include(GNUInstallDirs)
set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER "${HEADERS}")
install(TARGETS ${PROJECT_NAME}
        PUBLIC_HEADER DESTINATION include
)
