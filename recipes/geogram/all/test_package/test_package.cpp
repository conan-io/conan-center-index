#include <geogram/mesh/mesh.h>
#include <geogram/mesh/mesh_io.h>
#include <geogram/mesh/mesh_geometry.h>
#include <geogram/mesh/mesh_repair.h>
#include <geogram/delaunay/delaunay.h>
#include <geogram/voronoi/RVD.h>
#include <geogram/numerics/predicates.h>
#include <geogram/basic/logger.h>
#include <geogram/basic/command_line.h>
#include <geogram/basic/command_line_args.h>
#include <geogram/basic/file_system.h>
#include <geogram/basic/progress.h>
#include <stdarg.h>

int main(int argc, char** argv) {

    GEO::initialize();
    GEO::Logger::instance()->set_quiet(false);
    GEO::CmdLine::import_arg_group("standard");
    GEO::CmdLine::import_arg_group("algo");
    GEO::CmdLine::declare_arg_percent("size", 10.0, "elements size, in bbox diagonal percent");
    GEO::CmdLine::declare_arg("shrink", 0.9, "cells shrink");
    GEO::CmdLine::declare_arg("border_only", false, "output only RVC facets on the border");
    
    std::vector<std::string> filenames;
    GEO::CmdLine::parse(argc, argv, filenames, "points_filename <cell_filename>");
    
    return 0;
}