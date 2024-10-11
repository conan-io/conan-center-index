cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX C)

# Common

macro(add_component def comp)
    if(${def})
        list(APPEND OpenVINO_COMPONENTS ${comp})
    endif()
endmacro()

add_component(ENABLE_ONNX_FRONTEND ONNX)
add_component(ENABLE_PADDLE_FRONTEND Paddle)
add_component(ENABLE_TF_FRONTEND TensorFlow)
add_component(ENABLE_TF_LITE_FRONTEND TensorFlowLite)
add_component(ENABLE_PYTORCH_FRONTEND PyTroch)

find_package(OpenVINO REQUIRED COMPONENTS Runtime ${OpenVINO_COMPONENTS})

function(add_plugin_definition target def)
    if(${def})
        target_compile_definitions(${target} PRIVATE ${def})
    endif()
endfunction()

function(add_frontend_definition target def frontend)
    if(${def})
        target_compile_definitions(${target} PRIVATE ${def})
        if(NOT TARGET openvino::frontend::${frontend})
            message(FATAL_ERROR "Target for ${frontend} has not been created")
        endif()
    endif()
endfunction()

# C++ test_package

set(target ${PROJECT_NAME}_cpp)
add_executable(${target} test_package.cpp)

add_plugin_definition(${target} ENABLE_IR_FRONTEND)
add_frontend_definition(${target} ENABLE_ONNX_FRONTEND onnx)
add_frontend_definition(${target} ENABLE_PADDLE_FRONTEND paddle)
add_frontend_definition(${target} ENABLE_TF_FRONTEND tensorflow)
add_frontend_definition(${target} ENABLE_TF_LITE_FRONTEND tensorflow_lite)
add_frontend_definition(${target} ENABLE_PYTORCH_FRONTEND pytorch)

target_link_libraries(${target} PRIVATE openvino::runtime)
target_compile_features(${target} PRIVATE cxx_std_11)

# C test_package

set(target ${PROJECT_NAME}_c)
add_executable(${target} test_package.c)

add_plugin_definition(${target} ENABLE_INTEL_CPU)
add_plugin_definition(${target} ENABLE_INTEL_GPU)
add_plugin_definition(${target} ENABLE_AUTO)
add_plugin_definition(${target} ENABLE_HETERO)
add_plugin_definition(${target} ENABLE_AUTO_BATCH)

target_link_libraries(${target} PRIVATE openvino::runtime::c)
