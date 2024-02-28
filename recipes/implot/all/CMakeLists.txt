cmake_minimum_required(VERSION 3.4)
project(implot LANGUAGES CXX)

file(GLOB HEADER_FILES ${IMPLOT_SRC_DIR}/*.h)

add_library(${PROJECT_NAME}
    ${IMPLOT_SRC_DIR}/implot.cpp
    ${IMPLOT_SRC_DIR}/implot_items.cpp
    ${IMPLOT_SRC_DIR}/implot_demo.cpp
)
target_include_directories(${PROJECT_NAME} PRIVATE ${IMPLOT_SRC_DIR})

find_package(imgui CONFIG REQUIRED)

target_link_libraries(${PROJECT_NAME} PUBLIC imgui::imgui)

target_compile_definitions(${PROJECT_NAME} PRIVATE IMGUI_DEFINE_MATH_OPERATORS)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
set_target_properties(${PROJECT_NAME} PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)

include(GNUInstallDirs)

install(TARGETS ${PROJECT_NAME}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(FILES ${HEADER_FILES}
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
