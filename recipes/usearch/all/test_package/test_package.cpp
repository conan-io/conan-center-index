#include <usearch/index.hpp>
#include <usearch/index_dense.hpp>
#include <usearch/index_plugins.hpp>

int main()
{
    using namespace unum::usearch;

    metric_punned_t metric(256, metric_kind_t::l2sq_k, scalar_kind_t::f32_k);
    index_dense_t index = index_dense_t::make(metric);
    float vec[3] = {0.1, 0.3, 0.2};

    index.reserve(10);
    index.add(42, &vec[0]);
    auto results = index.search(&vec[0], 5);

    if (results.size() != 1)
        return EXIT_FAILURE;
    return EXIT_SUCCESS;
}
