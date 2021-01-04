#define APPROVALS_DOCTEST
#include "ApprovalTests.hpp"

TEST_CASE("Package") {
    CHECK(true);

    auto defaultReporterDisposer =
        ApprovalTests::Approvals::useAsFrontLoadedReporter(
            std::make_shared<ApprovalTests::QuietReporter>());

    ApprovalTests::Approvals::verify("Hello Approvals");
}
