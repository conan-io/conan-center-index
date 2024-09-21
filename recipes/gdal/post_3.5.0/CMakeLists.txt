cmake_minimum_required(VERSION 3.15)
project(gdal_cmake_wrapper)

if (GDAL_USE_OPENEXR)
    find_package(Imath REQUIRED)
    find_package(OpenEXR REQUIRED)
    add_library(OpenEXR::IlmImf ALIAS OpenEXR::IlmThread)
    add_library(OpenEXR::IlmImfUtil ALIAS OpenEXR::OpenEXR)
    add_library(OpenEXR::Half ALIAS Imath::Imath)
    # gdal includes without "Imath/" folder prefix
    target_include_directories(Imath::Imath INTERFACE ${Imath_INCLUDE_DIR})
    # and also without "OpenEXR/" prefix
    target_include_directories(OpenEXR::OpenEXR INTERFACE ${OpenEXR_INCLUDE_DIR})
endif()

add_subdirectory(src)
