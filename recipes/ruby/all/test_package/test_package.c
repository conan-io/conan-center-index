#include <ruby.h>

int main(int argc, char* argv[]) {
    ruby_sysinit(&argc, &argv);
    RUBY_INIT_STACK;
    ruby_init();

    rb_eval_string("puts 'Hello, ruby!'");

    return EXIT_SUCCESS;
}
