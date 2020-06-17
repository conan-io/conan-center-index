cmake_minimum_required(VERSION 3.12)
project(cmake_wrapper)

set(CONAN_BASIC_SETUP_ARGS TARGETS)
if(APPLE)
    # When building shared libraries,
    # the binaries in the build tree need RPATHS.
    list(APPEND CONAN_BASIC_SETUP_ARGS KEEP_RPATHS)
    set(CMAKE_SKIP_INSTALL_RPATH 1)
endif()

include("${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(${CONAN_BASIC_SETUP_ARGS})

# The following code disables CMake's find_package command
# by replacing it with a no-op stub and directly sets
# all necessary variables to values provided by respective
# Conan packages.

function(find_package)
    message(STATUS "[STUB] find_package(${ARGV})")
endfunction()

set(BOOST_CUSTOM YES)
set(Boost_LIBRARIES CONAN_PKG::boost)
set(Boost_INCLUDE_DIRS ${CONAN_INCLUDE_DIRS_BOOST})
set(Boost_LIBRARY_DIRS ${CONAN_LIB_DIRS_BOOST})

set(ZLIB_FOUND YES)
set(ZLIB_LIBRARIES CONAN_PKG::zlib)

set(TIFF_FOUND YES)
set(TIFF_LIBRARIES CONAN_PKG::libtiff)

set(OpenEXR_FOUND YES)
set(OPENEXR_LIBRARIES CONAN_PKG::openexr)
set(ILMBASE_LIBRARIES CONAN_PKG::openexr)
set(OPENEXR_INCLUDES ${CONAN_INCLUDE_DIRS_OPENEXR})
set(ILMBASE_INCLUDES ${CONAN_INCLUDE_DIRS_OPENEXR})

set(PugiXML_FOUND YES)
set(PUGIXML_FOUND YES)
set(PUGIXML_LIBRARIES CONAN_PKG::pugixml)
set(PUGIXML_INCLUDES ${CONAN_INCLUDE_DIRS_PUGIXML})

set(Libsquish_FOUND YES)
add_library(Libsquish::Libsquish UNKNOWN IMPORTED)
set_property(TARGET Libsquish::Libsquish PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::libsquish)

set(Robinmap_FOUND YES)
set(ROBINMAP_FOUND YES)
set(ROBINMAP_INCLUDES ${CONAN_INCLUDE_DIRS_TSL-ROBIN-MAP})

set(BZip2_FOUND YES)

set(fmt_FOUND YES)
set(FMT_FOUND YES)
set(FMT_INCLUDES ${CONAN_INCLUDE_DIRS_FMT})

if(TARGET CONAN_PKG::libjpeg-turbo)
    set(JPEG_FOUND YES)
    set(JPEGTurbo_FOUND YES)
    set(JPEG_LIBRARIES CONAN_PKG::libjpeg-turbo)
elseif(TARGET CONAN_PKG::libjpeg)
    set(JPEG_FOUND YES)
    set(JPEGTurbo_FOUND NO)
    set(JPEG_LIBRARIES CONAN_PKG::libjpeg)
endif()

if(TARGET CONAN_PKG::libpng)
    set(PNG_FOUND YES)
    set(PNG_LIBRARIES CONAN_PKG::libpng)
endif()

if(TARGET CONAN_PKG::freetype)
    set(Freetype_FOUND YES)
    set(FREETYPE_FOUND YES)
    set(FREETYPE_LIBRARIES CONAN_PKG::freetype)
endif()

if(TARGET CONAN_PKG::openjpeg)
    set(OpenJpeg_FOUND YES)
    set(OPENJPEG_FOUND YES)
    set(OPENJPEG_LIBRARIES CONAN_PKG::openjpeg)
endif()

if(TARGET CONAN_PKG::libwebp)
    set(Webp_FOUND YES)
    set(WEBP_FOUND YES)
    set(WEBP_LIBRARY CONAN_PKG::libwebp)
endif()

if(TARGET CONAN_PKG::giflib)
    set(GIF_FOUND YES)
    set(GIF_LIBRARIES CONAN_PKG::giflib)
endif()

if(TARGET CONAN_PKG::dcmtk)
    set(DCMTK_FOUND YES)
    set(DCMTK_LIBRARIES CONAN_PKG::dcmtk)
endif()

if(TARGET CONAN_PKG::libraw)
    set(LIBRAW_FOUND YES)
    set(LibRaw_r_LIBRARIES CONAN_PKG::libraw)
endif()

include_directories(
    BEFORE
    "${CMAKE_SOURCE_DIR}/source_subfolder/src/include"
    "${CMAKE_BINARY_DIR}/source_subfolder/src/include"
    "${CMAKE_BINARY_DIR}/source_subfolder/include"
)

add_subdirectory(source_subfolder)
