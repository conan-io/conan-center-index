#include <voro++/voro++.hh>

#include <cstdlib>
#include <cmath>

double rnd() {
    return double(rand()) / RAND_MAX;
}

int main() {
    voro::voronoicell v;
    v.init(-1, 1, -1, 1, -1, 1);

    for (int i = 0; i < 250; ++i) {
        double x = 2 * rnd() - 1;
        double y = 2 * rnd() - 1;
        double z = 2 * rnd() - 1;
        double rsq = x * x + y * y + z * z;
        if (rsq > 0.01 && rsq < 1) {
            double r = 1 / std::sqrt(rsq);
            x *= r;
            y *= r;
            z *= r;
            v.plane(x, y, z, 1);
        }
    }

    return 0;
}
