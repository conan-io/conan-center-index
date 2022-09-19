import functools
import os
import textwrap

# pylint: skip-file
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.43.0"

class LibAVIFConan(ConanFile):
    name = "libavif"
    description = "Library for encoding and decoding .avif files"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AOMediaCodec/libavif"
    topics = "avif"
    license = "BSD-2-Clause"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_decoder": ["aom", "dav1d"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_decoder": "dav1d",
    }
    generators = "cmake", "cmake_find_package_multi"
    exports_sources = "CMakeLists.txt", "patches/*"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    @property
    def _has_dav1d(self):
        return self.options.with_decoder == "dav1d"

    def requirements(self):
        self.requires("libaom-av1/3.1.2")
        self.requires("libyuv/cci.20201106")
        if self._has_dav1d:
            self.requires("dav1d/0.9.1")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        root = self._source_subfolder
        get_args = self.conan_data["sources"][self.version]
        tools.get(**get_args, destination=root, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["AVIF_CODEC_AOM"] = True
        if self._has_dav1d:
            cmake.definitions["AVIF_CODEC_DAV1D"] = True
            cmake.definitions["AVIF_CODEC_AOM_DECODE"] = False
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        self._configure_cmake().build()

    @property
    def _alias_path(self):
        return os.path.join("lib", "conan-official-avif-targets.cmake")

    def package(self):
        self.copy("LICENSE", "licenses", self._source_subfolder)
        self._configure_cmake().install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

        # TODO: remove in conan v2
        alias = os.path.join(self.package_folder, self._alias_path)
        content = textwrap.dedent("""\
            if(TARGET avif::avif AND NOT TARGET avif)
                add_library(avif INTERFACE IMPORTED)
                set_property(
                    TARGET avif PROPERTY
                    INTERFACE_LINK_LIBRARIES avif::avif
                )
            endif()
        """)
        tools.save(alias, content)

    def package_info(self):
        self.cpp_info.requires = ["libyuv::libyuv", "libaom-av1::libaom-av1"]
        if self._has_dav1d:
            self.cpp_info.requires.append("dav1d::dav1d")

        self.cpp_info.libs = ["avif"]
        if self.options.shared:
            self.cpp_info.defines = ["AVIF_DLL"]
        if self.settings.os != "Windows":
            self.cpp_info.system_libs = ["pthread", "m"]
            if self.settings.os == "Linux" and self._has_dav1d:
                self.cpp_info.system_libs.append("dl")

        self.cpp_info.set_property("cmake_file_name", "libavif")
        self.cpp_info.set_property("cmake_target_name", "avif")

        # TODO: remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "avif"
        self.cpp_info.names["cmake_find_package_multi"] = "avif"
        self.cpp_info.filenames["cmake_find_package"] = "libavif"
        self.cpp_info.filenames["cmake_find_package_multi"] = "libavif"
        self.cpp_info.build_modules["cmake"] = [self._alias_path]
        self.cpp_info.build_modules["cmake_find_package"] = [self._alias_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = \
            [self._alias_path]
        self.cpp_info.builddirs = ["lib"]
