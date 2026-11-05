from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
import os

required_conan_version = ">=2.4.0"

class NanoarrowConan(ConanFile):
    name = "nanoarrow"
    description = "A minimal Arrow C Data Interface implementation in C"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/apache/arrow-nanoarrow"
    topics = ("arrow", "c", "data-science")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ipc": [True, False],
        "with_device": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ipc": False,
        "with_device": False,
        "with_zstd": False,
    }
    implements = ["auto_shared_fpic"]
    languages = "C"

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_ipc:
            self.options.rm_safe("with_zstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_ipc:
            # flatcc is bundled because nanoarrow requires a version newer than 0.6.1
            if self.options.get_safe("with_zstd"):
                self.requires("zstd/[>=1.5 <1.6]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NANOARROW_IPC"] = self.options.with_ipc
        tc.variables["NANOARROW_DEVICE"] = self.options.with_device
        if self.options.with_ipc:
            tc.variables["NANOARROW_IPC_WITH_ZSTD"] = self.options.with_zstd
        
        tc.variables["NANOARROW_BUILD_TESTS"] = False
        tc.variables["NANOARROW_BUILD_APPS"] = False
        tc.variables["NANOARROW_BUNDLE"] = False
        tc.variables["NANOARROW_INSTALL_SHARED"] = self.options.shared 
        tc.variables["NANOARROW_DEBUG_EXTRA_WARNINGS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))
            rm(self, "*_static.lib", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "nanoarrow")
        
        suffix = "_shared" if self.options.shared else "_static"

        self.cpp_info.components["nanoarrow_core"].libs = [f"nanoarrow{suffix}"]
        self.cpp_info.components["nanoarrow_core"].set_property("cmake_target_name", "nanoarrow::nanoarrow")
        if self.options.shared:
            self.cpp_info.components["nanoarrow_core"].defines.append("NANOARROW_EXPORT_DLL")
        if self.settings.build_type == "Debug":
            self.cpp_info.components["nanoarrow_core"].defines.append("NANOARROW_DEBUG")
        
        if self.options.with_ipc:
            self.cpp_info.components["nanoarrow_ipc"].libs = [f"nanoarrow_ipc{suffix}"]
            self.cpp_info.components["nanoarrow_ipc"].requires = ["nanoarrow_core"]
            self.cpp_info.components["nanoarrow_ipc"].set_property("cmake_target_name", "nanoarrow::nanoarrow_ipc")
            if self.options.get_safe("with_zstd"):
                self.cpp_info.components["nanoarrow_ipc"].requires.append("zstd::zstd")

        if self.options.with_device:
            self.cpp_info.components["nanoarrow_device"].libs = [f"nanoarrow_device{suffix}"]
            self.cpp_info.components["nanoarrow_device"].requires = ["nanoarrow_core"]
            self.cpp_info.components["nanoarrow_device"].set_property("cmake_target_name", "nanoarrow::nanoarrow_device")
