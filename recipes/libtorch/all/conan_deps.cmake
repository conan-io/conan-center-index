# A wrapper for https://github.com/pytorch/pytorch/blob/v2.4.0/cmake/Dependencies.cmake

# Moved initialization of these vars here so they can be overridden
set(ATen_CPU_DEPENDENCY_LIBS)
set(ATen_XPU_DEPENDENCY_LIBS)
set(ATen_CUDA_DEPENDENCY_LIBS)
set(ATen_HIP_DEPENDENCY_LIBS)
set(ATen_PUBLIC_CUDA_DEPENDENCY_LIBS)
set(ATen_PUBLIC_HIP_DEPENDENCY_LIBS)
set(Caffe2_DEPENDENCY_LIBS)
set(Caffe2_CUDA_DEPENDENCY_LIBS)

find_package(cpuinfo REQUIRED CONFIG)
find_package(fp16 REQUIRED CONFIG)
find_package(fmt REQUIRED CONFIG)
find_package(httplib REQUIRED CONFIG)

list(APPEND Caffe2_DEPENDENCY_LIBS
    cpuinfo
    fp16::fp16
    fmt::fmt
)
add_library(fp16 ALIAS fp16::fp16)

if(CONAN_LIBTORCH_USE_PTHREADPOOL)
    find_package(pthreadpool REQUIRED CONFIG)
    list(APPEND Caffe2_DEPENDENCY_LIBS pthreadpool::pthreadpool)
    add_library(pthreadpool ALIAS pthreadpool::pthreadpool)
endif()

if(CONAN_LIBTORCH_USE_FLATBUFFERS)
    find_package(flatbuffers REQUIRED CONFIG)
    list(APPEND Caffe2_DEPENDENCY_LIBS flatbuffers::flatbuffers)
endif()

if(CONAN_LIBTORCH_USE_SLEEF)
    find_package(sleef REQUIRED CONFIG)
    list(APPEND ATen_CPU_DEPENDENCY_LIBS sleef::sleef)
endif()

if(USE_XNNPACK)
    find_package(xnnpack REQUIRED CONFIG)
    list(APPEND Caffe2_DEPENDENCY_LIBS xnnpack::xnnpack)
    add_library(XNNPACK INTERFACE)
endif()

if(USE_FBGEMM)
    find_package(fbgemmLibrary REQUIRED CONFIG)
    list(APPEND Caffe2_DEPENDENCY_LIBS fbgemm)
endif()

if(USE_PYTORCH_QNNPACK)
    find_package(fxdiv REQUIRED CONFIG)
    find_package(psimd REQUIRED CONFIG)
endif()

if(USE_MIMALLOC)
    find_package(mimalloc REQUIRED CONFIG)
endif()
