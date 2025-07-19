################################################################################
#                                                                              #
# This file is part of IfcOpenShell.                                           #
#                                                                              #
# IfcOpenShell is free software: you can redistribute it and/or modify         #
# it under the terms of the Lesser GNU General Public License as published by  #
# the Free Software Foundation, either version 3.0 of the License, or          #
# (at your option) any later version.                                          #
#                                                                              #
# IfcOpenShell is distributed in the hope that it will be useful,              #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 #
# Lesser GNU General Public License for more details.                          #
#                                                                              #
# You should have received a copy of the Lesser GNU General Public License     #
# along with this program. If not, see <http://www.gnu.org/licenses/>.         #
#                                                                              #
################################################################################

cmake_minimum_required(VERSION 3.21)
set(CMAKE_CXX_STANDARD_REQUIRED ON) # not necessary, but encouraged
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_program(CCACHE_FOUND ccache)
if(CCACHE_FOUND)
    set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE ccache)
endif()

add_definitions(-D_DISABLE_CONSTEXPR_MUTEX_CONSTRUCTOR)

cmake_policy(SET CMP0048 NEW)
cmake_policy(SET CMP0074 NEW)
cmake_policy(SET CMP0078 NEW)
cmake_policy(SET CMP0086 NEW)
if (POLICY CMP0144)
    cmake_policy(SET CMP0144 NEW) # find_package() uses upper-case <PACKAGENAME>_ROOT variables.
endif()

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release")
endif()

# use extra version to make pre-release using eg semver
if(NOT DEFINED EXTRA_VERSION)
    set(EXTRA_VERSION "-alpha.3")
endif()

option(WASM_BUILD "Build a WebAssembly binary." OFF)

option(ENABLE_BUILD_OPTIMIZATIONS "Enable certain compiler and linker optimizations on RelWithDebInfo and Release builds." OFF)
option(BUILD_SHARED_LIBS "Build IfcParse and IfcGeom as shared libs (SO/DLL)." OFF)
option(MSVC_PARALLEL_BUILD "Multi-threaded compilation in Microsoft Visual Studio (/MP)" OFF)
option(USE_VLD "Use Visual Leak Detector for debugging memory leaks, MSVC-only." OFF)
option(USE_MMAP "Adds a command line options to parse IFC files from memory mapped files using Boost.Iostreams" OFF)
option(NO_WARN "Disable all warnings" OFF)

option(BUILD_IFCGEOM "Build IfcGeom." ON)
option(BUILD_IFCPYTHON "Build IfcPython." ON)
option(BUILD_CONVERT "Build IfcConvert executable." ON)
option(BUILD_DOCUMENTATION "Build IfcOpenShell Documentation." OFF)
option(BUILD_EXAMPLES "Build example applications." ON)
option(BUILD_GEOMSERVER "Build IfcGeomServer executable." ON)
option(BUILD_IFCMAX "Build IfcMax, a 3ds Max plug-in, Windows-only." OFF)
option(BUILD_QTVIEWER "Build IfcOpenShell Qt GUI Viewer" OFF) # QtViewer requires Qt6
option(BUILD_PACKAGE "" OFF)

option(WITH_OPENCASCADE "Enable geometry interpretation using Open CASCADE" ON)
option(WITH_CGAL "Enable geometry interpretation using CGAL" ON)
option(COLLADA_SUPPORT "Build IfcConvert with COLLADA support (requires OpenCOLLADA)." ON)
option(GLTF_SUPPORT "Build IfcConvert with glTF support (requires json.hpp)." OFF)
option(HDF5_SUPPORT "Enable HDF5 support (requires HDF5, zlib)" ON)
option(WITH_PROJ "Enable output of Earth-Centered Earth-Fixed glTF output using the PROJ library" OFF)
option(IFCXML_SUPPORT "Build IfcParse with ifcXML support (requires libxml2)." ON)
option(USD_SUPPORT "Build IfcConvert with USD support (requires pixar's USD library)." OFF)
option(CITYJSON_SUPPORT "Build IfcConvert with CityJSON support (requires CityJSON library)." OFF)
option(WITH_RELATIONSHIP_VALIDATION "Build IfcConvert with option to validate geometrical relationships." OFF)

option(USERSPACE_PYTHON_PREFIX "Installs IfcPython for the current user only instead of system-wide." OFF)
option(ADD_COMMIT_SHA "Add commit sha and branch in version number, warning results in many rebuilds, requires git" OFF)

option(VERSION_OVERRIDE "Override the version defined in IfcParse.h with the file VERSION in the repository root" OFF)

if (VERSION_OVERRIDE)
    file(READ "VERSION" "RELEASE_VERSION_")
    string(STRIP "${RELEASE_VERSION_}" RELEASE_VERSION)
    message(STATUS "Detected version '${RELEASE_VERSION}'")
else()
    set(RELEASE_VERSION "0.8.0")
endif()

project(IfcOpenShell VERSION ${RELEASE_VERSION})

