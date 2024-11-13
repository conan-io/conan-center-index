#include <iostream>
#include <string>

#include "WinReg/WinReg.hpp"

int main() {
    auto subkey = L"Environment";
    winreg::RegKey key{HKEY_CURRENT_USER, subkey};
    auto value = key.GetStringValue(L"Path");
    std::wcout << value << std::endl;
    return 0;
}
