#include <iostream>
#include "apriltag.h"
#include "tagStandard41h12.h"
#include "common/image_u8.h"

int main(int argc, char *argv[])
{
    apriltag_detector_t *td = apriltag_detector_create();
    apriltag_family_t *tf = tagStandard41h12_create();
    apriltag_detector_add_family(td, tf);

    tagStandard41h12_destroy(tf);
    apriltag_detector_destroy(td);

    std::cout << "Apriltag test_package ran successfully" << std::endl;

    return 0;
}
