/*******************************************************************************
* Copyright 2019-2020 Intel Corporation
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*******************************************************************************/

/// @example getting_started.cpp
/// @copybrief getting_started_cpp
/// > Annotated version: @ref getting_started_cpp

#include <cmath>
#include <numeric>
#include <stdexcept>
#include <vector>

#include "oneapi/dnnl/dnnl.hpp"
#include "oneapi/dnnl/dnnl_debug.h"

#include "example_utils.hpp"

using namespace dnnl;

void getting_started_tutorial(engine::kind engine_kind) {
    engine eng(engine_kind, 0);
    stream engine_stream(eng);
    const int N = 1, H = 13, W = 13, C = 3;

    // Compute physical strides for each dimension
    const int stride_N = H * W * C;
    const int stride_H = W * C;
    const int stride_W = C;
    const int stride_C = 1;

    // An auxiliary function that maps logical index to the physical offset
    auto offset = [=](int n, int h, int w, int c) {
        return n * stride_N + h * stride_H + w * stride_W + c * stride_C;
    };

    // The image size
    const int image_size = N * H * W * C;

    // Allocate a buffer for the image
    std::vector<float> image(image_size);

    // Initialize the image with some values
    for (int n = 0; n < N; ++n)
        for (int h = 0; h < H; ++h)
            for (int w = 0; w < W; ++w)
                for (int c = 0; c < C; ++c) {
                    int off = offset(
                            n, h, w, c); // Get the physical offset of a pixel
                    image[off] = -std::cos(off / 10.f);
                }
    auto src_md = memory::desc(
            {N, C, H, W}, // logical dims, the order is defined by a primitive
            memory::data_type::f32, // tensor's data type
            memory::format_tag::nhwc // memory format, NHWC in this case
    );
    // [Init src_md]
    auto alt_src_md = memory::desc(
            {N, C, H, W}, // logical dims, the order is defined by a primitive
            memory::data_type::f32, // tensor's data type
            {stride_N, stride_C, stride_H, stride_W} // the strides
    );

    // Sanity check: the memory descriptors should be the same
    if (src_md != alt_src_md)
        throw std::logic_error("Memory descriptor initialization mismatch.");
    auto src_mem = memory(src_md, eng);
    write_to_dnnl_memory(image.data(), src_mem);

    // For dst_mem the library allocates buffer
    auto dst_mem = memory(src_md, eng);
    auto relu_d = eltwise_forward::desc(
            prop_kind::forward_inference, algorithm::eltwise_relu,
            src_md, // the memory descriptor for an operation to work on
            0.f, // alpha parameter means negative slope in case of ReLU
            0.f // beta parameter is ignored in case of ReLU
    );

    // ReLU primitive descriptor, which corresponds to a particular
    // implementation in the library
    auto relu_pd
            = eltwise_forward::primitive_desc(relu_d, // an operation descriptor
                    eng // an engine the primitive will be created for
            );

    auto relu = eltwise_forward(relu_pd); // !!! this can take quite some time
    relu.execute(engine_stream, // The execution stream
            {
                    // A map with all inputs and outputs
                    {DNNL_ARG_SRC, src_mem}, // Source tag and memory obj
                    {DNNL_ARG_DST, dst_mem}, // Destination tag and memory obj
            });

    engine_stream.wait();
    std::vector<float> relu_image(image_size);
    read_from_dnnl_memory(relu_image.data(), dst_mem);
}

int main(int argc, char **argv) {
    int exit_code = 0;

    engine::kind engine_kind = parse_engine_kind(argc, argv);
    try {
        getting_started_tutorial(engine_kind);
    } catch (dnnl::error &e) {
        std::cout << "oneDNN error caught: " << std::endl
                  << "\tStatus: " << dnnl_status2str(e.status) << std::endl
                  << "\tMessage: " << e.what() << std::endl;
        exit_code = 1;
    } catch (std::string &e) {
        std::cout << "Error in the example: " << e << "." << std::endl;
        exit_code = 2;
    }

    std::cout << "Example " << (exit_code ? "failed" : "passed") << " on "
              << engine_kind2str_upper(engine_kind) << "." << std::endl;
    return exit_code;
}
