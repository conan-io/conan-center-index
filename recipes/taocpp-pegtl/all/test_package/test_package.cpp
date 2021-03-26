#include <string>
#include <tao/pegtl.hpp>
#include <tao/pegtl/contrib/tracer.hpp>

namespace gr {
   using namespace tao::pegtl;

   struct C;
   struct B : seq< one< '(' >, C, one< '|' >, C, one< ')' > > {};
   struct H : seq< one< '|' >, C > {};
   struct C : seq< sor< B, plus< range< '1','2' > > >, star< H > > {};
}

int main() {
   std::string content = "(1|2)";
   tao::pegtl::string_input<> in( content, "from_content" );
   tao::pegtl::parse< gr::C, tao::pegtl::nothing, tao::pegtl::tracer >( in );
   return 0;
}
