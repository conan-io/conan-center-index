#include <stdlib.h>
#include <string.h>

#include <tcl.h>
#include <tk.h>

int main (int argc ,char *argv[]) {
    Tcl_FindExecutable(argv[0]);
    Tcl_Interp *interp = Tcl_CreateInterp();
    if (Tcl_Init(interp) != TCL_OK) {
        fprintf(stderr ,"Tcl_Init error: %s\n" ,Tcl_GetStringResult(interp));
        return EXIT_FAILURE;
    }

    if (Tk_Init(interp) != TCL_OK) {
        fprintf(stderr, "Tk_Init failed: %s\n", Tcl_GetStringResult(interp));
        fprintf(stderr, "But ignore it: there may not be a X server running.\n");
        return EXIT_SUCCESS;
    }

    Tcl_Finalize();
    return EXIT_SUCCESS;
}
