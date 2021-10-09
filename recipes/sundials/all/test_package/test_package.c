#include <nvector/nvector_serial.h>
#include <sunmatrix/sunmatrix_dense.h>
#include <sunlinsol/sunlinsol_dense.h>
#include <sundials/sundials_types.h>

int main()
{
  N_Vector y = N_VNew_Serial(1);
  NV_DATA_S(y)[0] = 2.0;
  SUNMatrix A = SUNDenseMatrix(1, 1);
  SUNLinearSolver LS = SUNLinSol_Dense(y, A);

  N_Vector v = N_VNew_Serial(1);;
  N_VScale(2.0, y, v);
  return 0;
}
