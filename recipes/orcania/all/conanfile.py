from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.52.0"


class OrcaniaConan(ConanFile):
    name = "orcania"
    description = "Potluck with different functions for different purposes that can be shared among C programs"
    homepage = "https://github.com/babelouest/orcania"
    topics = ("orcania", "utility", "functions", )
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "base64url": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "base64url": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def requirements(self):
        if is_msvc(self) and self.options.base64url:
            self.requires("getopt-for-visual-studio/20200201")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_BASE64URL"] = self.options.base64url
        tc.variables["BUILD_SHARED"] = self.options.shared
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", os.path.join(self.source_folder), os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        libname = "orcania"
        if is_msvc(self) and not self.options.shared:
            libname += "-static"
        self.cpp_info.libs = [libname]

        target_name = "Orcania::Orcanisa" if self.options.shared else "Orcania::Orcania-static"
        self.cpp_info.set_property("cmake_file_name", "Orcania")
        self.cpp_info.set_property("cmake_target_name", target_name)
        self.cpp_info.set_property("cmake_module_file_name", "Orcania")
        self.cpp_info.set_property("cmake_module_target_name", target_name)
        self.cpp_info.set_property("pkg_config_name", "libcorcania")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Orcania"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Orcania"
        self.cpp_info.names["cmake_find_package"] = "Orcania"
        self.cpp_info.names["cmake_find_package_multi"] = "Orcania"
        self.cpp_info.names["pkg_config"] = "liborcania"
