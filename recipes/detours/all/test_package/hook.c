#include <windows.h>
#include <detours.h>

#include <stdio.h>
#include <string.h>

typedef BOOL (WINAPI * tWriteFile)(HANDLE, LPCVOID, DWORD, LPDWORD, LPOVERLAPPED);
static tWriteFile OriginalWriteFile = WriteFile;
static BOOL WINAPI HookWriteFile(HANDLE hFile, LPCVOID lpBuffer, DWORD nNumberOfBytesToWrite, LPDWORD lpNumberOfBytesWritten, LPOVERLAPPED lpOverlapped) {
    char buffer[512];
    sprintf_s(buffer, sizeof(buffer), "I found your message! It was '%s'! I am 1337! :^)", (char*)lpBuffer);
    return OriginalWriteFile(hFile, buffer, (DWORD)strlen(buffer), lpNumberOfBytesWritten, lpOverlapped);
}

BOOL WINAPI DllMain(HINSTANCE hinst, DWORD dwReason, LPVOID reserve0d)
{
    if (DetourIsHelperProcess()) {
        return TRUE;
    }

    if (dwReason == DLL_PROCESS_ATTACH) {
        AllocConsole();
        DetourRestoreAfterWith();

        DetourTransactionBegin();
        DetourUpdateThread(GetCurrentThread());

        DetourAttach((PVOID*)&OriginalWriteFile, HookWriteFile);

        DetourTransactionCommit();
    } else if (dwReason == DLL_PROCESS_DETACH) {
        DetourTransactionBegin();
        DetourUpdateThread(GetCurrentThread());

        DetourDetach((PVOID*)&OriginalWriteFile, HookWriteFile);

        DetourTransactionCommit();
    }
    return TRUE;
}
