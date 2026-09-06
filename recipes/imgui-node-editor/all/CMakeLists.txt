cmake_minimum_required(VERSION 3.15)
project(imgui-node-editor CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

set(SOURCE_DIR src)
set(SOURCE_FILES
    ${SOURCE_DIR}/crude_json.cpp
    ${SOURCE_DIR}/imgui_canvas.cpp
    ${SOURCE_DIR}/imgui_node_editor.cpp
    ${SOURCE_DIR}/imgui_node_editor_api.cpp
)
set(HEADER_FILES
    ${SOURCE_DIR}/crude_json.h
    ${SOURCE_DIR}/imgui_bezier_math.h
    ${SOURCE_DIR}/imgui_bezier_math.inl
    ${SOURCE_DIR}/imgui_canvas.h
    ${SOURCE_DIR}/imgui_extra_math.h
    ${SOURCE_DIR}/imgui_extra_math.inl
    ${SOURCE_DIR}/imgui_node_editor.h
    ${SOURCE_DIR}/imgui_node_editor_internal.h
    ${SOURCE_DIR}/imgui_node_editor_internal.inl
)

find_package(imgui CONFIG REQUIRED)

add_library(${PROJECT_NAME} ${SOURCE_FILES})
target_include_directories(${PROJECT_NAME} PRIVATE ${SOURCE_DIR})
target_link_libraries(${PROJECT_NAME} PUBLIC imgui::imgui)

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME})
install(FILES ${HEADER_FILES}
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
        PERMISSIONS OWNER_WRITE OWNER_READ GROUP_READ WORLD_READ)
