#include <ruby.h>

int main() {
    ruby_init();
    rb_eval_string("puts 'Hello, ruby!'");

    return EXIT_SUCCESS;
}
