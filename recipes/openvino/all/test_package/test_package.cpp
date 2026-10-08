#include <stdbool.h>

#include <openvino/c/openvino.h>
#include <openvino/openvino.hpp>
#include <openvino/frontend/manager.hpp>

#define TEST(statement) { int value = (statement); if (value) return value; }


int main() {
    // Test frontends
    ov::frontend::FrontEndManager manager;
    auto frontend_available = [&] (const std::string & name) -> bool {
        try {
            manager.load_by_framework(name);
            return true;
        } catch (const std::exception &e) {
            return false;
        }
    };
    auto test_frontend = [&] (int test_id, const std::string &name, bool enabled) -> int {
        if (frontend_available(name) != enabled) {
            return test_id;
        }
        return 0;
    };
    TEST(test_frontend(1001, "ir", ENABLE_IR_FRONTEND));
    TEST(test_frontend(1002, "tflite", ENABLE_TF_LITE_FRONTEND));
    TEST(test_frontend(1003, "pytorch", ENABLE_PYTORCH_FRONTEND));
    TEST(test_frontend(1004, "onnx", ENABLE_ONNX_FRONTEND));
    TEST(test_frontend(1005, "tf", ENABLE_TF_FRONTEND));
    TEST(test_frontend(1006, "paddle", ENABLE_PADDLE_FRONTEND));

    ov::Core core;
    auto test_device = [&] (int test_id, const std::string &device, const std::string &prop, bool enabled) -> int {
        bool available = false;
        try {
            core.get_property(device, prop);
            available = true;
        } catch (const std::exception &e) { }
        if (available != enabled) {
            return test_id;
        }
        return 0;
    };
    TEST(test_device(1101, "CPU", "AVAILABLE_DEVICES", ENABLE_INTEL_CPU));
    //TEST(test_device(1102, "GPU", "AVAILABLE_DEVICES", ENABLE_INTEL_GPU));
    TEST(test_device(1103, "AUTO", "SUPPORTED_PROPERTIES", ENABLE_AUTO));
    TEST(test_device(1104, "BATCH", "SUPPORTED_PROPERTIES", ENABLE_AUTO_BATCH));
    TEST(test_device(1105, "HETERO", "SUPPORTED_PROPERTIES", ENABLE_HETERO));

    // Deinitialize OpenVINO. Important for old systems like Ubuntu 16.04 with obsolete glibc,
    // where application deinit can lead to the following issue on exit:
    // Inconsistency detected by ld.so: dl-close.c: 811: _dl_close: Assertion `map->l_init_called' failed!
    ov::shutdown();

    return 0;
}
