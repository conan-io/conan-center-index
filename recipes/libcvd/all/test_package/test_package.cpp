// https://github.com/edrosten/libcvd/blob/RELEASE_2_5_0/examples/distance_transform.cc

// Copyright (c) 2005--2013, The Authors
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions
// are met:
// 1. Redistributions of source code must retain the above copyright
//    notice, this list of conditions and the following disclaimer.
// 2. Redistributions in binary form must reproduce the above copyright
//    notice, this list of conditions and the following disclaimer in the
//    documentation and/or other materials provided with the distribution.
//
// THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND OTHER CONTRIBUTORS ``AS IS''
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR OTHER CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.

#include <cvd/distance_transform.h>
#include <cvd/image_io.h>

#include <algorithm>
#include <random>

using CVD::byte;
using CVD::euclidean_distance_transform_sq;
using CVD::Image;
using CVD::ImageRef;
using CVD::img_save;
using CVD::Rgb;
using std::max_element;
using std::mt19937;
using std::uniform_int_distribution;

int main()
{
	//Create a blank image.
	Image<byte> im(ImageRef(128, 128), 0);

	mt19937 engine;
	uniform_int_distribution<int> rand_x(0, im.size().x - 1);
	uniform_int_distribution<int> rand_y(0, im.size().y - 1);

	//Scatter down 7 points at random.
	for(int i = 1; i < 8; i++)
		im[rand_y(engine)][rand_x(engine)] = i;

	Image<int> dt(im.size());
	Image<ImageRef> inverse_dt(im.size());

	//Perform the distance transform
	euclidean_distance_transform_sq(im, dt, inverse_dt);

	//Create an output which is the distance transfom of the input,
	//but coloured according to which pixel is closest.
	int largest_distance = *max_element(dt.begin(), dt.end());

	Image<Rgb<byte>> out(im.size());

	for(int y = 0; y < im.size().y; y++)
		for(int x = 0; x < im.size().x; x++)
		{
			int c = floor(sqrt(dt[y][x] * 1.0 / largest_distance) * 255 + .5);

			Rgb<byte> r(0, 0, 0);
			if(im[inverse_dt[y][x]] & 1)
				r.red = c;
			if(im[inverse_dt[y][x]] & 2)
				r.green = c;
			if(im[inverse_dt[y][x]] & 4)
				r.blue = c;

			out[y][x] = r;
		}

	img_save(out, "distance_transform_result.png");
}
