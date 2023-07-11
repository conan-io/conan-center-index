from conan import ConanFile, __version__ as conan_version
from conan.tools.scm import Version
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.build import check_min_cppstd
from conan.tools.env import VirtualBuildEnv
import os


required_conan_version = ">=1.53.0"


class ProtobufCConan(ConanFile):
    name = "protobuf-c"
    description = "Protocol Buffers implementation in C"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/protobuf-c/protobuf-c"
    topics = ("protocol-buffers", "protocol-compiler", "serialization", "protocol-compiler")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "with_proto3": [True, False],
        "with_protoc": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "with_proto3": True,
        "with_protoc": True
    }

    def export_sources(self):
        export_conandata_patches(self)
        # TODO: This won't be needed once upstream PR (https://github.com/protobuf-c/protobuf-c/pull/555) gets merged
        copy(self, "protobuf-c.cmake", src=self.recipe_folder, dst=self.export_sources_folder, keep_path=False)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_protoc:
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_protoc:
            self.requires("protobuf/3.21.9")

    def package_id(self):
        # INFO: Protobuf-C provides a C library interface and an executable only.
        self.info.settings.rm_safe("compiler.libcxx")
        self.info.settings.rm_safe("compiler.cppstd")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def build_requirements(self):
        if self.options.with_protoc:
            # Since the package using protobuf-c will also need to use protoc (part of protobuf),
            # we want to make sure the protobuf dep is visible, but the visible param is only available in v2
            # TODO: Remove after dropping Conan 1.x
            if conan_version >= Version("2"):
                self.tool_requires("protobuf/3.21.9", visible=True)
            else:
                self.tool_requires("protobuf/3.21.9")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_PROTO3"] = self.options.with_proto3
        tc.cache_variables["BUILD_PROTOC"] = self.options.with_protoc
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["BUILD_TESTS"] = False
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
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.options.with_protoc:
            # TODO: This won't be needed once upstream PR (https://github.com/protobuf-c/protobuf-c/pull/555) gets merged
            copy(self, "protobuf-c.cmake", dst=os.path.join(self.package_folder, self._cmake_install_base_path), src=self.export_sources_folder)

    def package_info(self):
        self.cpp_info.libs = ["protobuf-c"]
        self.cpp_info.defines = ["PROTOBUF_C_USE_SHARED_LIB"] if self.options.shared else []
        self.cpp_info.set_property("pkg_config_name", "libprotobuf-c")

        if self.options.with_protoc:
            self.cpp_info.builddirs.append(self._cmake_install_base_path)
            # TODO: This won't be needed once upstream PR (https://github.com/protobuf-c/protobuf-c/pull/555) gets merged
            self.cpp_info.set_property("cmake_build_modules", [os.path.join(self._cmake_install_base_path, "protobuf-c.cmake")])

            # TODO: Remove after dropping Conan 1.x
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
