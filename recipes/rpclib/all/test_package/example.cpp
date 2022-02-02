#include <rpc/server.h>

double divide(double a, double b) { return a / b; }

struct subtractor {
    double operator()(double a, double b) { return a - b; }
};

struct multiplier {
    double multiply(double a, double b) { return a * b; }
};

int main() {
    rpc::server srv(8080);

    subtractor s;
    multiplier m;

    srv.bind("add", [](double a, double b) { return a + b; });
    srv.bind("sub", s);
    srv.bind("div", &divide);
    srv.bind("mul", [&m](double a, double b) { return m.multiply(a, b); });
    srv.bind("get", []()
    {
        return std::vector<uint32_t>({1,2,3,4,5,6,7});
    });

    // dont acutally run this, this is just for testing
    //srv.run();

    return 0;
}
