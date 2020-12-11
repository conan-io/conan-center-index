#include "semver.h"

int main() {
	semver_t v = {};
	semver_bump (&v);

	const char ver[] = "1.0.0";
	semver_is_valid(ver);
}
