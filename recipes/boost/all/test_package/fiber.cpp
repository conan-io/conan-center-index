#include <boost/fiber/all.hpp>

int main() {
    boost::fibers::fiber f([]{});
    f.join();
    return 0;
}
