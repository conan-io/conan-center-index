#include <iostream>
#include <string>
#include <strong_type.h>
using namespace std;

STRONG_TYPE(ST, string);

int main()
{
	ST st = "strong_type";
	cout << "hello " << st << "!\n";
}
