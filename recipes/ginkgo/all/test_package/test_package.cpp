#include <ginkgo/ginkgo.hpp>

int main(int, char **)
{
    auto refExec = gko::ReferenceExecutor::create();
    auto test = gko::solver::Bicgstab<>::build()
                    .with_preconditioner(gko::preconditioner::Jacobi<>::build().with_max_block_size(1u).on(refExec))
                    .with_criteria(
                        gko::stop::Iteration::build().with_max_iters(1u).on(
                            refExec),
                        gko::stop::ResidualNormReduction<>::build()
                            .with_reduction_factor(1e-10)
                            .on(refExec))
                    .on(refExec);

    std::cout << "test_install: the Ginkgo installation was correctly detected "
                 "and is complete."
              << std::endl;

    return 0;
}
