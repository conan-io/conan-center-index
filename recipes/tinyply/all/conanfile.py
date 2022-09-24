from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, get, load, rmdir, save
import os

required_conan_version = ">=1.50.0"


class TinyplyConan(ConanFile):
    name = "tinyply"
    description = "C++11 ply 3d mesh format importer & exporter."
    license = ["Unlicense", "BSD-2-Clause"]
    topics = ("tinyply", "ply", "geometry", "mesh", "file-format")
    homepage = "https://github.com/ddiakopoulos/tinyply"
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

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
        tc.variables["SHARED_LIB"] = self.options.shared
        tc.variables["BUILD_TESTS"] = False
        # Relocatable shared lib on macOS
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def _extract_license(self):
        readme = load(self, os.path.join(self.source_folder, "readme.md"))
        begin = readme.find("## License")
        return readme[begin:]

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tinyply")
        self.cpp_info.set_property("cmake_target_name", "tinyply::tinyply")
        self.cpp_info.set_property("pkg_config_name", "tinyply")
        self.cpp_info.libs = collect_libs(self)
