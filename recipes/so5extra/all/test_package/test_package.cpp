/*
 * Usage of select() with send_case() for calculation of Fibonacci numbers.
 */

#include <so_5_extra/mchains/fixed_size.hpp>

#include <so_5/all.hpp>

#include <chrono>

using namespace std;
using namespace std::chrono_literals;
using namespace so_5;

struct quit {};

void fibonacci( mchain_t values_ch, mchain_t quit_ch )
{
  int x = 0, y = 1;
  mchain_select_result_t r;
  do
  {
    r = select(
      from_all().handle_n(1),
      // Sends a new message of type 'int' with value 'x' inside
      // when values_ch is ready for a new outgoing message.
      send_case( values_ch, message_holder_t<int>::make(x),
          [&x, &y] { // This block of code will be called after the send().
            auto old_x = x;
            x = y; y = old_x + y;
          } ),
      // Receive a 'quit' message from quit_ch if it is here.
      receive_case( quit_ch, [](quit){} ) );
  }
  // Continue the loop while we send something and receive nothing.
  while( r.was_sent() && !r.was_handled() );
}

int main()
{
  wrapped_env_t sobj;

  thread fibonacci_thr;
  auto thr_joiner = auto_join( fibonacci_thr );

  // The chain for Fibonacci number will have limited capacity.
  auto values_ch = extra::mchains::fixed_size::create_mchain<2>(
      sobj.environment(),
      1s, // Wait no more than 1s on overflow.
      mchain_props::overflow_reaction_t::abort_app );

  // The chain for `quit` signal should contant no more than one message.
  auto quit_ch = extra::mchains::fixed_size::create_mchain<1>(
      sobj.environment(),
      mchain_props::overflow_reaction_t::drop_newest );

  auto ch_closer = auto_close_drop_content( values_ch, quit_ch );

  fibonacci_thr = thread{ fibonacci, values_ch, quit_ch };

  // Read the first 10 numbers from values_ch.
  receive( from( values_ch ).handle_n( 10 ),
      // And show every number to the standard output.
      []( int v ) { cout << v << ' '; } );

  send< quit >( quit_ch );

  cout << std::endl;
}
