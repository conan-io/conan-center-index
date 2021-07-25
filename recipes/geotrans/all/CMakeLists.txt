cmake_minimum_required(VERSION 3.4)
project(geotrans VERSION 3.8 LANGUAGES CXX)
####
# Conan
####
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

####
# Directories
####

set(DTCCDIR "${CMAKE_CURRENT_SOURCE_DIR}/CCS/src/dtcc/CoordinateSystems")
set(CCSERVICEDIR "${CMAKE_CURRENT_SOURCE_DIR}/CCS/src")
set(SRCDIR "${CMAKE_CURRENT_SOURCE_DIR}/GEOTRANS3/java_gui/geotrans3/jni")

####
# Sources
####
file(GLOB_RECURSE DTCCSRCS "${DTCCDIR}/*.cpp")
set(CCSSRCS "${CCSERVICEDIR}/CoordinateConversion/CoordinateConversionService.cpp")
file(GLOB_RECURSE CCSERVICESRCS "${CCSERVICEDIR}/dtcc/*.cpp")
list(FILTER CCSERVICESRCS EXCLUDE REGEX ".*${DTCCDIR}.*")
set(SRCS "${SRCDIR}/strtoval.cpp" "${SRCDIR}/fiomeths.cpp")

####
# Includes
####

# Construct DTCC includes
file(GLOB_RECURSE DTCC_HEADERS "${DTCCDIR}/*.h")
set(DTTCINCS "")
foreach(file ${DTCC_HEADERS})
    get_filename_component(DIR_PATH ${file} PATH)
    set(DTTCINCS ${DTTCINCS} ${DIR_PATH})
endforeach()
list(REMOVE_DUPLICATES DTTCINCS)

# Construct CCS includes. This is all headers not in DTTCINCS
file(GLOB_RECURSE CCS_HEADERS "${CCSERVICEDIR}/*.h")
set(INCS ${SRCDIR})
foreach(file ${CCS_HEADERS})
    get_filename_component(DIR_PATH ${file} PATH)
    set(INCS ${INCS} ${DIR_PATH})
endforeach()
list(REMOVE_DUPLICATES INCS)
list(FILTER INCS EXCLUDE REGEX ".*${DTCCDIR}.*")


# Create libMSPdtcc
add_library(MSPdtcc ${DTCCSRCS} ${CCSERVICESRCS})
target_compile_features(MSPdtcc PUBLIC cxx_std_11)
target_compile_options(MSPdtcc PRIVATE -pthread -Wno-deprecated)
target_include_directories(MSPdtcc PUBLIC include ${DTTCINCS} ${INCS})

# Create libMSPCoordinateConversionService
add_library(MSPCoordinateConversionService ${CCSSRCS} ${CCSERVICESRCS})
target_compile_features(MSPCoordinateConversionService PUBLIC cxx_std_11)
target_compile_options(MSPCoordinateConversionService PRIVATE -pthread -Wno-deprecated)
target_include_directories(MSPCoordinateConversionService PUBLIC include ${DTTCINCS} ${INCS})
