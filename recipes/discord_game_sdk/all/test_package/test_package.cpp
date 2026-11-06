#include <cstdlib>
#include <iostream>

#include <discord_game_sdk.h>
#include <discord.h>

int main()
{
    discord::Core *core{};
    auto result = discord::Core::Create(310270644849737729, DiscordCreateFlags_Default, &core);
    std::cout << "C++ wrapper Create result: " << static_cast<int>(result) << std::endl;

    struct DiscordCreateParams params;
    DiscordCreateParamsSetDefault(&params);
    params.client_id = 310270644849737729;
    params.flags = DiscordCreateFlags_Default;
    struct IDiscordCore *c_core = nullptr;
    enum EDiscordResult c_result = DiscordCreate(DISCORD_VERSION, &params, &c_core);
    std::cout << "C API DiscordCreate result: " << static_cast<int>(c_result) << std::endl;

    return EXIT_SUCCESS;
}
