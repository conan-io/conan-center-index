#include <iostream>
#include <Windows.h>
#include "syscall.hpp"

#ifndef NT_SUCCESS
#define NT_SUCCESS(Status) (((NTSTATUS)(Status)) >= 0)
#endif

int main() 
{
    using SyscallManager_t = syscall::Manager<
        syscall::policies::allocation::virtual_memory, 
        syscall::policies::generation::direct
    >;

    SyscallManager_t syscallManager;
    if (!syscallManager.initialize())
    {
        std::cerr << "test failed: syscall manager initialization failed!\n";
        return 1;
    }

    std::cout << "syscall manager initialized successfully.\n";

    PVOID pBaseAddress = nullptr;
    SIZE_T uSize = 0x1000;
    NTSTATUS status = -1;

    status = syscallManager.invoke<NTSTATUS>(
        SYSCALL_ID("NtAllocateVirtualMemory"),
        NtCurrentProcess(),
        &pBaseAddress,
        0, 
        &uSize,
        MEM_COMMIT | MEM_RESERVE,
        PAGE_READWRITE
    );
    
    std::cout << "ntAllocateVirtualMemory status: 0x" << std::hex << status << std::dec << std::endl;

    if (!NT_SUCCESS(status) || !pBaseAddress) {
        std::cerr << "test failed: NtAllocateVirtualMemory failed or returned null address.\n";
        return 1;
    }

    std::cout << "allocation successful at 0x" << std::hex << pBaseAddress << std::dec << std::endl;
    std::cout << "test passed!" << std::endl;
    
    uSize = 0;
    syscallManager.invoke<NTSTATUS>(
        SYSCALL_ID("NtFreeVirtualMemory"),
        NtCurrentProcess(),
        &pBaseAddress,
        &uSize,
        MEM_RELEASE
    );

    return 0;
}