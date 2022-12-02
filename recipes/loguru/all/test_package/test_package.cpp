#include <loguru.hpp>

int main(int argc, char** argv) {
    loguru::init(argc, argv);

    LOG_SCOPE_F(INFO, "logging scope");

    LOG_F(INFO, "42=={}", 42);
    LOG_F(INFO, "Use fmt? {}", LOGURU_USE_FMTLIB);
    LOG_F(INFO, "Scope text size: {}", LOGURU_SCOPE_TEXT_SIZE);
    LOG_F(INFO, "Filename width: {}", LOGURU_FILENAME_WIDTH);
    LOG_F(INFO, "Threadname width: {}", LOGURU_THREADNAME_WIDTH);
    LOG_F(INFO, "Catch sigabrt: {}", LOGURU_CATCH_SIGABRT);
    LOG_F(INFO, "Verbose scope endings: {}", LOGURU_VERBOSE_SCOPE_ENDINGS);
    LOG_F(INFO, "Redefine assert: {}", LOGURU_REDEFINE_ASSERT);
    LOG_F(INFO, "With fileabs: {}", LOGURU_WITH_FILEABS);
    LOG_F(INFO, "With rtti: {}", LOGURU_WITH_RTTI);
    LOG_F(INFO, "With streams: {}", LOGURU_WITH_STREAMS);

#if LOGURU_WITH_STREAMS == 1
    {
        LOG_SCOPE_F(INFO, "streams");
        LOG_S(INFO) << "log via streams";
    }
#endif

    LOG_F(INFO, "Replace GLog: {}", LOGURU_REPLACE_GLOG);

#if LOGURU_REPLACE_GLOG == 1
    {
        LOG_SCOPE_F(INFO, "replace glog");
        LOG(INFO) << "log via glog api";
    }
#endif

    return 0;
}

