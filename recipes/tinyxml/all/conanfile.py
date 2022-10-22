from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, save
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.47.0"


class TinyXmlConan(ConanFile):
    name = "tinyxml"
    description = "TinyXML is a simple, small, C++ XML parser that can be easily integrated into other programs."
    license = "Zlib"
    topics = ("xml", "parser")
    homepage = "http://www.grinninglizard.com/tinyxml/"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_stl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_stl": False,
    }

    exports_sources = "CMakeLists.txt"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} shared not supported by Visual Studio")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TINYXML_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["TINYXML_WITH_STL"] = self.options.with_stl
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def _extract_license(self):
        with open(os.path.join(self.source_folder, "tinyxml.h")) as f:
            content_lines = f.readlines()
        license_content = []
        for i in range(2, 22):
            license_content.append(content_lines[i][:-1])
        return "\n".join(license_content)

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["tinyxml"]
        if self.options.with_stl:
            self.cpp_info.defines = ["TIXML_USE_STL"]

        # TODO: to remove in conan v2, and do not port these names to CMakeDeps, it was a mistake
        self.cpp_info.names["cmake_find_package"] = "TinyXML"
        self.cpp_info.names["cmake_find_package_multi"] = "TinyXML"
