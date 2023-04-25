from conan import ConanFile
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"


class QuaZIPConan(ConanFile):
    name = "quazip"
    description = (
        "A simple C++ wrapper over Gilles Vollant's ZIP/UNZIP package "
        "that can be used to access ZIP archives."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/stachenov/quazip"
    license = "LGPL-2.1-linking-exception"
    topics = ("zip", "unzip", "compress")
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

    @property
    def _qt_major(self):
        return Version(self.dependencies["qt"].ref.version).major

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

    def requirements(self):
        self.requires("qt/5.15.9")
        self.requires("zlib/1.2.13")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["QUAZIP_QT_MAJOR_VERSION"] = self._qt_major
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        quazip_major = Version(self.version).major
        self.cpp_info.set_property("cmake_file_name", f"QuaZip-Qt{self._qt_major}")
        self.cpp_info.set_property("cmake_target_name", "QuaZip::QuaZip")
        self.cpp_info.set_property("pkg_config_name", f"quazip{quazip_major}-qt{self._qt_major}")
        suffix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"quazip{quazip_major}-qt{self._qt_major}{suffix}"]
        self.cpp_info.includedirs = [os.path.join("include", f"QuaZip-Qt{self._qt_major}-{self.version}")]
        if not self.options.shared:
            self.cpp_info.defines.append("QUAZIP_STATIC")

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.filenames["cmake_find_package"] = f"QuaZip-Qt{self._qt_major}"
        self.cpp_info.filenames["cmake_find_package_multi"] = f"QuaZip-Qt{self._qt_major}"
        self.cpp_info.names["cmake_find_package"] = "QuaZip"
        self.cpp_info.names["cmake_find_package_multi"] = "QuaZip"
        self.cpp_info.names["pkg_config"] = f"quazip{quazip_major}-qt{self._qt_major}"
