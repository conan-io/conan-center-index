from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, rmdir, collect_libs
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class SobjectizerConan(ConanFile):
    name = "sobjectizer"
    license = "BSD-3-Clause"
    homepage = "https://github.com/Stiffstream/sobjectizer"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
            "A framework for simplification of development of sophisticated "
            "concurrent and event-driven applications in C++ "
            "by using Actor, Publish-Subscribe and CSP models."
    )
    topics = ("concurrency", "actor-framework", "actors", "agents", "actor-model", "publish-subscribe", "CSP")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def _compiler_support_lut(self):
        if self.version >= Version("5.8.0"):
            # Since v5.8.0 requirements to compilers were updated:
            return {
                "gcc": "10",
                "clang": "11",
                "apple-clang": "13",
                "Visual Studio": "17",
                "msvc": "192"
            }

        return {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191"
        }

    def validate(self):
        minimal_cpp_standard = "17"
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = self._compiler_support_lut()

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warning(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warning(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return

        version = Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SOBJECTIZER_BUILD_SHARED"] = self.options.shared
        tc.variables["SOBJECTIZER_BUILD_STATIC"] = not self.options.shared
        tc.variables["SOBJECTIZER_INSTALL"] = True
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0091"] = "NEW"
        tc.generate()

        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "dev", "so_5"))
        cmake.build()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        cmake_target = "SharedLib" if self.options.shared else "StaticLib"
        self.cpp_info.set_property("cmake_file_name", "sobjectizer")
        self.cpp_info.set_property("cmake_target_name", "sobjectizer::{}".format(cmake_target))
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["_sobjectizer"].libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_sobjectizer"].system_libs = ["pthread", "m"]
        if not self.options.shared:
            self.cpp_info.components["_sobjectizer"].defines.append("SO_5_STATIC_LIB")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "sobjectizer"
        self.cpp_info.names["cmake_find_package_multi"] = "sobjectizer"
        self.cpp_info.components["_sobjectizer"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["_sobjectizer"].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components["_sobjectizer"].set_property("cmake_target_name", "sobjectizer::{}".format(cmake_target))
