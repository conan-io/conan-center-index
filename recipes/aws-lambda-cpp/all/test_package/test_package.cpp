#include <iostream>
#include "aws/lambda-runtime/version.h"

int main()
{
    std::cout << aws::lambda_runtime::get_version() << '\n';

    return 0;
}
