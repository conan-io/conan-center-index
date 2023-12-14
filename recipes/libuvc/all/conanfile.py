from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class LibuvcConan(ConanFile):
    name = "libuvc"
    description = "A cross-platform library for USB video devices"
    topics = ("libusb", "usb", "video")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libuvc/libuvc"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo", "mozjpeg"],
        "jpeg_turbo": [True, False, "deprecated"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_jpeg": "libjpeg",
        "jpeg_turbo": "deprecated",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

        # TODO: to remove once deprecated jpeg_turbo option removed
        if self.options.jpeg_turbo != "deprecated":
            self.output.warning("jpeg_turbo option is deprecated, please use with_jpeg option instead")
            if self.options.jpeg_turbo:
                self.options.with_jpeg == "libjpeg-turbo"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libusb/1.0.26")
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.0")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.3")

    def package_id(self):
        # TODO: to remove once deprecated jpeg_turbo option removed
        del self.info.options.jpeg_turbo

    def validate(self):
        if is_msvc(self):
            # Upstream issues, e.g.:
            # https://github.com/libuvc/libuvc/issues/100
            # https://github.com/libuvc/libuvc/issues/105
            raise ConanInvalidConfiguration("libuvc is not compatible with Visual Studio.")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = CMakeToolchain(self)
        tc.variables["CMAKE_BUILD_TARGET"] = "Shared" if self.options.shared else "Static"
        tc.variables["LIBUVC_WITH_JPEG"] = bool(self.options.with_jpeg)
        if Version(self.version) >= "0.0.7":
            tc.variables["BUILD_EXAMPLE"] = False

        # Relocatable shared libs on macOS
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

        CMakeDeps(self).generate()
        PkgConfigDeps(self).generate()
        # TODO: to remove when properly handled by conan (see https://github.com/conan-io/conan/issues/11962)
        env = Environment()
        env.prepend_path("PKG_CONFIG_PATH", self.generators_folder)
        env.vars(self).save_script("conanbuildenv_pkg_config_path")

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        cmake_target = "UVCShared" if self.options.shared else "UVCStatic"
        self.cpp_info.set_property("cmake_file_name", "libuvc")
        self.cpp_info.set_property("cmake_target_name", f"LibUVC::{cmake_target}")
        self.cpp_info.set_property("pkg_config_name", "libuvc")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["_libuvc"].libs = ["uvc"]
        self.cpp_info.components["_libuvc"].requires = ["libusb::libusb"]
        if self.options.with_jpeg == "libjpeg":
            self.cpp_info.components["_libuvc"].requires.append("libjpeg::libjpeg")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.cpp_info.components["_libuvc"].requires.append("libjpeg-turbo::jpeg")
        elif self.options.with_jpeg == "mozjpeg":
            self.cpp_info.components["_libuvc"].requires.append("mozjpeg::libjpeg")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "libuvc"
        self.cpp_info.filenames["cmake_find_package_multi"] = "libuvc"
        self.cpp_info.names["cmake_find_package"] = "LibUVC"
        self.cpp_info.names["cmake_find_package_multi"] = "LibUVC"
        self.cpp_info.components["_libuvc"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["_libuvc"].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components["_libuvc"].set_property("cmake_target_name", f"LibUVC::{cmake_target}")
        self.cpp_info.components["_libuvc"].set_property("pkg_config_name", "libuvc")
