#include <cstdio>
#include <cstdint>
#include <string>
#include "tweeny/tweeny.h"


int main(void) {
    auto helloworld = tweeny::from('h','e','l','l','o').to('w','o','r','l','d').during(2);
    for (int i = 0; i < 2; i++) {
        for (char c : helloworld.step(1)) { printf("%c", c); }
        printf("\n");
    }
}