list(APPEND CMAKE_PREFIX_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

message(STATUS "Build options:")
get_cmake_property(_variableNames VARIABLES)
foreach(_variableName ${_variableNames})
    if(_variableName MATCHES "^(BUILD_|WITH_|ENABLE_|USE_|OPTION_|COLLADA_SUPPORT|GLTF_SUPPORT|HDF5_SUPPORT|IFCXML_SUPPORT|USD_SUPPORT|CITYJSON_SUPPORT|WASM_BUILD|NO_WARN|USERSPACE_PYTHON_PREFIX|ADD_COMMIT_SHA|VERSION_OVERRIDE|MSVC_PARALLEL_BUILD)")
        message(STATUS "  ${_variableName} = [${${_variableName}}]")
    endif()
endforeach()

if((BUILD_CONVERT OR BUILD_GEOMSERVER OR BUILD_IFCPYTHON) AND(NOT BUILD_IFCGEOM))
    message(STATUS "'IfcGeom' is required with current outputs")
    set(BUILD_IFCGEOM ON)
endif()

if(MSVC AND MSVC_PARALLEL_BUILD)
    add_definitions("/MP")
endif()

if(NO_WARN)
    if(MSVC)
        add_compile_options("/w")
    else()
        add_compile_options("-w")
    endif()
endif()

include(GNUInstallDirs)

# Specify paths to install files
if(NOT BINDIR)
    set(BINDIR bin)
endif()
if(NOT IS_ABSOLUTE ${BINDIR})
    set(BINDIR ${CMAKE_INSTALL_BINDIR})
endif()
message(STATUS "BINDIR: ${BINDIR}")

if(NOT INCLUDEDIR)
    set(INCLUDEDIR include)
endif()
if(NOT IS_ABSOLUTE ${INCLUDEDIR})
    set(INCLUDEDIR ${CMAKE_INSTALL_INCLUDEDIR})
endif()
message(STATUS "INCLUDEDIR: ${INCLUDEDIR}")

if(NOT LIBDIR)
    set(LIBDIR lib)
endif()
if(NOT IS_ABSOLUTE ${LIBDIR})
    set(LIBDIR ${CMAKE_INSTALL_LIBDIR})
endif()
message(STATUS "LIBDIR: ${LIBDIR}")

set(IFCOPENSHELL_LIBRARY_DIR "") # for *nix rpaths

if(BUILD_SHARED_LIBS)
    add_definitions(-DIFC_SHARED_BUILD)
    if(MSVC)
        message(WARNING "Building DLLs against the static VC run-time. This is not recommended if the DLLs are to be redistributed.")
        # C4521: 'identifier' : class 'type' needs to have dll-interface to be used by clients of class 'type2'
        # There will be couple hundreds of these so suppress them away, https://msdn.microsoft.com/en-us/library/esew7y1w.aspx
        add_definitions(-wd4251)
    endif()

    set(IFCOPENSHELL_LIBRARY_DIR "${LIBDIR}")
endif()

set(CMAKE_FIND_ROOT_PATH_BACKUP "${CMAKE_FIND_ROOT_PATH}")

macro(clear_wasm_sysroot)
if(WASM_BUILD)
    # when using the nix/build-all.py build script we should not
    # look into the sysroot for most of the dependencies but rather
    # in the designated build/ folder created by the script.
    set(CMAKE_FIND_ROOT_PATH "")
endif()
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE NEVER)
endmacro()

macro(restore_wasm_sysroot)
if(WASM_BUILD)
    # reset to use sysroot
    set(CMAKE_FIND_ROOT_PATH "${CMAKE_FIND_ROOT_PATH_BACKUP}")
endif()
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
endmacro()

if(WITH_CGAL)
    add_definitions(-DIFOPSH_WITH_CGAL)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DIFOPSH_WITH_CGAL)

    if(CITYJSON_SUPPORT)
		add_definitions(-DIFOPSH_WITH_CITYJSON)
    endif()

    # set(CMAKE_FIND_DEBUG_MODE TRUE)
    find_package(gmp REQUIRED CONFIG)
    # set(CMAKE_FIND_DEBUG_MODE FALSE)
    list(APPEND CGAL_LIBRARIES "gmp::gmpxx")
    find_package(mpfr REQUIRED CONFIG)
    list(APPEND CGAL_LIBRARIES "mpfr::mpfr")

    list(APPEND GEOMETRY_KERNELS cgal)
endif()

if(WITH_OPENCASCADE)
    add_definitions(-DIFOPSH_WITH_OPENCASCADE)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DIFOPSH_WITH_OPENCASCADE)
    list(APPEND GEOMETRY_KERNELS opencascade)
endif()

if(GLTF_SUPPORT OR CITYJSON_SUPPORT)
    UNIFY_ENVVARS_AND_CACHE(JSON_INCLUDE_DIR)
    clear_wasm_sysroot()
    find_path(json_header_path "nlohmann/json.hpp" HINTS ${JSON_INCLUDE_DIR})
    restore_wasm_sysroot()
    set(JSON_INCLUDE_DIR ${json_header_path})

    if(json_header_path)
        message(STATUS "JSON for Modern C++ header file found in ${JSON_INCLUDE_DIR}")
    else()
        message(FATAL_ERROR "Unable to find JSON for Modern C++ header file, aborting")
    endif()

    add_definitions(-DWITH_GLTF)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_GLTF)
endif()

