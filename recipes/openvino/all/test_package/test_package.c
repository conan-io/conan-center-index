#include <stdbool.h>

#include <openvino/c/openvino.h>

#define TEST(statement) { int value = (statement); if (value) return value; }

#define TEST_GET_PROP(id, device, prop, enabled) { char *out; bool passed = ov_core_get_property(core, device, prop, &out);  }


bool device_available(ov_core_t *core, char *device, char *prop) {
    char *ret;
    return ov_core_get_property(core, device, prop, &ret) == 0;
}

int test_device(int test_id, ov_core_t *core, char *device, char *prop, bool enabled) {
    if (device_available(core, device, prop) != enabled) {
        return test_id;
    }
    return 0;
}


int main() {
    ov_core_t* core = NULL;
    char* ret = NULL;
    if (ov_core_create(&core)) {
        return 1000;
    }

    TEST(test_device(1101, core, "CPU", "AVAILABLE_DEVICES", ENABLE_INTEL_CPU));
    //TEST(test_device(1102, core, "GPU", "AVAILABLE_DEVICES", ENABLE_INTEL_GPU));
    TEST(test_device(1103, core, "AUTO", "SUPPORTED_PROPERTIES", ENABLE_AUTO));
    TEST(test_device(1104, core, "BATCH", "SUPPORTED_PROPERTIES", ENABLE_AUTO_BATCH));
    TEST(test_device(1105, core, "HETERO", "SUPPORTED_PROPERTIES", ENABLE_HETERO));

    ov_core_free(core);
    return 0;
}
