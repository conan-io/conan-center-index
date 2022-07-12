#include "libexif/exif-data.h"

int main() {
    ExifData *exif = exif_data_new();
    exif_data_free(exif);
    return 0;
}
