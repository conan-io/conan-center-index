cmake_minimum_required(VERSION 3.1)
project(coz CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if(NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 11)
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Threads REQUIRED)

file(GLOB_RECURSE sources source_subfolder/libcoz/*.cpp)
file(GLOB_RECURSE headers source_subfolder/include/*.h)

add_library(${PROJECT_NAME} SHARED ${sources})
set_target_properties(${PROJECT_NAME} PROPERTIES
    PUBLIC_HEADER "${headers}"
    VERSION ${CONAN_PACKAGE_VERSION})
target_include_directories(${PROJECT_NAME}
    PUBLIC source_subfolder/libcoz
    PRIVATE source_subfolder/include)
target_link_libraries(${PROJECT_NAME} PUBLIC dl rt Threads::Threads elf++ dwarf++)

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/${PROJECT_NAME})

install(PROGRAMS source_subfolder/coz DESTINATION bin)
install(FILES source_subfolder/LICENSE.md DESTINATION licenses)
