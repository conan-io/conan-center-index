#include <tensorflow/lite/interpreter.h>
#include <tensorflow/lite/kernels/register.h>
#include <iostream>


int main(int argc, char * argv[]) {
    std::unique_ptr<tflite::Interpreter> interpreter;
    interpreter = std::make_unique<tflite::Interpreter>();

    const int num_tensors = interpreter->tensors_size();
    std::cout << "Number of tensors in the interpreter: " << num_tensors << std::endl;


    return 0;
}
