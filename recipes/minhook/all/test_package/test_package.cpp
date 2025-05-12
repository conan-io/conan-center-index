#include <Windows.h>

#include <iostream>

#include "MinHook.h"

typedef int(WINAPI *MESSAGEBOXW)(HWND, LPCWSTR, LPCWSTR, UINT);

// Pointer for calling original MessageBoxW.
MESSAGEBOXW fpMessageBoxW = NULL;

// Dummy MessageBox function for testing.
int WINAPI DummyMessageBoxW(HWND hWnd, LPCWSTR lpText, LPCWSTR lpCaption, UINT uType)
{
    const int box_width = 40;
    std::wstring text(lpText);
    std::wstring caption(lpCaption);

    // Top border
    std::wcout << "+" << std::wstring(box_width - 2, '-') << "+\n";

    // Caption
    std::wcout << "| " << caption << std::wstring(box_width - 3 - caption.size(), ' ') << "|\n";
    std::wcout << "| " << std::wstring(box_width - 4, '=') << " |\n";

    // Text
    std::wcout << "| " << text << std::wstring(box_width - 3 - text.size(), ' ') << "|\n";

    // Bottom border
    std::wcout << "+" << std::wstring(box_width - 2, '-') << "+\n";

    return IDOK;  // The OK button was selected.
}

// Detour function which overrides MessageBoxW.
int WINAPI DetourMessageBoxW(HWND hWnd, LPCWSTR lpText, LPCWSTR lpCaption, UINT uType)
{
    return fpMessageBoxW(hWnd, L"Hooked!", lpCaption, uType);
}

int main()
{
    // Initialize MinHook.
    if (MH_Initialize() != MH_OK) {
        return 1;
    }

    // Create a hook for MessageBoxW, in disabled state.
    if (MH_CreateHook(&DummyMessageBoxW, &DetourMessageBoxW, reinterpret_cast<LPVOID *>(&fpMessageBoxW)) != MH_OK) {
        return 1;
    }

    // Enable the hook for MessageBoxW.
    if (MH_EnableHook(&DummyMessageBoxW) != MH_OK) {
        return 1;
    }

    // Expected to tell "Hooked!".
    DummyMessageBoxW(NULL, L"Not hooked...", L"MinHook Sample", MB_OK);

    // Disable the hook for MessageBoxW.
    if (MH_DisableHook(&DummyMessageBoxW) != MH_OK) {
        return 1;
    }

    // Expected to tell "Not hooked...".
    DummyMessageBoxW(NULL, L"Not hooked...", L"MinHook Sample", MB_OK);

    // Uninitialize MinHook.
    if (MH_Uninitialize() != MH_OK) {
        return 1;
    }

    return 0;
}
