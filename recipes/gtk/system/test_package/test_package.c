#include <stdlib.h>
#include <gtk/gtk.h>

int main(void) {

#if GTK_MAJOR_VERSION == 3
    printf("GTK major version: %u\n", gtk_get_major_version());
#elif GTK_MAJOR_VERSION == 2
    gtk_disable_setlocale();
    printf("GTK major version: %u\n", gtk_major_version);
#else
    return 1;
#endif

return 0;

}
