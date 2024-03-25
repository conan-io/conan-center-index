#include <cuda/std/atomic>
#include <cuda/std/version>
#include <iostream>

int main() {
    std::cout << "libcu++ API version: "
        << _LIBCUDACXX_CUDA_API_VERSION_MAJOR << "."
        << _LIBCUDACXX_CUDA_API_VERSION_MINOR << "."
        << _LIBCUDACXX_CUDA_API_VERSION_PATCH << std::endl;
    std::cout << "libcu++ ABI version: " << _LIBCUDACXX_CUDA_ABI_VERSION << std::endl;
    cuda::std::atomic<int> x;
    return 0;
}
