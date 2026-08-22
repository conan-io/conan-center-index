#include <cstdlib>

#include "scip/scip.h"


int main() {
      SCIP* scip;
      SCIPcreate(&scip);
      SCIPprintVersion(scip, NULL);
      SCIPinfoMessage(scip, NULL, "\n");
      return EXIT_SUCCESS;
}
