cmake_minimum_required(VERSION 3.15)
project(vlfeat C)

if(MSVC)
  # https://github.com/vlfeat/vlfeat/blob/v0.9.21/Makefile.mak#L147-L152
  add_definitions(-D_CRT_SECURE_NO_DEPRECATE)
  add_definitions(-D__LITTLE_ENDIAN__)
  add_compile_options(/Zp8)
endif()

# https://github.com/vlfeat/vlfeat/blob/v0.9.21/Makefile#L154-L158
set(CMAKE_C_STANDARD 99)

# https://github.com/vlfeat/vlfeat/blob/v0.9.21/make/dll.mak#L40
set(CMAKE_C_VISIBILITY_PRESET hidden)

file(GLOB VLFEAT_SOURCES vl/*.c)
file(GLOB VLFEAT_HEADERS vl/*.h)

add_library(vl ${VLFEAT_SOURCES})
if(BUILD_SHARED_LIBS)
  add_definitions(-DVL_BUILD_DLL)
endif()

# https://github.com/vlfeat/vlfeat/blob/v0.9.21/make/dll.mak#L28-L45
if(ENABLE_SSE2)
  add_definitions(-D__SSE2__)
  if(MSVC)
    add_compile_options(/arch:SSE2)
  else()
    add_compile_options(-msse2)
  endif()
else()
  add_definitions(-DVL_DISABLE_SSE2)
endif()

if(ENABLE_AVX)
  add_definitions(-D__AVX__)
  if(MSVC)
    add_compile_options(/arch:AVX)
  else()
    add_compile_options(-mavx)
  endif()
else()
  add_definitions(-DVL_DISABLE_AVX)
endif()

if(ENABLE_THREADS)
  find_package(Threads REQUIRED)
  target_link_libraries(vl PRIVATE Threads::Threads)
else()
  add_definitions(-DVL_DISABLE_THREADS)
endif()

if(ENABLE_OPENMP)
  find_package(OpenMP REQUIRED)
  target_link_libraries(vl PRIVATE OpenMP::OpenMP_C)
endif()

include(GNUInstallDirs)
install(
  TARGETS vl
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES ${VLFEAT_HEADERS} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/vl)
