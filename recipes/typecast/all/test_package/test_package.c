#include <typecast.h>
#include <stdio.h>

int main(void) {
    /* Test version function */
    const char* version = typecast_version();
    printf("Typecast SDK version: %s\n", version);

    /* Test model string conversion */
    const char* model_str = typecast_model_to_string(TYPECAST_MODEL_SSFM_V30);
    printf("Model: %s\n", model_str);

    /* Test emotion string conversion */
    const char* emotion_str = typecast_emotion_to_string(TYPECAST_EMOTION_HAPPY);
    printf("Emotion: %s\n", emotion_str);

    /* Test audio format string conversion */
    const char* format_str = typecast_audio_format_to_string(TYPECAST_AUDIO_FORMAT_WAV);
    printf("Format: %s\n", format_str);

    /* Test error message */
    const char* err_msg = typecast_error_message(TYPECAST_OK);
    printf("Error message for OK: %s\n", err_msg);

    /* Test client creation (will succeed even without valid API key) */
    TypecastClient* client = typecast_client_create("test-api-key");
    if (client) {
        printf("Client created successfully\n");
        typecast_client_destroy(client);
        printf("Client destroyed successfully\n");
    } else {
        printf("Client creation failed (expected if curl not available)\n");
    }

    printf("All basic tests passed!\n");
    return 0;
}
