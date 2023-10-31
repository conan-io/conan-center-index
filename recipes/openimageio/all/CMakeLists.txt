cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper LANGUAGES CXX)

set(libs
    BZip2
    Boost
    DCMTK
    FFmpeg
    Freetype
    GIF
    HDF5
    JPEG
    LibRaw
    Libheif
    libjpeg-turbo
    Nuke
    OpenCV
    OpenColorIO
    OpenEXR
    OpenJPEG
    OpenVDB
    PNG
    Ptex
    R3DSDK
    Robinmap
    TBB
    TIFF
    WebP
    ZLIB
    fmt
    libsquish
    pugixml
)
foreach(lib IN LISTS libs)
    find_package(${lib} QUIET CONFIG)
    string(TOUPPER "${lib}" lib_upper)
    if(${lib}_FOUND)
        set(${lib}_INCLUDE_DIR ${${lib}_INCLUDE_DIRS})
        set(${lib_upper}_FOUND ${${lib}_FOUND})
        set(${lib_upper}_INCLUDE_DIR ${${lib}_INCLUDE_DIRS})
        set(${lib_upper}_INCLUDE_DIRS ${${lib}_INCLUDE_DIRS})
        set(${lib_upper}_LIBRARIES ${${lib}_LIBRARIES})
        set(${lib_upper}_LIBRARY_DIRS ${${lib}_LIBRARY_DIRS})
        set(${lib_upper}_LIBS ${${lib}_LIBS})
    endif()
endforeach()

set(LibRaw_r_LIBRARIES ${LibRaw_LIBRARIES})
set(LibRaw_r_DEFINITIONS ${LibRaw_DEFINITIONS})

include_directories(
    ${fmt_INCLUDE_DIRS}
    ${OpenEXR_INCLUDE_DIRS}
    ${Robinmap_INCLUDE_DIRS}
)

add_subdirectory(src)

target_link_libraries(OpenImageIO PRIVATE
    fmt::fmt
    tsl::robin_map
    $<TARGET_NAME_IF_EXISTS:Freetype::Freetype>
)
