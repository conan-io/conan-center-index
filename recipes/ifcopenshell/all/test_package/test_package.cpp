#include <string>
#include <iostream>
#include <fstream>
#include <optional>

#define IfcSchema Ifc4x3_add2
#include <ifcparse/Ifc4x3_add2.h>
#include <ifcparse/IfcHierarchyHelper.h>

using namespace std::string_literals;

typedef IfcParse::IfcGlobalId guid;
boost::none_t const null = boost::none;

int main()
{

	IfcHierarchyHelper<IfcSchema> file;
	file.header().file_name()->setname("gardenShed.ifc");

	IfcSchema::IfcWallStandardCase *south_wall = new IfcSchema::IfcWallStandardCase(guid(), 0, "South wall"s, null, null, 0, 0, null, IfcSchema::IfcWallTypeEnum::IfcWallType_STANDARD);
	file.addBuildingProduct(south_wall);

	std::ofstream ofs("gardenShed.ifc");
	ofs << file;
	return 0;
}
