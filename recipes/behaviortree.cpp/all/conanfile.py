from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
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
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tools": [True, False],
        "with_coroutines": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tools": False,
        "with_coroutines": False,
    }

    @property
    def _minimum_cppstd_required(self):
        return 14 if Version(self.version) < "4.0" else 17

    @property
    def _minimum_compilers_version(self):
        if Version(self.version) < "4.0":
            return {
                "gcc": "5",
                "clang": "5",
                "apple-clang": "12",
            }
        else:
            return {
                "gcc": "8",
                "clang": "7",
                "apple-clang": "12",
            }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_coroutines:
            self.requires("boost/1.80.0")
        self.requires("ncurses/6.3")
        self.requires("zeromq/4.3.4")
        self.requires("cppzmq/4.9.0")

    def validate(self):
        if self.info.settings.os == "Windows" and self.info.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Windows.")
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cppstd_required)
        check_min_vs(self, 191 if Version(self.version) < "4.0" else 192)
        if not is_msvc(self):
            minimum_version = self._minimum_compilers_version.get(str(self.info.settings.compiler), False)
            if not minimum_version:
                self.output.warn(f"{self.ref} requires C++{self._minimum_cppstd_required}. Your compiler is unknown. Assuming it supports C++{self._minimum_cppstd_required}.")
            elif Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("BehaviorTree.CPP requires C++{}, which your compiler does not support."
                                                .format(self._minimum_cppstd_required))

        if self.settings.compiler == "clang" and str(self.settings .compiler.libcxx) == "libstdc++":
            raise ConanInvalidConfiguration(f"{self.ref} needs recent libstdc++ with charconv. please switch to gcc, or to libc++")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "4.0":
            tc.variables["BUILD_EXAMPLES"] = False
            tc.variables["BUILD_UNIT_TESTS"] = False
            tc.variables["BUILD_TOOLS"] = self.options.with_tools
            tc.variables["ENABLE_COROUTINES"] = self.options.with_coroutines
        else:
            tc.variables["BTCPP_SHARED_LIBS"] = self.options.shared
            tc.variables["BTCPP_EXAMPLES"] = False
            tc.variables["BTCPP_UNIT_TESTS"] = False
            tc.variables["BTCPP_BUILD_TOOLS"] = self.options.with_tools
            tc.variables["BTCPP_ENABLE_COROUTINES"] = self.options.with_coroutines
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
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
        if Version(self.version) < "4.0":
            self.cpp_info.set_property("cmake_file_name", "BehaviorTreeV3")
        else:
            self.cpp_info.set_property("cmake_file_name", "BehaviorTree")

        libname = "behaviortree_cpp_v3" if Version(self.version) < "4.0" else "behaviortree_cpp"
        self.cpp_info.set_property("cmake_target_name", f"BT::{libname}")

        postfix = "d" if self.settings.os == "Windows" and self.settings.build_type == "Debug" else ""
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components[libname].libs = [f"{libname}{postfix}"]
        self.cpp_info.components[libname].requires = ["zeromq::zeromq", "cppzmq::cppzmq", "ncurses::ncurses"]
        if self.options.with_coroutines:
            self.cpp_info.components[libname].requires.append("boost::coroutine")
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components[libname].system_libs.append("pthread")
        if Version(self.version) >= "4.0" and \
            self.settings.compiler == "gcc" and Version(self.settings.compiler.version).major == "8":
            self.cpp_info.components[libname].system_libs.append("stdc++fs")

        if self.options.with_tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var with : {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        if Version(self.version) < "4.0":
            self.cpp_info.filenames["cmake_find_package"] = "BehaviorTreeV3"
            self.cpp_info.filenames["cmake_find_package_multi"] = "BehaviorTreeV3"
        else:
            self.cpp_info.filenames["cmake_find_package"] = "BehaviorTree"
            self.cpp_info.filenames["cmake_find_package_multi"] = "BehaviorTree"

        self.cpp_info.names["cmake_find_package"] = "BT"
        self.cpp_info.names["cmake_find_package_multi"] = "BT"
        self.cpp_info.components[libname].names["cmake_find_package"] = libname
        self.cpp_info.components[libname].names["cmake_find_package_multi"] = libname
        self.cpp_info.components[libname].set_property("cmake_target_name", f"BT::{libname}")
