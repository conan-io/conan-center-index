cmake_minimum_required(VERSION 3.4)
project(svm C CXX)

include(GNUInstallDirs)

add_library(svm ${LIBSVM_SRC_DIR}/svm.cpp)
set_property(TARGET svm PROPERTY WINDOWS_EXPORT_ALL_SYMBOLS ON)
set_target_properties(svm PROPERTIES PUBLIC_HEADER ${LIBSVM_SRC_DIR}/svm.h)

add_executable(svm-predict ${LIBSVM_SRC_DIR}/svm-predict.c)
target_link_libraries(svm-predict svm)

add_executable(svm-train ${LIBSVM_SRC_DIR}/svm-train.c)
target_link_libraries(svm-train svm)

add_executable(svm-scale ${LIBSVM_SRC_DIR}/svm-scale.c)

install(TARGETS svm
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/svm
        )

install(TARGETS svm-predict svm-train svm-scale
        DESTINATION ${CMAKE_INSTALL_BINDIR}
        )
