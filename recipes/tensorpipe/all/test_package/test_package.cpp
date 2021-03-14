#include <tensorpipe/tensorpipe.h>

#include <memory>

int main() {
    auto context = std::make_shared<tensorpipe::Context>();
    context->registerTransport(0, "uv", tensorpipe::transport::uv::create());
    return 0;
}
