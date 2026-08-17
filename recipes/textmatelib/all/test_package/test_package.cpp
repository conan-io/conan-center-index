#include <tml/c_api.h>
#include <cstdlib>

int main() {
    TextMateOnigLib lib = textmate_oniglib_create();
    if (!lib) {
        return EXIT_FAILURE;
    }

    TextMateRegistry registry = textmate_registry_create(lib);
    if (!registry) {
        textmate_oniglib_dispose(lib);
        return EXIT_FAILURE;
    }

    textmate_registry_dispose(registry);
    textmate_oniglib_dispose(lib);
    return EXIT_SUCCESS;
}