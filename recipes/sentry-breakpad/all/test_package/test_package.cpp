#ifdef _WIN32
# include "client/windows/handler/exception_handler.h"
#elif defined(__APPLE__)
# include "client/mac/handler/exception_handler.h"
#else
# include "client/linux/handler/exception_handler.h"
#endif

#include <iostream>

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

#elif defined(__APPLE__)

bool callback(void* context,
              int exception_type,
              int exception_code,
              int exception_subcode,
              mach_port_t thread_name) {
    return true;
}

#else
bool callback(const google_breakpad::MinidumpDescriptor &descriptor,
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
    google_breakpad::ExceptionHandler eh(
      /* dump_path */ L".",
      filter_callback,
      callback,
      /* context */ nullptr,
      google_breakpad::ExceptionHandler::HANDLER_ALL
    );
#elif defined(__APPLE__)
    google_breakpad::ExceptionHandler eh(
      callback,
      /* context */ nullptr,
      /* install_handler*/ true
    );
#else
    google_breakpad::MinidumpDescriptor descriptor("path/to/cache");
    google_breakpad::ExceptionHandler eh(
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
