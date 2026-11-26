#include <StormLib.h>
#include <cassert>
#include <fstream>
#include <iostream>
#include <string>

int main() {
    // Test locale API
    SFileSetLocale(0);
    assert(SFileGetLocale() == 0);
    std::cout << "locale API: OK" << std::endl;

    // Create a new MPQ archive
    HANDLE hMpq = NULL;
    bool ok = SFileCreateArchive("test.mpq", MPQ_CREATE_ARCHIVE_V2, 16, &hMpq);
    assert(ok && hMpq != NULL);
    std::cout << "create archive: OK" << std::endl;

    SFileCloseArchive(hMpq);

    std::remove("test.mpq");

    std::cout << "All tests passed" << std::endl;
    return 0;
}
