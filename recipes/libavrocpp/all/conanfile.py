from conan import ConanFile
from conan.tools.files import get, copy, rm, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=2.1"


class LibavrocppConan(ConanFile):
    name = "libavrocpp"
    description = "Avro is a data serialization system."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://avro.apache.org/"
    topics = ("serialization", "deserialization","avro")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
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
        self.requires("boost/[>=1.81.0 <=1.89.0]", transitive_headers=True)
        self.requires("snappy/[>=1.1.9 <2]")
        self.requires("fmt/[>=12 <13]", transitive_headers=True)
        self.requires("zlib/[>=1.3.1 <2]")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        replace_in_file(self, os.path.join(self.source_folder, "lang", "c++", "CMakeLists.txt"),
                        "-Werror", "")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["AVRO_BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["AVRO_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["AVRO_BUILD_TESTS"] = False
        tc.cache_variables["CMAKE_DISABLE_FIND_PACKAGE_zstd"] = True # please open an issue if this is needed
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("fmt", "cmake_target_aliases", ["fmt::fmt-header-only"])
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "lang", "c++"))
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="NOTICE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        if self.settings.os == "Windows":
            for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
                rm(self, dll_pattern_to_remove, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["avrocpp"] if self.options.shared else ["avrocpp_s"]
        self.cpp_info.set_property("cmake_file_name", "avro-cpp")
        self.cpp_info.set_property("cmake_target_name", "avro-cpp::avrocpp" if self.options.shared else "avro-cpp::avrocpp_s")
        if self.options.shared:
            self.cpp_info.defines.append("AVRO_DYN_LINK")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        self.cpp_info.requires = [
            "zlib::zlib",
            "snappy::snappy",
            "boost::headers",
            "fmt::fmt",
        ]
