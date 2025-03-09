#include <vilib/feature_detection/fast/fast_common.h>
#include <vilib/feature_detection/fast/fast_gpu.h>

using namespace vilib;

#define PYRAMID_LEVELS      1
#define PYRAMID_MIN_LEVEL   0
#define PYRAMID_MAX_LEVEL   PYRAMID_LEVELS
#define FAST_EPSILON        10.0f
#define FAST_MIN_ARC_LENGTH 10
#define FAST_SCORE          SUM_OF_ABS_DIFF_ON_ARC
#define HORIZONTAL_BORDER   0
#define VERTICAL_BORDER     0
#define CELL_SIZE_WIDTH     32
#define CELL_SIZE_HEIGHT    32

int main() {
  int width = 512;
  int height = 512;
  FASTGPU(width, height, CELL_SIZE_WIDTH, CELL_SIZE_HEIGHT, PYRAMID_MIN_LEVEL,
          PYRAMID_MAX_LEVEL, HORIZONTAL_BORDER, VERTICAL_BORDER, FAST_EPSILON,
          FAST_MIN_ARC_LENGTH, FAST_SCORE);
}
