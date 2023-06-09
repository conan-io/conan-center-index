from conan import ConanFile, __version__ as conan_version
from conan.tools.scm import Version
from conan.tools.apple import is_apple_os
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
import os


required_conan_version = ">=1.53.0"


class ProtobufCConan(ConanFile):
    name = "protobuf-c"
    description = "Protocol Buffers implementation in C"
    license = "LicenseRef-LICENSE"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/protobuf-c/protobuf-c"
    topics = ("protocol-buffers", "protocol-compiler", "serialization", "protocol-compiler")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_proto3": [True, False],
        "with_protoc": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_proto3": True,
        "with_protoc": True
    }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 14)

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "protobuf-gen-c.cmake", src=self.recipe_folder, dst=self.export_sources_folder, keep_path=False)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        # Since the package using protobuf-c will also need to use protoc (part of protobuf),
        # we want to make sure the protobuf dep is visible, but the visible param is only available in v2
        if conan_version >= Version("2"):
            self.tool_requires("protobuf/3.21.9", visible=True)
        else:
            self.tool_requires("protobuf/3.21.9")

    def requirements(self):
        self.requires("protobuf/3.21.9")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_PROTO3"] = self.options.with_proto3
        tc.cache_variables["BUILD_PROTOC"] = self.options.with_protoc
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["BUILD_TESTS"] = False
        if is_apple_os(self) and self.options.shared:
            # Workaround against SIP on macOS for consumers while invoking protoc when protobuf lib is shared
            tc.variables["CMAKE_INSTALL_RPATH"] = "@loader_path/../lib"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "build-cmake"))
        cmake.build()

    @property
    def _cmake_install_base_path(self):
        return os.path.join("lib", "cmake", "protobuf-c")

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "protobuf-gen-c.cmake", dst=os.path.join(self.package_folder, self._cmake_install_base_path), src=self.export_sources_folder)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["protobuf-c"]
        self.cpp_info.builddirs.append(self._cmake_install_base_path)

        # upstream CMake config file name and target name matches the package name

        self.cpp_info.set_property("cmake_build_modules", [
            os.path.join(self._cmake_install_base_path, "protobuf-gen-c.cmake")
        ])

        bin_dir = os.path.join(self.package_folder, "bin")
        self.buildenv_info.append_path("PATH", bin_dir)
