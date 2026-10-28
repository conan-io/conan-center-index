#include <stdio.h>
#include <string.h>

#include <tiny_gltf_v3.h>

int main(void) {
    static const char json[] = "{\"asset\":{\"version\":\"2.0\"}}";

    tg3_parse_options options;
    tg3_error_stack errors;
    tg3_model model;
    tg3_error_code err;

    tg3_parse_options_init(&options);
    tg3_error_stack_init(&errors);

    err = tg3_parse(&model, &errors, (const uint8_t *)json, strlen(json), NULL, 0, &options);
    printf("tg3_parse: %d\n", (int)err);
    if (err == TG3_OK) {
        tg3_model_free(&model);
    }
    tg3_error_stack_free(&errors);

    return 0;
}
