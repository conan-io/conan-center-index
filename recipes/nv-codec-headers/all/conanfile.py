import os

from conan import ConanFile
from conan.tools.files import chdir, get, load, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class FFNvEncHeaders(ConanFile):
    name = "nv-codec-headers"
    description = "FFmpeg version of headers required to interface with Nvidia's codec APIs"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/FFmpeg/nv-codec-headers"
    topics = ("ffmpeg", "video", "nvidia", "headers", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            if "CONAN_MAKE_PROGRAM" not in os.environ:
                self.build_requires("make/4.4")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make()

    def _extract_license(self):
        # Extract the License/s from the header to a file
        tmp = load(self, os.path.join(self.source_folder, "include", "ffnvcodec", "nvEncodeAPI.h"))
        license_contents = tmp[2 : tmp.find("*/", 1)]  # The license begins with a C comment /* and ends with */
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

    def package(self):
        self._extract_license()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install(args=["PREFIX=/"])
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("pkg_config_name", "ffnvcodec")
