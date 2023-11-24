#include <launchdarkly/client_side/client.hpp>
#include <launchdarkly/context_builder.hpp>

#include <iostream>
#include <cstring>

// Set MOBILE_KEY to your LaunchDarkly mobile key.
#define MOBILE_KEY "12345"

// Set FEATURE_FLAG_KEY to the feature flag key you want to evaluate.
#define FEATURE_FLAG_KEY "my-boolean-flag"

// Set INIT_TIMEOUT_MILLISECONDS to the amount of time you will wait for
// the client to become initialized.
#define INIT_TIMEOUT_MILLISECONDS 3000

using namespace launchdarkly;

int main() {
    if (!strlen(MOBILE_KEY)) {
        printf(
            "*** Please edit main.c to set MOBILE_KEY to your LaunchDarkly "
            "mobile key first\n\n");
        return 1;
    }

    auto config = client_side::ConfigBuilder(MOBILE_KEY).Build();
    if (!config) {
        std::cout << "error: config is invalid: " << config.error() << '\n';
        return 1;
    }

    auto context =
        ContextBuilder().Kind("user", "example-user-key").Name("Sandy").Build();

    auto client = client_side::Client(std::move(*config), std::move(context));

    auto start_result = client.StartAsync();
    auto status = start_result.wait_for(
        std::chrono::milliseconds(INIT_TIMEOUT_MILLISECONDS));
    if (status == std::future_status::ready) {
        if (start_result.get()) {
            std::cout << "*** SDK successfully initialized!\n\n";
        } else {
            std::cout << "*** SDK failed to initialize (this is expected)\n";
            return 0;
        }
    } else {
        std::cout << "*** SDK initialization didn't complete in "
                  << INIT_TIMEOUT_MILLISECONDS << "ms\n";
        return 1;
    }

    bool flag_value = client.BoolVariation(FEATURE_FLAG_KEY, false);

    std::cout << "*** Feature flag '" << FEATURE_FLAG_KEY << "' is "
              << (flag_value ? "true" : "false") << " for this user\n\n";

    return 0;
}
