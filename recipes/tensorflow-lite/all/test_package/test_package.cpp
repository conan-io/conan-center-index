#include <tensorflow/lite/model.h>
#include <tensorflow/lite/interpreter.h>
#include <tensorflow/lite/kernels/register.h>
#include <tensorflow/lite/optional_debug_tools.h>

#include <iostream>
#include <memory>


int main(int argc, char * argv[]) {
    if ( argc != 2) {
        std::cerr << "Pass model file path as argument" << std::endl;
        return -1;
    }
    auto model = tflite::FlatBufferModel::BuildFromFile(argv[1]);
    if (!model) {
        throw std::runtime_error("Failed to load TFLite model");
    }

    tflite::ops::builtin::BuiltinOpResolver resolver;
    tflite::InterpreterBuilder builder(*model, resolver);
    std::unique_ptr<tflite::Interpreter> interpreter;
    builder(&interpreter);

    if (interpreter->AllocateTensors() != kTfLiteOk) {
        throw std::runtime_error("Failed to allocate tensors");
    }

    tflite::PrintInterpreterState(interpreter.get());
    auto input = interpreter->typed_input_tensor<float>(0);
    *input = 42.0F;
    std::cout << "==== Running SQUARE(x) Model ====\n\n";
    if (interpreter->Invoke() != kTfLiteOk) {
        throw std::runtime_error("Failed to execute model");
    }
    auto output = interpreter->typed_output_tensor<float>(0);
    std::cout << "SQUARE(" << *input << ") = " << *output << std::endl;

    return 0;
}
