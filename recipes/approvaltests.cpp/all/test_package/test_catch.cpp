#define APPROVALS_CATCH
#include "ApprovalTests.hpp"

TEST_CASE("Package") {
    REQUIRE(true);

    auto defaultReporterDisposer =
        ApprovalTests::Approvals::useAsFrontLoadedReporter(
            std::make_shared<ApprovalTests::QuietReporter>());

    ApprovalTests::Approvals::verify("Hello Approvals");
}
