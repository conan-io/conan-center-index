import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import can_run, check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir, save
from conan.tools.scm import Version

required_conan_version = ">=1.54.0"


class Hdf5Conan(ConanFile):
    name = "hdf5"
    description = "HDF5 is a data model, library, and file format for storing and managing data."
    license = "BSD-3-Clause"
    topics = "hdf", "data"
    homepage = "https://portal.hdfgroup.org/display/HDF5/HDF5"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_cxx": [True, False],
        "hl": [True, False],
        "threadsafe": [True, False],
        "with_zlib": [True, False],
        "szip_support": [None, "with_libaec", "with_szip"],
        "szip_encoding": [True, False],
        "parallel": [True, False],
        "enable_unsupported": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_cxx": True,
        "hl": True,
        "threadsafe": False,
        "with_zlib": True,
        "szip_support": None,
        "szip_encoding": False,
        "parallel": False,
        "enable_unsupported": False
    }

    @property
    def _min_cppstd(self):
        if Version(self.version) < "1.14.0":
            return "98"
        return "11"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.enable_cxx:
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")
        if (not self.options.enable_unsupported and (self.options.enable_cxx or self.options.hl))\
            or (self.settings.os == "Windows" and not self.options.shared):
            del self.options.threadsafe
        if not bool(self.options.szip_support):
            del self.options.szip_encoding

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.13")
        if self.options.szip_support == "with_libaec":
            self.requires("libaec/1.0.6")
        elif self.options.szip_support == "with_szip":
            self.requires("szip/2.1.1")
        if self.options.parallel:
            self.requires("openmpi/4.1.0")

    def validate(self):
        if not can_run(self):
            # While building it runs some executables like H5detect
            raise ConanInvalidConfiguration("Current recipe doesn't support cross-building (yet)")
        if self.options.parallel and not self.options.enable_unsupported:
            if self.options.enable_cxx:
                raise ConanInvalidConfiguration("Parallel and C++ options are mutually exclusive, forcefully allow with enable_unsupported=True")
            if self.options.get_safe("threadsafe", False):
                raise ConanInvalidConfiguration("Parallel and Threadsafe options are mutually exclusive, forcefully allow with enable_unsupported=True")
        if self.options.szip_support == "with_szip" and \
                self.options.szip_encoding and \
                not self.dependencies["szip"].options.enable_encoding:
            raise ConanInvalidConfiguration("encoding must be enabled in szip dependency (szip:enable_encoding=True)")
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def build_requirements(self):
        if Version(self.version) >= "1.14.0":
            self.tool_requires("cmake/[>=3.18 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _inject_stdlib_flag(self, tc):
        if self.settings.os == "Linux" and self.settings.compiler == "clang":
            cpp_stdlib = f" -stdlib={self.settings.compiler.libcxx}".rstrip("1")  # strip 11 from stdlibc++11
            tc.variables["CMAKE_CXX_FLAGS"] = tc.variables.get("CMAKE_CXX_FLAGS", "") + cpp_stdlib
        return tc

    def generate(self):
        cmakedeps = CMakeDeps(self)
        cmakedeps.generate()

        tc = CMakeToolchain(self)
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        if self.settings.get_safe("compiler.libcxx"):
            tc = self._inject_stdlib_flag(tc)
        if self.options.szip_support == "with_libaec":
            tc.variables["USE_LIBAEC"] = True
        tc.variables["HDF5_EXTERNALLY_CONFIGURED"] = True
        tc.variables["HDF5_EXTERNAL_LIB_PREFIX"] = ""
        tc.variables["HDF5_USE_FOLDERS"] = False
        tc.variables["HDF5_NO_PACKAGES"] = True
        tc.variables["ALLOW_UNSUPPORTED"] = False
        if Version(self.version) >= "1.10.6":
            tc.variables["ONLY_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["BUILD_STATIC_EXECS"] = False
        tc.variables["HDF5_ENABLE_COVERAGE"] = False
        tc.variables["HDF5_ENABLE_USING_MEMCHECKER"] = False
        if Version(self.version) >= "1.10.0":
            tc.variables["HDF5_MEMORY_ALLOC_SANITY_CHECK"] = False
        if Version(self.version) >= "1.10.5":
            tc.variables["HDF5_ENABLE_PREADWRITE"] = True
        tc.variables["HDF5_ENABLE_DEPRECATED_SYMBOLS"] = True
        tc.variables["HDF5_BUILD_GENERATORS"] = False
        tc.variables["HDF5_ENABLE_TRACE"] = False
        if self.settings.build_type == "Debug":
            tc.variables["HDF5_ENABLE_INSTRUMENT"] = False  # Option?
        tc.variables["HDF5_ENABLE_PARALLEL"] = self.options.parallel
        tc.variables["HDF5_ENABLE_Z_LIB_SUPPORT"] = self.options.with_zlib
        tc.variables["HDF5_ENABLE_SZIP_SUPPORT"] = bool(self.options.szip_support)
        tc.variables["HDF5_ENABLE_SZIP_ENCODING"] = self.options.get_safe("szip_encoding", False)
        tc.variables["HDF5_PACKAGE_EXTLIBS"] = False
        tc.variables["HDF5_ENABLE_THREADSAFE"] = self.options.get_safe("threadsafe", False)
        tc.variables["HDF5_ENABLE_DEBUG_APIS"] = False # Option?
        tc.variables["BUILD_TESTING"] = False

        tc.variables["HDF5_INSTALL_INCLUDE_DIR"] = "include/hdf5"

        tc.variables["HDF5_BUILD_TOOLS"] = False
        tc.variables["HDF5_BUILD_EXAMPLES"] = False
        tc.variables["HDF5_BUILD_HL_LIB"] = self.options.hl
        tc.variables["HDF5_BUILD_FORTRAN"] = False
        tc.variables["HDF5_BUILD_CPP_LIB"] = self.options.enable_cxx
        if Version(self.version) >= "1.10.0":
            tc.variables["HDF5_BUILD_JAVA"] = False
        tc.variables["ALLOW_UNSUPPORTED"] = self.options.enable_unsupported
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        # Do not force PIC
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                "set (CMAKE_POSITION_INDEPENDENT_CODE ON)", "")
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _components(self):
        hdf5_requirements = []
        if self.options.with_zlib:
            hdf5_requirements.append("zlib::zlib")
        if self.options.szip_support == "with_libaec":
            hdf5_requirements.append("libaec::libaec")
        elif self.options.szip_support == "with_szip":
            hdf5_requirements.append("szip::szip")
        if self.options.parallel:
            hdf5_requirements.append("openmpi::openmpi")

        return {
            "hdf5_c": {"component": "C", "alias_target": "hdf5", "requirements": hdf5_requirements},
            "hdf5_hl": {"component": "HL", "alias_target": "hdf5_hl", "requirements": ["hdf5_c"]},
            "hdf5_cpp": {"component": "CXX", "alias_target": "hdf5_cpp", "requirements": ["hdf5_c"]},
            "hdf5_hl_cpp": {"component": "HL_CXX", "alias_target": "hdf5_hl_cpp", "requirements": ["hdf5_c", "hdf5_cpp", "hdf5_hl"]},
        }

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)

        # add the additional hdf5_hl_cxx target when both CXX and HL components are specified
        content += textwrap.dedent("""\
                if(TARGET HDF5::HL AND TARGET HDF5::CXX AND NOT TARGET hdf5::hdf5_hl_cpp)
                    add_library(hdf5::hdf5_hl_cpp INTERFACE IMPORTED)
                    set_property(TARGET hdf5::hdf5_hl_cpp PROPERTY INTERFACE_LINK_LIBRARIES HDF5::HL_CXX)
                endif()
            """)
        save(self, module_file, content)

    def _create_cmake_module_variables(self, module_file, is_parallel):
        content = "set(HDF5_IS_PARALLEL {})".format("ON" if is_parallel else "OFF")
        save(self, module_file, content)

    @property
    def _module_targets_file_rel_path(self):
        return os.path.join("lib", "cmake",
                            f"conan-official-{self.name}-targets.cmake")

    @property
    def _module_variables_file_rel_path(self):
        return os.path.join("lib", "cmake",
                            f"conan-official-{self.name}-variables.cmake")

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "libhdf5.settings", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

        # remove extra libs... building 1.8.21 as shared also outputs static libs on Linux.
        if self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))

        # Mimic the official CMake FindHDF5 targets. HDF5::HDF5 refers to the global target as per conan,
        # but component targets have a lower case namespace prefix. hdf5::hdf5 refers to the C library only
        components = self._components()
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_targets_file_rel_path),
            {f"hdf5::{component['alias_target']}": f"HDF5::{component['component']}" for component in components.values()}
        )
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_variables_file_rel_path),
            self.options.get_safe("parallel", False)
        )

    def package_info(self):
        def add_component(component_name, component, alias_target, requirements):
            def _config_libname(lib):
                if self.settings.os == "Windows" and self.settings.compiler != "gcc" and not self.options.shared:
                    lib = "lib" + lib
                if self.settings.build_type == "Debug":
                    debug_postfix = "_D" if self.settings.os == "Windows" else "_debug"
                    return lib + debug_postfix
                # See config/cmake_ext_mod/HDFMacros.cmake
                return lib

            self.cpp_info.components[component_name].set_property("cmake_target_name", f"hdf5::{alias_target}")
            self.cpp_info.components[component_name].set_property("pkg_config_name", alias_target)
            self.cpp_info.components[component_name].libs = [_config_libname(alias_target)]
            self.cpp_info.components[component_name].requires = requirements
            self.cpp_info.components[component_name].includedirs.append(os.path.join("include", "hdf5"))

            # TODO: to remove in conan v2 once cmake_find_package_* generators removed
            self.cpp_info.components[component_name].names["cmake_find_package"] = component
            self.cpp_info.components[component_name].names["cmake_find_package_multi"] = component
            self.cpp_info.components[component_name].build_modules["cmake_find_package"] = [self._module_targets_file_rel_path, self._module_variables_file_rel_path]
            self.cpp_info.components[component_name].build_modules["cmake_find_package_multi"] = [self._module_targets_file_rel_path, self._module_variables_file_rel_path]

        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "HDF5")
        self.cpp_info.set_property("cmake_target_name", "HDF5::HDF5")
        self.cpp_info.set_property("pkg_config_name", "hdf5-all-do-not-use") # to avoid conflict with hdf5_c component
        self.cpp_info.set_property("cmake_build_modules", [self._module_variables_file_rel_path])

        components = self._components()
        add_component("hdf5_c", **components["hdf5_c"])
        self.cpp_info.components["hdf5_c"].includedirs.append(os.path.join("include", "hdf5"))
        if self.settings.os == "Linux":
            self.cpp_info.components["hdf5_c"].system_libs.extend(["dl", "m"])
            if self.options.get_safe("threadsafe"):
                self.cpp_info.components["hdf5_c"].system_libs.append("pthread")

        if self.options.shared:
            self.cpp_info.components["hdf5_c"].defines.append("H5_BUILT_AS_DYNAMIC_LIB")
        if self.options.get_safe("enable_cxx"):
            add_component("hdf5_cpp", **components["hdf5_cpp"])
        if self.options.get_safe("hl"):
            add_component("hdf5_hl", **components["hdf5_hl"])
            if self.options.get_safe("enable_cxx"):
                add_component("hdf5_hl_cpp", **components["hdf5_hl_cpp"])

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "HDF5"
        self.cpp_info.names["cmake_find_package_multi"] = "HDF5"
