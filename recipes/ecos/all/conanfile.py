from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.33.0"


class EcosConan(ConanFile):
    name = "ecos"
    description = "ECOS is a numerical software for solving convex second-order cone programs (SOCPs)."
    license = "GPL-3.0-or-later"
    topics = ("ecos", "conic-solver")
    homepage = "https://github.com/embotech/ecos"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_long": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_long": True,
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        # TODO: unvendor suitesparse
        pass

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["USE_LONG"] = self.options.use_long
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "ecos"
        self.cpp_info.names["cmake_find_package_multi"] = "ecos"
        self.cpp_info.libs = ["ecos"]
        self.cpp_info.defines.append("CTRLC=1")
        if self.options.use_long:
            self.cpp_info.defines.extend(["LDL_LONG", "DLONG"])
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
