import os
from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=1.37.0"

class KhrplatformConan(ConanFile):
    name = "khrplatform"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.khronos.org/registry/EGL/"
    description = "Khronos EGL platform interfaces"
    topics = ("opengl", "gl", "egl", "khr", "khronos")
    no_copy_source = True

    def source(self):
        tools.files.download(self, filename="khrplatform.h", **self.conan_data["sources"][self.version])

    def package(self):
        self.copy(pattern="khrplatform.h", dst=os.path.join("include", "KHR"))
        license_data = tools.load(os.path.join(self.source_folder, "khrplatform.h"))
        begin = license_data.find("/*") + len("/*")
        end = license_data.find("*/")
        license_data = license_data[begin:end]
        license_data = license_data.replace("**", "")
        tools.save("LICENSE", license_data)
        self.copy("LICENSE", dst="licenses")

    def package_id(self):
        self.info.header_only()
