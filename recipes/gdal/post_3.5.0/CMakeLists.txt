cmake_minimum_required(VERSION 3.15)
project(gdal_cmake_wrapper)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR})
include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

include(CMakePushCheckState)


if (${GDAL_USE_POPPLER})
    find_package(poppler)
    set(Poppler_VERSION_STRING ${poppler_VERSION})
    add_library(Poppler::Poppler ALIAS poppler::libpoppler)
endif()

file(GLOB CONAN_GENERATED_CMAKE_FILES "${CMAKE_CURRENT_SOURCE_DIR}/Find*.cmake")
foreach(CMAKE_FILE ${CONAN_GENERATED_CMAKE_FILES})
    include(${CMAKE_FILE})
endforeach()

if (${GDAL_USE_ARROW})
    find_package(Arrow REQUIRED)
    add_library(arrow_shared ALIAS arrow::arrow)
endif()

if (${GDAL_USE_CRYPTOPP})
    find_package(cryptopp REQUIRED)
    add_library(CRYPTOPP::CRYPTOPP ALIAS cryptopp::cryptopp-static)
endif()

if (${GDAL_USE_DEFLATE})
    find_package(libdeflate REQUIRED)
    add_library(Deflate::Deflate ALIAS libdeflate::libdeflate)
endif()

if (${GDAL_USE_LZ4})
    find_package(lz4 REQUIRED)
    add_library(LZ4::LZ4 ALIAS lz4::lz4)
endif()

if (${GDAL_USE_BLOSC})
    find_package(c-blosc REQUIRED)
    add_library(Blosc::Blosc ALIAS c-blosc::c-blosc)
endif()

if (${GDAL_USE_OPENEXR})
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

if (${GDAL_USE_FREEXL})
    find_package(freexl REQUIRED)
    add_library(FREEXL::freexl ALIAS freexl::freexl)
endif()

if (${GDAL_USE_OPENJPEG})
    add_library(OPENJPEG::OpenJPEG ALIAS OpenJPEG::OpenJPEG)
endif()

if (${GDAL_USE_GIF})
    find_package(GIF REQUIRED)
endif()

if (${GDAL_USE_CFITSIO})
    find_package(cfitsio)
    add_library(CFITSIO::CFITSIO ALIAS cfitsio::cfitsio)
endif()

if (${GDAL_USE_SQLITE3})
    find_package(SQLite3)
endif()

if (${GDAL_USE_LIBXML2})
    find_package(LibXml2)
endif()

if (${GDAL_USE_POSTGRESQL})
    find_package(PostgreSQL)
    add_library(PostgreSQL::PostgreSQL ALIAS PostgreSQL::pq)
endif()

if (${GDAL_USE_HDF5})
    find_package(HDF5)
    set(HDF5_C_LIBRARIES HDF5::C)
endif()

if (${GDAL_CONAN_PACKAGE_FOR_MYSQL} STREQUAL "libmysqlclient")
    find_package(mysql REQUIRED)
endif()
if (${GDAL_CONAN_PACKAGE_FOR_MYSQL} STREQUAL "mariadb-connector-c")
    find_package(mariadb-connector-c REQUIRED)
endif()

if (${GDAL_USE_ZLIB})
    find_package(ZLIB)
endif()

if (${GDAL_CONAN_PACKAGE_FOR_JPEG} STREQUAL "libjpeg-turbo")
    find_package(libjpeg-turbo REQUIRED)
    add_library(JPEG::JPEG ALIAS ${TARGET_FOR_JPEG})
endif()


add_subdirectory("source_subfolder")
