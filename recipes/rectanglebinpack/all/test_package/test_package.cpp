/*
 * Original source code:
 * https://github.com/juj/RectangleBinPack/blob/29eec60fe2c9aa0df855dddabd8d4d17023b95f3/test/MaxRectsBinPackTest.cpp
 */

#include <cstdint>
#include <cstdio>
#include <vector>
#include <rectanglebinpack/MaxRectsBinPack.h>

using namespace rbp;

bool AreDisjoint(const Rect &a, const Rect &b)
{
	return a.x >= b.x + b.width || a.x + a.width <= b.x ||
		a.y >= b.y + b.height || a.y + a.height <= b.y;
}

bool AllRectsDisjoint(std::vector<Rect> &packed)
{
	for(size_t i = 0; i < packed.size(); ++i)
		for(size_t j = i+1; j < packed.size(); ++j)
		{
			if (!AreDisjoint(packed[i], packed[j]))
				return false;
		}
	return true;
}

int main()
{
	MaxRectsBinPack pack(256, 256, true);

	std::vector<Rect> packed;
	srand(12412);
	for(int i = 1; i < 128; ++i)
	{
		int a = (rand() % 128) + 1;
		int b = (rand() % 128) + 1;
		Rect r = pack.Insert(a, b, MaxRectsBinPack::RectBestShortSideFit);
		if (!r.width)
			break;
		packed.push_back(r);
	}
	printf("Packed %d rectangles. All rects disjoint: %s. Occupancy: %f\n",
		(int)packed.size(), AllRectsDisjoint(packed) ? "yes" : "NO!", pack.Occupancy());
}
