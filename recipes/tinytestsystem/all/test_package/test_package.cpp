#include <tts/tts.hpp>

TTS_CASE( "Check basic tests" )
{
  TTS_EXPECT(true);
  TTS_EXPECT_NOT(false);

  int x = 0;
  TTS_EQUAL( x, x );
  TTS_NOT_EQUAL( 1, x );
  TTS_LESS(x,1);
  TTS_GREATER(1,x);
  TTS_LESS_EQUAL(x,1);
  TTS_GREATER_EQUAL(x,0);
}
