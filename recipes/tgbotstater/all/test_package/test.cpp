#include "tg_stater/state_storage/common.hpp"
#include "tg_stater/state_storage/memory.hpp"
#include <tgbot/Bot.h>
#include <tg_stater/bot.hpp>
#include <tg_stater/handler/handler.hpp>

#include <variant>
#include <vector>

struct StateA {
    std::vector<int> v;
};

struct StateB {
    int x;
};

using State = std::variant<StateA, StateB>;
using StateManager = tg_stater::StateProxy<tg_stater::MemoryStateStorage<State>>;

int main() {
    using namespace tg_stater;

    TgBot::Bot bot{""};

    static constexpr const char helpCmd[] = "help";
    auto help = [](StateA&, const TgBot::Message& m, const TgBot::Api& bot, const StateManager& stateManager) {
        bot.sendMessage(m.chat->id, "This is a test bot");
        stateManager.put(StateB{1});
    };

    // Test for compilation
    Setup<State>::Stater<
        Handler<Events::Command{helpCmd}, help>
    > stater{};
    // No run since no token provided
    // stater.start(std::move(bot));
}
