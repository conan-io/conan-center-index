cmake_minimum_required(VERSION 3.15)
project(gdal_cmake_wrapper)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

include(CMakePushCheckState)

set(CMAKE_MODULE_PATH "${CMAKE_BINARY_DIR}")

if (${GDAL_USE_POPPLER})
    find_package(poppler)
    set(Poppler_VERSION_STRING ${poppler_VERSION})
    add_library(Poppler::Poppler ALIAS CONAN_PKG::poppler)
endif()

file(GLOB CONAN_GENERATED_CMAKE_FILES "${CMAKE_BINARY_DIR}/Find*.cmake")
foreach(CMAKE_FILE ${CONAN_GENERATED_CMAKE_FILES})
    include(${CMAKE_FILE})
endforeach()

add_library(PROJ::proj ALIAS CONAN_PKG::proj)

if (${GDAL_USE_ARROW})
    add_library(arrow_shared ALIAS CONAN_PKG::arrow)
endif()

if (${GDAL_USE_CRYPTOPP})
    add_library(CRYPTOPP::CRYPTOPP ALIAS CONAN_PKG::cryptopp)
endif()

if (${GDAL_USE_DEFLATE})
    add_library(Deflate::Deflate ALIAS CONAN_PKG::libdeflate)
endif()

if (${GDAL_USE_LZ4})
    add_library(LZ4::LZ4 ALIAS CONAN_PKG::lz4)
endif()

if (${GDAL_USE_BLOSC})
    add_library(Blosc::Blosc ALIAS CONAN_PKG::c-blosc)
endif()

if (${GDAL_USE_OPENJPEG})
    add_library(OPENJPEG::OpenJPEG ALIAS CONAN_PKG::openjpeg)
endif()

if (${GDAL_USE_GIF})
    add_library(GIF::GIF ALIAS CONAN_PKG::giflib)
endif()

if (${GDAL_USE_CFITSIO})
    add_library(CFITSIO::CFITSIO ALIAS CONAN_PKG::cfitsio)
endif()

if (${GDAL_USE_SQLITE3})
    add_library(SQLite::SQLite3 ALIAS CONAN_PKG::sqlite3)
endif()

if (${GDAL_USE_LIBXML2})
    add_library(LibXml2::LibXml2 ALIAS CONAN_PKG::libxml2)
endif()

if (${GDAL_USE_POSTGRESQL})
    add_library(PostgreSQL::PostgreSQL ALIAS CONAN_PKG::libpq)
endif()

if (${GDAL_USE_HDF5})
    find_package(HDF5)
endif()

if (${GDAL_USE_ZLIB})
    find_package(ZLIB)
endif()

add_subdirectory("source_subfolder")