# Add USD support to serializers 
if(USD_SUPPORT)
    find_package(openusd REQUIRED CONFIG)
    UNIFY_ENVVARS_AND_CACHE(USD_INCLUDE_DIR)
    UNIFY_ENVVARS_AND_CACHE(USD_LIBRARY_DIR)

    if("${USD_INCLUDE_DIR}" STREQUAL "")
        find_path(USD_INCLUDE_DIR pxr.h
            PATHS
                /usr/include/pxr
                /usr/local/include/pxr
            REQUIRED
        )
        if(USD_INCLUDE_DIR)
            message(STATUS "Found USD include files in: ${USD_INCLUDE_DIR}")
        else()
            message(FATAL_ERROR "Unable to find USD include directory, specify USD_INCLUDE_DIR manually.")
        endif()
    else()
        set(USD_INCLUDE_DIR ${USD_INCLUDE_DIR} CACHE FILEPATH "USD header files")
        message(STATUS "Looking for USD include files in: ${USD_INCLUDE_DIR}")
    endif()

    set(USD_LIBRARIES
            usd_usd 
            usd_usdGeom
            usd_usdShade 
            usd_usdLux 
            usd_vt 
            usd_sdf 
            usd_tf 
            usd_gf
        )

    find_library(USD_LIBRARY
        NAMES ${USD_LIBRARIES}
        PATHS ${USD_LIBRARY_DIR})
    if(USD_LIBRARY)
        message(STATUS "USD libraries ${USD_LIBRARIES} found in: ${USD_LIBRARY_DIR}")
        link_directories(${USD_LIBRARY_DIR})
    else()
        message(FATAL_ERROR "Unable to find USD libraries in: ${USD_LIBRARY_DIR}")
    endif()

    add_definitions(-DWITH_USD)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_USD)
endif(USD_SUPPORT)

# Find Boost: On win32 the (hardcoded) default is to use static libraries and
# runtime, when doing running conda-build we pick what conda prepared for us.
if(WIN32 AND("$ENV{CONDA_BUILD}" STREQUAL ""))
    set(Boost_USE_STATIC_LIBS ON)
    set(Boost_USE_STATIC_RUNTIME OFF)
    set(Boost_USE_MULTITHREADED ON)

    # Disable Boost's autolinking as the libraries to be linked to are supplied
    # already by CMake, and wrong libraries would be asked for when code is
    # compiled with a toolset different from default.
    if(MSVC)
        add_definitions(-DBOOST_ALL_NO_LIB)

        # Necessary for boost version >= 1.67
        set(BCRYPT_LIBRARIES "bcrypt.lib")
    endif()
else()
    # Disable Boost's autolinking as the libraries to be linked to are supplied
    # already by CMake, and it's going to conflict if there are multiple, as is
    # the case in conda-forge's libboost feedstock.
    add_definitions(-DBOOST_ALL_NO_LIB)

    if(WIN32)
        # Necessary for boost version >= 1.67
        set(BCRYPT_LIBRARIES "bcrypt.lib")
    endif()
endif()

if(WASM_BUILD)
    set(BOOST_COMPONENTS)
else()
    # @todo review this, shouldn't this be all possible header-only now?
    # ... or rewritten using C++17 features?
    set(BOOST_COMPONENTS system program_options regex thread date_time)
endif()

if(USE_MMAP)
    if(MSVC)
        # filesystem is necessary for the utf-16 wpath
        set(BOOST_COMPONENTS ${BOOST_COMPONENTS} iostreams filesystem)
    else()
        set(BOOST_COMPONENTS ${BOOST_COMPONENTS} iostreams)
    endif()

    add_definitions(-DUSE_MMAP)
endif()

clear_wasm_sysroot()
find_package(Boost REQUIRED COMPONENTS ${BOOST_COMPONENTS})
restore_wasm_sysroot()
message(STATUS "Boost include files found in ${Boost_INCLUDE_DIRS}")
message(STATUS "Boost libraries found in ${Boost_LIBRARY_DIRS}")

