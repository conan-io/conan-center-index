cmake_minimum_required(VERSION 3.15)
project(liblqr LANGUAGES C)

find_package(glib REQUIRED CONFIG)

set(LQR_SRC_SUBDIR ${LQR_SRC_DIR}/lqr)

file(GLOB LQR_SRCS_FILES ${LQR_SRC_SUBDIR}/*.c)

add_library(lqr-1 ${LQR_SRCS_FILES})
target_include_directories(lqr-1 PUBLIC ${LQR_SRC_DIR} ${LQR_SRC_SUBDIR})
target_link_libraries(lqr-1 PUBLIC glib::glib-2.0)
if(WIN32)
    if(BUILD_SHARED_LIBS)
        target_compile_definitions(lqr-1 PRIVATE LQR_EXPORTS)
    else()
        target_compile_definitions(lqr-1 PUBLIC LQR_DISABLE_DECLSPEC)
    endif()
endif()

install(FILES ${LQR_SRC_SUBDIR}/lqr.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/lqr-1)
install(
    FILES
        ${LQR_SRC_SUBDIR}/lqr_base.h
        ${LQR_SRC_SUBDIR}/lqr_carver_bias_pub.h
        ${LQR_SRC_SUBDIR}/lqr_carver_list_pub.h
        ${LQR_SRC_SUBDIR}/lqr_carver_pub.h
        ${LQR_SRC_SUBDIR}/lqr_carver_rigmask_pub.h
        ${LQR_SRC_SUBDIR}/lqr_cursor_pub.h
        ${LQR_SRC_SUBDIR}/lqr_energy_pub.h
        ${LQR_SRC_SUBDIR}/lqr_gradient_pub.h
        ${LQR_SRC_SUBDIR}/lqr_progress_pub.h
        ${LQR_SRC_SUBDIR}/lqr_rwindow_pub.h
        ${LQR_SRC_SUBDIR}/lqr_vmap_list_pub.h
        ${LQR_SRC_SUBDIR}/lqr_vmap_pub.h
    DESTINATION
        ${CMAKE_INSTALL_INCLUDEDIR}/lqr-1/lqr
)
install(
    TARGETS lqr-1
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
