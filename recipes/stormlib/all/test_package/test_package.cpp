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

    // Write a temp source file and add it to the archive
    { std::ofstream f("tmp.txt"); f << "Hello StormLib!"; }
    ok = SFileAddFileEx(hMpq, "tmp.txt", "hello.txt", MPQ_FILE_COMPRESS, MPQ_COMPRESSION_ZLIB, MPQ_COMPRESSION_NEXT_SAME);
    assert(ok);
    std::cout << "add file: OK" << std::endl;

    // Verify the file exists inside the archive
    assert(SFileHasFile(hMpq, "hello.txt"));
    std::cout << "has file: OK" << std::endl;

    // Extract and verify content
    ok = SFileExtractFile(hMpq, "hello.txt", "extracted.txt", 0);
    assert(ok);
    std::ifstream fin("extracted.txt");
    std::string content((std::istreambuf_iterator<char>(fin)), std::istreambuf_iterator<char>());
    assert(content == "Hello StormLib!");
    std::cout << "extract file: OK" << std::endl;

    SFileCloseArchive(hMpq);

    std::remove("test.mpq");
    std::remove("tmp.txt");
    std::remove("extracted.txt");

    std::cout << "All tests passed" << std::endl;
    return 0;
}
