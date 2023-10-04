from conan import ConanFile
from conan.tools.gnu import AutotoolsToolchain, Autotools, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy, mkdir, rmdir
import pathlib

class gengenConan(ConanFile):
    name = "gengen"

    # Optional metadata
    license = "GPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/gengen/"
    description = "A parameterized-text-generator generator based on a template "
    topics = ("gnu", "generator", "devtool")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    package_type="application"
    generators = "AutotoolsDeps", "AutotoolsToolchain"

    def build_requirements(self):
        self.tool_requires("flex/2.6.4")
        self.tool_requires("bison/3.8.2")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            strip_root=True)

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()

        #copy license to package folder
        lic_path = str(pathlib.Path(self.package_folder) / "licenses")
        mkdir(self, lic_path)
        copy(self, "COPYING", self.source_folder, lic_path)

        #don't need docs etc
        share_dir = str(pathlib.Path(self.package_folder) / "share")
        rmdir(self, share_dir)

    def package_info(self):
        self.cpp_info.includedirs.clear()
        self.cpp_info.libdirs.clear()

    def package_id(self):
        # Only consumed as a compiled application
        del self.info.settings.compiler
