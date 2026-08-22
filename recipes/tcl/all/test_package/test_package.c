#include <tcl.h>

#include <stdlib.h>
#include <string.h>

// from https://wiki.tcl-lang.org/page/How+to+embed+Tcl+in+C+applications

static int
StringCatCmd(
    ClientData dummy,                /* Not used. */
    Tcl_Interp *interp,                /* Current interpreter. */
    int objc,                        /* Number of arguments. */
    Tcl_Obj *const objv[])        /* Argument objects. */
{
    int i;
    Tcl_Obj *objResultPtr;

    if (objc < 2) {
        /*
         * If there are no args, the result is an empty object.
         * Just leave the preset empty interp result.
         */
        return TCL_OK;
    }
    if (objc == 2) {
        /*
         * Other trivial case, single arg, just return it.
         */
        Tcl_SetObjResult(interp, objv[1]);
        return TCL_OK;
    }
    objResultPtr = objv[1];
    if (Tcl_IsShared(objResultPtr)) {
        objResultPtr = Tcl_DuplicateObj(objResultPtr);
    }
    for(i = 2;i < objc;i++) {
        Tcl_AppendObjToObj(objResultPtr, objv[i]);
    }
    Tcl_SetObjResult(interp, objResultPtr);

    return TCL_OK;
}

Tcl_Command ExtendTcl (Tcl_Interp *interp) {
    return Tcl_CreateObjCommand(
        interp, "stringcat", StringCatCmd, NULL, NULL);
}

int main (int argc ,char *argv[]) {
    Tcl_FindExecutable(argv[0]);
    Tcl_Interp *interp = Tcl_CreateInterp();
    if (Tcl_Init(interp) != TCL_OK) {
        fprintf(stderr ,"Tcl_Init error: %s\n" ,Tcl_GetStringResult(interp));
        return EXIT_FAILURE;
    }
    Tcl_Command cmdToken = ExtendTcl(interp);

    if (Tcl_Eval(interp, "stringcat \"hello\" \" \" \"world\" \"\n\"") != TCL_OK) {
        fprintf(stderr, "Tc_Eval failed: %s", Tcl_GetStringResult(interp));
        return EXIT_FAILURE;
    }

    const char *res = Tcl_GetStringResult(interp);
    if (strcmp("hello world\n", res)) {
        fprintf(stderr, "concatenated string does not match\n");
        return EXIT_FAILURE;
    }

    if (Tcl_DeleteCommandFromToken(interp, cmdToken) == -1) {
        fprintf(stderr, "Tcl_DeleteCommand failed: %s", Tcl_GetStringResult(interp));
        return EXIT_FAILURE;
    }
    Tcl_Finalize();
    return EXIT_SUCCESS;
}
