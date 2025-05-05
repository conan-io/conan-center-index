cmake_minimum_required(VERSION 3.4)
project(noise LANGUAGES CXX)

set(NOISE_SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src/noise/src)

file(GLOB NOISE_SRC_FILES
    ${NOISE_SRC_DIR}/*.cpp
    ${NOISE_SRC_DIR}/model/*.cpp
    ${NOISE_SRC_DIR}/module/*.cpp
)

add_library(${PROJECT_NAME} ${NOISE_SRC_FILES})
set_target_properties(${PROJECT_NAME} PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)

find_library(M_LIB m)
if(M_LIB)
    target_link_libraries(${PROJECT_NAME} PUBLIC ${M_LIB})
endif()

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

foreach(SRC_SUBDIR "." "model" "module")
    file(GLOB NOISE_HDR_FILES ${NOISE_SRC_DIR}/${SRC_SUBDIR}/*.h)
    install(FILES ${NOISE_HDR_FILES} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/noise/${SRC_SUBDIR})
endforeach()
