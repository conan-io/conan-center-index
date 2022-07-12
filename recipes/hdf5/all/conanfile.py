from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os
import textwrap

required_conan_version = ">=1.43.0"


class Hdf5Conan(ConanFile):
    name = "hdf5"
    description = "HDF5 is a data model, library, and file format for storing and managing data."
    license = "BSD-3-Clause"
    topics = ("hdf5", "hdf", "data")
    homepage = "https://portal.hdfgroup.org/display/HDF5/HDF5"
    url = "https://github.com/conan-io/conan-center-index"

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
    }

    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.enable_cxx:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd
        if self.options.enable_cxx or self.options.hl or (self.settings.os == "Windows" and not self.options.shared):
            del self.options.threadsafe
        if not bool(self.options.szip_support):
            del self.options.szip_encoding

    def requirements(self):
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")
        if self.options.szip_support == "with_libaec":
            self.requires("libaec/1.0.6")
        elif self.options.szip_support == "with_szip":
            self.requires("szip/2.1.1")
        if self.options.parallel:
            self.requires("openmpi/4.1.0")

    def validate(self):
        if hasattr(self, "settings_build") and tools.cross_building(self, skip_x64_x86=True):
            # While building it runs some executables like H5detect
            raise ConanInvalidConfiguration("Current recipe doesn't support cross-building (yet)")
        if self.options.parallel:
            if self.options.enable_cxx:
                raise ConanInvalidConfiguration("Parallel and C++ options are mutually exclusive")
            if self.options.get_safe("threadsafe", False):
                raise ConanInvalidConfiguration("Parallel and Threadsafe options are mutually exclusive")
        if self.options.szip_support == "with_szip" and self.options.szip_encoding and \
           not self.options["szip"].enable_encoding:
            raise ConanInvalidConfiguration("encoding must be enabled in szip dependency (szip:enable_encoding=True)")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # Do not force PIC
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "set (CMAKE_POSITION_INDEPENDENT_CODE ON)", "")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["HDF5_EXTERNALLY_CONFIGURED"] = True
        cmake.definitions["HDF5_EXTERNAL_LIB_PREFIX"] = ""
        cmake.definitions["HDF5_USE_FOLDERS"] = False
        cmake.definitions["HDF5_NO_PACKAGES"] = True
        cmake.definitions["ALLOW_UNSUPPORTED"] = False
        if tools.Version(self.version) >= "1.10.6":
            cmake.definitions["ONLY_SHARED_LIBS"] = self.options.shared
        cmake.definitions["BUILD_STATIC_EXECS"] = False
        cmake.definitions["HDF5_ENABLE_COVERAGE"] = False
        cmake.definitions["HDF5_ENABLE_USING_MEMCHECKER"] = False
        if tools.Version(self.version) >= "1.10.0":
            cmake.definitions["HDF5_MEMORY_ALLOC_SANITY_CHECK"] = False
        if tools.Version(self.version) >= "1.10.5":
            cmake.definitions["HDF5_ENABLE_PREADWRITE"] = True
        cmake.definitions["HDF5_ENABLE_DEPRECATED_SYMBOLS"] = True
        cmake.definitions["HDF5_BUILD_GENERATORS"] = False
        cmake.definitions["HDF5_ENABLE_TRACE"] = False
        if self.settings.build_type == "Debug":
            cmake.definitions["HDF5_ENABLE_INSTRUMENT"] = False  # Option?
        cmake.definitions["HDF5_ENABLE_PARALLEL"] = self.options.parallel
        cmake.definitions["HDF5_ENABLE_Z_LIB_SUPPORT"] = self.options.with_zlib
        cmake.definitions["HDF5_ENABLE_SZIP_SUPPORT"] = bool(self.options.szip_support)
        if bool(self.options.szip_support):
            cmake.definitions["CONAN_SZIP_LIBNAME"] = self._get_szip_lib() # this variable is added by conanize-link-szip*.patch
        cmake.definitions["HDF5_ENABLE_SZIP_ENCODING"] = self.options.get_safe("szip_encoding", False)
        cmake.definitions["HDF5_PACKAGE_EXTLIBS"] = False
        cmake.definitions["HDF5_ENABLE_THREADSAFE"] = self.options.get_safe("threadsafe", False)
        cmake.definitions["HDF5_ENABLE_DEBUG_APIS"] = False # Option?
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["HDF5_INSTALL_INCLUDE_DIR"] = os.path.join(self.package_folder, "include", "hdf5")
        cmake.definitions["HDF5_BUILD_TOOLS"] = False
        cmake.definitions["HDF5_BUILD_EXAMPLES"] = False
        cmake.definitions["HDF5_BUILD_HL_LIB"] = self.options.hl
        cmake.definitions["HDF5_BUILD_FORTRAN"] = False
        cmake.definitions["HDF5_BUILD_CPP_LIB"] = self.options.enable_cxx
        if tools.Version(self.version) >= "1.10.0":
            cmake.definitions["HDF5_BUILD_JAVA"] = False

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _get_szip_lib(self):
        return {
            "with_libaec": "libaec",
            "with_szip": "szip",
        }.get(str(self.options.szip_support))

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

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets, is_parallel):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                    if(TARGET {aliased} AND NOT TARGET {alias})
                        add_library({alias} INTERFACE IMPORTED)
                        set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                    endif()
                """.format(alias=alias, aliased=aliased))

        # add the additional hdf5_hl_cxx target when both CXX and HL components are specified
        content += textwrap.dedent("""\
                if(TARGET HDF5::HL AND TARGET HDF5::CXX AND NOT TARGET hdf5::hdf5_hl_cpp)
                    add_library(hdf5::hdf5_hl_cpp INTERFACE IMPORTED)
                    set_property(TARGET hdf5::hdf5_hl_cpp PROPERTY INTERFACE_LINK_LIBRARIES HDF5::HL_CXX)
                endif()
            """)
        content += textwrap.dedent("set(HDF5_IS_PARALLEL {})".format("ON" if is_parallel else "OFF"))
        tools.save(module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake",
                            "conan-official-{}-targets.cmake".format(self.name))

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.remove(os.path.join(self.package_folder, "lib", "libhdf5.settings"))
        # Mimic the official CMake FindHDF5 targets. HDF5::HDF5 refers to the global target as per conan,
        # but component targets have a lower case namespace prefix. hdf5::hdf5 refers to the C library only
        components = self._components()
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"hdf5::{}".format(component["alias_target"]): "HDF5::{}".format(component["component"]) for component in components.values()},
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

            # TODO: to remove in conan v2 once cmake_find_package_* generators removed
            self.cpp_info.components[component_name].names["cmake_find_package"] = component
            self.cpp_info.components[component_name].names["cmake_find_package_multi"] = component
            self.cpp_info.components[component_name].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components[component_name].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]

        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "HDF5")
        self.cpp_info.set_property("cmake_target_name", "HDF5::HDF5")
        self.cpp_info.set_property("pkg_config_name", "hdf5-all-do-not-use") # to avoid conflict with hdf5_c component

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
