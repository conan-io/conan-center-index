#include <onnxruntime_cxx_api.h>
#include <stdexcept>
#include <stdio.h>

int mainT(const ORTCHAR_T* model_path) {
    Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "Default");
    Ort::Session session(nullptr);
    Ort::SessionOptions session_options;
    try {
        Ort::Session(env, model_path, session_options);
    } catch (const std::exception& ex) {
        fprintf(stderr, "%s\n", ex.what());
        return 10;
    }
    return 0;
}

#ifdef _WIN32
int wmain(int argc, wchar_t *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "%S: modelpath\n", argv[0]);
        return 1;
    }
    return mainT(argv[1]);
}
#else
int main(int argc, const char* argv[]) {
    if (argc < 2) {
        fprintf(stderr, "%s: modelpath\n", argv[0]);
        return 1;
    }
    return mainT(argv[1]);
}
#endif
