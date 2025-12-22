#include <string>
#include <iostream>
#include <fstream>
#include <optional>

#define IfcSchema Ifc4x3_add2
#include <ifcparse/Ifc4x3_add2.h>
#include <ifcparse/IfcHierarchyHelper.h>

using namespace std::string_literals;

// Some convenience typedefs and definitions. 
typedef IfcParse::IfcGlobalId guid;
typedef std::pair<double, double> XY;
boost::none_t const null = boost::none;

int main() {

	IfcHierarchyHelper<IfcSchema> file;
	file.header().file_name()->setname("gardenShed.ifc");

	file.addBuildingProduct(south_wall);

	std::ofstream ofs("gardenShed.ifc");
    ofs << file;
	return 0;
}
