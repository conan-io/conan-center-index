cmake_minimum_required(VERSION 3.8)
project(geotrans LANGUAGES CXX)
####
# Conan
####
include(${CMAKE_SOURCE_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

####
# Directories
####

set(SRC_SUBFOLDER "${CMAKE_SOURCE_DIR}/source_subfolder")
set(DTCCDIR "${SRC_SUBFOLDER}/CCS/src/dtcc/CoordinateSystems")
set(CCSERVICEDIR "${SRC_SUBFOLDER}/CCS/src")
set(SRCDIR "${SRC_SUBFOLDER}/GEOTRANS3/java_gui/geotrans3/jni")

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

set(PUBLIC_HEADERS ${DTTC_HEADERS} ${CCS_HEADERS})

####
# Dependencies
####

find_package(Threads REQUIRED)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
# Create libMSPdtcc
add_library(MSPdtcc ${DTCCSRCS} ${CCSERVICESRCS})
target_compile_features(MSPdtcc PUBLIC cxx_std_11)
if (WIN32)
    add_compile_definitions(MSPdtcc PRIVATE LITTLE_ENDIAN=1)
endif(WIN32)
target_include_directories(MSPdtcc PUBLIC include ${DTTCINCS} ${INCS})
set_target_properties(MSPdtcc PROPERTIES PUBLIC_HEADER "${PUBLIC_HEADERS}")
target_link_libraries(MSPdtcc PRIVATE Threads::Threads)

# Create libMSPCoordinateConversionService
add_library(MSPCoordinateConversionService ${CCSSRCS} ${CCSERVICESRCS})
target_compile_features(MSPCoordinateConversionService PUBLIC cxx_std_11)
target_include_directories(MSPCoordinateConversionService PUBLIC include ${DTTCINCS} ${INCS})
set_target_properties(MSPCoordinateConversionService  PROPERTIES PUBLIC_HEADER "${PUBLIC_HEADERS}")
target_link_libraries(MSPCoordinateConversionService PUBLIC MSPdtcc)

include(GNUInstallDirs)
install(TARGETS MSPdtcc MSPCoordinateConversionService
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
install(DIRECTORY "${SRC_SUBFOLDER}/data/" DESTINATION res)
