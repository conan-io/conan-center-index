#include "subunit/child.h"

int main() {
    subunit_test_start("subunit_test_package");
    subunit_progress(SUBUNIT_PROGRESS_SET, 0);
    subunit_progress(SUBUNIT_PROGRESS_SET, 25);
    subunit_progress(SUBUNIT_PROGRESS_SET, 50);
    subunit_progress(SUBUNIT_PROGRESS_SET, 75);
    subunit_progress(SUBUNIT_PROGRESS_SET, 99);
    subunit_test_pass("subunit_test_package");
    return 0;
}
