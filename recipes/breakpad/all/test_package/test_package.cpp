#include <iostream>
#include "client/linux/handler/exception_handler.h"

using namespace google_breakpad;

namespace {

bool callback(const MinidumpDescriptor &descriptor,
              void *context,
              bool succeeded) {
    // if succeeded is true, descriptor.path() contains a path
    // to the minidump file. Context is the context passed to
    // the exception handler's constructor.
    return succeeded;
}

}

int main(int argc, char *argv[]) {

    std::cout << "Breakpad test_package" << std::endl;

    MinidumpDescriptor descriptor("path/to/cache");
    ExceptionHandler eh(
      descriptor,
      /* filter */ nullptr,
      callback,
      /* context */ nullptr,
      /* install handler */ true,
      /* server FD */ -1
    );

    // run your program here
    return 0;
}
