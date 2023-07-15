#include <iostream>
#include "nim_cpp_wrapper/nim_cpp_api.h"

int main(int argc, char* argv[]) {
    nim::Client::Init("", "", "", nim::SDKConfig());
    nim::Client::Cleanup2();
}
