cmake_minimum_required(VERSION 3.15)

project(foxglove-sdk VERSION "${FOXGLOVE_SDK_VERSION}" LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(INCLUDE_DIR "${CMAKE_CURRENT_BINARY_DIR}/include")
set(SRC_DIR "${CMAKE_CURRENT_BINARY_DIR}/src")

# Pre-built C library
if (${BUILD_SHARED_LIBS})
    file(GLOB C_LIBRARIES 
        "${CMAKE_CURRENT_BINARY_DIR}/lib/*.so"
        "${CMAKE_CURRENT_BINARY_DIR}/lib/*.dylib"
        "${CMAKE_CURRENT_BINARY_DIR}/lib/*.dll"
    )
else()
    file(GLOB C_LIBRARIES 
        "${CMAKE_CURRENT_BINARY_DIR}/lib/*.a"
        "${CMAKE_CURRENT_BINARY_DIR}/lib/*.lib"
    )
endif()

file(GLOB_RECURSE FOXGLOVE_SOURCES 
    "${SRC_DIR}/*.cpp"
)

add_library(foxglove_cpp ${FOXGLOVE_SOURCES})

set_target_properties(foxglove_cpp PROPERTIES
    VERSION ${FOXGLOVE_SDK_VERSION}
    SOVERSION ${FOXGLOVE_SDK_VERSION_MAJOR}
)

target_include_directories(foxglove_cpp 
    PUBLIC ${INCLUDE_DIR}
)

target_link_libraries(foxglove_cpp PRIVATE ${C_LIBRARIES})

install(TARGETS foxglove_cpp
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(DIRECTORY ${INCLUDE_DIR}/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING PATTERN "*.h" PATTERN "*.hpp"
)

install(FILES ${C_LIBRARIES}
    DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
