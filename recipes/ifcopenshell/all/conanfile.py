from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os


required_conan_version = ">=2.0.9"

class IfcopenshellConan(ConanFile):
    name = "ifcopenshell"
    description = "Open source IFC library and geometry engine"
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ifcopenshell.org/"
    topics = ("ifc", "bim", "topic3")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "schemas": ["ANY"],
        "with_ifcgeom": [True, False],
        "with_opencascade": [True, False],
        "with_cgal": [True, False],
        "with_ifcxml": [True, False],
        "with_hdf5_support": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "schemas": ["2x3", "4", "4x1", "4x2", "4x3", "4x3_tc1", "4x3_add1", "4x3_add2"],
        "with_ifcgeom": True,
        "with_opencascade": True,
        "with_cgal": True,
        "with_ifcxml": True,
        "with_hdf5_support": True,
    }

    @property
    def _all_supported_ifc_schemas(self):
        return sorted(["2x3", "4", "4x1", "4x2", "4x3", "4x3_tc1", "4x3_add1", "4x3_add2"])

    def _supported_ifc_schemas(self, info=False):
        options = self.info.options if info else self.options
        return sorted(set(str(options.schemas).split(",")))
    
    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        self.options.schemas = ",".join(self._all_supported_ifc_schemas)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        # normalize the schemas option (sorted+comma separated)
        self.info.options.schemas = ",".join(self._supported_ifc_schemas(info=True))

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        unsupported_schemas = [schema for schema in self._supported_ifc_schemas() if schema not in self._all_supported_ifc_schemas]
        if unsupported_schemas:
            raise ConanInvalidConfiguration(
                f"Invalid schema(s) in schemas option: {unsupported_schemas}\n"
                f"Valid supported ifc schemas are: {self._all_supported_ifc_schemas}")

    def requirements(self):
        if self.options.with_hdf5_support:
            self.requires("hdf5/1.14.6")
        if self.options.with_ifcgeom:
            if self.options.with_opencascade:
                self.requires("opencascade/7.9.1")
            if self.options.with_cgal:
                self.requires("cgal/6.0.1")
                self.requires("gmp/6.3.0")
                self.requires("mpfr/4.2.1")
            self.requires("eigen/3.4.0", transitive_headers=True)
        self.requires("boost/1.83.0")
        if self.options.with_ifcgeom or self.options.with_ifcxml:
            self.requires("libxml2/2.13.6")

    def build_requirements(self):
        self.tool_requires("cmake/[>=4 <5]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SCHEMA_VERSIONS"] = ";".join(self._supported_ifc_schemas())
        tc.variables["BUILD_IFCGEOM"] = self.options.with_ifcgeom
        tc.variables["WITH_OPENCASCADE"] = self.options.with_opencascade
        tc.variables["WITH_CGAL"] = self.options.with_cgal
        if self.options.with_cgal:
            tc.variables["CGAL_INCLUDE_DIR"] = self.dependencies['cgal'].cpp_info.includedirs[0]
            tc.variables["CGAL_LIBRARY_DIR"] = self.dependencies['cgal'].cpp_info.libdirs[0]

            tc.variables["GMP_INCLUDE_DIR"] = self.dependencies['gmp'].cpp_info.includedirs[0]
            tc.variables["GMP_LIBRARY_DIR"] = self.dependencies['gmp'].cpp_info.libdirs[0]
            
            tc.variables["MPFR_INCLUDE_DIR"] = self.dependencies['mpfr'].cpp_info.includedirs[0]
            tc.variables["MPFR_LIBRARY_DIR"] = self.dependencies['mpfr'].cpp_info.libdirs[0]

        tc.variables["IFCXML_SUPPORT"] = self.options.with_ifcxml
        tc.variables["COLLADA_SUPPORT"] = False
        tc.variables["BUILD_IFCPYTHON"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        if self.options.with_ifcgeom:
            tc.variables["EIGEN_DIR"] = self.dependencies["eigen"].cpp_info.includedirs[0] + "/eigen3/"

        if self.options.with_hdf5_support:
            tc.variables["HDF5_SUPPORT"] = self.options.with_hdf5_support
            tc.variables["HDF5_INCLUDE_DIR"] = self.dependencies['hdf5'].cpp_info.includedirs[0]
            tc.variables["HDF5_LIBRARY_DIR"] = self.dependencies['hdf5'].cpp_info.libdirs[0]

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="cmake")
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            if self.options.with_ifcgeom:
                self.cpp_info.system_libs.append("pthread")

        self.cpp_info.components["IfcParse"].libs = ["IfcParse"]
        self.cpp_info.components["IfcParse"].requires = ["boost::boost", "libxml2::libxml2"]
        # self.cpp_info.components["IfcParse"].defines.append(f"SCHEMA_SEQ=({")(".join(self._supported_ifc_schemas())})")
        for schema in self._supported_ifc_schemas():
            self.cpp_info.components["IfcParse"].defines.append(f"HAS_SCHEMA_{schema}")

        if self.options.with_ifcgeom:
            for schema in self._supported_ifc_schemas():
                component_name = f"geometry_mapping_ifc{schema}"
                self.cpp_info.components[component_name].libs = [component_name]
                self.cpp_info.components[component_name].requires = ["IfcParse"]

            if self.options.with_cgal:
                self.cpp_info.components["geometry_kernel_cgal"].libs = ["geometry_kernel_cgal"]
                self.cpp_info.components["geometry_kernel_cgal"].requires = ["cgal::cgal", "mpfr::mpfr", "gmp::gmp", "eigen::eigen"]

                self.cpp_info.components["geometry_kernel_cgal_simple"].libs = ["geometry_kernel_cgal_simple"]
                self.cpp_info.components["geometry_kernel_cgal_simple"].requires = ["cgal::cgal", "mpfr::mpfr", "gmp::gmp", "eigen::eigen"]

            if self.options.with_opencascade:
                self.cpp_info.components["geometry_kernel_opencascade"].libs = ["geometry_kernel_opencascade"]
                self.cpp_info.components["geometry_kernel_opencascade"].requires = ["opencascade::occt_tkernel", "opencascade::occt_tkmath", "opencascade::occt_tkbrep", "opencascade::occt_tkgeombase", "opencascade::occt_tkgeomalgo", "opencascade::occt_tkg3d", "opencascade::occt_tkg2d", "opencascade::occt_tkshhealing", "opencascade::occt_tktopalgo", "opencascade::occt_tkmesh", "opencascade::occt_tkprim", "opencascade::occt_tkbool", "opencascade::occt_tkbo", "opencascade::occt_tkfillet", "opencascade::occt_tkxsbase", "opencascade::occt_tkoffset", "opencascade::occt_tkhlr", "eigen::eigen"]

            self.cpp_info.components["IfcGeom"].libs = ["IfcGeom"]
            for schema in self._supported_ifc_schemas():
                self.cpp_info.components["IfcGeom"].requires.append(f"geometry_mapping_ifc{schema}")
            self.cpp_info.components["IfcGeom"].requires = ["IfcParse", "eigen::eigen"]
            if self.options.with_cgal:
                self.cpp_info.components["IfcGeom"].requires.extend(["geometry_kernel_cgal", "geometry_kernel_cgal_simple"])
            if self.options.with_opencascade:
                self.cpp_info.components["IfcGeom"].requires.append("geometry_kernel_opencascade")
                
        if self.options.with_opencascade:
            self.cpp_info.components["geometry_serializer"].libs = ["geometry_serializer"]
            for schema in self._supported_ifc_schemas():
                component_name = f"geometry_serializer_ifc{schema}"
                self.cpp_info.components[component_name].libs = [component_name]
                self.cpp_info.components[component_name].requires = ["opencascade::occt_tkbrep"]
                self.cpp_info.components["geometry_serializer"].requires.append(component_name)
        
        self.cpp_info.components["Serializers"].libs = ["Serializers"]
        self.cpp_info.components["Serializers"].requires = ["IfcGeom"]
        if self.options.with_hdf5_support:
            self.cpp_info.components["Serializers"].requires.append("hdf5::hdf5")
        for schema in self._supported_ifc_schemas():
            component_name = f"Serializers_ifc{schema}"
            self.cpp_info.components[component_name].libs = [component_name]
            self.cpp_info.components["Serializers"].requires.append(component_name)
            if self.options.with_hdf5_support:
                self.cpp_info.components[component_name].requires.append("hdf5::hdf5")
