#include <libdjvu/ddjvuapi.h>
#include <stdio.h>

int main() {
    ddjvu_context_t* context = ddjvu_context_create("test_package");
    if (!context) {
        printf("Failed to create djvu context\n");
        return 1;
    }
    printf("DjVu context initialized successfully.\n");
    int cache_size = ddjvu_cache_get_size(context);
    printf("Cache size: %d\n", cache_size);
    ddjvu_context_release(context);
    return 0;
}
