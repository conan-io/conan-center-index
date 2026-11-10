import os

from conan import ConanFile
from conan.tools.files import copy, get, load, save
from conan.tools.layout import basic_layout

required_conan_version = ">=2.0"


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

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _extract_license(self):
        # Extract the License/s from the header to a file
        tmp = load(self, os.path.join(self.source_folder, "include", "ffnvcodec", "nvEncodeAPI.h"))
        license_contents = tmp[2 : tmp.find("*/", 1)]  # The license begins with a C comment /* and ends with */
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

    def package(self):
        self._extract_license()
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("pkg_config_name", "ffnvcodec")
