#include <aws/core/Aws.h>


int main(void)
{
  Aws::SDKOptions options;
  Aws::InitAPI(options);
  Aws::ShutdownAPI(options);
  return EXIT_SUCCESS;
}
