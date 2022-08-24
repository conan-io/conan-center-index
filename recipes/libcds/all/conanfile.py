from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


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

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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

    def requirements(self):
        self.requires("boost/1.78.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration("Macos M1 not supported (yet)")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["WITH_TESTS"] = False
        self._cmake.definitions["WITH_TESTS_COVERAGE"] = False
        self._cmake.definitions["WITH_BOOST_ATOMIC"] = False
        self._cmake.definitions["WITH_ASAN"] = False
        self._cmake.definitions["WITH_TSAN"] = False
        self._cmake.definitions["ENABLE_UNIT_TEST"] = False
        self._cmake.definitions["ENABLE_STRESS_TEST"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        cmake_target = "cds" if self.options.shared else "cds-s"
        self.cpp_info.set_property("cmake_file_name", "LibCDS")
        self.cpp_info.set_property("cmake_target_name", "LibCDS::{}".format(cmake_target))
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["_libcds"].libs = tools.collect_libs(self)
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
