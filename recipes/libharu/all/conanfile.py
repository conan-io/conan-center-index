from conans import CMake, ConanFile, tools
import os
import re

required_conan_version = ">=1.33.0"

class LibharuConan(ConanFile):
    name = "libharu"
    description = "Haru is a free, cross platform, open-sourced software library for generating PDF."
    topics = ("conan", "libharu", "pdf", "generate", "generator")
    license = "ZLIB"
    homepage = "http://libharu.org/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt", "patches/**"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake", "cmake_find_package"

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

    def requirements(self):
        self.requires("zlib/1.2.11")
        self.requires("libpng/1.6.37")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LIBHPDF_SHARED"] = self.options.shared
        self._cmake.definitions["LIBHPDF_STATIC"] = not self.options.shared
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_license(self):
        readme = tools.load(os.path.join(self._source_subfolder, "README"))
        match = next(re.finditer("\n[^\n]*license[^\n]*\n", readme, flags=re.I | re.A))
        return readme[match.span()[1]:].strip("*").strip()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        for fn in ("CHANGES", "INSTALL", "README"):
            os.unlink(os.path.join(self.package_folder, fn))
        tools.rmdir(os.path.join(self.package_folder, "if"))
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())

    def package_info(self):
        libprefix = "lib" if self.settings.compiler == "Visual Studio" else ""
        libsuffix = "{}{}".format("" if self.options.shared else "s",
                                  "d" if self.settings.compiler == "Visual Studio" and self.settings.build_type == "Debug" else "")
        self.cpp_info.libs = ["{}hpdf{}".format(libprefix, libsuffix)]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines = ["HPDF_DLL"]
        if self.settings.os == "Linux" and not self.options.shared:
            self.cpp_info.system_libs = ["m"]
