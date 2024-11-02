#include "test_package.h"

int main()
{
    compute_hash();

    // Using the library in both translation units ensures correct linkage with
    // header-only builds.
    compute_hash_in_another_tu();
}