if(BUILD_IFCGEOM)
    find_package(Eigen3 REQUIRED CONFIG)
    
    # Open CASCADE
    if(WITH_OPENCASCADE)
        find_package(OpenCASCADE CONFIG)
        if(OpenCASCADE_FOUND)
            message(STATUS "Open CASCADE found in ${OpenCASCADE_DIR}")
        else()
            if("${OCC_INCLUDE_DIR}" STREQUAL "")
                clear_wasm_sysroot()
                find_path(OCC_INCLUDE_DIR Standard_Version.hxx
                PATHS
                    /usr/include/occt
                    /usr/include/oce
                    /usr/include/opencascade
                REQUIRED
                )
                restore_wasm_sysroot()

                if(OCC_INCLUDE_DIR)
                    message(STATUS "Found Open CASCADE include files in: ${OCC_INCLUDE_DIR}")
                else()
                    message(FATAL_ERROR "Unable to find Open CASCADE include directory, specify OCC_INCLUDE_DIR manually.")
                endif()
            else()
                set(OCC_INCLUDE_DIR ${OCC_INCLUDE_DIR} CACHE FILEPATH "Open CASCADE header files")
                message(STATUS "Looking for Open CASCADE include files in: ${OCC_INCLUDE_DIR}")
            endif()
        endif()
        message(STATUS "OCC_INCLUDE_DIR: ${OCC_INCLUDE_DIR}")
        if(OCC_INCLUDE_DIR)
            file(STRINGS ${OCC_INCLUDE_DIR}/Standard_Version.hxx OCC_MAJOR
                REGEX "#define OCC_VERSION_MAJOR.*"
            )
            string(REGEX MATCH "[0-9]+" OCC_MAJOR ${OCC_MAJOR})
            file(STRINGS ${OCC_INCLUDE_DIR}/Standard_Version.hxx OCC_MINOR
            REGEX "#define OCC_VERSION_MINOR.*"
            )
            string(REGEX MATCH "[0-9]+" OCC_MINOR ${OCC_MINOR})
            file(STRINGS ${OCC_INCLUDE_DIR}/Standard_Version.hxx OCC_MAINT
            REGEX "#define OCC_VERSION_MAINTENANCE.*"
            )
            string(REGEX MATCH "[0-9]+" OCC_MAINT ${OCC_MAINT})
            set(OCC_VERSION_STRING "${OCC_MAJOR}.${OCC_MINOR}.${OCC_MAINT}")
        endif(OCC_INCLUDE_DIR)

        set(OPENCASCADE_LIBRARY_NAMES
            TKernel TKMath TKBRep TKGeomBase TKGeomAlgo TKG3d TKG2d TKShHealing TKTopAlgo TKMesh TKPrim TKBool TKBO
            TKFillet TKXSBase TKOffset TKHLR 

            # @todo investigate the exact conditions when this is necessary
            TKBin
            # For OCC 7.8.0 and later
            TKDESTEP TKDEIGES
        )

        message(STATUS "OPENCASCADE_LIBRARY_NAMES: ${OPENCASCADE_LIBRARY_NAMES}")
        message(STATUS "OCC_LIBRARY_DIR: ${OCC_LIBRARY_DIR}")
        if("${OCC_LIBRARY_DIR}" STREQUAL "")
            find_library(OCC_LIBRARY TKernel
                PATHS
                    /usr/lib
                REQUIRED
            )

            if(OCC_LIBRARY)
                GET_FILENAME_COMPONENT(OCC_LIBRARY_DIR ${OCC_LIBRARY} PATH)
                message(STATUS "Found Open CASCADE library files in: ${OCC_LIBRARY_DIR}")
            else()
                message(FATAL_ERROR "Unable find Open CASCADE library directory, specify OCC_LIBRARY_DIR manually.")
            endif()
        else()
            set(OCC_LIBRARY_DIR ${OCC_LIBRARY_DIR} CACHE FILEPATH "Open CASCADE library files")
            message(STATUS "Looking for Open CASCADE library files in: ${OCC_LIBRARY_DIR}")
        endif()

        if(NOT OpenCASCADE_FOUND)
            clear_wasm_sysroot()
            find_library(libTKernel NAMES TKernel TKerneld PATHS ${OCC_LIBRARY_DIR} NO_DEFAULT_PATH)
            restore_wasm_sysroot()

            if(libTKernel)
                message(STATUS "Required Open Cascade Library files found")
            else()
                message(FATAL_ERROR "Unable to find Open Cascade library files, aborting")
            endif()

            # Use the found libTKernel as a template for all other OCC libraries
            # TODO Extract this into macro/function
            foreach(lib ${OPENCASCADE_LIBRARY_NAMES})
                # Make sure we'll handle the Windows/MSVC debug postfix convention too.
                string(REPLACE TKerneld "${lib}" lib_path "${libTKernel}")
                string(REPLACE TKernel "${lib}" lib_path "${lib_path}")
                list(APPEND OPENCASCADE_LIBRARIES "${lib_path}")
            endforeach()

            if(MSVC)
                add_definitions(-DHAVE_NO_DLL)
            endif()

            if(WIN32)
                # OCC might require linking to Winsock depending on the version and build configuration
                list(APPEND OPENCASCADE_LIBRARIES ws2_32.lib)
            endif()

            # Make sure cross-referenced symbols between static OCC libraries get
            # resolved. Also add thread and rt libraries.
            get_filename_component(libTKernelExt ${libTKernel} EXT)
            if("${libTKernelExt}" STREQUAL ".a")
                set(OCCT_STATIC ON)
            endif()
        else()
            set(OPENCASCADE_LIBRARIES ${OPENCASCADE_LIBRARY_NAMES})
        endif()

        if(OCCT_STATIC)
            find_package(Threads)
            
            if(WASM_BUILD)
                set(OPENCASCADE_LIBRARIES ${OPENCASCADE_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
            else()
                set(OPENCASCADE_LIBRARIES -Wl,--start-group ${OPENCASCADE_LIBRARIES} -Wl,--end-group ${CMAKE_THREAD_LIBS_INIT})
            endif()
        
            if(NOT APPLE AND NOT WIN32)
                set(OPENCASCADE_LIBRARIES ${OPENCASCADE_LIBRARIES} "rt")
            endif()
            if(NOT WIN32)
                set(OPENCASCADE_LIBRARIES ${OPENCASCADE_LIBRARIES} "dl")
            endif()
        endif()
    endif(WITH_OPENCASCADE)
endif(BUILD_IFCGEOM)

if(COLLADA_SUPPORT)
    # Find OpenCOLLADA
    if("${OPENCOLLADA_INCLUDE_DIR}" STREQUAL "")
        message(STATUS "No OpenCOLLADA include directory specified")
        set(OPENCOLLADA_INCLUDE_DIR "/usr/include/opencollada" CACHE FILEPATH "OpenCOLLADA header files")
    else()
        set(OPENCOLLADA_INCLUDE_DIR "${OPENCOLLADA_INCLUDE_DIR}" CACHE FILEPATH "OpenCOLLADA header files")
    endif()

    if("${OPENCOLLADA_LIBRARY_DIR}" STREQUAL "")
        message(STATUS "No OpenCOLLADA library directory specified")
        find_library(OPENCOLLADA_FRAMEWORK_LIB NAMES OpenCOLLADAFramework
            PATHS /usr/lib64/opencollada /usr/lib/opencollada /usr/lib64 /usr/lib /usr/local/lib64 /usr/local/lib)
        get_filename_component(OPENCOLLADA_LIBRARY_DIR ${OPENCOLLADA_FRAMEWORK_LIB} PATH)
    endif()

    find_library(OpenCOLLADAFramework NAMES OpenCOLLADAFramework OpenCOLLADAFrameworkd PATHS ${OPENCOLLADA_LIBRARY_DIR} NO_DEFAULT_PATH)

    if(OpenCOLLADAFramework)
        message(STATUS "OpenCOLLADA library files found")
    else()
        message(FATAL_ERROR "COLLADA_SUPPORT enabled, but unable to find OpenCOLLADA libraries. "
            "Disable COLLADA_SUPPORT or fix OpenCOLLADA paths to proceed.")
    endif()

    set(OPENCOLLADA_LIBRARY_DIR "${OPENCOLLADA_LIBRARY_DIR}" CACHE FILEPATH "OpenCOLLADA library files")

    set(OPENCOLLADA_INCLUDE_DIRS "${OPENCOLLADA_INCLUDE_DIR}/COLLADABaseUtils" "${OPENCOLLADA_INCLUDE_DIR}/COLLADAStreamWriter")

    find_file(COLLADASWStreamWriter_h "COLLADASWStreamWriter.h" ${OPENCOLLADA_INCLUDE_DIRS})

    if(COLLADASWStreamWriter_h)
        message(STATUS "OpenCOLLADA header files found")
        add_definitions(-DWITH_OPENCOLLADA)
        set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_OPENCOLLADA)

        set(OPENCOLLADA_LIBRARY_NAMES
            GeneratedSaxParser MathMLSolver OpenCOLLADABaseUtils OpenCOLLADAFramework OpenCOLLADASaxFrameworkLoader
            OpenCOLLADAStreamWriter UTF buffer ftoa
        )

        # Use the found OpenCOLLADAFramework as a template for all other OpenCOLLADA libraries
        foreach(lib ${OPENCOLLADA_LIBRARY_NAMES})
            # Make sure we'll handle the Windows/MSVC debug postfix convention too.
            string(REPLACE OpenCOLLADAFrameworkd "${lib}" lib_path "${OpenCOLLADAFramework}")
            string(REPLACE OpenCOLLADAFramework "${lib}" lib_path "${lib_path}")
            list(APPEND OPENCOLLADA_LIBRARIES "${lib_path}")
        endforeach()

        if("${PCRE_LIBRARY_DIR}" STREQUAL "")
            if(WIN32)
                find_library(pcre_library NAMES pcre pcred PATHS ${OPENCOLLADA_LIBRARY_DIR} NO_DEFAULT_PATH)
            else()
                find_library(pcre_library NAMES pcre PATHS ${OPENCOLLADA_LIBRARY_DIR})
            endif()

            get_filename_component(PCRE_LIBRARY_DIR ${pcre_library} PATH)
        else()
            find_library(pcre_library NAMES pcre pcred PATHS ${PCRE_LIBRARY_DIR} NO_DEFAULT_PATH)
        endif()

        if(pcre_library)
            set(OPENCOLLADA_LIBRARY_DIR ${OPENCOLLADA_LIBRARY_DIR} ${PCRE_LIBRARY_DIR})

            if(MSVC)
                # Add release lib regardless whether release or debug found. Debug version will be appended below.
                list(APPEND OPENCOLLADA_LIBRARIES "${PCRE_LIBRARY_DIR}/pcre.lib")
            else()
                list(APPEND OPENCOLLADA_LIBRARIES "${pcre_library}")
            endif()
        else()
            message(FATAL_ERROR "COLLADA_SUPPORT enabled, but unable to find PCRE. "
                "Disable COLLADA_SUPPORT or fix PCRE_LIBRARY_DIR path to proceed.")
        endif()
    else()
        message(FATAL_ERROR "COLLADA_SUPPORT enabled, but unable to find OpenCOLLADA headers. "
            "Disable COLLADA_SUPPORT or fix OpenCOLLADA paths to proceed.")
    endif()
endif(COLLADA_SUPPORT)

if(HDF5_SUPPORT)
    find_package(HDF5 REQUIRED)
    if("${HDF5_INCLUDE_DIR}" STREQUAL "")
        message(STATUS "No HDF5 include directory specified")
    else()
        set(HDF5_INCLUDE_DIR "${HDF5_INCLUDE_DIR}" CACHE FILEPATH "HDF5 header files")
    endif()

    if("${HDF5_LIBRARY_DIR}" STREQUAL "")
        message(STATUS "No HDF5 library directory specified")
    else()
        set(HDF5_LIBRARY_DIR "${HDF5_LIBRARY_DIR}" CACHE FILEPATH "HDF5 library files")
    endif()

    if(HDF5_LIBRARY_DIR)
        # result of the HDF5 ctest package
        # Find zlib using cmake find_library. How should this be implemented?
        # FIND_LIBRARY(NAMES z libz libz_debug PATHS ... NO_DEFAULT_PATH)
        if("$ENV{CONDA_BUILD}" STREQUAL "")
            # result of the HDF5 ctest package
            if(WIN32)
                set(zlib_post lib)
                set(lib_ext lib)
            else()
                set(lib_ext a)
            endif()

            if("${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
                set(debug_postfix "_debug")
            endif()

            if(HDF5_FOUND)
                set(HDF5_LIBRARIES "HDF5::HDF5")
            else()
                set(HDF5_LIBRARIES
                    "${HDF5_LIBRARY_DIR}/libhdf5_cpp${debug_postfix}.${lib_ext}"
                    "${HDF5_LIBRARY_DIR}/libhdf5${debug_postfix}.${lib_ext}"
                    "${HDF5_LIBRARY_DIR}/libz${zlib_post}${debug_postfix}.${lib_ext}"
                    "${HDF5_LIBRARY_DIR}/libsz${debug_postfix}.${lib_ext}"
                    "${HDF5_LIBRARY_DIR}/libaec${debug_postfix}.${lib_ext}"
                )
            endif()

        else()
            message(STATUS "Packaging hdf5 and zlib for conda distribution")

            if(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
                # macOS
                set(zlib_post libz)
                set(lib_ext dylib)
                set(HDF5_LIBRARIES
                "${HDF5_LIBRARY_DIR}/libhdf5_cpp.${lib_ext}"
                "${HDF5_LIBRARY_DIR}/libhdf5.${lib_ext}"
                "${HDF5_LIBRARY_DIR}/${zlib_post}.${lib_ext}"
            )
            else()
                # linux and windows
                # Find HDF5 package
                find_package(HDF5 REQUIRED COMPONENTS C CXX)
                # Find ZLIB package
                find_package(ZLIB REQUIRED)
                # Include directories
                include_directories(${HDF5_INCLUDE_DIRS} ${ZLIB_INCLUDE_DIRS})
                # Link libraries
                set(HDF5_LIBRARIES ${HDF5_LIBRARIES} ${ZLIB_LIBRARIES})
                message(STATUS "HDF5 libraries: ${HDF5_LIBRARIES}")
            endif()
        endif()
    endif()

    if(NOT HDF5_LIBRARIES)
        # debian default
        set(HDF5_LIBRARIES
            /usr/lib/x86_64-linux-gnu/hdf5/serial/libhdf5_cpp.so
            /usr/lib/x86_64-linux-gnu/hdf5/serial/libhdf5.so
            /usr/lib/x86_64-linux-gnu/libsz.so
            /usr/lib/x86_64-linux-gnu/libaec.so
            z dl
        )
    endif()

    add_definitions(-DWITH_HDF5)
    set(SWIG_DEFINES ${SWIG_DEFINES} -DWITH_HDF5)
endif(HDF5_SUPPORT)

if(ENABLE_BUILD_OPTIMIZATIONS)
    if(MSVC)
        # NOTE: RelWithDebInfo and Release use O2 (= /Ox /Gl /Gy/ = Og /Oi /Ot /Oy /Ob2 /Gs /GF /Gy) by default,
        # with the exception with RelWithDebInfo has /Ob1 instead. /Ob2 has been observed to improve the performance
        # of IfcConvert significantly.
        # TODO Setting of /GL and /LTCG don't seem to apply for static libraries (IfcGeom, IfcParse)
        # C++
        set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /Ob2 /GL")
        set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELEASE} /Zi")

        # Linker
        # /OPT:REF enables also /OPT:ICF and disables INCREMENTAL
        set(CMAKE_SHARED_LINKER_FLAGS_RELEASE "${CMAKE_SHARED_LINKER_FLAGS_RELEASE} /LTCG /OPT:REF")

        # /OPT:NOICF is recommended when /DEBUG is used (http://msdn.microsoft.com/en-us/library/xe4t6fc1.aspx)
        set(CMAKE_SHARED_LINKER_FLAGS_RELWITHDEBINFO "${CMAKE_SHARED_LINKER_FLAGS_RELEASE} /DEBUG /OPT:NOICF")
        set(CMAKE_EXE_LINKER_FLAGS_RELEASE "${CMAKE_EXE_LINKER_FLAGS_RELEASE} /LTCG /OPT:REF")
        set(CMAKE_EXE_LINKER_FLAGS_RELWITHDEBINFO "${CMAKE_EXE_LINKER_FLAGS_RELEASE} /DEBUG /OPT:NOICF")
    else()
        # GCC-like: Release should use O3 but RelWithDebInfo 02 so enforce 03. Anything other useful that could be added here?
        set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3")
        set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELEASE} -O3")
    endif()
else()
    # @tfk I commented this out as this kind of defeats the purpose of RelWithDebInfo. For the
    # best debugging experience simply use Debug. Note that in MSVC you can selectively toggle
    # optimization on a specific file if you're investigating a specific issue.
    # if(MSVC)
    #     set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELWITHDEBINFO} /Od")
    # endif()
endif(ENABLE_BUILD_OPTIMIZATIONS)

if(MSVC)
    # warning due to virtual inheritance
    add_definitions(-wd4250)
    # warning due to select definitions in the schema being redundant
    add_definitions(-wd4584)

    # didn't work well on ifcopenbot, @todo make configurable
    # add_definitions(/MP)

    # Enable solution folders (free VS versions prior to 2012 don't support solution folders)
    if(MSVC_VERSION GREATER 1600)
        set_property(GLOBAL PROPERTY USE_FOLDERS ON)
    endif()

    if(USE_VLD)
        add_definitions(-DUSE_VLD)
    endif()

    # Enforce Unicode for CRT and Win32 API calls
    add_definitions(-D_UNICODE -DUNICODE)

    # Disable warnings about unsafe C functions; we could use the safe C99 & C11 versions if we have no need for supporting old compilers.
    add_definitions(-D_SCL_SECURE_NO_WARNINGS -D_CRT_SECURE_NO_WARNINGS)
    add_definitions(-bigobj) # required for building the big ifcXXX.objs, https://msdn.microsoft.com/en-us/library/ms173499.aspx

    # Bump up the warning level from the default 3 to 4.
    add_definitions(-W4)

    if(MSVC_VERSION GREATER 1800) # > 2013
        # Disable overeager and false positives causing C4458 ("declaration of 'indentifier' hides class member"), at least for now.
        add_definitions(-wd4458)
    endif()

    # Enforce standards-conformance on VS > 2015, older Boost versions fail to compile with this
    if(MSVC_VERSION GREATER 1900 AND(Boost_MAJOR_VERSION GREATER 1 OR Boost_MINOR_VERSION GREATER 66))
        add_definitions(-permissive-)
    endif()

    # Link against the static VC runtime
    # TODO Make this configurable
    # if("$ENV{CONDA_BUILD}" STREQUAL "")
    #     foreach(flag CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE CMAKE_CXX_FLAGS_MINSIZEREL
    #     CMAKE_CXX_FLAGS_RELWITHDEBINFO CMAKE_C_FLAGS CMAKE_C_FLAGS_DEBUG CMAKE_C_FLAGS_RELEASE
    #     CMAKE_C_FLAGS_MINSIZEREL CMAKE_C_FLAGS_RELWITHDEBINFO)
    #         if(${flag} MATCHES "/MD")
    #             STRING(REGEX REPLACE "/MD" "/MT" ${flag} "${${flag}}")
    #         endif()
    #         if(${flag} MATCHES "/MDd")
    #             STRING(REGEX REPLACE "/MDd" "/MTd" ${flag} "${${flag}}")
    #         endif()
    #     endforeach()
    # endif()

	add_definitions(-D_ENABLE_EXTENDED_ALIGNED_STORAGE)
	# See #5158.
	if(CMAKE_CXX_COMPILER_VERSION VERSION_GREATER_EQUAL 19.40)
		add_definitions(-D_DISABLE_CONSTEXPR_MUTEX_CONSTRUCTOR)
	endif()
else()
    add_definitions(-Wall -Wextra)

    if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        add_definitions(-Wno-tautological-constant-out-of-range-compare)
    else()
        add_definitions(-Wno-maybe-uninitialized)
    endif()

    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU" AND(CMAKE_CXX_COMPILER_VERSION VERSION_GREATER 9.0 OR CMAKE_CXX_COMPILER_VERSION VERSION_EQUAL 9.0))
        # OpenCascade spews a lot of deprecated-copy warnings
        add_definitions(-Wno-deprecated-copy)
    endif()

    # -fPIC is not relevant on Windows and creates pointless warnings
    if(UNIX)
        add_definitions(-fPIC)
    endif()
endif(MSVC)

include_directories(${INCLUDE_DIRECTORIES} ${OCC_INCLUDE_DIR} ${OPENCOLLADA_INCLUDE_DIRS}
	${Boost_INCLUDE_DIRS} ${LIBXML2_INCLUDE_DIR} ${JSON_INCLUDE_DIR} ${HDF5_INCLUDE_DIR}
    ${EIGEN_DIR} ${CGAL_INCLUDE_DIR} ${GMP_INCLUDE_DIR} ${MPFR_INCLUDE_DIR} ${USD_INCLUDE_DIR}
    ${TBB_INCLUDE_DIR}
)

if(NOT SCHEMA_VERSIONS)
    if(WASM_BUILD)
        # super arbitrarily try to keep size down at least a little bit
        set(SCHEMA_VERSIONS "2x3" "4")
    else()
        set(SCHEMA_VERSIONS "2x3" "4" "4x1" "4x2" "4x3" "4x3_tc1" "4x3_add1" "4x3_add2")
    endif()
endif()

message(STATUS "IFC SCHEMA_VERSIONS that will be used for the build: ${SCHEMA_VERSIONS}.")

foreach(schema ${SCHEMA_VERSIONS})
    add_definitions(-DHAS_SCHEMA_${schema})
endforeach()

string(REPLACE ";" ")(" schema_version_seq "(${SCHEMA_VERSIONS})")
add_definitions(-DSCHEMA_SEQ=${schema_version_seq})

if(COMPILE_SCHEMA)
    # @todo, this appears to be untested at the moment
    find_package(PythonInterp)

    if(NOT PYTHONINTERP_FOUND)
        message(FATAL_ERROR "A Python interpreter is necessary when COMPILE_SCHEMA is enabled. Disable COMPILE_SCHEMA or fix Python paths to proceed.")
    endif()

    set(IFC_RELEASE_NOT_USED ${SCHEMA_VERSIONS})

    # Install pyparsing if necessary
    execute_process(COMMAND ${PYTHON_EXECUTABLE} -m pip freeze OUTPUT_VARIABLE PYTHON_PACKAGE_LIST)

    if("${PYTHON_PACKAGE_LIST}" STREQUAL "")
        execute_process(COMMAND pip freeze OUTPUT_VARIABLE PYTHON_PACKAGE_LIST)

        if("${PYTHON_PACKAGE_LIST}" STREQUAL "")
            message(WARNING "Failed to find pip. Pip is required to automatically install pyparsing")
        endif()
    endif()

    string(FIND "${PYTHON_PACKAGE_LIST}" pyparsing PYPARSING_FOUND)

    if("${PYPARSING_FOUND}" STREQUAL "-1")
        message(STATUS "Installing pyparsing")
        execute_process(COMMAND ${PYTHON_EXECUTABLE} -m pip "install" --user pyparsing RESULT_VARIABLE SUCCESS)

        if(NOT "${SUCCESS}" STREQUAL "0")
            execute_process(COMMAND pip "install" --user pyparsing RESULT_VARIABLE SUCCESS)

            if(NOT "${SUCCESS}" STREQUAL "0")
                message(WARNING "Failed to automatically install pyparsing. Please install manually")
            endif()
        endif()
    else()
        message(STATUS "Python interpreter with pyparsing found")
    endif()

    # Bootstrap the parser
    message(STATUS "Compiling schema, this will take a while...")
    execute_process(COMMAND ${PYTHON_EXECUTABLE} bootstrap.py express.bnf
        WORKING_DIRECTORY ../src/ifcexpressparser
        OUTPUT_FILE express_parser.py
        RESULT_VARIABLE SUCCESS)

    if(NOT "${SUCCESS}" STREQUAL "0")
        message(FATAL_ERROR "Failed to bootstrap parser. Make sure pyparsing is installed")
    endif()

    # Generate code
    execute_process(COMMAND ${PYTHON_EXECUTABLE} ../ifcexpressparser/express_parser.py ../../${COMPILE_SCHEMA}
        WORKING_DIRECTORY ../src/ifcparse
        OUTPUT_VARIABLE COMPILED_SCHEMA_NAME)

    # Prevent the schema that had just been compiled from being excluded
    foreach(schema ${SCHEMA_VERSIONS})
        if("${COMPILED_SCHEMA_NAME}" STREQUAL "${schema}")
            list(REMOVE_ITEM IFC_RELEASE_NOT_USED "${schema}")
        endif()
    endforeach()
endif(COMPILE_SCHEMA)

# Boost >= 1.58 requires BOOST_OPTIONAL_USE_OLD_DEFINITION_OF_NONE to build on some Linux distros.
if(NOT Boost_VERSION LESS 105800)
    add_definitions(-DBOOST_OPTIONAL_USE_OLD_DEFINITION_OF_NONE)
endif()

set(IFCOPENSHELL_LIBRARIES IfcParse)

if(BUILD_IFCGEOM)
	foreach(schema ${SCHEMA_VERSIONS})
		set(IFCGEOM_SCHEMA_LIBRARIES ${IFCGEOM_SCHEMA_LIBRARIES} geometry_mapping_ifc${schema})
	endforeach()
	if(WASM_BUILD)
	    set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} IfcGeom ${IFCGEOM_SCHEMA_LIBRARIES})
	else()
	    set(IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES} IfcGeom ${IFCGEOM_SCHEMA_LIBRARIES} IfcGeom ${IFCGEOM_SCHEMA_LIBRARIES})	
	endif()
