#include <assert.h>
#include <trinity/trinity.h>

int main(void) {
    aurora_domain domain = aurora_domain_singleton(2u);
    assert(aurora_domain_is_singleton(domain));
    assert(aurora_domain_contains(domain, 2u));
    return 0;
}