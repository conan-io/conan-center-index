#include <openvino/c/openvino.h>
#include <openvino/core/visibility.hpp>
#include <openvino/frontend/manager.hpp>

#define OV_SUCCESS(statement) \
    if ((statement) != 0) \
        return 1;

#define OV_FAIL(statement) \
    if ((statement) == 0) \
        return 1;

int test_available_devices() {
    ov_core_t* core = NULL;
    char* ret = NULL;
    OV_SUCCESS(ov_core_create(&core));
#ifdef ENABLE_INTEL_CPU
    OV_SUCCESS(ov_core_get_property(core, "CPU", "AVAILABLE_DEVICES", &ret));
#else
    OV_FAIL(ov_core_get_property(core, "CPU", "AVAILABLE_DEVICES", &ret));
#endif
#ifdef ENABLE_INTEL_GPU
    OV_SUCCESS(ov_core_get_property(core, "GPU", "AVAILABLE_DEVICES", &ret));
#else
    OV_FAIL(ov_core_get_property(core, "GPU", "AVAILABLE_DEVICES", &ret));
#endif
#ifdef ENABLE_AUTO
    OV_SUCCESS(ov_core_get_property(core, "AUTO", "SUPPORTED_METRICS", &ret));
    OV_SUCCESS(ov_core_get_property(core, "MULTI", "SUPPORTED_METRICS", &ret));
#else
    OV_FAIL(ov_core_get_property(core, "AUTO", "SUPPORTED_METRICS", &ret));
    OV_FAIL(ov_core_get_property(core, "MULTI", "SUPPORTED_METRICS", &ret));
#endif
#ifdef ENABLE_HETERO
    OV_SUCCESS(ov_core_get_property(core, "HETERO", "SUPPORTED_METRICS", &ret));
#else
    OV_FAIL(ov_core_get_property(core, "HETERO", "SUPPORTED_METRICS", &ret));
#endif
#ifdef ENABLE_AUTO_BATCH
    OV_SUCCESS(ov_core_get_property(core, "BATCH", "SUPPORTED_METRICS", &ret));
#else
    OV_FAIL(ov_core_get_property(core, "BATCH", "SUPPORTED_METRICS", &ret));
#endif
    ov_core_free(core);
    return 0;
}

int test_available_frontends() {
    ov::frontend::FrontEndManager manager;
    auto frontend_found = [&] (const std::string & name) -> int {
        try {
            manager.load_by_framework(name);
        } catch (const std::exception & e) {
            return 1;
        }
        return 0;
    };

#ifdef ENABLE_IR_FRONTEND
    OV_SUCCESS(frontend_found("ir"));
#else
    OV_FAIL(frontend_found("ir"));
#endif
#ifdef ENABLE_TF_LITE_FRONTEND
    OV_SUCCESS(frontend_found("tflite"));
#else
    OV_FAIL(frontend_found("tflite"));
#endif
#ifdef ENABLE_PYTORCH_FRONTEND
    OV_SUCCESS(frontend_found("pytorch"));
#else
    OV_FAIL(frontend_found("pytorch"));
#endif
#ifdef ENABLE_ONNX_FRONTEND
    OV_SUCCESS(frontend_found("onnx"));
#else
    OV_FAIL(frontend_found("onnx"));
#endif
#ifdef ENABLE_TF_FRONTEND
    OV_SUCCESS(frontend_found("tf"));
#else
    OV_FAIL(frontend_found("tf"));
#endif
#ifdef ENABLE_PADDLE_FRONTEND
    OV_SUCCESS(frontend_found("paddle"));
#else
    OV_FAIL(frontend_found("paddle"));
#endif
    return 0;
}

int main() {
    OV_SUCCESS(test_available_devices());
    OV_SUCCESS(test_available_frontends());

    // Deinitialize OpenVINO. Important for old systems like Ubuntu 16.04 with obsolete glibc,
    // where application deinit can lead to the following issue on exit:
    // Inconsistency detected by ld.so: dl-close.c: 811: _dl_close: Assertion `map->l_init_called' failed!
    ov::shutdown();

    return 0;
}
