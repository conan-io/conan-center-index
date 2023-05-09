#include <cstdlib>
#include <soplex.h>

using namespace soplex;
using namespace std;

int main() {
    SoPlex mysoplex;
    mysoplex.setIntParam(SoPlex::OBJSENSE, SoPlex::OBJSENSE_MAXIMIZE);

    DSVector dummycol(0); // obj: max x + 3y
    mysoplex.addColReal(LPCol(1.0, dummycol, 1.0, 0.0));
    mysoplex.addColReal(LPCol(3.0, dummycol, 1.0, 0.0));

    DSVector row1(2);
    row1.add(0, 1.0);
    row1.add(1, 1.0);
    mysoplex.addRowReal(LPRow(0.0, row1, 2.0)); // x + y <= 2
    mysoplex.addRowReal(LPRow(1.0, row1, infinity)); // 1 <= x + y

    mysoplex.optimize();

    auto objective = mysoplex.objValueReal();
    bool objectiveValueIsFour = objective > 3.9 && objective < 4.1;
    return objectiveValueIsFour ? EXIT_SUCCESS : EXIT_FAILURE;
}
