find_dependency(CUDAToolkit REQUIRED)

target_link_libraries(SUNDIALS::nveccuda INTERFACE CUDA::cudart)
if(TARGET SUNDIALS::sunmatrixcusparse)
    target_link_libraries(SUNDIALS::sunmatrixcusparse INTERFACE CUDA::cusparse)
endif()
if(TARGET SUNDIALS::sunlinsolcusolversp)
    target_link_libraries(SUNDIALS::sunlinsolcusolversp INTERFACE CUDA::cusolver)
endif()
