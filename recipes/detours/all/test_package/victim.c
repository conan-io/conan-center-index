#include <windows.h>

#include <string.h>

int main(int argc, const char *args[])
{
    HANDLE stdout = GetStdHandle(STD_OUTPUT_HANDLE);
    const char* text = "A secret text";
    WriteFile(stdout, text, (DWORD)strlen(text), NULL, NULL);
    return 0;
}
