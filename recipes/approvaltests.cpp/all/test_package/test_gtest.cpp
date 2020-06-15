#define APPROVALS_GOOGLETEST
#include "ApprovalTests.hpp"

TEST(Package, GTest) {
    SUCCEED();

    auto defaultReporterDisposer =
        ApprovalTests::Approvals::useAsFrontLoadedReporter(
            std::make_shared<ApprovalTests::QuietReporter>());

    ApprovalTests::Approvals::verify("Hello Approvals");
}
