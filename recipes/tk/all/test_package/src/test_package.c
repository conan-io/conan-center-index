#include <stdlib.h>
#include <string.h>

#include <tcl.h>
#include <tk.h>

int main() {
    Tcl_Interp *interp = Tcl_CreateInterp();
    if (Tcl_Init(interp) != TCL_OK) {
        fprintf(stderr ,"Tcl_Init error: %s\n" ,Tcl_GetStringResult(interp));
        return EXIT_FAILURE;
    }
    Tk_Uid id = Tk_GetUid("hello");
    Tcl_Finalize();
    fprintf(stderr, "Test package success.\n");
    return EXIT_SUCCESS;
}
