#include "cpp_project_framework/cpp_project_framework.h"

#include "cpp_project_framework/filesystem.h"
#include "cpp_project_framework/gtest.h"


/// Dummy test
TEST(CppProjectFrameworkTest, DummyTest)
{
    EXPECT_TRUE(true);
}

 /// Test for GET_TEST_CASE_NAME() macro
TEST(CppProjectFrameworkGoogleTestTest, GetTestCaseName)
{
    EXPECT_STREQ(GET_TEST_CASE_NAME(), "CppProjectFrameworkGoogleTestTest.GetTestCaseName");
}

/// Test for SCOPED_TRACE_CODE_BLOCK() macro
TEST(CppProjectFrameworkGoogleTestTest, ScopedTraceCodeBlock)
{
    SCOPED_TRACE_CODE_BLOCK(EXPECT_STREQ(GET_TEST_CASE_NAME(), "CppProjectFrameworkGoogleTestTest.ScopedTraceCodeBlock"));
}

/// Test for filesystem header
TEST(CppProjectFrameworkFileSystemTest, FileSystem)
{
    namespace fs = sheepgrass::filesystem;
    EXPECT_TRUE(fs::is_directory(fs::current_path()));
}
