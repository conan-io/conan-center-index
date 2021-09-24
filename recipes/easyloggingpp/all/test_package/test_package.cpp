#include "easylogging++.h"
INITIALIZE_EASYLOGGINGPP

#ifdef ELPP_FEATURE_CRASH_LOG
void myCrashHandler(int sig) {
  LOG(ERROR) << "Woops! Crashed!";
  el::Helpers::logCrashReason(sig, true);
  // FOLLOWING LINE IS ABSOLUTELY NEEDED AT THE END IN ORDER TO ABORT APPLICATION
  el::Helpers::crashAbort(sig);
}
#endif

int main() {
   LOG(INFO) << "My first info log using default logger";
   #ifdef ELPP_FEATURE_CRASH_LOG
   LOG(INFO) << "Installed crash handler";
   el::Helpers::setCrashHandler(myCrashHandler);
   #endif
   return 0;
}
