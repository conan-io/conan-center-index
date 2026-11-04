#include <stdlib.h>


#include <xmlsec/xmlsec.h>


int main(int argc, char **argv) {
    /* Init xmlsec library */
    if(xmlSecInit() < 0) {
        fprintf(stderr, "Error: xmlsec initialization failed.\n");
        return(-1);
    }

    /* Check loaded library version */
    if(xmlSecCheckVersion() != 1) {
        fprintf(stderr, "Error: loaded xmlsec library version is not compatible.\n");
        return(-1);
    }

    if(xmlSecCheckVersionExact() != 1) {
        fprintf(stderr, "Error: loaded xmlsec library version is not exact.\n");
        return(-1);
    }
    
    /* Shutdown xmlsec library */
    xmlSecShutdown();    
    return(0);
}
