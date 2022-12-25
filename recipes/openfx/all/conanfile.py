from conans import ConanFile, CMake, tools
import os


class openfx(ConanFile):
    name = "openfx"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://openeffects.org"
    description = "OpenFX image processing plug-in standard."
    topics = ("image-processing", "standard")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
    }
    requires = ("opengl/system", "expat/2.4.8")
    exports_sources = "CMakeLists.txt", "cmake/*", "symbols/*"

    generators = "cmake", "cmake_find_package"
    _cmake = None

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            destination="source_subfolder",
            strip_root=True
        )

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    @property
    def _build_modules(self):
        return [os.path.join("lib", "cmake", "OpenFX.cmake")]

    def package(self):
        cmake = self._configure_cmake()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        cmake.install()

        self.copy("*.symbols", src="symbols", dst="lib/symbols")
        self.copy("*.cmake", src="cmake", dst="lib/cmake")
        self.copy("LICENSE", src="source_subfolder/Support", dst="licenses")
        self.copy("readme.md")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "openfx"
        self.cpp_info.names["cmake_find_package_multi"] = "openfx"

        self.cpp_info.set_property("cmake_build_modules", self._build_modules)
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
        self.cpp_info.build_modules["cmake_find_package"] = self._build_modules
        self.cpp_info.build_modules["cmake_find_package_multi"] = self._build_modules

        if self.options.shared:
            self.cpp_info.libs = ["OfxSupport"]
        else:
            self.cpp_info.libs = ["OfxHost", "OfxSupport"]

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["GL"])
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreFoundation", "OpenGL"]
