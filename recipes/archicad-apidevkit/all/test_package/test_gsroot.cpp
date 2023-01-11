#include <cstdlib>
#include <Color.hpp>

int main ()
{
	Gfx::Color someColor;
	someColor.SetRed (176);

	return someColor.GetRed () == 176 ? EXIT_SUCCESS : EXIT_FAILURE;
}
