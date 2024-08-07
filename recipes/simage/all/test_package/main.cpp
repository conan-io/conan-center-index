#include <iostream>
#include <simage.h>

using std::cout;
using std::endl;


int main()
{

  int major, minor, patch;
  simage_version(&major, &minor, &patch);

  cout << "simage version: " << "{" << major << "." << minor << "." << patch <<"}" << endl;
  return 0;
}
