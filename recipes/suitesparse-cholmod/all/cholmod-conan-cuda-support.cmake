# Reproduces the CUDA dependencies added by https://github.com/DrTimothyAldenDavis/SuiteSparse/blob/v7.7.0/CHOLMOD/GPU/CMakeLists.txt

find_dependency(CUDAToolkit REQUIRED)

target_link_libraries(SuiteSparse::CHOLMOD INTERFACE CUDA::nvrtc CUDA::cudart_static CUDA::cublas)
target_compile_definitions(SuiteSparse::CHOLMOD INTERFACE "CHOLMOD_HAS_CUDA")
