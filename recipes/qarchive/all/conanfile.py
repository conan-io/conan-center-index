from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class QarchiveConan(ConanFile):
    name = "qarchive"
    license = "BSD-3-Clause"
    homepage = "https://antonyjr.in/QArchive/"
    url = "https://github.com/conan-io/conan-center-index"
    description = (
        "QArchive is a cross-platform C++ library that modernizes libarchive, "
        "This library helps you to extract and compress archives supported by libarchive"
    )
    topics = ("qt", "compress", "libarchive")
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
        self.requires("libarchive/3.7.4")
        self.requires("qt/[>=5.15 <7]", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.27 <4]")
        self.tool_requires("qt/<host_version>")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["QARCHIVE_QT_VERSION_MAJOR"] = str(self._qt_major)
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "QArchive")
        self.cpp_info.set_property("cmake_target_name", "QArchive")
        self.cpp_info.set_property("pkg_config_name", "QArchive")
        self.cpp_info.libs = ["QArchive"]
        self.cpp_info.includedirs.append(os.path.join("include", "QArchive"))
        self.cpp_info.requires = ["qt::qtCore", "libarchive::libarchive"]
