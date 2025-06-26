/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

 // Schema selection for IFC schemas in descending order (highest first)
#ifdef HAS_SCHEMA_4x3_add2
#define IfcSchema Ifc4x3_add2
#elif defined(HAS_SCHEMA_4x3_add1)
#define IfcSchema Ifc4x3_add1
#elif defined(HAS_SCHEMA_4x3_tc1)
#define IfcSchema Ifc4x3_tc1
#elif defined(HAS_SCHEMA_4x3)
#define IfcSchema Ifc4x3
#elif defined(HAS_SCHEMA_4x2)
#define IfcSchema Ifc4x2
#elif defined(HAS_SCHEMA_4x1)
#define IfcSchema Ifc4x1
#elif defined(HAS_SCHEMA_4)
#define IfcSchema Ifc4
#elif defined(HAS_SCHEMA_2x3)
#define IfcSchema Ifc2x3
#else
#error "No IFC schema defined. At least one HAS_SCHEMA_<version> must be defined."
#endif

#include <string>
#include <iostream>
#include <fstream>

// #include <TColgp_Array2OfPnt.hxx>
// #include <TColStd_Array1OfReal.hxx>
// #include <TColStd_Array1OfInteger.hxx>
// #include <Geom_BSplineSurface.hxx>
// #include <BRepBuilderAPI_MakeFace.hxx>
// #include <Standard_Version.hxx>
// #include <Precision.hxx>


#include <ifcparse/macros.h>

 // Schema selection for IFC schemas in descending order (highest first)
#ifdef HAS_SCHEMA_4x3_add2
#define IfcSchema Ifc4x3_add2
#include <ifcparse/Ifc4x3_add2.h>
#elif defined(HAS_SCHEMA_4x3_add1)
#define IfcSchema Ifc4x3_add1
#include <ifcparse/Ifc4x3_add1.h>
#elif defined(HAS_SCHEMA_4x3_tc1)
#define IfcSchema Ifc4x3_tc1
#include <ifcparse/Ifc4x3_tc1.h>
#elif defined(HAS_SCHEMA_4x3)
#define IfcSchema Ifc4x3
#include <ifcparse/Ifc4x3.h>
#elif defined(HAS_SCHEMA_4x2)
#define IfcSchema Ifc4x2
#include <ifcparse/Ifc4x2.h>
#elif defined(HAS_SCHEMA_4x1)
#define IfcSchema Ifc4x1
#include <ifcparse/Ifc4x1.h>
#elif defined(HAS_SCHEMA_4)
#define IfcSchema Ifc4
#include <ifcparse/Ifc4.h>
#elif defined(HAS_SCHEMA_2x3)
#define IfcSchema Ifc2x3
#define IFC2X3_COMPATIBLE
#include <ifcparse/Ifc2x3.h>
#else
#error "No compatible IFC schema defined. At least one HAS_SCHEMA_<version> must be defined."
#endif

#include <ifcparse/IfcBaseClass.h>
#include <ifcparse/IfcHierarchyHelper.h>
// #include <ifcgeom/Serialization/Serialization.h>

using namespace std::string_literals;
typedef IfcParse::IfcGlobalId guid;
boost::none_t const null = boost::none;

// // Create a simple NURBS surface for IfcSite to test Open CASCADE
// void createGroundShape(TopoDS_Shape& shape) {
//     TColgp_Array2OfPnt cv(0, 1, 0, 1);
//     cv.SetValue(0, 0, gp_Pnt(-1000, -1000, 0));
//     cv.SetValue(0, 1, gp_Pnt(-1000, 1000, 0));
//     cv.SetValue(1, 0, gp_Pnt(1000, -1000, 0));
//     cv.SetValue(1, 1, gp_Pnt(1000, 1000, 0));
//     TColStd_Array1OfReal knots(0, 1);
//     knots(0) = 0;
//     knots(1) = 1;
//     TColStd_Array1OfInteger mult(0, 1);
//     mult(0) = 2;
//     mult(1) = 2;
//     Handle(Geom_BSplineSurface) surf = new Geom_BSplineSurface(cv, knots, knots, mult, mult, 1, 1);
// #if OCC_VERSION_HEX < 0x60502
//     shape = BRepBuilderAPI_MakeFace(surf);
// #else
//     shape = BRepBuilderAPI_MakeFace(surf, Precision::Confusion());
// #endif
// }

int main() {
    // Initialize IFC file
    IfcHierarchyHelper<IfcSchema> file;
    file.header().file_name().name("Test.ifc");

    IfcSchema::IfcWall* wall = new IfcSchema::IfcWall(
        guid(),                 // GlobalId
        nullptr,                // OwnerHistory
        "Test Wall"s,           // Name
        boost::none,            // Description
        boost::none,            // ObjectType
        nullptr,                // ObjectPlacement
        nullptr,                // Representation
        boost::none            // v8_Tag
#if !defined(IFC2X3_COMPATIBLE)
        , boost::none // PredefinedType (required for IFC4 and later)
#endif
    );

    file.addBuildingProduct(wall);
    wall->setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());
    wall->setRepresentation(file.addBox(1000, 300, 2000));
    wall->setObjectPlacement(file.addLocalPlacement());

    // Create a site with a simple NURBS surface to test Open CASCADE
    // TopoDS_Shape shape;
    // createGroundShape(shape);
    // IfcSchema::IfcProductDefinitionShape* ground_representation = IfcGeom::tesselate(STRINGIFY(IfcSchema), shape, 100.)->as<IfcSchema::IfcProductDefinitionShape>();
    // file.getSingle<IfcSchema::IfcSite>()->setRepresentation(ground_representation);
    // file.addEntity(ground_representation);

    // Write IFC file
    std::ofstream f("Test.ifc");
    if (!f.is_open()) {
        std::cerr << "Failed to open Test.ifc" << std::endl;
        return 1;
    }
    f << file;
    f.close();

    std::cout << "Test.ifc created successfully" << std::endl;
    return 0;
}
