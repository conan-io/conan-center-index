cmake_minimum_required(VERSION 3.4)
project(bigint LANGUAGES CXX)

include(GNUInstallDirs)

add_library(bigint
    ${BIGINT_SRC_DIR}/BigUnsigned.cc
    ${BIGINT_SRC_DIR}/BigInteger.cc
    ${BIGINT_SRC_DIR}/BigIntegerAlgorithms.cc
    ${BIGINT_SRC_DIR}/BigUnsignedInABase.cc
    ${BIGINT_SRC_DIR}/BigIntegerUtils.cc
)

set(BIGINT_PUBLIC_HEADERS
    ${BIGINT_SRC_DIR}/BigIntegerLibrary.hh
    ${BIGINT_SRC_DIR}/NumberlikeArray.hh
    ${BIGINT_SRC_DIR}/BigUnsigned.hh
    ${BIGINT_SRC_DIR}/BigInteger.hh
    ${BIGINT_SRC_DIR}/BigIntegerAlgorithms.hh
    ${BIGINT_SRC_DIR}/BigUnsignedInABase.hh
    ${BIGINT_SRC_DIR}/BigIntegerUtils.hh
)

set_target_properties(bigint PROPERTIES
    WINDOWS_EXPORT_ALL_SYMBOLS ON
    PUBLIC_HEADER "${BIGINT_PUBLIC_HEADERS}"
)

install(
    TARGETS bigint
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
