#include <iostream>

#ifdef CPP_VALIDATOR_2_0
#include "dracosha/validator/validator.hpp"
#include "dracosha/validator/validate.hpp"
using namespace DRACOSHA_VALIDATOR_NAMESPACE;
#else
#include "hatn/validator/validator.hpp"
#include "hatn/validator/validate.hpp"
using namespace HATN_VALIDATOR_NAMESPACE;
#endif

int main()
{

    // define validator
    auto v=validator(gt,100); // value must be greater than 100

    // validate variables
    error err;

    validate(90,v,err);
    assert(err); // validation failed, 90 is less than 100

    validate(200,v,err);
    assert(!err); // validation succeeded, 200 is greater than 100

    std::cout << "Example 1 done" << std::endl;

    return 0;
}
