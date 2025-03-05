# https://github.com/osmcode/libosmium/blob/v2.20.0/cmake/FindOsmium.cmake

set(OSMIUM_FOUND TRUE)
set(OSMIUM_INCLUDE_DIRS ${${CMAKE_FIND_PACKAGE_NAME}_INCLUDE_DIR})
set(OSMIUM_LIBRARIES ${${CMAKE_FIND_PACKAGE_NAME}_LIBRARIES})
set(OSMIUM_VERSION ${${CMAKE_FIND_PACKAGE_NAME}_VERSION})

#    OSMIUM_XML_LIBRARIES - Libraries needed for XML I/O.
set(OSMIUM_XML_LIBRARIES libosmium::xml)
#    OSMIUM_PBF_LIBRARIES - Libraries needed for PBF I/O.
set(OSMIUM_PBF_LIBRARIES libosmium::pbf)
#    OSMIUM_IO_LIBRARIES  - Libraries needed for XML or PBF I/O.
set(OSMIUM_IO_LIBRARIES libosmium::io)
