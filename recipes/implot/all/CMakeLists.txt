cmake_minimum_required(VERSION 3.15)
project(implot LANGUAGES CXX)

file(GLOB HEADER_FILES ${IMPLOT_SRC_DIR}/*.h)

add_library(${PROJECT_NAME}
    ${IMPLOT_SRC_DIR}/implot.cpp
    ${IMPLOT_SRC_DIR}/implot_items.cpp
    # implot_demo.cpp is included so that user can use it to display the main documentation of implot.
    # Note that these functions are not declared by the public headers.
    # https://github.com/conan-io/conan-center-index/pull/20374
    ${IMPLOT_SRC_DIR}/implot_demo.cpp
)
target_include_directories(${PROJECT_NAME} PRIVATE ${IMPLOT_SRC_DIR})

find_package(imgui CONFIG REQUIRED)

target_link_libraries(${PROJECT_NAME} PUBLIC imgui::imgui)

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
