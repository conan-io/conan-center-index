#include <llvm/ExecutionEngine/Interpreter.h>
#include <llvm/ExecutionEngine/GenericValue.h>
#include <llvm/ExecutionEngine/ExecutionEngine.h>
#include <llvm/IRReader/IRReader.h>
#include <llvm/IR/LLVMContext.h>
#include <llvm/Support/TargetSelect.h>
#include <llvm/Support/SourceMgr.h>

#include <memory>


int main(int argc, char const* argv[]) {
    if (argc < 2)
        return 0;

    llvm::InitializeNativeTarget();
    llvm::SMDiagnostic smd;
    llvm::LLVMContext context;
    std::string error;

    llvm::EngineBuilder engine_builder{
        llvm::parseIRFile(argv[1], smd, context)
    };
    engine_builder.setEngineKind(llvm::EngineKind::Interpreter);
    engine_builder.setErrorStr(&error);

    auto execution_engine = std::unique_ptr<llvm::ExecutionEngine>(
        engine_builder.create()
    );
    execution_engine->runStaticConstructorsDestructors(false);

    auto test_function = execution_engine->FindFunctionNamed("test");
    auto result = execution_engine->runFunction(
        test_function,
        llvm::ArrayRef<llvm::GenericValue>()
    );
    return result.IntVal.getSExtValue();
}
