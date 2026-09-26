#include <cstdlib>
#include <rubberband/RubberBandStretcher.h>

int main() {
    RubberBand::RubberBandStretcher stretcher(48000, 1);
    return stretcher.getEngineVersion() > 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
