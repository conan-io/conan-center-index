#include "hermes/hermes.h"
#include "hermes/Public/RuntimeConfig.h"

int main() {
    hermes::vm::RuntimeConfig config;
    auto rt = facebook::hermes::makeHermesRuntime(config);

    rt->global().getPropertyAsFunction(*rt, "eval").call(*rt, "var q = 0;");

    return 0;
}
