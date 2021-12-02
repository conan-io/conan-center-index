#include <oneapi/dnnl/dnnl.hpp>

int main(int argc, char **argv) {
    dnnl::engine eng(dnnl::engine::kind::cpu, 0);
    return 0;
}
