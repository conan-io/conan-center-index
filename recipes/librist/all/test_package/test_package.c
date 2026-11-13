#include <librist/librist.h>

#include <stdio.h>

int main(void)
{
    struct rist_ctx* context = NULL;
    if (rist_sender_create(&context, RIST_PROFILE_MAIN, 0, NULL) != 0)
    {
        fprintf(stderr, "rist_sender_create failed\n");
        return 1;
    }
    printf("librist version %s, API %s\n", librist_version(), librist_api_version());
    rist_destroy(context);
    return 0;
}
