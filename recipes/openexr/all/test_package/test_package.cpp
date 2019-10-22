#include <string>
#include <iostream>
#include <ImfRgbaFile.h>
#include <ImfArray.h>

int main(int argc, char **argv)
{
	int const width = 512;
	int const height = 512;

	Imf::RgbaOutputFile file_exr(
		"example.exr",
		width, height,
		Imf::WRITE_RGBA);
	file_exr.writePixels(height);

	return 0;
}
