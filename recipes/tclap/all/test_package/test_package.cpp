#include <cassert>
#include <string>
#include <iostream>
#include <algorithm>
#include <tclap/CmdLine.h>

using namespace TCLAP;
using namespace std;

int main(int, char**)
{
	int argc = 4;
	const char * argv[] = { "test", "-r", "-n", "mike" };

	CmdLine cmd("Command description message", ' ', "0.9");

	ValueArg<string> nameArg("n","name","Name to print",true,"homer","string");
	cmd.add( nameArg );

	SwitchArg reverseSwitch("r","reverse","Print name backwards", false);
	cmd.add(reverseSwitch);

	cmd.parse(argc, argv);

	string name = nameArg.getValue();
	bool reverseName = reverseSwitch.getValue();

	assert(reverseName);
	reverse(name.begin(), name.end());
	assert(name == "ekim");

	return 0;
}
