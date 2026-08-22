#include <iostream>
#include <scippp/model.hpp>
#include <scippp/version.hpp>
using namespace scippp;
int main() {
    std::cout << "This is SCIP++ version " << scippp::getVersion() << std::endl;
    Model model("Simple");
    auto x1 = model.addVar("x_1", 1);
    auto x2 = model.addVar("x_2", 1);
    model.addConstr(3 * x1 + 2 * x2 <= 1, "capacity");
    model.setObjsense(Sense::MAXIMIZE);
    model.solve();
}
