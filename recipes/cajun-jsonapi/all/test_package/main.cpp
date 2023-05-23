#include <cajun/json/reader.h> // Recommended include path as of v2.1.0
#include <cajun/json/writer.h>
#include <json/elements.h> // Shortened include path used prior to v2.1.0

#include <iostream>
#include <sstream>

int main()
{
    using namespace json;

    Object objAPA;
    objAPA["Name"] = String("Schlafly American Pale Ale");
    objAPA["Origin"] = String("St. Louis, MO, USA");
    objAPA["ABV"] = Number(3.8);
    objAPA["BottleConditioned"] = Boolean(true);

    Array arrayBeer;
    arrayBeer.Insert(objAPA);

    Object objDocument;
    objDocument["Delicious Beers"] = arrayBeer;

    Number numDeleteThis = objDocument["AnotherMember"];

    objDocument["Delicious Beers"][1]["Name"] = String("John Smith's Extra Smooth");
    objDocument["Delicious Beers"][1]["Origin"] = String("Tadcaster, Yorkshire, UK");
    objDocument["Delicious Beers"][1]["ABV"] = Number(3.8);
    objDocument["Delicious Beers"][1]["BottleConditioned"] = Boolean(false);

    const Object &objRoot = objDocument;

    const Array &arrayBeers = objRoot["Delicious Beers"];
    const Object &objBeer0 = arrayBeers[0];
    const String &strName0 = objBeer0["Name"];

    const Number numAbv1 = objRoot["Delicious Beers"][1]["ABV"];

    std::cout << "First beer name: " << strName0.Value() << std::endl;
    std::cout << "First beer ABV: " << numAbv1.Value() << std::endl;

    return 0;
}
