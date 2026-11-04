#include <uconfig/uconfig.h>
#include <uconfig/format/Env.h>

#include <cstdlib>
#include <iostream>

struct AppConfig: public uconfig::Config<uconfig::EnvFormat>
{
    uconfig::Variable<unsigned> variable;

    using uconfig::Config<uconfig::EnvFormat>::Config;

    virtual void Init(const std::string& env_prefix) override
    {
        Register<uconfig::EnvFormat>(env_prefix + "_VARIABLE", &variable);
    }
};

int main() {
    AppConfig app_config;
    uconfig::EnvFormat formatter;

    app_config.Parse(formatter, "APP", nullptr);
    std::map<std::string, std::string> config_map;
    app_config.Emit(formatter, "APP", &config_map);

    for (const auto& [name, value] : config_map) {
        std::cout << name << "=" << value << std::endl;
    }
    return 0;
}
