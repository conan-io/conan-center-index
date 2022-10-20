from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get
import os

required_conan_version = ">=1.46.0"


class QuircConan(ConanFile):
    name = "quirc"
    description = "QR decoder library"
    license = "ISC"
    topics = ("quirc", "qr", "decoder")
    homepage = "https://github.com/dlbeer/quirc"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "max_regions": [254, 65534],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "max_regions": 254,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
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
        tc.variables["QUIRC_SRC_DIR"] = os.path.join(self.source_folder, "lib").replace("\\", "/")
        tc.variables["QUIRC_VERSION"] = self.version
        tc.variables["QUIRC_MAX_REGIONS"] = self.options.max_regions
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["quirc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
