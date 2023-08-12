cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

# TODO
find_package(OpenVINO REQUIRED COMPONENTS Runtime ONNX TensorFlow TensorFlowLite Paddle PyTroch)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE openvino::runtime)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

function(add_plugin def)
    if(${def})
        target_compile_definitions(${PROJECT_NAME} PRIVATE ${def})
    endif()
endfunction()

add_plugin(ENABLE_INTEL_CPU)
add_plugin(ENABLE_INTEL_GPU)
add_plugin(ENABLE_AUTO)
add_plugin(ENABLE_HETERO)
add_plugin(ENABLE_AUTO_BATCH)

function(add_frontend def frontend)
    if(${def})
        target_compile_definitions(${PROJECT_NAME} PRIVATE ${def})
        if(NOT TARGET openvino::frontend::${frontend})
            message(FATAL_ERROR "Target for ${frontend} has not been created")
        endif()
    endif()
endfunction()

add_plugin(ENABLE_IR_FRONTEND)
add_frontend(ENABLE_ONNX_FRONTEND onnx)
add_frontend(ENABLE_PADDLE_FRONTEND paddle)
add_frontend(ENABLE_TF_FRONTEND tensorflow)
add_frontend(ENABLE_TF_LITE_FRONTEND tensorflow_lite)
add_frontend(ENABLE_PYTORCH_FRONTEND pytorch)
