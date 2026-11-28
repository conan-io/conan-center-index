#include <llcpp/llcpp.hpp>

int main() {
    llcpp::Config config;
    llcpp::Bot bot(config);
    bot.on_text([](llcpp::Context&) { return true; });
    return bot.dispatch(llcpp::Update{}) ? 0 : 1;
}
