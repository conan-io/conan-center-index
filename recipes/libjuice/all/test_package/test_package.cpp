#include <cstdlib>
#include <juice/juice.h>

int main(void) {
    juice_config config;
    juice_agent_t * agent = juice_create(&config);
    juice_destroy(agent);
    return EXIT_SUCCESS;
}
