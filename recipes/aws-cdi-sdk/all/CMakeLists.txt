cmake_minimum_required(VERSION 3.15)
project(cdisdk LANGUAGES C CXX)

find_package(AWSSDK REQUIRED CONFIG)
add_subdirectory(aws-cpp-sdk-cdi)

find_package(aws-libfabric REQUIRED CONFIG)
find_package(Threads REQUIRED)

file(GLOB_RECURSE CDI_SOURCES "src/cdi/*.c*" "src/common/src/*.c" )
if(NOT WIN32)
    list(FILTER CDI_SOURCES EXCLUDE REGEX "src/common/src/os_windows.c")
endif()
add_library(cdisdk ${CDI_SOURCES})
target_include_directories(cdisdk PRIVATE include src/common/include src/cdi)
target_link_libraries(cdisdk PRIVATE
    AWS::aws-cpp-sdk-cdi
    AWS::aws-sdk-cpp-monitoring
    aws-libfabric::aws-libfabric
    Threads::Threads
)
set_target_properties(cdisdk PROPERTIES
    SOVERSION ${PRODUCT_VERSION}
    VERSION ${MAJOR_MINOR_VERSION}
    C_STANDARD 99
    CXX_STANDARD 11
)
# https://github.com/aws/aws-cdi-sdk/blob/v2.4.1/Makefile#L214-L232
target_compile_definitions(cdisdk PRIVATE _LINUX _POSIX_C_SOURCE=200112L)
if (NOT MSVC)
    target_compile_options(cdisdk PRIVATE
        -Wall -Wextra
        "$<$<CONFIG:DEBUG>:-O0;-g;-DDEBUG>"
        "$<$<CONFIG:RELEASE>:-O3;-DNDEBUG>"
    )
    # https://github.com/aws/aws-cdi-sdk/blob/v2.4.1/Makefile#L376-L379
    target_link_options(cdisdk PRIVATE -z defs -Wl,--version-script ${CMAKE_SOURCE_DIR}/libcdisdk.vers)
endif()
if (UNIX)
    target_link_libraries(cdisdk PRIVATE dl rt m)
endif()

install(TARGETS cdisdk
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)
install(DIRECTORY include/ DESTINATION include)
