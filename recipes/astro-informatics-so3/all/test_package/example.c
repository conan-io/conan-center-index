#include <so3/so3_sampling.h>
#include <so3/so3_types.h>

int main(int argc, char *argv[])
{
  so3_parameters_t params;
  params.sampling_scheme = SO3_SAMPLING_MW;
  so3_sampling_weight(&params, 2);
  return 0;
}
