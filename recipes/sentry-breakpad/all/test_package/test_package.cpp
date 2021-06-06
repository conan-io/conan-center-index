#ifdef _WIN32
# include "client/windows/handler/exception_handler.h"
#else
# include "client/linux/handler/exception_handler.h"
#endif

#include <iostream>

using namespace google_breakpad;

namespace {

#ifdef _WIN32

bool filter_callback(void *context, EXCEPTION_POINTERS *exinfo,
                     MDRawAssertionInfo* assertion) {
    // If a FilterCallback returns true, Breakpad will continue processing
    return true;
}

bool callback(const wchar_t* dump_path,
              const wchar_t* minidump_id,
              void* context,
              EXCEPTION_POINTERS* exinfo,
              MDRawAssertionInfo* assertion,
              bool succeeded) {
    // succeeded indicates whether a minidump file was successfully written.
    return succeeded;
}
#else
bool callback(const MinidumpDescriptor &descriptor,
              void *context,
              bool succeeded) {
    // if succeeded is true, descriptor.path() contains a path
    // to the minidump file. Context is the context passed to
    // the exception handler's constructor.
    return succeeded;
}
#endif

}

int main(int argc, char *argv[]) {
    std::cout << "Breakpad test_package\n";

#ifdef _WIN32
    ExceptionHandler eh(
      /* dump_path */ L".",
      filter_callback,
      callback,
      /* context */ nullptr,
      ExceptionHandler::HANDLER_ALL
    );
#else
    MinidumpDescriptor descriptor("path/to/cache");
    ExceptionHandler eh(
      descriptor,
      /* filter */ nullptr,
      callback,
      /* context */ nullptr,
      /* install handler */ true,
      /* server FD */ -1
    );
#endif

    // run your program here
    return 0;
}
