from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, copy, rmdir, replace_in_file, save, rm
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

import os

required_conan_version = ">=1.53.0"

class BehaviorTreeCPPConan(ConanFile):
    name = "behaviortree.cpp"
    description = "This C++ library provides a framework to create BehaviorTrees"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/BehaviorTree/BehaviorTree.CPP"
    topics = ("ai", "robotics", "games", "coordination")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tools": [True, False],
        "with_coroutines": [True, False],
        "enable_groot_interface": [True, False],
        "enable_sqlite_logging": [True, False],
        "enable_manual_selector": [True, False],
        "use_v3_compatible_names": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tools": False,
        "with_coroutines": False,
        "enable_groot_interface": True,
        "enable_sqlite_logging": True,
        "enable_manual_selector": False,
        "use_v3_compatible_names": False,
    }
    options_description = {
        "with_tools": "Build commandline tools",
        "with_coroutines": "Enable Boost coroutines",
        "enable_groot_interface": "Add Groot2 connection (requires ZeroMQ)",
        "enable_sqlite_logging": "Add SQLite logging",
        "enable_manual_selector": "Build manual selector node",
        "use_v3_compatible_names": "Use v3 compatible names",
    }

    @property
    def _minimum_cppstd_required(self):
        if Version(self.version) >= "4.0":
            return 17
        return 14

    @property
    def _minimum_compilers_version(self):
        if Version(self.version) >= "4.0":
            return {
                "gcc": "8",
                "clang": "7",
                "apple-clang": "12",
                "msvc": "192",
                "Visual Studio": "16",
            }
        else:
            return {
                "gcc": "5",
                "clang": "5",
                "apple-clang": "12",
                "msvc": "191",
                "Visual Studio": "15",
            }

    def export_sources(self):
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "4.0":
            del self.options.use_v3_compatible_names
        if Version(self.version) >= "4.1.0":
            del self.options.with_coroutines
        if Version(self.version) >= "4.1.1":
            del self.options.enable_manual_selector
        else:
            del self.options.enable_groot_interface
            del self.options.enable_sqlite_logging

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _with_boost(self):
        return self.options.get_safe("with_coroutines", False)

    @property
    def _with_lexy(self):
        # FIXME: using vendored version temporarily due to a missing CCI binary
        # return Version(self.version) >= "4.0.0"
        return False

    @property
    def _with_minitrace(self):
        return Version(self.version) >= "4.3.4"

    @property
    def _with_ncurses(self):
        return self.options.get_safe("enable_manual_selector", False)

    @property
    def _with_sqlite3(self):
        return self.options.get_safe("enable_sqlite_logging", False)

    @property
    def _with_tinyxml2(self):
        return Version(self.version) >= "4.0.0"

    @property
    def _with_zeromq(self):
        if Version(self.version) >= "4.1.1":
            return self.options.enable_groot_interface
        return Version(self.version) >= "4.0.0"

    def requirements(self):
        if self._with_boost:
            self.requires("boost/1.83.0")
        if self._with_ncurses:
            self.requires("ncurses/6.4")
        if self._with_lexy:
            self.requires("foonathan-lexy/2022.12.1")
        if self._with_minitrace:
            self.requires("minitrace/cci.20230905")
        if self._with_sqlite3:
            self.requires("sqlite3/3.44.2")
        if self._with_tinyxml2:
            self.requires("tinyxml2/10.0.0")
        if self._with_zeromq:
            self.requires("zeromq/4.3.5")

        # TODO: other vendored dependencies
        # - cppzmq is customized and not compatible with Conan version
        # - cpp-sqlite
        # - minicoro
        # - wildcards

    def validate(self):
        if self.info.settings.os == "Windows" and self.info.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Windows.")
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cppstd_required)
        minimum_version = self._minimum_compilers_version.get(str(self.info.settings.compiler), False)
        if not minimum_version:
            self.output.warn(f"{self.ref} requires C++{self._minimum_cppstd_required}. "
                             f"Your compiler is unknown. Assuming it supports C++{self._minimum_cppstd_required}.")
        elif Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"BehaviorTree.CPP requires C++{self._minimum_cppstd_required}, which your compiler does not support."
            )

        if self.settings.compiler == "clang" and str(self.settings .compiler.libcxx) == "libstdc++":
            raise ConanInvalidConfiguration(f"{self.ref} needs recent libstdc++ with charconv. please switch to gcc, or to libc++")

        if self.settings.compiler == "apple-clang" and cross_building(self) and self.settings.arch in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration(f"Cross-compiling for {self.settings.arch} is not yet supported. Contributions are welcome!")

    def build_requirements(self):
        if Version(self.version) >= "4.1.0":
            self.tool_requires("cmake/[>=3.16.3 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        tc = CMakeToolchain(self)
        tc.variables["CMAKE_PROJECT_behaviortree_cpp_INCLUDE"] = "conan_deps.cmake"
        tc.variables["WITH_LEXY"] = self._with_lexy
        tc.variables["WITH_MINITRACE"] = self._with_minitrace
        tc.variables["WITH_TINYXML2"] = self._with_tinyxml2
        if not self.options.get_safe("enable_manual_selector"):
            # Avoid accidental use of system ncurses
            tc.variables["CMAKE_DISABLE_FIND_PACKAGE_Curses"] = True
        if Version(self.version) < "4.0":
            tc.variables["BUILD_EXAMPLES"] = False
            tc.variables["BUILD_UNIT_TESTS"] = False
            tc.variables["BUILD_TOOLS"] = self.options.with_tools
            tc.variables["ENABLE_COROUTINES"] = self.options.with_coroutines
            tc.variables["BUILD_MANUAL_SELECTOR"] = self.options.get_safe("enable_manual_selector", False)
        else:
            tc.variables["BTCPP_SHARED_LIBS"] = self.options.shared
            tc.variables["BTCPP_EXAMPLES"] = False
            tc.variables["BTCPP_UNIT_TESTS"] = False
            tc.variables["BTCPP_BUILD_TOOLS"] = self.options.with_tools
            tc.variables["BTCPP_ENABLE_COROUTINES"] = self.options.get_safe("with_coroutines", False)
            tc.variables["BTCPP_MANUAL_SELECTOR"] = self.options.get_safe("enable_manual_selector", False)
            tc.variables["BTCPP_GROOT_INTERFACE"] = self.options.get_safe("enable_groot_interface", False)
            tc.variables["BTCPP_SQLITE_LOGGING"] = self.options.get_safe("enable_sqlite_logging", False)
            tc.variables["USE_V3_COMPATIBLE_NAMES"] = self.options.use_v3_compatible_names
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        if Version(self.version) >= "4.1.0":
            deps.set_property("zeromq", "cmake_file_name", "ZeroMQ")
        else:
            deps.set_property("zeromq", "cmake_file_name", "ZMQ")
        deps.generate()

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        # Let Conan handle -fPIC
        replace_in_file(self, cmakelists, "set(CMAKE_POSITION_INDEPENDENT_CODE ON)\n", "")
        # Unvendor lexy
        if self._with_lexy:
            rmdir(self, os.path.join(self.source_folder, "3rdparty", "lexy"))
            save(self, os.path.join(self.source_folder, "3rdparty", "lexy", "CMakeLists.txt"), "")
        # Unvendor minitrace
        if self._with_minitrace:
            rmdir(self, os.path.join(self.source_folder, "3rdparty", "minitrace"))
            replace_in_file(self, cmakelists, "3rdparty/minitrace/minitrace.cpp", "")
            replace_in_file(self, os.path.join(self.source_folder, "src", "loggers", "bt_minitrace_logger.cpp"),
                            "minitrace/minitrace.h", "minitrace.h")
        # Unvendor tinyxml2
        if self._with_tinyxml2:
            rmdir(self, os.path.join(self.source_folder, "3rdparty", "tinyxml2"))
            replace_in_file(self, cmakelists, "3rdparty/tinyxml2/tinyxml2.cpp", "")
            replace_in_file(self, os.path.join(self.source_folder, "src", "xml_parsing.cpp"),
                            "tinyxml2/tinyxml2.h", "tinyxml2.h")
        # Ensure ZeroMQ and other packages are provided by Conan
        rm(self, "Find*.cmake", os.path.join(self.source_folder, "cmake"))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "BehaviorTreeV3"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if Version(self.version) >= "4.0":
            cmake_file_name = "BehaviorTree"
            libname = "behaviortree_cpp"
        else:
            cmake_file_name = "BehaviorTreeV3"
            libname = "behaviortree_cpp_v3"
        self.cpp_info.set_property("cmake_file_name", cmake_file_name)
        self.cpp_info.set_property("cmake_target_name", f"BT::{libname}")

        requires = []
        if self._with_boost:
            requires.append("boost::coroutine")
        if self._with_lexy:
            requires.append("foonathan-lexy::foonathan-lexy")
        if self._with_minitrace:
            requires.append("minitrace::minitrace")
        if self._with_ncurses:
            requires.append("ncurses::ncurses")
        if self._with_sqlite3:
            requires.append("sqlite3::sqlite3")
        if self._with_tinyxml2:
            requires.append("tinyxml2::tinyxml2")
        if self._with_zeromq:
            requires.append("zeromq::zeromq")

        postfix = "d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components[libname].libs = [f"{libname}{postfix}"]
        self.cpp_info.components[libname].requires = requires
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components[libname].system_libs.extend(["pthread", "dl"])
        if Version(self.version) >= "4.0" and \
            self.settings.compiler == "gcc" and Version(self.settings.compiler.version).major == "8":
            self.cpp_info.components[libname].system_libs.append("stdc++fs")

        if self.options.with_tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = cmake_file_name
        self.cpp_info.filenames["cmake_find_package_multi"] = cmake_file_name
        self.cpp_info.names["cmake_find_package"] = "BT"
        self.cpp_info.names["cmake_find_package_multi"] = "BT"
        self.cpp_info.components[libname].names["cmake_find_package"] = libname
        self.cpp_info.components[libname].names["cmake_find_package_multi"] = libname
        self.cpp_info.components[libname].set_property("cmake_target_name", f"BT::{libname}")
