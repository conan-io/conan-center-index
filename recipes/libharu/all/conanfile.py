from conan.tools.microsoft import is_msvc
from conan import ConanFile, tools
from conans import CMake
import functools
import os
import re

required_conan_version = ">=1.45.0"


class LibharuConan(ConanFile):
    name = "libharu"
    description = "Haru is a free, cross platform, open-sourced software library for generating PDF."
    topics = ("libharu", "pdf", "generate", "generator")
    license = "ZLIB"
    homepage = "http://libharu.org/"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("zlib/1.2.12")
        self.requires("libpng/1.6.37")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["LIBHPDF_SHARED"] = self.options.shared
        cmake.definitions["LIBHPDF_STATIC"] = not self.options.shared
        # To install relocatable shared lib on Macos
        cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_license(self):
        readme = tools.files.load(self, os.path.join(self._source_subfolder, "README"))
        match = next(re.finditer("\n[^\n]*license[^\n]*\n", readme, flags=re.I | re.A))
        return readme[match.span()[1]:].strip("*").strip()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        for fn in ("CHANGES", "INSTALL", "README"):
            os.unlink(os.path.join(self.package_folder, fn))
        tools.files.rmdir(self, os.path.join(self.package_folder, "if"))
        tools.files.save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())

    def package_info(self):
        libprefix = "lib" if is_msvc(self) else ""
        libsuffix = "{}{}".format(
            "" if self.options.shared else "s",
            "d" if is_msvc(self) and self.settings.build_type == "Debug" else "",
        )
        self.cpp_info.libs = [f"{libprefix}hpdf{libsuffix}"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines = ["HPDF_DLL"]
        if self.settings.os in ["Linux", "FreeBSD"] and not self.options.shared:
            self.cpp_info.system_libs = ["m"]
