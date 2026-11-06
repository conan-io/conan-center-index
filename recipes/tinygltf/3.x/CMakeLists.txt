cmake_minimum_required(VERSION 3.15)
project(tinygltf LANGUAGES C)

include(GNUInstallDirs)

add_library(tinygltf ${TINYGLTF_SRC_DIR}/tiny_gltf_v3.c)
target_include_directories(tinygltf PRIVATE ${TINYGLTF_SRC_DIR})
set_target_properties(tinygltf PROPERTIES
    C_STANDARD 11
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)
if(TINYGLTF_ENABLE_FS)
    target_compile_definitions(tinygltf PRIVATE TINYGLTF3_ENABLE_FS)
endif()

install(TARGETS tinygltf
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
install(FILES
    ${TINYGLTF_SRC_DIR}/tiny_gltf_v3.h
    ${TINYGLTF_SRC_DIR}/tinygltf_json_c.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
