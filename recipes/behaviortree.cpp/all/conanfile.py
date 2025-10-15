from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import get, copy, rmdir, replace_in_file, rm
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
        "enable_groot_interface": [True, False],
        "enable_sqlite_logging": [True, False],
        "use_v3_compatible_names": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tools": False,
        "enable_groot_interface": True,
        "enable_sqlite_logging": True,
        "use_v3_compatible_names": False,
    }
    options_description = {
        "with_tools": "Build commandline tools",
        "enable_groot_interface": "Add Groot2 connection (requires cppzmq)",
        "enable_sqlite_logging": "Add SQLite logging",
        "use_v3_compatible_names": "Use v3 compatible names",
    }

    implements = ["auto_shared_fpic"]

    @property
    def _minimum_cppstd_required(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
            "msvc": "192",
            "Visual Studio": "16",
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("flatbuffers/24.12.23")
        self.requires("foonathan-lexy/2025.05.0")
        self.requires("minicoro/0.1.3")
        self.requires("minitrace/cci.20230905")
        self.requires("tinyxml2/11.0.0")
        if self.options.enable_groot_interface:
            self.requires("cppzmq/4.11.0")
        if self.options.enable_sqlite_logging:
            self.requires("sqlite3/3.50.4")

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
            raise ConanInvalidConfiguration(f"Cross-compiling for {self.settings.arch} with apple-clang is not yet supported. Contributions are welcome!")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16.3 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        venv = VirtualBuildEnv(self)
        venv.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["USE_VENDORED_CPPZMQ"] = False
        tc.cache_variables["USE_VENDORED_FLATBUFFERS"] = False
        tc.cache_variables["USE_VENDORED_LEXY"] = False
        tc.cache_variables["USE_VENDORED_MINICORO"] = False
        tc.cache_variables["USE_VENDORED_MINITRACE"] = False
        tc.cache_variables["USE_VENDORED_TINYXML2"] = False

        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["BTCPP_EXAMPLES"] = False

        tc.cache_variables["BTCPP_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["BTCPP_GROOT_INTERFACE"] = self.options.enable_groot_interface
        tc.cache_variables["BTCPP_SQLITE_LOGGING"] = self.options.enable_sqlite_logging
        tc.cache_variables["BTCPP_BUILD_TOOLS"] = self.options.with_tools
        tc.generate()

        cmd = CMakeDeps(self)
        # Override flatbuffer's target name since it could also be  flatbuffers::flatbuffers_shared
        cmd.set_property("flatbuffers", "cmake_target_name", "flatbuffers::flatbuffers")
        cmd.generate()

    def _patch_sources(self):
        # Let Conan handle -fPIC
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "set(CMAKE_POSITION_INDEPENDENT_CODE ON)\n", "")
        # Remove vendored code, just in case
        rmdir(self, os.path.join(self.source_folder, "3rdparty"))
        # Remove Find modules, just in case
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
        self.cpp_info.set_property("cmake_file_name", "BehaviorTree")
        self.cpp_info.set_property("cmake_target_name", "BT::behaviortree_cpp")

        requires = ["foonathan-lexy::foonathan-lexy", "tinyxml2::tinyxml2", "flatbuffers::flatbuffers", "minicoro::minicoro", "minitrace::minitrace"]  
        if self.options.enable_sqlite_logging:
            requires.append("sqlite3::sqlite3")
        if self.options.enable_groot_interface:
            requires.append("cppzmq::cppzmq")

        postfix = "d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["behaviortree_cpp"].libs = [f"behaviortree_cpp{postfix}"]
        self.cpp_info.components["behaviortree_cpp"].requires = requires
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["behaviortree_cpp"].system_libs.extend(["pthread", "dl"])
        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version).major == "8":
            self.cpp_info.components["behaviortree_cpp"].system_libs.append("stdc++fs")

        if self.options.with_tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "BehaviorTree"
        self.cpp_info.filenames["cmake_find_package_multi"] = "BehaviorTree"
        self.cpp_info.names["cmake_find_package"] = "BT"
        self.cpp_info.names["cmake_find_package_multi"] = "BT"
        self.cpp_info.components["behaviortree_cpp"].names["cmake_find_package"] = "behaviortree_cpp"
        self.cpp_info.components["behaviortree_cpp"].names["cmake_find_package_multi"] = "behaviortree_cpp"
        self.cpp_info.components["behaviortree_cpp"].set_property("cmake_target_name", "BT::behaviortree_cpp")
