#include "clang/Frontend/FrontendActions.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include <memory>

using namespace clang;
using namespace clang::driver;
using namespace clang::tooling;

static llvm::cl::OptionCategory MyToolCategory("my-tool options");

int main(int argc, const char **argv) {
    auto expectedParser = CommonOptionsParser::create(argc, argv, MyToolCategory);
    if (!expectedParser) {
        llvm::errs() << expectedParser.takeError();
        return 1;
    }
    CommonOptionsParser &op = expectedParser.get();
    ClangTool cltool(op.getCompilations(), op.getSourcePathList());
    cltool.run(newFrontendActionFactory<ASTPrintAction>().get());
    return 0;
}
