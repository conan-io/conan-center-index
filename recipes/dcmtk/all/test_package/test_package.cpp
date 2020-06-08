#include "dcmdata/dcfilefo.h"
#include "dcmdata/dcuid.h"
#include "dcmdata/dcdeftag.h"

#include <iostream>

int main(int argc, char *argv[])
{
    char uid[100];
    unsigned char data[256];
    for(unsigned i=0; i < sizeof(data); ++i) {
        data[i] = i;
    }


    DcmFileFormat fileformat;
    DcmDataset *dataset = fileformat.getDataset();
    dataset->putAndInsertString(DCM_SOPClassUID, UID_SecondaryCaptureImageStorage);
    dataset->putAndInsertString(DCM_SOPInstanceUID, dcmGenerateUniqueIdentifier(uid, SITE_INSTANCE_UID_ROOT));
    dataset->putAndInsertString(DCM_PatientName, "Doe^John");
    /* ... */
    dataset->putAndInsertUint8Array(DCM_PixelData, data, sizeof(data));
    OFCondition status = fileformat.saveFile("test.dcm", EXS_LittleEndianExplicit);
    if (status.bad()) {
        std::cerr << "Error: cannot write DICOM file (" << status.text() << ")\n";
        return 1;
    }
    return 0;
}
