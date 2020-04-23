#define BOOST_TEST_MODULE Module

//#include <boost/test/unit_test.hpp> // static or dynamic boost build
#include <boost/test/included/unit_test.hpp> // header only boost

#define APPROVALS_BOOSTTEST
#include "ApprovalTests.hpp"

BOOST_AUTO_TEST_SUITE(Suite)

BOOST_AUTO_TEST_CASE(TestCase)
{
    BOOST_CHECK(true);
    ApprovalTests::Approvals::verify("Hello Approvals", ApprovalTests::QuietReporter());
}

BOOST_AUTO_TEST_SUITE_END()
