#include <stdlib.h>

#include <libwacom/libwacom.h>


int main(void) {
    WacomDeviceDatabase *db = libwacom_database_new();
    if (!db) {
      return EXIT_FAILURE;
    }
    libwacom_database_destroy(db);
    return EXIT_SUCCESS;
}
