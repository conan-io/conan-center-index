find_dependency(CUDAToolkit REQUIRED)
if (WIN32)
    # As of 12.3.1 CUDA Toolkit for Windows does not offer a static cublas library
    target_link_libraries(llama-cpp::common INTERFACE CUDA::cudart_static CUDA::cublas CUDA::cublasLt CUDA::cuda_driver)
else ()
    target_link_libraries(llama-cpp::common INTERFACE CUDA::cudart_static CUDA::cublas_static CUDA::cublasLt_static CUDA::cuda_driver)
endif()
