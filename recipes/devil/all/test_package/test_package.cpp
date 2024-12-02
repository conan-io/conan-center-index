#include <cstdlib>
#include <IL/il.h>
#include <IL/ilu.h>
#include <IL/ilut.h>


int main() {
    ilInit();
    iluGetImageInfo(0);

    ilShutDown();

    return EXIT_SUCCESS;
}
