from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
import os

required_conan_version = ">=1.47.0"


class H3Conan(ConanFile):
    name = "h3"
    description = "Hexagonal hierarchical geospatial indexing system."
    license = "Apache-2.0"
    topics = ("h3", "hierarchical", "geospatial", "indexing")
    homepage = "https://github.com/uber/h3"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_filters": [True, False],
        "h3_prefix": ["ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_filters": True,
        "h3_prefix": "",
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
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["H3_PREFIX"] = self.options.h3_prefix
        tc.variables["ENABLE_COVERAGE"] = False
        tc.variables["BUILD_BENCHMARKS"] = False
        tc.variables["BUILD_FILTERS"] = self.options.build_filters
        tc.variables["BUILD_GENERATORS"] = False
        tc.variables["WARNINGS_AS_ERRORS"] = False
        tc.variables["ENABLE_FORMAT"] = False
        tc.variables["ENABLE_LINTING"] = False
        tc.variables["ENABLE_DOCS"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.generate()

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
        self.cpp_info.set_property("cmake_file_name", "h3")
        self.cpp_info.set_property("cmake_target_name", "h3::h3")
        self.cpp_info.libs = ["h3"]
        self.cpp_info.defines.append("H3_PREFIX={}".format(self.options.h3_prefix))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        if self.options.build_filters:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
