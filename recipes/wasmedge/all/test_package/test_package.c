#include <stdlib.h>
#include <wasmedge/wasmedge.h>

int main() {
    WasmEdge_ConfigureContext *ConfCxt = WasmEdge_ConfigureCreate();
    WasmEdge_ConfigureAddHostRegistration(ConfCxt, WasmEdge_HostRegistration_Wasi);
    WasmEdge_VMContext *VMCxt = WasmEdge_VMCreate(ConfCxt, NULL);

    WasmEdge_String FuncName = WasmEdge_StringCreateByCString("fib");

    WasmEdge_VMDelete(VMCxt);
    WasmEdge_ConfigureDelete(ConfCxt);
    WasmEdge_StringDelete(FuncName);

    return EXIT_SUCCESS;
}
