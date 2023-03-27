from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools.files import get, patch, rmdir, copy
import os

required_conan_version = ">=1.58.0"


class CglmConan(ConanFile):
    name = "cglm"
    description = "Highly Optimized Graphics Math (glm) for C "
    topics = ("cglm", "graphics", "opengl", "simd", "vector", "glm")
    homepage = "https://github.com/recp/cglm"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ("CMakeLists.txt", )
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": False,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    @property
    def _build_subfolder(self):
        return self.build_folder

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.header_only:
            del self.settings.arch
            del self.settings.build_type
            del self.settings.compiler
            del self.settings.os

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["CGLM_STATIC"] = not self.options.shared
        tc.cache_variables["CGLM_SHARED"] = self.options.shared
        tc.cache_variables["CGLM_USE_TEST"] = False
        tc.generate()

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch_args in self.conan_data.get("patches", {}).get(self.version, []):
            patch(self, **patch_args)

        if not self.options.header_only:
            cmake = CMake(self)
            cmake.configure(build_script_folder=self._source_subfolder)
            cmake.build()

    def package(self):
        copy(self, "LICENSE", self._source_subfolder, os.path.join(self.package_folder, "licenses"))

        if self.options.header_only:
            copy(self, "*", os.path.join(self._source_subfolder, "include"), os.path.join(self.package_folder, "include"))

        else:
            cmake = CMake(self)
            cmake.install()

            rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cglm")
        self.cpp_info.set_property("cmake_target_name", "cglm::cglm")
        self.cpp_info.set_property("pkg_config_name", "cglm")

        if not self.options.header_only:
            self.cpp_info.libs = ["cglm"]
            if self.settings.os in ("Linux", "FreeBSD"):
                self.cpp_info.system_libs.append("m")

        # backward support of cmake_find_package, cmake_find_package_multi & pkg_config generators
        #self.cpp_info.names["pkg_config"] = "cglm"
        #self.cpp_info.names["cmake_find_package"] = "cglm"
        #self.cpp_info.names["cmake_find_package_multi"] = "cglm"
