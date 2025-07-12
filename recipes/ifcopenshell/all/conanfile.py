
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.apple import is_apple_os

required_conan_version = ">=2.1"

IFC_SCHEMAS = sorted(["2x3", "4", "4x1", "4x2", "4x3", "4x3_tc1", "4x3_add1", "4x3_add2"])

class IfcopenshellConan(ConanFile):
    name = "ifcopenshell"
    description = "Open source IFC library and geometry engine"
    license = "LGPL-3.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ifcopenshell.org/"
    topics = ("ifc", "bim")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_ifcgeom": [True, False],
        "build_ifcgeomserver": [True, False],
        "build_convert": [True, False],
        "build_convert_with_usd": [True, False],
        "build_convert_with_proj": [True, False],
        "ifcxml_support": [True, False],
        "use_mmap": [True, False],
        "with_cgal": [True, False],
        "with_hdf5": [True, False],
        
        "with_ifcpython": [True, False],
        "build_qtviewer": [True, False],
    }
    options.update({f"schema_{schema}": [True, False] for schema in IFC_SCHEMAS})
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_ifcgeom": True,
        "build_ifcgeomserver": True,
        "build_convert": True,
        "build_convert_with_usd": False,
        "build_convert_with_proj": True,
        "ifcxml_support": True,
        "use_mmap": True,
        "with_cgal": True,
        "with_hdf5": True,
        
        "with_ifcpython": True,
        "build_qtviewer": False,
    }   
    # Limit the default set of schemas to the basic ones and the latest to limit the size of the build.
    default_options.update({f"schema_{schema}": schema in ["4x3_add2"] for schema in IFC_SCHEMAS})
    # default_options.update({f"schema_{schema}": schema in ["2x3", "4", "4x1", "4x2", "4x3", "4x3_tc1", "4x3_add1", "4x3_add2"] for schema in IFC_SCHEMAS})
    implements = ["auto_shared_fpic"]

    @property
    def _selected_ifc_schemas(self):
        return [schema for schema in IFC_SCHEMAS if self.options.get_safe(f"schema_{schema}")]

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.build_ifcgeom:
            del self.options.with_cgal
    
    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)
        if self.options.build_convert and not self.options.build_ifcgeom:
            raise ConanInvalidConfiguration("build_convert requires build_ifcgeom to be enabled")
        if is_apple_os(self):
            raise ConanInvalidConfiguration("Disable temporary apple platform")
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Disable temporary windows platform")
        # if self.settings.os == "Linux":
        #     raise ConanInvalidConfiguration("Disable temporary linux platform")

    def requirements(self):
        self.requires("boost/1.83.0", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("with_hdf5"):
            # Used in public serializers/HdfSerializer.h, ifcgeom/kernels/opencascade/IfcGeomTree.h
            self.requires("hdf5/[^1.8]", transitive_headers=True, transitive_libs=True)
        if self.options.build_ifcgeom:
            self.requires("opencascade/[^7.5]", transitive_headers=True, transitive_libs=True)
            # ifcgeom/taxonomy.h
            self.requires("eigen/3.4.0", transitive_headers=True)
            if self.options.get_safe("with_cgal"):
                # Used in ifcgeom/kernels/cgal public headers
                # self.requires("cgal/[>=5.6]", transitive_headers=True, transitive_libs=True)
                # TODO migrate cpp to be compatible with latest cgal to avoid compilation errors on src/src/ifcconvert/validate_space_boundaries.cpp:
                # https://c3i.jfrog.io/artifactory/cci-build-logs/cci/prod/PR-27623/84/package_build_logs/build_log_ifcopenshell_0_8_3_cci_20250613_f8f37b5967ba18eef190cb0e92b6b561_9f5b6011d7ba49ff30af97cb4929b54a80903d97.txt
                self.requires("cgal/5.5.5")
                self.requires("gmp/[^6.3.0]")
                self.requires("mpfr/[^4.2.1]")
        if self.options.get_safe("with_cgal") or self.options.ifcxml_support:
            self.requires("libxml2/[^2.12.5]")
        if self.options.build_convert:
            if self.options.build_convert_with_usd:
                # See https://github.com/conan-io/conan-center-index/pull/24506
                self.requires("openusd/25.02")
            if self.options.build_convert_with_proj:
                self.requires("proj/9.6.0")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21 <5]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        def includedir(dep):
            return self.dependencies[dep].cpp_info.includedirs[0].replace("\\", "/")

        def libdir(dep):
            return self.dependencies[dep].cpp_info.libdirs[0].replace("\\", "/")

        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_IFCGEOM"] = self.options.build_ifcgeom
        tc.cache_variables["BUILD_GEOMSERVER"] = self.options.build_ifcgeomserver
        tc.cache_variables["BUILD_CONVERT"] = self.options.build_convert
        # validate_space_boundaries.cpp:106:57: error: no matching function for call to 'IfcEntityInstanceData::toString() const
        # See https://c3i.jfrog.io/artifactory/cci-build-logs/cci/prod/PR-27623/86/package_build_logs/build_log_ifcopenshell_0_8_3_cci_20250613_855f5322a78c6ae836318b516e5c29ba_b8f0ca9f77a4d376fb7cb9ba9f229be5f13244f9.txt
        # tc.cache_variables["WITH_RELATIONSHIP_VALIDATION"] = self.options.build_convert
        tc.cache_variables["USD_SUPPORT"] = self.options.build_convert and self.options.build_convert_with_usd
        tc.cache_variables["WITH_PROJ"] = self.options.build_convert and self.options.build_convert_with_proj

        tc.cache_variables["BUILD_GEOMSERVER"] = False
        tc.cache_variables["BUILD_IFCPYTHON"] = False
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["IFCXML_SUPPORT"] = self.options.ifcxml_support
        tc.cache_variables["USE_MMAP"] = self.options.use_mmap
        tc.cache_variables["SCHEMA_VERSIONS"] = ";".join(self._selected_ifc_schemas)
        tc.cache_variables["WITH_OPENCASCADE"] = self.options.build_ifcgeom
        tc.cache_variables["WITH_CGAL"] = self.options.get_safe("with_cgal", False)
        tc.cache_variables["HDF5_SUPPORT"] = self.options.get_safe("with_hdf5", False)
        tc.cache_variables["COLLADA_SUPPORT"] = False
        if self.options.build_ifcgeom:
            tc.cache_variables["EIGEN_DIR"] = includedir("eigen") + "/eigen3/"
        if self.options.get_safe("with_cgal"):
            tc.cache_variables["CGAL_INCLUDE_DIR"] = includedir("cgal")
            tc.cache_variables["CGAL_LIBRARY_DIR"] = libdir("cgal")
            tc.cache_variables["GMP_INCLUDE_DIR"] = includedir("gmp")
            tc.cache_variables["GMP_LIBRARY_DIR"] = libdir("gmp")
            tc.cache_variables["MPFR_INCLUDE_DIR"] = includedir("mpfr")
            tc.cache_variables["MPFR_LIBRARY_DIR"] = libdir("mpfr")
        if self.options.get_safe("with_hdf5"):
            tc.cache_variables["HDF5_INCLUDE_DIR"] = includedir("hdf5")
            tc.cache_variables["HDF5_LIBRARY_DIR"] = libdir("hdf5")

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        # cmake.build()
        cmake.build(cli_args=["--verbose"], build_tool_args=["-j", "2"])

    def package(self):
        copy(self, "COPYING*", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

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
        if self.options.use_mmap:
            ifcparse.requires.extend(["boost::iostreams", "boost::filesystem",])
            ifcparse.defines.append("USE_MMAP")
        if self.options.ifcxml_support:
            ifcparse.requires.append("libxml2::libxml2")
            ifcparse.defines.append("WITH_IFCXML")
        ifcparse.defines.append(f"SCHEMA_SEQ=({')('.join(self._selected_ifc_schemas)})")
        for schema in self._selected_ifc_schemas:
            ifcparse.defines.append(f"HAS_SCHEMA_{schema}")
        if self.options.shared:
            ifcparse.defines.append("IFC_SHARED_BUILD")
        if self.settings.os in ["Linux", "FreeBSD"]:
            ifcparse.system_libs = ["m", "dl"]

        if self.options.build_ifcgeom:
            ifcgeom = _add_component("IfcGeom", requires=["IfcParse", "eigen::eigen"])
            if self.settings.os in ["Linux", "FreeBSD"]:
                ifcgeom.system_libs.append("pthread")
            # When kernels, mappings and geometry_serializers are built as OBJECT target, we define conan dependencies directly to IfcGeom
            if self.options.get_safe("with_cgal"):
                # ifcgeom.requires.append("geometry_kernel_cgal")
                ifcgeom.defines.append("IFOPSH_WITH_CGAL")
                ifcgeom.requires += ["cgal::cgal", "mpfr::mpfr", "gmp::gmp", "eigen::eigen"]
            ifcgeom.requires += [
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
            ]
            ifcgeom.defines.append("IFOPSH_WITH_OPENCASCADE")
            # if self.options.get_safe("with_cgal"):
            #     _add_component("geometry_kernel_cgal", requires=["cgal::cgal", "mpfr::mpfr", "gmp::gmp", "eigen::eigen",])
            #     ifcgeom.requires.append("geometry_kernel_cgal")
            #     simple = _add_component("geometry_kernel_cgal_simple", requires=["cgal::cgal", "gmp::gmp", "eigen::eigen",])
            #     simple.defines.append("IFOPSH_SIMPLE_KERNEL")
            #     ifcgeom.requires.append("geometry_kernel_cgal_simple")

            # _add_component("geometry_kernel_opencascade", requires=[
            #     "opencascade::occt_tkernel",
            #     "opencascade::occt_tkmath",
            #     "opencascade::occt_tkbrep",
            #     "opencascade::occt_tkgeombase",
            #     "opencascade::occt_tkgeomalgo",
            #     "opencascade::occt_tkg3d",
            #     "opencascade::occt_tkg2d",
            #     "opencascade::occt_tkshhealing",
            #     "opencascade::occt_tktopalgo",
            #     "opencascade::occt_tkmesh",
            #     "opencascade::occt_tkprim",
            #     "opencascade::occt_tkbool",
            #     "opencascade::occt_tkbo",
            #     "opencascade::occt_tkfillet",
            #     "opencascade::occt_tkxsbase",
            #     "opencascade::occt_tkoffset",
            #     "opencascade::occt_tkhlr",
            #     "eigen::eigen",
            # ])
            # ifcgeom.requires.append("geometry_kernel_opencascade")
            # ifcgeom.defines.append("IFOPSH_WITH_OPENCASCADE")
            if self.options.with_hdf5:
                ifcgeom.requires.append("hdf5::hdf5_cpp")
            # for schema in self._selected_ifc_schemas:
            #     _add_component(f"geometry_mapping_ifc{schema}", requires=["IfcParse"])
            #     ifcgeom.requires.append(f"geometry_mapping_ifc{schema}")

        if self.options.build_convert:
            serializers = _add_component("Serializers", requires=["IfcGeom"])
            if self.options.with_hdf5:
                serializers.requires.append("hdf5::hdf5_cpp")
            if self.options.build_convert_with_usd:
                serializers.requires.append("openusd::openusd")
            if self.options.build_convert_with_proj:
                serializers.requires.append("proj::proj")

 
            for schema in self._selected_ifc_schemas:
                component_name = f"Serializers_ifc{schema}"
                _add_component(component_name)
                self.cpp_info.components["Serializers"].requires.append(component_name)

            # geometry_serializer = _add_component("geometry_serializer", ["IfcParse", "IfcGeom", "opencascade::occt_tktopalgo", "opencascade::occt_tkbrep"])
            # for schema in self._selected_ifc_schemas:
            #     component_name = f"geometry_serializer_ifc{schema}"
            #     # _add_component(component_name, requires=["IfcParse", f"Serializers_ifc{schema}", f"geometry_mapping_ifc{schema}", "IfcGeom", "opencascade::occt_tkmesh", "opencascade::occt_tkxmesh", "opencascade::occt_tkmeshvs", "opencascade::occt_tktopalgo", "opencascade::occt_tkbrep", "opencascade::occt_tkgeomalgo"])
            #     _add_component(component_name, requires=["IfcParse", f"Serializers_ifc{schema}", "IfcGeom", "opencascade::occt_tkmesh", "opencascade::occt_tkxmesh", "opencascade::occt_tkmeshvs", "opencascade::occt_tktopalgo", "opencascade::occt_tkbrep", "opencascade::occt_tkgeomalgo"])
            #     geometry_serializer.requires.append(component_name)
