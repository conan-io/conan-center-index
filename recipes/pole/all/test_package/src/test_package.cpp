#include <pole.h>

using namespace POLE;

int main() 
{
    Storage aStorage("test.ole");
	if( aStorage.open(true,true))
	{
		Stream sStream(&aStorage,"/test_stream", true);
		constexpr char acPoleStr[] = "POLE library trial";
		sStream.write((unsigned char*)acPoleStr, sizeof(acPoleStr));
		sStream.flush();
	}
	aStorage.close();
}
