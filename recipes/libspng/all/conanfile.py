from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=1.52.0"


class LibspngConan(ConanFile):
    name = "libspng"
    description = "Simple, modern libpng alternative "
    topics = ("png", "libpng", "spng")
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/randy408/libspng/"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_miniz": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_miniz": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_miniz:
            self.requires("miniz/2.2.0")
        else:
            self.requires("zlib/1.2.12")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SPNG_SHARED"] = self.options.shared
        tc.variables["SPNG_STATIC"] = not self.options.shared
        tc.variables["SPNG_USE_MINIZ"] = self.options.with_miniz
        tc.variables["BUILD_EXAMPLES"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

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

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libspng")
        if not self.options.shared:
            self.cpp_info.defines = ["SPNG_STATIC"]
        self.cpp_info.libs = ["spng"] if self.options.shared else ["spng_static"]
        if self.settings.os in ["Linux", "Android", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
