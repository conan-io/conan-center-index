from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
import os

required_conan_version = ">=1.50.0"


class CppKafkaConan(ConanFile):
    name = "cppkafka"
    description = "Modern C++ Apache Kafka client library (wrapper for librdkafka)"
    topics = ("librdkafka", "kafka")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mfontanini/cppkafka"
    license = "MIT"

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
        self.requires("librdkafka/1.9.2")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CPPKAFKA_BUILD_SHARED"] = self.options.shared
        tc.variables["CPPKAFKA_DISABLE_TESTS"] = True
        tc.variables["CPPKAFKA_DISABLE_EXAMPLES"] = True
        tc.variables["CPPKAFKA_RDKAFKA_STATIC_LIB"] = False # underlying logic is useless
        if self.settings.os == "Windows":
            tc.preprocessor_definitions["NOMINMAX"] = 1
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
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CppKafka")
        self.cpp_info.set_property("cmake_target_name", "CppKafka::cppkafka")
        self.cpp_info.set_property("pkg_config_name", "cppkafka")

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["_cppkafka"].libs = ["cppkafka"]
        self.cpp_info.components["_cppkafka"].requires = ["boost::headers", "librdkafka::librdkafka"]
        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.components["_cppkafka"].system_libs = ["mswsock", "ws2_32"]
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_cppkafka"].system_libs = ["pthread"]
        if not self.options.shared:
            self.cpp_info.components["_cppkafka"].defines.append("CPPKAFKA_STATIC")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "CppKafka"
        self.cpp_info.names["cmake_find_package_multi"] = "CppKafka"
        self.cpp_info.components["_cppkafka"].names["cmake_find_package"] = "cppkafka"
        self.cpp_info.components["_cppkafka"].names["cmake_find_package_multi"] = "cppkafka"
        self.cpp_info.components["_cppkafka"].set_property("cmake_target_name", "CppKafka::cppkafka")
        self.cpp_info.components["_cppkafka"].set_property("pkg_config_name", "cppkafka")
