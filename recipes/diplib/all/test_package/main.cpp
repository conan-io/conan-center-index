#include <iostream>
#include <diplib.h>

using std::cout;
using std::endl;

int main()
{
  cout << "DIPlib information:" << endl;
  cout << "version: " << dip::libraryInformation.version << endl;
  cout << "compilation date: " << dip::libraryInformation.date << endl;
  cout << "options: " << dip::libraryInformation.type << endl;

}
