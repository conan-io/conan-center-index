#include <OpenNI.h>

using namespace openni;

int main()
{
	Status rc = OpenNI::initialize();
	OpenNI::shutdown();
}
