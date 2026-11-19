import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir, replace_in_file

required_conan_version = ">=2.5"

class InfluxdbCxxConan(ConanFile):
    name = "influxdb-cxx"
    description = "InfluxDB C++ client library."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/offa/influxdb-cxx"
    topics = ("influxdb", "influxdb-client")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "boost": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "boost": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cpr/[>=1.10 <2]")
        if self.options.boost:
            self.requires("boost/[>=1.82.0 <2]")

    def validate(self):
        check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # BUILD_SHARED_LIBS is defined explicitly in CMakeLists.txt
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["INFLUXCXX_TESTING"] = False
        tc.cache_variables["INFLUXCXX_WITH_BOOST"] = self.options.boost
        tc.cache_variables["INFLUXCXX_WERROR"] = False
        if self.options.shared:
            # See https://github.com/offa/influxdb-cxx/issues/194
            # Feedback pending: https://github.com/offa/influxdb-cxx/pull/245
            tc.preprocessor_definitions["InfluxDB_EXPORTS"] = 1
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        # Let the profile's compiler.cppstd drive the standard (validate() enforces the minimum)
        replace_in_file(self, cmakelists,
                        "set(CMAKE_CXX_STANDARD 20)\n"
                        "set(CMAKE_CXX_STANDARD_REQUIRED ON)\n"
                        "set(CMAKE_CXX_EXTENSIONS OFF)\n", "")
        # Let the toolchain handle fPIC, otherwise, keep the upstream behavior
        if self.options.get_safe("fPIC") is not None:
            replace_in_file(self, cmakelists, "set(CMAKE_POSITION_INDEPENDENT_CODE ON)\n", "")

    def build(self):
        self._patch_sources()  # it needs to read the self.options (forbidden in source())
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["InfluxDB"]
        self.cpp_info.set_property("cmake_file_name", "InfluxDB")
        self.cpp_info.set_property("cmake_target_name", "InfluxData::InfluxDB")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
