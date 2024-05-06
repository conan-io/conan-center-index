find_dependency(CUDAToolkit REQUIRED)

set(_Ceres_CUDA_dependencies CUDA::cublas CUDA::cudart CUDA::cusolver CUDA::cusparse)
target_link_libraries(Ceres::ceres INTERFACE ${_Ceres_CUDA_dependencies})
if(TARGET Ceres::ceres_cuda_kernels)
    target_link_libraries(Ceres::ceres_cuda_kernels INTERFACE ${_Ceres_CUDA_dependencies})
endif()
