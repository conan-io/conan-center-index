cmake_minimum_required(VERSION 3.4)
project(r8brain-free-src LANGUAGES C CXX)

add_library(r8brain)

target_sources(r8brain PRIVATE ${R8BRAIN_SRC_DIR}/r8bbase.cpp)
if(R8BRAIN_WITH_PFFFT)
  target_compile_definitions(r8brain PUBLIC R8B_PFFFT)
  find_package(pffft REQUIRED CONFIG)
  target_link_libraries(r8brain pffft::pffft)
endif()
if(R8BRAIN_WITH_PFFFT_DOUBLE)
  target_compile_definitions(r8brain PUBLIC R8B_PFFFT_DOUBLE)
  target_sources(r8brain PRIVATE ${R8BRAIN_SRC_DIR}/pffft_double/pffft_double.c)
endif()

set_target_properties(r8brain PROPERTIES
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)

include(GNUInstallDirs)

install(
  TARGETS r8brain
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

file(GLOB PUBLIC_HEADERS ${R8BRAIN_SRC_DIR}/*.h ${R8BRAIN_SRC_DIR}/*.inc)
install(FILES ${PUBLIC_HEADERS} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
if(R8BRAIN_WITH_PFFFT_DOUBLE)
  list(APPEND PFFFT_DOUBLE_HEADERS 
    ${R8BRAIN_SRC_DIR}/pffft_double/pffft_double.h
  )
  install(FILES ${PFFFT_DOUBLE_HEADERS} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/pffft_double)

  list(APPEND PFFFT_DOUBLE_SIMD_HEADERS 
    ${R8BRAIN_SRC_DIR}/pffft_double/simd/pf_avx_double.h
    ${R8BRAIN_SRC_DIR}/pffft_double/simd/pf_double.h
    ${R8BRAIN_SRC_DIR}/pffft_double/simd/pf_neon_double.h
    ${R8BRAIN_SRC_DIR}/pffft_double/simd/pf_neon_double_from_avx.h
    ${R8BRAIN_SRC_DIR}/pffft_double/simd/pf_scalar_double.h
    ${R8BRAIN_SRC_DIR}/pffft_double/simd/pf_sse2_double.h 
  )
  install(FILES ${PFFFT_DOUBLE_SIMD_HEADERS} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/pffft_double/simd)
endif()
