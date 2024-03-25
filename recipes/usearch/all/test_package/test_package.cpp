#include <usearch/usearch.hpp>

using namespace unum::usearch;

int main()
{
  index_gt<cos_gt<float>> index;
  float vec[3] = {0.1, 0.3, 0.2};

  index.reserve(10);
  index.add(42, {&vec[0], 3});

  auto results = index.search({&vec[0], 3}, 5);
  for (std::size_t i = 0; i != results.size(); ++i)
  {
    (void)results[i].member.label;
    (void)results[i].member.vector;
    (void)results[i].distance;
  }

  if (results.size() != 1)
    return EXIT_FAILURE;
  return EXIT_SUCCESS;
}
