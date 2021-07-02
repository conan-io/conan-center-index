# Custom cmake config because the maintainer doesn't want maintain CMake configs.
# https://github.com/conan-io/conan-center-index/pull/1544/files#r420852884

cmake_minimum_required(VERSION 3.0)
project(bx)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

include(GNUInstallDirs)

set(BX_SOURCE_SUBFOLDER "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder")

file(GLOB BX_SOURCES ${BX_SOURCE_SUBFOLDER}/src/*.cpp)
list(REMOVE_ITEM BX_SOURCES ${BX_SOURCE_SUBFOLDER}/src/amalgamated.cpp)
add_library(bx STATIC ${BX_SOURCES})
target_include_directories(bx PUBLIC ${BX_SOURCE_SUBFOLDER}/include ${BX_SOURCE_SUBFOLDER}/3rdparty)
install(TARGETS bx PUBLIC_HEADER ARCHIVE LIBRARY RUNTIME)
set_property(TARGET bx PROPERTY CXX_STANDARD 14)
install(DIRECTORY ${BX_SOURCE_SUBFOLDER}/include/bx DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

if(MSVC)
    target_include_directories(bx PUBLIC ${BX_SOURCE_SUBFOLDER}/include/compat/msvc)
    install(DIRECTORY ${BX_SOURCE_SUBFOLDER}/include/compat/msvc/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/bx/compat)
elseif(MINGW OR CYGWIN OR MSYS)
    target_include_directories(bx PUBLIC ${BX_SOURCE_SUBFOLDER}/include/compat/mingw)
    install(DIRECTORY ${BX_SOURCE_SUBFOLDER}/include/compat/mingw/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/bx/compat)
elseif(UNIX)
    if(APPLE)
        if(IOS)
            target_include_directories(bx PUBLIC ${BX_SOURCE_SUBFOLDER}/include/compat/ios)
            install(DIRECTORY ${BX_SOURCE_SUBFOLDER}/include/compat/ios/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/bx/compat)
        else()
            target_include_directories(bx PUBLIC ${BX_SOURCE_SUBFOLDER}/include/compat/osx)
            install(DIRECTORY ${BX_SOURCE_SUBFOLDER}/include/compat/osx/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/bx/compat)
        endif()
    else()
        if(SYSTEM_NAME STREQUAL "FreeBSD")
            target_include_directories(bx PUBLIC ${BX_SOURCE_SUBFOLDER}/include/compat/freebsd)
            install(DIRECTORY ${BX_SOURCE_SUBFOLDER}/include/compat/freebsd/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/bx/compat)
        endif()
    endif()
endif()

if(WIN32)
	target_link_libraries(bx PUBLIC psapi)
endif()

target_compile_definitions(bx PUBLIC "__STDC_LIMIT_MACROS" "__STDC_FORMAT_MACROS" "__STDC_CONSTANT_MACROS" PRIVATE "$<$<CONFIG:Debug>:BX_CONFIG_DEBUG=1>")

if(UNIX AND NOT APPLE AND NOT ANDROID)
	find_package(Threads)
	target_link_libraries(bx ${CMAKE_THREAD_LIBS_INIT} dl)

	target_link_libraries(bx rt)
elseif(APPLE)
	find_library(FOUNDATION_LIBRARY Foundation)
	mark_as_advanced(FOUNDATION_LIBRARY)
	target_link_libraries(bx PUBLIC ${FOUNDATION_LIBRARY})
endif()
