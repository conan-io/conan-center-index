#include <iostream>

#include "mosure/inversify.hpp"


namespace inversify = mosure::inversify;

namespace symbols {
    using foo = inversify::Symbol<bool>;
}


int main() {
    inversify::Container<
        symbols::foo
    > container;

    container.bind<symbols::foo>().toConstantValue(true);

    std::cout <<"working: " << container.get<symbols::foo>() << std::endl;
    return 0;
}
