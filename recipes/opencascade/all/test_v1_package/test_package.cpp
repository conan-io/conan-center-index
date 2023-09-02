#include <BRepBuilderAPI_MakeEdge.hxx>
#include <TopoDS_Edge.hxx>
#include <GC_MakeCircle.hxx>
#include <gce_MakeCirc.hxx>
#include <gp_Circ.hxx>

#include <iostream>

int main() {
    gp_Pnt pc(0, 0, 0);
    gp_Circ cir = gce_MakeCirc(pc, gp::DZ(), 5);
    auto geometry = GC_MakeCircle(cir).Value();
    TopoDS_Edge edge = BRepBuilderAPI_MakeEdge(geometry);
}
