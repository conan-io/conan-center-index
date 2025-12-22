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
	IfcSchema::IfcWallStandardCase* south_wall = new IfcSchema::IfcWallStandardCase(
		guid(), 			// GlobalId
		0, 					// OwnerHistory
		"South wall"s,	 	// Name
		null, 				// Description
		null, 				// ObjectType
		0, 					// ObjectPlacement
		0, 					// Representation
		null				// Tag
		, IfcSchema::IfcWallTypeEnum::IfcWallType_STANDARD
	);
	file.addBuildingProduct(south_wall);

	auto person = file.getSingle<IfcSchema::IfcPerson>();
	person->setFamilyName(std::string("DUGUEPEROUX"));
	person->setGivenName(std::string("Esteban"));

	auto personAndOrganization = file.getSingle<IfcSchema::IfcPersonAndOrganization>();

	auto organization = file.getSingle<IfcSchema::IfcOrganization>();

	auto application = file.getSingle<IfcSchema::IfcApplication>();
	application->setApplicationFullName(std::string("conan_ifcopenshell_test"));
	application->setVersion(std::string("0.0.1"));

	auto ownerHistory = file.getSingle<IfcSchema::IfcOwnerHistory>();
	ownerHistory->setState(IfcSchema::IfcStateEnum::IfcState_READWRITE);

	// https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcSite.htm
	auto project = file.getSingle<IfcSchema::IfcProject>();
	project->setName(std::string("Garden Shed Project"));
    project->setDescription(std::string("A simple garden shed model"));
	project->setPhase(std::string("Conceptual Design"));

	auto site = file.getSingle<IfcSchema::IfcSite>();

	std::vector<int> v = {8, 4, 5, 9};
	boost::optional<std::vector<int>> latitude = v;
	site->setRefLatitude(latitude);
	site->setRefLongitude(latitude);
	site->setRefElevation(59);

	auto gardenShedBuilding = file.getSingle<IfcSchema::IfcBuilding>();

	std::ofstream ofs("gardenShed.ifc");
    ofs << file;
	return 0;
}
