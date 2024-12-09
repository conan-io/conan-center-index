from conan import ConanFile
from conan.tools.files import copy, download, load, save
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class KhrplatformConan(ConanFile):
    name = "khrplatform"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.khronos.org/registry/EGL/"
    description = "Khronos EGL platform interfaces"
    topics = ("opengl", "gl", "egl", "khr", "khronos")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        download(self, filename="khrplatform.h", **self.conan_data["sources"][self.version])

    def build(self):
        pass

    def _extract_license(self):
        license_data = load(self, os.path.join(self.source_folder, "khrplatform.h"))
        begin = license_data.find("/*") + len("/*")
        end = license_data.find("*/")
        return license_data[begin:end].replace("**", "")

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        copy(self, "khrplatform.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include", "KHR"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
