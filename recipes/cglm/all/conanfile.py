from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.29.1"


class CglmConan(ConanFile):
    name = "cglm"
    description = "Highly Optimized Graphics Math (glm) for C "
    topics = ("cglm", "graphics", "opengl", "simd", "vector", "glm")
    homepage = "https://github.com/recp/cglm"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ("CMakeLists.txt", )
    generators = "cmake"
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
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["CGLM_STATIC"] = not self.options.shared
        self._cmake.definitions["CGLM_SHARED"] = self.options.shared
        self._cmake.definitions["CGLM_USE_TEST"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        if not self.options.header_only:
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

        if self.options.header_only:
            self.copy("*", src=os.path.join(self._source_subfolder, "include"), dst="include")
        else:
            cmake = self._configure_cmake()
            cmake.install()

            tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cglm")
        self.cpp_info.set_property("cmake_target_name", "cglm::cglm")
        self.cpp_info.set_property("pkg_config_name", "cglm")

        if not self.options.header_only:
            self.cpp_info.libs = ["cglm"]
            if self.settings.os in ("Linux", "FreeBSD"):
                self.cpp_info.system_libs.append("m")

        # backward support of cmake_find_package, cmake_find_package_multi & pkg_config generators
        self.cpp_info.names["pkg_config"] = "cglm"
        self.cpp_info.names["cmake_find_package"] = "cglm"
        self.cpp_info.names["cmake_find_package_multi"] = "cglm"
