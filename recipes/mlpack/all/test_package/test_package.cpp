#include <mlpack/methods/random_forest.hpp>

using namespace mlpack;

int main()
{
    const size_t numClasses = 2;
    const size_t minimumLeafSize = 5;
    const size_t numTrees = 10;

    arma::mat dataset;
    arma::Row<size_t> labels, predictions;
    RandomForest<GiniGain, RandomDimensionSelect> rf(dataset, labels, numClasses, numTrees, minimumLeafSize);
    rf.Classify(dataset, predictions);
}
