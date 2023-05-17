cmake_minimum_required(VERSION 3.4)
project(cgltf C)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(SRC_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cgltf.c
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cgltf_write.c
)
set(HEADER_FILES
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cgltf.h
  ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/cgltf_write.h
)

add_library(${PROJECT_NAME} ${SRC_FILES})
set_property(TARGET ${PROJECT_NAME} PROPERTY C_STANDARD 99)
if(MSVC AND BUILD_SHARED_LIBS)
  set_property(TARGET ${PROJECT_NAME} PROPERTY WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

include(GNUInstallDirs)
install(
  TARGETS ${PROJECT_NAME}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(FILES ${HEADER_FILES} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
