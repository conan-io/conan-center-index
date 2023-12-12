from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.54.0"


class LibAVIFConan(ConanFile):
    name = "libavif"
    description = "Library for encoding and decoding .avif files"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AOMediaCodec/libavif"
    topics = ("avif",)
    package_type = "library"
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

    @property
    def _depends_on_sharpyuv(self):
        return Version(self.version) >= "0.11.0"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    @property
    def _has_dav1d(self):
        return self.options.with_decoder == "dav1d"

    def requirements(self):
        self.requires("libaom-av1/3.6.1")
        self.requires("libyuv/1854")
        if self._has_dav1d:
            self.requires("dav1d/1.2.1")
        if self._depends_on_sharpyuv:
            self.requires("libwebp/1.3.2")

    def validate(self):
        if self._depends_on_sharpyuv and Version(self.dependencies["libwebp"].ref.version) < "1.3.0":
            raise ConanInvalidConfiguration(f"{self.ref} requires libwebp >= 1.3.0 in order to get libsharpyuv")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["AVIF_ENABLE_WERROR"] = False
        tc.variables["AVIF_CODEC_AOM"] = True
        tc.variables["AVIF_CODEC_DAV1D"] = self.options.with_decoder == "dav1d"
        tc.variables["AVIF_CODEC_AOM_DECODE"] = self.options.with_decoder == "aom"
        tc.variables["LIBYUV_VERSION"] = self.dependencies["libyuv"].ref.version
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakelists, "find_package(libyuv QUIET)", "find_package(libyuv REQUIRED CONFIG)")
        replace_in_file(self, cmakelists, "${LIBYUV_LIBRARY}", "libyuv::libyuv")
        replace_in_file(self, cmakelists, "find_package(dav1d REQUIRED)", "find_package(dav1d REQUIRED CONFIG)")
        replace_in_file(self, cmakelists, "${DAV1D_LIBRARY}", "dav1d::dav1d")
        replace_in_file(self, cmakelists, "find_package(aom REQUIRED)", "find_package(libaom-av1 REQUIRED CONFIG)")
        replace_in_file(self, cmakelists, "${AOM_LIBRARIES}", "libaom-av1::libaom-av1")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    @property
    def _alias_path(self):
        return os.path.join("lib", "conan-official-avif-targets.cmake")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

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
        save(self, alias, content)

    def package_info(self):
        self.cpp_info.libs = ["avif"]
        if self.options.shared:
            self.cpp_info.defines = ["AVIF_DLL"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "m"])
            if self._has_dav1d:
                self.cpp_info.system_libs.append("dl")

        self.cpp_info.requires = ["libyuv::libyuv", "libaom-av1::libaom-av1"]
        if self._has_dav1d:
            self.cpp_info.requires.append("dav1d::dav1d")
        if self._depends_on_sharpyuv:
            self.cpp_info.requires.append("libwebp::sharpyuv")

        self.cpp_info.set_property("cmake_file_name", "libavif")
        self.cpp_info.set_property("cmake_target_name", "avif")
        self.cpp_info.set_property("pkg_config_name", "libavif")

        # TODO: remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "avif"
        self.cpp_info.names["cmake_find_package_multi"] = "avif"
        self.cpp_info.filenames["cmake_find_package"] = "libavif"
        self.cpp_info.filenames["cmake_find_package_multi"] = "libavif"
        self.cpp_info.build_modules["cmake_find_package"] = [self._alias_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = \
            [self._alias_path]

