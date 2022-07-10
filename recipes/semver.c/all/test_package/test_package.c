#include <stdio.h>
#include "semver.h"

int main(void) {
	semver_t v;
	semver_bump (&v);

	const char ver[] = "1.0.0";
	const int valid = semver_is_valid(ver);
	printf("%s is valid: %d\n", ver, valid);

	return 0;
}
