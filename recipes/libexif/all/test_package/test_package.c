#include "libexif/exif-data.h"

int main(int argc, char *argv[]) {
    ExifData *exif = exif_data_new();
    exif_data_free(exif);
    return 0;
}
