from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, save
import os

required_conan_version = ">=1.53.0"


class MikkTSpaceConan(ConanFile):
    name = "mikktspace"
    description = " A common standard for tangent space used in baking tools to produce normal maps."
    homepage = "https://github.com/mmikk/MikkTSpace"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Zlib"
    topics = ("tangent", "space", "normal")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MIKKTSPACE_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    @property
    def _extracted_license(self):
        content_lines = open(os.path.join(self.source_folder, "mikktspace.h")).readlines()
        license_content = []
        for i in range(4, 21):
            license_content.append(content_lines[i][4:-1])
        return "\n".join(license_content)

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extracted_license)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["mikktspace"]
        if not self.options.shared and self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
