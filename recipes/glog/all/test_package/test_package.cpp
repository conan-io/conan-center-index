#include <iostream>
#ifdef _WIN32
#ifndef __MINGW32__
#define GOOGLE_GLOG_DLL_DECL 
#endif
#endif
#include <glog/logging.h>

int main(int argc, char** argv) {
    google::InitGoogleLogging(argv[0]);
    LOG(INFO) << "It works";
    return 0;
}