endif()

set_property(GLOBAL PROPERTY IFCOPENSHELL_LIBRARIES ${IFCOPENSHELL_LIBRARIES})

# IfcParse
add_subdirectory(src/ifcparse)

if(BUILD_IFCGEOM)
    add_subdirectory(src/ifcgeom)
endif(BUILD_IFCGEOM)

if(BUILD_CONVERT OR BUILD_IFCPYTHON)
    # Serializers
    add_subdirectory(src/serializers)
endif(BUILD_CONVERT OR BUILD_IFCPYTHON)

if(BUILD_CONVERT)
    add_subdirectory(src/ifcconvert)
endif(BUILD_CONVERT)

# IfcGeomServer
if(BUILD_GEOMSERVER)
    add_subdirectory(src/ifcgeomserver)
endif(BUILD_GEOMSERVER)

if(ADD_COMMIT_SHA)
    find_package(Git)

    if(GIT_FOUND)
        if (VERSION_OVERRIDE)
            set (git_branch ${RELEASE_VERSION})
        else()
            message("git found: ${GIT_EXECUTABLE} with version ${GIT_VERSION_STRING}")
            execute_process(
                COMMAND ${GIT_EXECUTABLE} branch -a --contains HEAD
                WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                OUTPUT_VARIABLE git_branches
                OUTPUT_STRIP_TRAILING_WHITESPACE
            )
            string(REPLACE "\n" ";" git_branch_list "${git_branches}")

            foreach(git_branch_candidate IN ITEMS ${git_branch_list})
		        string(REPLACE "*" "" git_branch_candidate_temp "${git_branch_candidate}")
		        string(STRIP "${git_branch_candidate_temp}" git_branch_candidate_2)
                if(NOT git_branch_candidate_2 MATCHES "^HEAD$")
                    string(REPLACE "/" ";" git_branch_candidate_2_list "${git_branch_candidate_2}")
                    list(GET git_branch_candidate_2_list -1 git_branch)
                endif()
            endforeach()
        endif()

        execute_process(
            COMMAND ${GIT_EXECUTABLE} rev-parse --short HEAD
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            OUTPUT_VARIABLE git_sha
            OUTPUT_STRIP_TRAILING_WHITESPACE
        )

        message(STATUS "IfcOpenShell branch: \"${git_branch}\"")
        message(STATUS "IfcOpenShell commit: \"${git_sha}\"")

        if ("${git_branch}" STREQUAL "" OR "${git_sha}" STREQUAL "")
            message(FATAL_ERROR "Unable to determine commit sha and/or branch")
        endif()

        add_definitions(-DIFCOPENSHELL_BRANCH=${git_branch})
        add_definitions(-DIFCOPENSHELL_COMMIT=${git_sha})
    endif()
endif(ADD_COMMIT_SHA)

if(MSVC)
    # @todo still needs to be understood better, but the cgal and cgal-simple kernel cause multiply defined boost lambda placeholders _1 ... _3
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} /FORCE:MULTIPLE")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} /FORCE:MULTIPLE")
    set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} /FORCE:MULTIPLE")
endif()

if(BUILD_IFCPYTHON)
    add_subdirectory(src/ifcwrap ifcwrap)
endif()

if(BUILD_EXAMPLES)
    add_subdirectory(src/examples examples)
endif()

if(BUILD_IFCMAX)
    add_subdirectory(src/ifcmax ifcmax)
endif()

if(WITH_CGAL AND BUILD_IFCPYTHON)
    add_subdirectory(src/svgfill svgfill)        
endif()

if(BUILD_QTVIEWER)
    add_subdirectory(src/qtviewer qtviewer)
endif()

