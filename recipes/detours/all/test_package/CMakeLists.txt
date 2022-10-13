cmake_minimum_required(VERSION 3.8)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(detours REQUIRED CONFIG)

add_executable(victim victim.c)

set(HOOK_SOURCES hook.c)
if(MSVC)
    list(APPEND HOOK_SOURCES hook_msvc.def)
else()
    list(APPEND HOOK_SOURCES hook_mingw.def)
endif()
add_library(hook SHARED ${HOOK_SOURCES})
target_link_libraries(hook PRIVATE detours::detours)
if(NOT MSVC)
    target_link_options(hook PRIVATE -static-libgcc -static-libstdc++)
endif()
set_target_properties(hook PROPERTIES PREFIX "")

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE detours::detours)
