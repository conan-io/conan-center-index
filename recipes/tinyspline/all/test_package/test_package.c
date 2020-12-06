#include <tinyspline.h>

int main() {
  tsBSpline spline;
  ts_bspline_new(6, 3, 3, TS_OPENED, &spline);
  ts_bspline_free(&spline);

  return 0;
}
