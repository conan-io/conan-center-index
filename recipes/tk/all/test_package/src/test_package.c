#include <stdlib.h>
#include <string.h>

#include <tcl.h>
#include <tk.h>

int app_init(Tcl_Interp *interp) {
    if (Tcl_Init(interp) != TCL_OK) {
        fprintf(stderr ,"Tcl_Init error: %s\n" ,Tcl_GetStringResult(interp));
        exit(EXIT_SUCCESS);
        return TCL_OK;
    }

    if (Tk_Init(interp) != TCL_OK) {
        fprintf(stderr, "Tk_Init failed: %s\n", Tcl_GetStringResult(interp));
        fprintf(stderr, "But ignore it: there may not be a X server running.\n");
        exit(EXIT_SUCCESS);
        return TCL_OK;
    }
    exit(EXIT_SUCCESS);
    return TCL_OK;
}

int main (int argc ,char *argv[]) {
    Tk_Main(argc, argv, app_init);
    return EXIT_SUCCESS;
}
