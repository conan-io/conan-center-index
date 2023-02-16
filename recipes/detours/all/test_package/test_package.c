#include <windows.h>
#include <detours.h>

#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define ARRAY_SIZE(ARR)  ((sizeof(ARR))/sizeof(*(ARR)))

int CDECL main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Need at least one argument\n");
        return 1;
    }

    SECURITY_ATTRIBUTES saAttr;
    saAttr.nLength = sizeof(SECURITY_ATTRIBUTES);
    saAttr.bInheritHandle = TRUE;
    saAttr.lpSecurityDescriptor = NULL;

    HANDLE hChildStd_IN_Rd = NULL;
    HANDLE hChildStd_IN_Wr = NULL;
    HANDLE hChildStd_OUT_Rd = NULL;
    HANDLE hChildStd_OUT_Wr = NULL;

    if (!CreatePipe(&hChildStd_OUT_Rd, &hChildStd_OUT_Wr, &saAttr, 0)) {
        fprintf(stderr, "StdoutRd CreatePipe\n");
        return 1;
    }
    if (!SetHandleInformation(hChildStd_OUT_Rd, HANDLE_FLAG_INHERIT, 0)) {
        fprintf(stderr, "Stdout SetHandleInformation");
    }
    if (!CreatePipe(&hChildStd_IN_Rd, &hChildStd_IN_Wr, &saAttr, 0)) {
        fprintf(stderr, "Stdin CreatePipe");
    }
    if (!SetHandleInformation(hChildStd_IN_Wr, HANDLE_FLAG_INHERIT, 0)) {
        fprintf(stderr, "Stdin SetHandleInformation");
    }

    STARTUPINFOA si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&si, sizeof(si));
    ZeroMemory(&pi, sizeof(pi));
    si.cb = sizeof(si);
    si.hStdError = hChildStd_OUT_Wr;
    si.hStdOutput = hChildStd_OUT_Wr;
    si.hStdInput = hChildStd_IN_Rd;
    si.dwFlags |= STARTF_USESTDHANDLES;

    char exe[1024];
    strcpy_s(exe, sizeof(exe), argv[1]);
    strcat_s(exe, sizeof(exe), "\\");
    strcat_s(exe, sizeof(exe), "victim.exe");

    char command[1024];
    strcpy_s(command, sizeof(command), exe);

    char hook_dll[1024];;
    strcpy_s(hook_dll, sizeof(hook_dll), argv[1]);
    strcat_s(hook_dll, sizeof(hook_dll), "\\");
    strcat_s(hook_dll, sizeof(hook_dll), "hook.dll");
    const char* hooks[] = {
        hook_dll,
    };

    printf("Starting \"%s`\n", exe);
    printf(" with command: \"%s`\n", command);
    printf(" with dlls:\n");
    for (size_t i = 0; i < ARRAY_SIZE(hooks); ++i) {
        printf("  - %s\n", hooks[i]);
    }
    fflush(stdout);

    DWORD dwFlags = CREATE_DEFAULT_ERROR_MODE | CREATE_SUSPENDED | CREATE_NO_WINDOW;

    SetLastError(0);
    if (!DetourCreateProcessWithDllsA(
            exe,
            command,
            NULL,
            NULL,
            TRUE,
            dwFlags,
            NULL,
            NULL,
            &si,
            &pi,
            ARRAY_SIZE(hooks),
            hooks,
            NULL)) {
        DWORD dwError = GetLastError();
        printf("%s: DetourCreateProcessWithDllEx failed: %ld\n", argv[0], dwError);
        if (dwError == ERROR_INVALID_HANDLE) {
#if DETOURS_64BIT
            printf("%s: Can't detour a 32-bit target process from a 64-bit parent process.\n", argv[0]);
#else
            printf("%s: Can't detour a 64-bit target process from a 32-bit parent process.\n", argv[0]);
#endif
        }
        printf("ERROR");
        return 1;
    }

    ResumeThread(pi.hThread);
    CloseHandle(hChildStd_OUT_Wr);
    CloseHandle(hChildStd_IN_Rd);

    for (;;)
    {
        DWORD dwRead, dwWritten;
        char chBuf[256];
        BOOL bSuccess = ReadFile( hChildStd_OUT_Rd, chBuf, sizeof(chBuf), &dwRead, NULL);
        if( ! bSuccess || dwRead == 0 ) {
            break;
        }

        bSuccess = WriteFile(GetStdHandle(STD_OUTPUT_HANDLE), chBuf,
                             dwRead, &dwWritten, NULL);
        if (!bSuccess) {
            break;
        }
    }

    WaitForSingleObject(pi.hProcess, INFINITE);

    DWORD dwResult = 0;
    if (!GetExitCodeProcess(pi.hProcess, &dwResult)) {
        printf("%s: GetExitCodeProcess failed: %ld\n", argv[0], GetLastError());
        return 9010;
    }

    return dwResult;
}
