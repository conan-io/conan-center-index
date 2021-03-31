cmake_minimum_required(VERSION 3.12)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

#-----------------------------
# Workaround for github action
# see https://github.com/actions/setup-python/issues/121#issuecomment-777748504
if (POLICY CMP0094)
    cmake_policy(SET CMP0094 NEW)
endif ()
if (NOT DEFINED Python_FIND_REGISTRY)
    set(Python_FIND_REGISTRY "LAST")
endif ()
if (NOT DEFINED Python_FIND_FRAMEWORK)
    set(Python_FIND_FRAMEWORK "LAST")
endif ()
#-----------------------------

find_package(Python 3.8.0 REQUIRED)
set(PYTHON_EXECUTABLE ${Python_EXECUTABLE})

find_package(Eigen3 REQUIRED)
set(EIGEN3_FOUND 1)
set(EIGEN3_INCLUDE_DIR ${Eigen3_INCLUDE_DIR})

add_library(cpuinfo INTERFACE IMPORTED)
add_library(clog INTERFACE IMPORTED)
set_property(TARGET cpuinfo PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::cpuinfo)
set_property(TARGET clog PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::cpuinfo)

if(USE_PYTORCH_QNNPACK)
    add_library(fxdiv INTERFACE IMPORTED)
    set_property(TARGET fxdiv PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::fxdiv)

    add_library(psimd INTERFACE IMPORTED)
    set_property(TARGET psimd PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::psimd)

    add_library(fp16 INTERFACE IMPORTED)
    set_property(TARGET fp16 PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::fp16)
endif()

if(USE_TENSORPIPE)
    add_library(tensorpipe INTERFACE IMPORTED)
    set_property(TARGET tensorpipe PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::tensorpipe)
endif()

if(CONAN_LIBTORCH_USE_SLEEF)
    add_library(sleef INTERFACE IMPORTED)
    set_property(TARGET sleef PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::sleef)
endif()

if(CONAN_LIBTORCH_USE_PTHREADPOOL)
    add_library(pthreadpool INTERFACE IMPORTED)
    set_property(TARGET pthreadpool PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::pthreadpool)
endif()

add_subdirectory(source_subfolder)
