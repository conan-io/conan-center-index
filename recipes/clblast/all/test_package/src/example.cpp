
// =================================================================================================
// This file is part of the CLBlast project. Author(s):
//   Cedric Nugteren <www.cedricnugteren.nl>
//
// This file demonstrates the use of the SGEMM routine. It is a stand-alone
// example, but it does require the Khronos C++ OpenCL API header file
// (downloaded by CMake). The example uses C++ features, but CLBlast can also be
// used using the regular C-style OpenCL API.
//
// Note that this example is meant for illustration purposes only. CLBlast
// provides other programs for performance benchmarking ('client_xxxxx') and for
// correctness testing ('test_xxxxx').
//
// =================================================================================================

#include <chrono>
#include <cstdio>
#include <vector>

#define CL_USE_DEPRECATED_OPENCL_1_1_APIS // to disable deprecation warnings
#define CL_USE_DEPRECATED_OPENCL_1_2_APIS // to disable deprecation warnings

// Includes the C++ OpenCL API. If not yet available, it can be found here:
// https://raw.githubusercontent.com/KhronosGroup/OpenCL-CLHPP/main/include/CL/opencl.hpp
#define CL_HPP_TARGET_OPENCL_VERSION 120
#define CL_HPP_MINIMUM_OPENCL_VERSION 120
#define CL_TARGET_OPENCL_VERSION 120
#include "CL/opencl.hpp"

// Includes the CLBlast library
#include <clblast.h>

// =================================================================================================

// Example use of the single-precision Xgemm routine SGEMM
int main() {
  // OpenCL platform/device settings
  const auto platform_id = 0;
  const auto device_id = 0;

  // Example SGEMM arguments
  const size_t m = 128;
  const size_t n = 64;
  const size_t k = 512;
  const float alpha = 0.7f;
  const float beta = 1.0f;
  const auto a_ld = k;
  const auto b_ld = n;
  const auto c_ld = n;

  // Initializes the OpenCL platform
  auto platforms = std::vector<cl::Platform>();
  cl::Platform::get(&platforms);
  if (platforms.size() == 0 || platform_id >= platforms.size()) {
    return 1;
  }
  auto platform = platforms[platform_id];

  // Initializes the OpenCL device
  auto devices = std::vector<cl::Device>();
  platform.getDevices(CL_DEVICE_TYPE_ALL, &devices);
  if (devices.size() == 0 || device_id >= devices.size()) {
    return 1;
  }
  auto device = devices[device_id];

  // Creates the OpenCL context, queue, and an event
  auto device_as_vector = std::vector<cl::Device>{device};
  auto context = cl::Context(device_as_vector);
  auto queue = cl::CommandQueue(context, device);
  auto event = cl_event{nullptr};

  // Populate host matrices with some example data
  auto host_a = std::vector<float>(m * k);
  auto host_b = std::vector<float>(n * k);
  auto host_c = std::vector<float>(m * n);
  for (auto &item : host_a) {
    item = 12.193f;
  }
  for (auto &item : host_b) {
    item = -8.199f;
  }
  for (auto &item : host_c) {
    item = 0.0f;
  }

  // Copy the matrices to the device
  auto device_a =
      cl::Buffer(context, CL_MEM_READ_WRITE, host_a.size() * sizeof(float));
  auto device_b =
      cl::Buffer(context, CL_MEM_READ_WRITE, host_b.size() * sizeof(float));
  auto device_c =
      cl::Buffer(context, CL_MEM_READ_WRITE, host_c.size() * sizeof(float));
  queue.enqueueWriteBuffer(device_a, CL_TRUE, 0, host_a.size() * sizeof(float),
                           host_a.data());
  queue.enqueueWriteBuffer(device_b, CL_TRUE, 0, host_b.size() * sizeof(float),
                           host_b.data());
  queue.enqueueWriteBuffer(device_c, CL_TRUE, 0, host_c.size() * sizeof(float),
                           host_c.data());

  // Start the timer
  auto start_time = std::chrono::steady_clock::now();

  // Call the SGEMM routine. Note that the type of alpha and beta (float)
  // determine the precision.
  auto queue_plain = queue();
  auto status = clblast::Gemm(
      clblast::Layout::kRowMajor, clblast::Transpose::kNo,
      clblast::Transpose::kNo, m, n, k, alpha, device_a(), 0, a_ld, device_b(),
      0, b_ld, beta, device_c(), 0, c_ld, &queue_plain, &event);

  // Record the execution time
  if (status == clblast::StatusCode::kSuccess) {
    clWaitForEvents(1, &event);
    clReleaseEvent(event);
  }
  auto elapsed_time = std::chrono::steady_clock::now() - start_time;
  auto time_ms =
      std::chrono::duration<double, std::milli>(elapsed_time).count();

  // Example completed. See "clblast.h" for status codes (0 -> success).
  printf("Completed SGEMM in %.3lf ms with status %d\n", time_ms,
         static_cast<int>(status));
  return 0;
}

// =================================================================================================
