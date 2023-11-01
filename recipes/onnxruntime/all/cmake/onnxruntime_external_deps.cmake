# Replacement for https://github.com/microsoft/onnxruntime/blob/v1.16.1/cmake/external/onnxruntime_external_deps.cmake

if(NOT onnxruntime_DISABLE_ABSEIL)
  find_package(absl REQUIRED CONFIG)
  list(APPEND onnxruntime_EXTERNAL_LIBRARIES abseil::abseil)
  include_directories(${absl_INCLUDE_DIRS})
endif()

find_package(re2 REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES re2::re2)

#flatbuffers 1.11.0 does not have flatbuffers::IsOutRange, therefore we require 1.12.0+
find_package(Flatbuffers REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES flatbuffers::flatbuffers)

find_package(Protobuf 3.21.12 REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES protobuf::libprotobuf)
set(ONNX_CUSTOM_PROTOC_EXECUTABLE protoc)
set(PROTOC_EXECUTABLE protoc)

find_package(date REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES date_interface)

find_package(Boost REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES Boost::mp11)

find_package(nlohmann_json REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES nlohmann_json::nlohmann_json)

find_package(cpuinfo REQUIRED CONFIG)
set(CPUINFO_SUPPORTED ${cpuinfo_FOUND})

if (NOT WIN32)
  find_package(nsync REQUIRED CONFIG)
  list(APPEND onnxruntime_EXTERNAL_LIBRARIES nsync::nsync_cpp)
  include_directories(${nsync_INCLUDE_DIRS})
endif()

find_package(Microsoft.GSL 4.0 REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES Microsoft.GSL::GSL)
include_directories(${Microsoft.GSL_INCLUDE_DIRS})

find_package(safeint REQUIRED CONFIG)
include_directories(${safeint_INCLUDE_DIRS})

find_package(ONNX REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES onnx onnx_proto)

find_package(Eigen3 REQUIRED CONFIG)
list(APPEND onnxruntime_EXTERNAL_LIBRARIES Eigen3::Eigen)
set(eigen_INCLUDE_DIRS ${Eigen3_INCLUDE_DIRS})

if(WIN32)
  find_package(wil REQUIRED CONFIG)
  list(APPEND onnxruntime_EXTERNAL_LIBRARIES WIL::WIL)
endif()

# XNNPACK EP
if (onnxruntime_USE_XNNPACK)
  if (onnxruntime_DISABLE_CONTRIB_OPS)
    message(FATAL_ERROR "XNNPACK EP requires the internal NHWC contrib ops to be available "
                         "but onnxruntime_DISABLE_CONTRIB_OPS is ON")
  endif()
  find_package(xnnpack REQUIRED CONFIG)
  list(APPEND onnxruntime_EXTERNAL_LIBRARIES xnnpack::xnnpack)
endif()

if (onnxruntime_USE_MIMALLOC)
  find_package(mimalloc REQUIRED CONFIG)
  add_definitions(-DUSE_MIMALLOC)
endif()

# The source code of onnx_proto is generated, we must build this lib first before starting to compile the other source code that uses ONNX protobuf types.
# The other libs do not have the problem. All the sources are already there. We can compile them in any order.
set(onnxruntime_EXTERNAL_DEPENDENCIES
  onnx_proto
  flatbuffers::flatbuffers
)

if (onnxruntime_RUN_ONNX_TESTS)
  add_definitions(-DORT_RUN_EXTERNAL_ONNX_TESTS)
endif()

if(onnxruntime_ENABLE_ATEN)
  message("Aten fallback is enabled.")
  find_package(dlpack REQUIRED CONFIG)
endif()

if(onnxruntime_ENABLE_TRAINING OR (onnxruntime_ENABLE_TRAINING_APIS AND onnxruntime_BUILD_UNIT_TESTS))
  find_package(cxxopts REQUIRED CONFIG)
endif()

set(onnxruntime_LINK_DIRS )
if (onnxruntime_USE_CUDA)
      #TODO: combine onnxruntime_CUDNN_HOME and onnxruntime_CUDA_HOME, assume they are the same
      if (WIN32)
        if(onnxruntime_CUDNN_HOME)
          list(APPEND onnxruntime_LINK_DIRS ${onnxruntime_CUDNN_HOME}/lib ${onnxruntime_CUDNN_HOME}/lib/x64)
        endif()
        list(APPEND onnxruntime_LINK_DIRS ${onnxruntime_CUDA_HOME}/x64/lib64)
      else()
        if(onnxruntime_CUDNN_HOME)
          list(APPEND onnxruntime_LINK_DIRS  ${onnxruntime_CUDNN_HOME}/lib ${onnxruntime_CUDNN_HOME}/lib64)
        endif()
        list(APPEND onnxruntime_LINK_DIRS ${onnxruntime_CUDA_HOME}/lib64)
      endif()
endif()

if(onnxruntime_USE_SNPE)
    include(external/find_snpe.cmake)
    list(APPEND onnxruntime_EXTERNAL_LIBRARIES ${SNPE_NN_LIBS})
endif()

file(TO_NATIVE_PATH ${CMAKE_BINARY_DIR}  ORT_BINARY_DIR)
file(TO_NATIVE_PATH ${PROJECT_SOURCE_DIR}  ORT_SOURCE_DIR)
