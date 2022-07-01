cmake_minimum_required(VERSION 3.1)
project(PackageTest C CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

option(BUILD_NO_CHANGES "Build no_changes sources" ON)
option(BUILD_INCLUDE_OVERRIDE "Build include_override sources" ON)
option(BUILD_MI_API "Build mi_api sources" ON)

find_package(mimalloc REQUIRED CONFIG)
if(TARGET mimalloc-static)
    set(MIMALLOC_LIBS mimalloc-static)
else()
    set(MIMALLOC_LIBS mimalloc)
endif()


if (BUILD_NO_CHANGES)
    add_executable(no_changes no_changes.c)
    target_link_libraries(no_changes ${MIMALLOC_LIBS})
    target_compile_features(no_changes PUBLIC c_std_11)

    add_executable(no_changes_cpp no_changes.cpp)
    target_link_libraries(no_changes_cpp ${MIMALLOC_LIBS})
    target_compile_features(no_changes_cpp PUBLIC cxx_std_17)
endif (BUILD_NO_CHANGES)

if (BUILD_INCLUDE_OVERRIDE)
    add_executable(include_override include_override.c)
    target_link_libraries(include_override ${MIMALLOC_LIBS})
    target_compile_features(include_override PUBLIC c_std_11)

    add_executable(include_override_cpp include_override.cpp)
    target_link_libraries(include_override_cpp ${MIMALLOC_LIBS})
    target_compile_features(include_override_cpp PUBLIC cxx_std_17)
endif (BUILD_INCLUDE_OVERRIDE)

if (BUILD_MI_API)
    add_executable(mi_api mi_api.c)
    target_link_libraries(mi_api ${MIMALLOC_LIBS})
    target_compile_features(mi_api PUBLIC c_std_11)

    add_executable(mi_api_cpp mi_api.cpp)
    target_link_libraries(mi_api_cpp ${MIMALLOC_LIBS})
    target_compile_features(mi_api_cpp PUBLIC cxx_std_17)
endif (BUILD_MI_API)
