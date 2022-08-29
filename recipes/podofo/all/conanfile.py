from conans import ConanFile, CMake, tools
import functools
import os

required_conan_version = ">=1.36.0"


class PodofoConan(ConanFile):
    name = "podofo"
    license = "GPL-3.0", "LGPL-3.0"
    homepage = "http://podofo.sourceforge.net"
    url = "https://github.com/conan-io/conan-center-index"
    description = "PoDoFo is a library to work with the PDF file format."
    topics = ("PDF", "PoDoFo", "podofo")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threadsafe": [True, False],
        "with_openssl": [True, False],
        "with_libidn": [True, False],
        "with_jpeg": [True, False],
        "with_tiff": [True, False],
        "with_png": [True, False],
        "with_unistring": [True, False],
        "with_tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threadsafe": True,
        "with_openssl": True,
        "with_libidn": True,
        "with_jpeg": True,
        "with_tiff": True,
        "with_png": True,
        "with_unistring": True,
        "with_tools": False,
    }

    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self._is_msvc:
            # libunistring recipe raises for Visual Studio
            # TODO: Enable again when fixed?
            self.options.with_unistring = False

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("freetype/2.12.1")
        self.requires("zlib/1.2.12")
        if self.settings.os != "Windows":
            self.requires("fontconfig/2.13.93")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")
        if self.options.with_libidn:
            self.requires("libidn/1.36")
        if self.options.with_jpeg:
            self.requires("libjpeg/9d")
        if self.options.with_tiff:
            self.requires("libtiff/4.3.0")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_unistring:
            self.requires("libunistring/0.9.10")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd") and tools.Version(self.version) >= "0.9.7":
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["PODOFO_BUILD_TOOLS"] = self.options.with_tools
        cmake.definitions["PODOFO_BUILD_SHARED"] = self.options.shared
        cmake.definitions["PODOFO_BUILD_STATIC"] = not self.options.shared
        if not self.options.threadsafe:
            cmake.definitions["PODOFO_NO_MULTITHREAD"] = True
        if not tools.valid_min_cppstd(self, 11) and tools.Version(self.version) >= "0.9.7":
            cmake.definitions["CMAKE_CXX_STANDARD"] = 11

        # To install relocatable shared lib on Macos
        cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"

        # Custom CMake options injected in our patch, required to ensure reproducible builds
        cmake.definitions["PODOFO_WITH_OPENSSL"] = self.options.with_openssl
        cmake.definitions["PODOFO_WITH_LIBIDN"] = self.options.with_libidn
        cmake.definitions["PODOFO_WITH_LIBJPEG"] = self.options.with_jpeg
        cmake.definitions["PODOFO_WITH_TIFF"] = self.options.with_tiff
        cmake.definitions["PODOFO_WITH_PNG"] = self.options.with_png
        cmake.definitions["PODOFO_WITH_UNISTRING"] = self.options.with_unistring

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        podofo_version = tools.Version(self.version)
        pkg_config_name = f"libpodofo-{podofo_version.major}" if podofo_version < "0.9.7" else "libpodofo"
        self.cpp_info.set_property("pkg_config_name", pkg_config_name)
        self.cpp_info.names["pkg_config"] = pkg_config_name
        self.cpp_info.libs = ["podofo"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("USING_SHARED_PODOFO")
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.threadsafe:
            self.cpp_info.system_libs = ["pthread"]
