#include <cstdlib>
#include <iostream>
#include <tgbot/tgbot.h>

int main() {
    TgBot::CurlHttpClient curlHttpClient;
    TgBot::Bot bot("CONAN_TG_BOT_TOKEN", curlHttpClient, "");
    std::cout << "Bot Token: " << bot.getToken() << std::endl;

    return EXIT_SUCCESS;
}
