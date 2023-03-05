#include <nabo/nabo.h>

#include <memory>

int main()
{
    Eigen::MatrixXf M = Eigen::MatrixXf::Random(3, 100);
    Eigen::VectorXf q = Eigen::VectorXf::Random(3);
    auto nns = std::unique_ptr<Nabo::NNSearchF>(Nabo::NNSearchF::createKDTreeLinearHeap(M));

    const int K = 5;
    Eigen::VectorXi indices(K);
    Eigen::VectorXf dists2(K);
    nns->knn(q, indices, dists2, K);

    return 0;
}
