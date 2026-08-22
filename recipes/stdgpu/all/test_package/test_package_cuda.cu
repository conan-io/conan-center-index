// Based on https://github.com/stotko/stdgpu/blob/32e0517/examples/cuda/vector.cu
#include <thrust/copy.h>
#include <thrust/reduce.h>
#include <thrust/sequence.h>

#include <stdgpu/iterator.h> // device_begin, device_end
#include <stdgpu/memory.h>   // createDeviceArray, destroyDeviceArray
#include <stdgpu/platform.h> // STDGPU_HOST_DEVICE
#include <stdgpu/vector.cuh> // stdgpu::vector

#include <cstdlib>
#include <iostream>

__global__ void insert_neighbors_with_duplicates(const int *d_input, const stdgpu::index_t n,
                                                 stdgpu::vector<int> vec) {
    stdgpu::index_t i = static_cast<stdgpu::index_t>(blockIdx.x * blockDim.x + threadIdx.x);

    if (i >= n)
        return;

    int num = d_input[i];
    int num_neighborhood[3] = {num - 1, num, num + 1};

    for (int num_neighbor : num_neighborhood) {
        vec.push_back(num_neighbor);
    }
}

int sum_stdgpu(stdgpu::index_t n) {
    int *d_input = createDeviceArray<int>(n);
    auto vec = stdgpu::vector<int>::createDeviceObject(3 * n);

    thrust::sequence(stdgpu::device_begin(d_input), stdgpu::device_end(d_input), 1);

    stdgpu::index_t threads = 32;
    stdgpu::index_t blocks = (n + threads - 1) / threads;
    insert_neighbors_with_duplicates<<<static_cast<unsigned int>(blocks),
                                       static_cast<unsigned int>(threads)>>>(d_input, n, vec);
    cudaDeviceSynchronize();

    auto range_vec = vec.device_range();
    int sum = thrust::reduce(range_vec.begin(), range_vec.end(), 0, thrust::plus<int>());

    destroyDeviceArray<int>(d_input);
    stdgpu::vector<int>::destroyDeviceObject(vec);

    return sum;
}

int main() {
    const int n = 20;
    const int sum_closed_form = 3 * (n * (n + 1) / 2);
    std::cout << "Sum: " << sum_stdgpu(n) << ", expected: " << sum_closed_form << std::endl;
    return EXIT_SUCCESS;
}
