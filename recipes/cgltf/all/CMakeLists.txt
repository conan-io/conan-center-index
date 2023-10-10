cmake_minimum_required(VERSION 3.4)
project(cgltf C)

set(SOURCES_DIR ${CMAKE_CURRENT_LIST_DIR}/src)

set(SRC_FILES
  ${SOURCES_DIR}/cgltf.c
  ${SOURCES_DIR}/cgltf_write.c
)
set(HEADER_FILES
  ${SOURCES_DIR}/cgltf.h
  ${SOURCES_DIR}/cgltf_write.h
)

add_library(${PROJECT_NAME} ${SRC_FILES})
set_property(TARGET ${PROJECT_NAME} PROPERTY C_STANDARD 99)
if(MSVC AND BUILD_SHARED_LIBS)
  set_property(TARGET ${PROJECT_NAME} PROPERTY WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME})
install(FILES ${HEADER_FILES} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
