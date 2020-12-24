#include <acado/acado_code_generation.hpp>
#include <cstdlib>

USING_NAMESPACE_ACADO

int main(int argc, char *argv[])
{
  const double dt = 0.1;
  const int N = 10;
  const int Ni = 1;

  DifferentialState pos_x;
  DifferentialState pos_y;
  DifferentialState velocity;
  DifferentialState heading;

  Control acceleration;
  Control steering_angle;

  DifferentialEquation kinematics;
  kinematics << dot(pos_x) == velocity * cos(heading);
  kinematics << dot(pos_y) == velocity * sin(heading);
  kinematics << dot(velocity) == acceleration;
  kinematics << dot(heading) == velocity * steering_angle;

  OCP control_problem(0.0, N * dt, N);

  control_problem.subjectTo(kinematics);

  control_problem.subjectTo(-1.0 <= heading <= 1.0);
  control_problem.subjectTo(0.0 <= velocity <= 30.0);
  control_problem.subjectTo(-1.0 <= steering_angle <= 1.0);
  control_problem.setNOD(3);

  control_problem.subjectTo(-3.0 <= acceleration <= 3.0);

  Function observation;
  observation << velocity;
  observation << steering_angle;
  observation << acceleration;

  BMatrix weights = eye<bool>(observation.getDim());

  control_problem.minimizeLSQ(weights, observation);

  Function terminal_observation;
  terminal_observation << velocity;

  BMatrix terminal_weights = eye<bool>(terminal_observation.getDim());

  control_problem.minimizeLSQEndTerm(terminal_weights, terminal_observation);

  OCPexport mpc(control_problem);
  mpc.set(INTEGRATOR_TYPE, INT_RK4);
  mpc.set(NUM_INTEGRATOR_STEPS, N * Ni);
  mpc.set(QP_SOLVER, QP_QPOASES);
  mpc.set(HESSIAN_APPROXIMATION, GAUSS_NEWTON);
  mpc.set(DISCRETIZATION_TYPE, MULTIPLE_SHOOTING);
  mpc.set(GENERATE_TEST_FILE, NO);
  mpc.set(GENERATE_MAKE_FILE, NO);
  mpc.set(HOTSTART_QP, YES);
  mpc.set(SPARSE_QP_SOLUTION, CONDENSING);
  mpc.set(FIX_INITIAL_STATE, YES);
  mpc.set(CG_USE_VARIABLE_WEIGHTING_MATRIX, YES);

  if (mpc.exportCode(argv[1]) != SUCCESSFUL_RETURN)
  {
    return EXIT_FAILURE;
  }

  return EXIT_SUCCESS;
}
