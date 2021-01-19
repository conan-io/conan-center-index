#include <tinyspline.h>

int main() {
  tsBSpline spline;
#ifdef TINYSPLINE_API_0_3
  tsStatus status;
  ts_bspline_new(6, 3, 3, TS_OPENED, &spline, &status);
#else
  ts_bspline_new(6, 3, 3, TS_OPENED, &spline);
#endif
  ts_bspline_free(&spline);

  return 0;
}
