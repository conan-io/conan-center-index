cmake_minimum_required(VERSION 3.2)
project(fft LANGUAGES C)

option(FFT_THREADS "use threads" OFF)

set(HEADERS "fft.h;fft2.h;fft3.h;dct.h;${CMAKE_CURRENT_BINARY_DIR}/fft_export.h")

add_library(${PROJECT_NAME} fft_build.c)

set_target_properties(${PROJECT_NAME} PROPERTIES
  PUBLIC_HEADER "${HEADERS}"
  C_VISIBILITY_PRESET hidden)
target_include_directories(${PROJECT_NAME} PRIVATE ${FFT_SRC_DIR} ${CMAKE_CURRENT_BINARY_DIR})

if(FFT_THREADS)
  find_package(Threads REQUIRED)
  if(WIN32)
    target_compile_definitions(${PROJECT_NAME} PRIVATE USE_CDFT_WINTHREADS)
    target_compile_definitions(${PROJECT_NAME} PRIVATE USE_FFT2D_WINTHREADS)
    target_compile_definitions(${PROJECT_NAME} PRIVATE USE_FFT3D_WINTHREADS)
  else()
    target_compile_definitions(${PROJECT_NAME} PRIVATE USE_CDFT_PTHREADS)
    target_compile_definitions(${PROJECT_NAME} PRIVATE USE_FFT2D_PTHREADS)
    target_compile_definitions(${PROJECT_NAME} PRIVATE USE_FFT3D_PTHREADS)
  endif()
  target_compile_definitions(${PROJECT_NAME} PRIVATE "CDFT_THREADS_BEGIN_N=${FFT_THREADS_BEGIN_N}")
  target_compile_definitions(${PROJECT_NAME} PRIVATE "CDFT_4THREADS_BEGIN_N=${FFT_THREADS_BEGIN_N}")
  target_compile_definitions(${PROJECT_NAME} PRIVATE "FFT2D_THREADS_BEGIN_N=${FFT_THREADS_BEGIN_N}")
  target_compile_definitions(${PROJECT_NAME} PRIVATE "FFT2D_MAX_THREADS=${FFT_MAX_THREADS}")
  target_compile_definitions(${PROJECT_NAME} PRIVATE "FFT3D_THREADS_BEGIN_N=${FFT_THREADS_BEGIN_N}")
  target_compile_definitions(${PROJECT_NAME} PRIVATE "FFT3D_MAX_THREADS=${FFT_MAX_THREADS}")

  target_link_libraries(${PROJECT_NAME} PUBLIC Threads::Threads)
endif()

include(GenerateExportHeader)
generate_export_header(${PROJECT_NAME})

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
  PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/fft
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
