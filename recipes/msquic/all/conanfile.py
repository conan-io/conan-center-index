from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get, rmdir
import os
import yaml


class MsQuicConan(ConanFile):
    name = "msquic"
    package_type = "library"

    # Metadata
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Cross-platform, C implementation of the IETF QUIC protocol"
    homepage = "https://github.com/microsoft/msquic"
    topics = ("quic", "networking", "protocol", "microsoft", "ietf")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    implements = ["auto_shared_fpic"]
    exports = "submoduledata.yml"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

        submodule_filename = os.path.join(self.recipe_folder, "submoduledata.yml")
        with open(submodule_filename, "r") as submodule_stream:
            submodules_data = yaml.safe_load(submodule_stream)
            for path, submodule in submodules_data["submodules"][self.version].items():
                archive_name = os.path.splitext(
                    os.path.basename(submodule["url"]))[0]
                get(self, url=submodule["url"],
                    sha256=submodule["sha256"],
                    destination=path,
                    filename=archive_name,
                    strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["QUIC_BUILD_TOOLS"] = False
        tc.cache_variables["QUIC_BUILD_TEST"] = False
        tc.cache_variables["QUIC_BUILD_PERF"] = False
        tc.cache_variables["QUIC_BUILD_SHARED"] = bool(self.options.shared)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "msquic")
        self.cpp_info.set_property("cmake_target_name", "msquic::msquic")
        self.cpp_info.libs = ["msquic"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "dl", "m"]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "Security"]
