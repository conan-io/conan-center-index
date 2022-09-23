from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, get, rmdir
import os

required_conan_version = ">=1.50.0"


class LibcdsConan(ConanFile):
    name = "libcds"
    description = "C++11 library of Concurrent Data Structures."
    license = "BSL-1.0"
    topics = ("libcds", "concurrent", "lock-free", "containers", "hazard-pointer", "rcu")
    homepage = "https://github.com/khizmax/libcds"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.79.0")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if self.info.settings.os == "Macos" and self.info.settings.arch == "armv8":
            raise ConanInvalidConfiguration("Macos M1 not supported (yet)")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_TESTS"] = False
        tc.variables["WITH_TESTS_COVERAGE"] = False
        tc.variables["WITH_BOOST_ATOMIC"] = False
        tc.variables["WITH_ASAN"] = False
        tc.variables["WITH_TSAN"] = False
        tc.variables["ENABLE_UNIT_TEST"] = False
        tc.variables["ENABLE_STRESS_TEST"] = False
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        cmake_target = "cds" if self.options.shared else "cds-s"
        self.cpp_info.set_property("cmake_file_name", "LibCDS")
        self.cpp_info.set_property("cmake_target_name", "LibCDS::{}".format(cmake_target))
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["_libcds"].libs = collect_libs(self)
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.components["_libcds"].defines = ["CDS_BUILD_STATIC_LIB"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_libcds"].system_libs = ["pthread"]
        if self.settings.compiler in ["gcc", "clang", "apple-clang"] and self.settings.arch == "x86_64":
            self.cpp_info.components["_libcds"].cxxflags = ["-mcx16"]
        self.cpp_info.components["_libcds"].requires = ["boost::boost"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "LibCDS"
        self.cpp_info.names["cmake_find_package_multi"] = "LibCDS"
        self.cpp_info.components["_libcds"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["_libcds"].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components["_libcds"].set_property("cmake_target_name", "LibCDS::{}".format(cmake_target))
