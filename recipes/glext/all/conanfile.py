import os

from conan import ConanFile
from conan.tools.files import copy, download, load, save
from conan.tools.layout import basic_layout

required_conan_version = ">=1.52.0"


class GlextConan(ConanFile):
    name = "glext"
    description = "OpenGL 1.2 and above compatibility profile and extension interfaces"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.khronos.org/registry/OpenGL/index_gl.php"
    topics = ("opengl", "gl", "glext", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opengl/system")
        self.requires("khrplatform/cci.20200529")

    def package_id(self):
        self.info.clear()

    def source(self):
        download(self, filename="glext.h", **self.conan_data["sources"][self.version])

    def _extract_license(self):
        license_data = load(self, os.path.join(self.source_folder, "glext.h"))
        begin = license_data.find("/*") + len("/*")
        end = license_data.find("*/")
        license_data = license_data[begin:end]
        license_data = license_data.replace("**", "")
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_data)

    def package(self):
        self._extract_license()
        copy(self, "glext.h",
             dst=os.path.join(self.package_folder, "include", "GL"),
             src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
