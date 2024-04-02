#include <openvino/c/openvino.h>

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
    OV_SUCCESS(ov_core_get_property(core, "AUTO", "SUPPORTED_PROPERTIES", &ret));
    OV_SUCCESS(ov_core_get_property(core, "MULTI", "SUPPORTED_PROPERTIES", &ret));
#else
    OV_FAIL(ov_core_get_property(core, "AUTO", "SUPPORTED_PROPERTIES", &ret));
    OV_FAIL(ov_core_get_property(core, "MULTI", "SUPPORTED_PROPERTIES", &ret));
#endif
#ifdef ENABLE_HETERO
    OV_SUCCESS(ov_core_get_property(core, "HETERO", "SUPPORTED_PROPERTIES", &ret));
#else
    OV_FAIL(ov_core_get_property(core, "HETERO", "SUPPORTED_PROPERTIES", &ret));
#endif
#ifdef ENABLE_AUTO_BATCH
    OV_SUCCESS(ov_core_get_property(core, "BATCH", "SUPPORTED_PROPERTIES", &ret));
#else
    OV_FAIL(ov_core_get_property(core, "BATCH", "SUPPORTED_PROPERTIES", &ret));
#endif
    ov_core_free(core);
    return 0;
}

int main() {
    OV_SUCCESS(test_available_devices());
    return 0;
}
