from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, save
import os

required_conan_version = ">=1.52.0"


class WinflexbisonConan(ConanFile):
    name = "winflexbison"
    description = "Flex and Bison for Windows"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/lexxmark/winflexbison"
    topics = ("flex", "bison")
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("winflexbison is only supported on Windows.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _extract_license(self):
        with open(os.path.join(self.source_folder, "bison", "data", "skeletons", "glr.cc")) as f:
            content_lines = f.readlines()
        license_content = []
        for i in range(2, 16):
            license_content.append(content_lines[i][2:-1])
        return "\n".join(license_content)

    def package(self):
        if self.settings.build_type in ("Release", "Debug"):
            exec_build_path = os.path.join(self.source_folder, "bin")
        else:
            exec_build_path = self.build_folder
        package_bin_folder = os.path.join(self.package_folder, "bin")
        copy(self, "*.exe", src=exec_build_path, dst=package_bin_folder, keep_path=False)
        copy(self, "data/*", src=os.path.join(self.source_folder, "bison"), dst=package_bin_folder, keep_path=True)
        copy(self, "FlexLexer.h", src=os.path.join(self.source_folder, "flex", "src"), dst=os.path.join(self.package_folder, "include"), keep_path=False)

        # Copy licenses
        package_license_folder = os.path.join(self.package_folder, "licenses")
        save(self, os.path.join(package_license_folder, "COPYING.GPL3"), self._extract_license())
        copy(self, "COPYING", src=os.path.join(self.source_folder, "flex", "src"), dst=package_license_folder, keep_path=False)
        rename(self, os.path.join(package_license_folder, "COPYING"), os.path.join(package_license_folder, "bison-license"))
        copy(self, "COPYING", src=os.path.join(self.source_folder, "bison", "src"), dst=package_license_folder, keep_path=False)
        rename(self, os.path.join(package_license_folder, "COPYING"), os.path.join(package_license_folder, "flex-license"))

    def package_info(self):
        # A conan recipe can't emulate 2 Find module files,
        # and FindFLEX.cmake & FindBISON.cmake are too complex to emulate anyway
        self.cpp_info.set_property("cmake_find_mode", "none")

        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        lex_path = os.path.join(self.package_folder, "bin", "win_flex").replace("\\", "/")
        self.output.info("Setting LEX environment variable: {}".format(lex_path))
        self.buildenv_info.define_path("LEX", lex_path)

        yacc_path = os.path.join(self.package_folder, "bin", "win_bison -y").replace("\\", "/")
        self.output.info("Setting YACC environment variable: {}".format(yacc_path))
        self.buildenv_info.define_path("YACC", yacc_path)

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.LEX = lex_path
        self.env_info.YACC = yacc_path
