from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, mkdir, rename, rmdir
import os

required_conan_version = ">=2.1"


class LibkqueueConan(ConanFile):
    name = "libkqueue"
    description = "kqueue(2) compatibility library"
    license = "BSD-2-Clause"
    topics = ("kqueue")
    homepage = "https://github.com/mheily/libkqueue"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_SHARED"] = self.options.shared
        tc.variables["ENABLE_STATIC"] = not self.options.shared
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.os == "Windows" and self.options.shared:
            mkdir(self, os.path.join(self.package_folder, "bin"))
            rename(self, os.path.join(self.package_folder, "lib", "kqueue.dll"),
                   os.path.join(self.package_folder, "bin", "kqueue.dll"))

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "libkqueue::libkqueue")
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.libs = ["kqueue_static"]
        else:
            self.cpp_info.libs = ["kqueue"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")

        self.cpp_info.set_property("cmake_file_name", "libkqueue")
