
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, apply_conandata_patches, export_conandata_patches, rm, rmdir

required_conan_version = ">=2.1"

IFC_SCHEMAS = sorted(["2x3", "4", "4x1", "4x2", "4x3", "4x3_tc1", "4x3_add1", "4x3_add2"])

class IfcopenshellConan(ConanFile):
    name = "ifcopenshell"
    description = "Open source IFC library and geometry engine"
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/IfcOpenShell/IfcOpenShell"
    topics = ("ifc", "bim", "building", "3d")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    
    options.update({f"schema_{schema}": [True, False] for schema in IFC_SCHEMAS})
    
    default_options = {
        "shared": False,
        "fPIC": True,
    }   
    # Limit the default set of schemas to the basic ones and the latest to limit the size of the build.
    default_options.update({f"schema_{schema}": schema in ["2x3", "4", "4x3_add2"] for schema in IFC_SCHEMAS})
    implements = ["auto_shared_fpic"]

    @property
    def _selected_ifc_schemas(self):
        return [schema for schema in IFC_SCHEMAS if self.options.get_safe(f"schema_{schema}")]

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
    
    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

    def requirements(self):
        # Boost release fixed by cgal to avoid conflict
        self.requires("boost/1.83.0", transitive_headers=True, transitive_libs=True)
        # Used in public serializers/HdfSerializer.h, ifcgeom/kernels/opencascade/IfcGeomTree.h
        self.requires("hdf5/[^1.8]", transitive_headers=True, transitive_libs=True)
        self.requires("opencascade/[^7.8]", transitive_headers=True, transitive_libs=True)
        # ifcgeom/taxonomy.h
        self.requires("eigen/3.4.0", transitive_headers=True)
        # Used in ifcgeom/kernels/cgal public headers
        self.requires("cgal/5.6.3", transitive_headers=True, transitive_libs=True)
        self.requires("libxml2/[^2.12.5]")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21 <5]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["SCHEMA_VERSIONS"] = ";".join(self._selected_ifc_schemas)
        tc.cache_variables["USE_MMAP"] = True
        tc.cache_variables["BUILD_CONVERT"] = False
        tc.cache_variables["BUILD_GEOMSERVER"] = False
        tc.cache_variables["COLLADA_SUPPORT"] = False
        tc.cache_variables["BUILD_IFCPYTHON"] = False
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        # rm(self, "*.cmake", os.path.join(self.source_folder, "cmake"))
        cmake = CMake(self)
        cmake.configure(build_script_folder="cmake")
        cmake.build()

    def package(self):
        copy(self, "COPYING*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        # No official CMake or .pc config exported. Based on CPack values for consistency.
        self.cpp_info.set_property("cmake_file_name", "IfcOpenShell")

        def _add_component(name, requires=None):
            component = self.cpp_info.components[name]
            component.set_property("cmake_target_name", name)
            component.libs = [name]
            component.requires = requires or []
            return component

        ifcparse = _add_component("IfcParse", requires=[
            "boost::system",
            "boost::program_options",
            "boost::regex",
            "boost::thread",
            "boost::date_time",
        ])
        # For mmap
        ifcparse.requires.extend(["boost::iostreams", "boost::filesystem",])
        ifcparse.defines.append("USE_MMAP")

        # For IFCXML support
        ifcparse.requires.append("libxml2::libxml2")
        ifcparse.defines.append("WITH_IFCXML")
        ifcparse.defines.append(f"SCHEMA_SEQ=({')('.join(self._selected_ifc_schemas)})")
        for schema in self._selected_ifc_schemas:
            ifcparse.defines.append(f"HAS_SCHEMA_{schema}")
        if self.options.shared:
            ifcparse.defines.append("IFC_SHARED_BUILD")
        if self.settings.os in ["Linux", "FreeBSD"]:
            ifcparse.system_libs = ["m", "dl"]

        ifcgeom = _add_component("IfcGeom", requires=["IfcParse", "eigen::eigen", "opencascade::occt_tkernel"])
        if self.settings.os in ["Linux", "FreeBSD"]:
            ifcgeom.system_libs.append("pthread")
        ifcgeom.defines.append("IFOPSH_WITH_OPENCASCADE")
        # For HDF5 support
        ifcgeom.requires.append("hdf5::hdf5_cpp")

        _add_component("geometry_kernel_opencascade", requires=[
            "IfcGeom", 
            "opencascade::occt_tkernel",
            "opencascade::occt_tkmath",
            "opencascade::occt_tkbrep",
            "opencascade::occt_tkgeombase",
            "opencascade::occt_tkgeomalgo",
            "opencascade::occt_tkg3d",
            "opencascade::occt_tkg2d",
            "opencascade::occt_tkshhealing",
            "opencascade::occt_tktopalgo",
            "opencascade::occt_tkmesh",
            "opencascade::occt_tkprim",
            "opencascade::occt_tkbool",
            "opencascade::occt_tkbo",
            "opencascade::occt_tkfillet",
            "opencascade::occt_tkxsbase",
            "opencascade::occt_tkoffset",
            "opencascade::occt_tkhlr",
            "eigen::eigen",
        ])
            
        _add_component("geometry_kernel_cgal", requires=["IfcGeom", "cgal::cgal", "eigen::eigen"])
        _add_component("geometry_kernel_cgal_simple", requires=["IfcGeom", "cgal::cgal", "eigen::eigen"])
        ifcgeom.defines.append("IFOPSH_WITH_CGAL")
        ifcgeom.requires += ["cgal::cgal", "eigen::eigen"]
