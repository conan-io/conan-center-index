#include <dicom/dicom.h>

int main(void) {
    DcmError *error = NULL;
    dcm_filehandle_create_from_file(&error, "xyz");
    return 0;
}
