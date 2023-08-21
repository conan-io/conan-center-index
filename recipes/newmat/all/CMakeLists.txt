cmake_minimum_required(VERSION 3.0)

project(
  "newmat"
  DESCRIPTION
    "The package is intended for scientists and engineers who need to \
    manipulate a variety of types of matrices using standard matrix \
    operations. Emphasis is on the kind of operations needed in statistical \
    calculations such as least squares, linear equation solve and eigenvalues."
  HOMEPAGE_URL "http://www.robertnz.net/nm11.htm"
  LANGUAGES CXX)

option(SETUP_C_SUBSCRIPTS "Activate SETUP_C_SUBSCRIPTS if you want to use traditional C style element access" OFF)
if (SETUP_C_SUBSCRIPTS)
   add_compile_definitions(SETUP_C_SUBSCRIPTS)
endif()
message("Build with C style element access ${SETUP_C_SUBSCRIPTS}")
 
# -------------
# target
# -------------
set(source_subfolder_ "src")
set(lib_name ${PROJECT_NAME})
add_library(${lib_name})

target_sources(
  ${lib_name}
  PRIVATE
    ${source_subfolder_}/bandmat.cpp
    ${source_subfolder_}/jacobi.cpp
    ${source_subfolder_}/newmat3.cpp
    ${source_subfolder_}/newmat8.cpp
    ${source_subfolder_}/nm_misc.cpp
    ${source_subfolder_}/cholesky.cpp
    ${source_subfolder_}/myexcept.cpp
    ${source_subfolder_}/newmat4.cpp
    ${source_subfolder_}/newmat9.cpp
    ${source_subfolder_}/solution.cpp
    ${source_subfolder_}/evalue.cpp
    ${source_subfolder_}/newfft.cpp
    ${source_subfolder_}/newmat5.cpp
    ${source_subfolder_}/newmatex.cpp
    ${source_subfolder_}/sort.cpp
    ${source_subfolder_}/fft.cpp
    ${source_subfolder_}/newmat1.cpp
    ${source_subfolder_}/newmat6.cpp
    ${source_subfolder_}/newmatnl.cpp
    ${source_subfolder_}/submat.cpp
    ${source_subfolder_}/hholder.cpp
    ${source_subfolder_}/newmat2.cpp
    ${source_subfolder_}/newmat7.cpp
    ${source_subfolder_}/newmatrm.cpp
    ${source_subfolder_}/svd.cpp
)

set(include_dir ${PROJECT_SOURCE_DIR}/${source_subfolder_})

target_include_directories(
  ${lib_name} PUBLIC $<BUILD_INTERFACE:${include_dir}>)
target_include_directories(
  ${lib_name} INTERFACE $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)

# code has throwing desctructors, thus try to compile with c++98
set_property(TARGET ${lib_name} PROPERTY CXX_STANDARD 98)

# -------------
# installation
# -------------
include(GNUInstallDirs)
install(
  FILES
    ${include_dir}/controlw.h
    ${include_dir}/include.h
    ${include_dir}/myexcept.h
    ${include_dir}/newmatap.h
    ${include_dir}/newmat.h
    ${include_dir}/newmatio.h
    ${include_dir}/newmatnl.h
    ${include_dir}/newmatrc.h
    ${include_dir}/newmatrm.h
    ${include_dir}/precisio.h
    ${include_dir}/solution.h
  DESTINATION 
    include/newmat
)
install(
    TARGETS ${lib_name}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
