#include <deco/Deco.h>
#include <iostream>
#include <string>

int main()
{
	using namespace std;

	const string sample {
		"hello:\n"
		"	world!\n"
		":\n"
	};

	deco::parse(sample.begin(), sample.end());

	cout << sample << endl;
}
