cmake_minimum_required(VERSION 3.1)

project(LibRaw)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

file(GLOB_RECURSE headers "source_subfolder/libraw/*.h")

set(sources
    "source_subfolder/src/libraw_c_api.cpp"
    "source_subfolder/src/libraw_cxx.cpp"
    "source_subfolder/src/libraw_datastream.cpp"
    "source_subfolder/internal/dcraw_common.cpp"
    "source_subfolder/internal/dcraw_fileio.cpp"
    "source_subfolder/internal/demosaic_packs.cpp"
)

if(WIN32)
    add_definitions(-DWIN32)

    if(BUILD_SHARED_LIBS)
        add_definitions(-DLIBRAW_BUILDLIB)
    else()
        add_definitions(-DLIBRAW_NODLL)
    endif()
endif()

if (TARGET CONAN_PKG::libjpeg OR TARGET CONAN_PKG::libjpeg-turbo)
    add_definitions(-DUSE_JPEG -DUSE_JPEG8)
endif ()
if (TARGET CONAN_PKG::lcms)
    add_definitions(-DUSE_LCMS2)
endif ()
if (TARGET CONAN_PKG::jasper)
    add_definitions(-DUSE_JASPER)
endif ()

add_library(raw ${headers} ${sources})
set_property(TARGET raw PROPERTY CXX_STANDARD 11)
target_include_directories(raw PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/" ${CONAN_INCLUDE_DIRS})
target_link_libraries(raw PUBLIC ${CONAN_LIBS})
target_compile_options(raw PUBLIC $<$<CXX_COMPILER_ID:MSVC>:/W0>)

install(DIRECTORY "source_subfolder/libraw" DESTINATION include)
install(TARGETS raw ARCHIVE DESTINATION lib RUNTIME DESTINATION bin LIBRARY DESTINATION lib)
