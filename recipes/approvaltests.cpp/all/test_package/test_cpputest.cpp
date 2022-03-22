#define APPROVALS_CPPUTEST
#include "ApprovalTests.hpp"

#include "CppUTest/TestHarness.h"

using namespace ApprovalTests;

TEST_GROUP(Group){};

TEST(Group, Package)
{
    auto defaultReporterDisposer =
        ApprovalTests::Approvals::useAsFrontLoadedReporter(
            std::make_shared<ApprovalTests::QuietReporter>());

    ApprovalTests::Approvals::verify("Hello Approvals");
}
