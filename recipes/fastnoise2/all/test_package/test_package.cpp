#include "FastNoise/FastNoise.h"

int main() {
    auto fnSimplex = FastNoise::New<FastNoise::Simplex>();
    auto fnFractal = FastNoise::New<FastNoise::FractalFBm>();

    fnFractal->SetSource( fnSimplex );
    fnFractal->SetOctaveCount( 5 );

    return 0;
}
