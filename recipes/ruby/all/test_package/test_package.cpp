#include <ruby.h>

// when --static-linked-ext is used, ruby defines EXTSTATIC as 1
#if defined(EXTSTATIC) && EXTSTATIC
#  define RUBY_STATIC_LINKED_EXT2
#else
#  undef RUBY_STATIC_LINKED_EXT2
#endif

int main(int argc, char* argv[]) {
  ruby_sysinit(&argc, &argv);
  RUBY_INIT_STACK;
  ruby_init();

  rb_eval_string("puts 'Hello, ruby!'");

#ifdef RUBY_STATIC_RUBY
  rb_eval_string("puts 'Ruby itself is statically linked'");
#else
  rb_eval_string("puts 'Ruby itself is dynamically linked'");
#endif

#ifdef RUBY_STATIC_LINKED_EXT
  rb_eval_string("puts 'Ruby has statically linked extensions'");
#else
  rb_eval_string("puts 'Ruby has dynamically linked extensions'");
#endif

#ifdef RUBY_STATIC_LINKED_EXT2
  rb_eval_string("puts 'Ruby has statically linked extensions (EXTSTATIC)'");
#else
  rb_eval_string("puts 'Ruby has dynamically linked extensions (EXTSTATIC)'");
#endif

#ifdef RUBY_STATIC_RUBY
  rb_provide("bigdecimal");
  rb_provide("bigdecimal.so");
#else
  ruby_init_loadpath();
#endif

  rb_eval_string(R"(
       begin
         (require 'bigdecimal')
         puts "I can correctly load one of the extension gems - bigdecimal"
       rescue Exception => e
         puts
         puts "Error: #{e.message}"
         puts "Backtrace:\n\t" + e.backtrace.join("\n\t")
         raise
       end
     )");

  ruby_finalize();

  return EXIT_SUCCESS;
}
