#include <cstdlib>
#include <iostream>
#include <Lielab.hpp>


int main(void) {
    Lielab::domain::so u(3);
    Lielab::domain::so v(3);
    Lielab::domain::so w(3);
    Lielab::domain::so ansso(3);
    Lielab::domain::SO Gso(3);

    Eigen::VectorXd xx(3);
    xx << 1.0, 0.0, 0.0;
    Eigen::VectorXd yy(3);
    yy << 0.0, 1.0, 0.0;
    Eigen::VectorXd zz(3);
    zz << 0.0, 0.0, 1.0;
    Eigen::MatrixXd truthso(3,3);

    u.set_vector(xx);
    v.set_vector(yy);
    w.set_vector(zz);
    Gso = Lielab::functions::exp(v);

    // GuG^-1
    ansso = Lielab::functions::Ad(Gso, u);
    std::cout << "Lielab v" << Lielab::VERSION << std::endl;
    std::cout << Lielab::AUTHOR << std::endl;
    std::cout << Lielab::LOCATION << std::endl;

    return EXIT_SUCCESS;
}