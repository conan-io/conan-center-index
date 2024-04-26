# Custom find_package() wrapper because CMakeDeps does not support upper-case CMake var output expected by the project.
macro(custom_find_package name)
    find_package(${name} ${ARGN}
        QUIET CONFIG
        # Allow only Conan packages
        NO_DEFAULT_PATH
        PATHS ${CMAKE_PREFIX_PATH}
    )
    string(TOUPPER ${name} name_upper)
    set(${name_upper}_FOUND TRUE)
    set(${name_upper}_VERSION_STRING ${${name}_VERSION_STRING})
    set(${name_upper}_INCLUDE_DIRS ${${name}_INCLUDE_DIRS})
    set(${name_upper}_INCLUDE_DIR ${${name}_INCLUDE_DIR})
    set(${name_upper}_LIBRARIES ${${name}_LIBRARIES})
    set(${name_upper}_DEFINITIONS ${${name}_DEFINITIONS})
    unset(name_upper)
endmacro()

custom_find_package(DC1394)
#custom_find_package(DepthSense)
custom_find_package(Eigen3)
custom_find_package(FFMPEG)
custom_find_package(JPEG)
custom_find_package(libraw)
custom_find_package(libusb1)
custom_find_package(Lz4)
#custom_find_package(MediaFoundation)
custom_find_package(OpenEXR)
#custom_find_package(OpenNI2)
#custom_find_package(OpenNI)
#custom_find_package(Pleora)
custom_find_package(PNG)
custom_find_package(pybind11)
custom_find_package(RealSense2)
#custom_find_package(RealSense)
#custom_find_package(TeliCam)
custom_find_package(TIFF)
custom_find_package(uvc)
custom_find_package(X11)
custom_find_package(zstd)

# Unvendored dependencies
find_package(PalSigslot REQUIRED CONFIG)
link_libraries(Pal::Sigslot)
find_package(tinyobjloader REQUIRED CONFIG)
