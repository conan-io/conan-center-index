from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


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
        "with_ycgco_r": [True, False],
        "with_gain_map": [True, False],
        "with_metav1": [True, False],
        "with_sample_transform": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_decoder": "dav1d",
        "with_ycgco_r": False,
        "with_gain_map": False,
        "with_metav1": False,
        "with_sample_transform": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if Version(self.version) < "1.1.0":
            del self.options.with_gain_map
            del self.options.with_metav1
            del self.options.with_sample_transform

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
        self.requires("libwebp/[>=1.3.2 <2]")
        if self._has_dav1d:
            self.requires("dav1d/[>=1.4 <2]")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.19]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["AVIF_ENABLE_WERROR"] = False
        tc.variables["AVIF_CODEC_AOM"] = True
        tc.variables["AVIF_CODEC_DAV1D"] = self.options.with_decoder == "dav1d"
        tc.variables["AVIF_CODEC_AOM_DECODE"] = self.options.with_decoder == "aom"
        tc.variables["LIBYUV_VERSION"] = self.dependencies["libyuv"].ref.version
        if "with_ycgco_r" in self.options:
            tc.variables["AVIF_ENABLE_EXPERIMENTAL_YCGCO_R"] = self.options.with_ycgco_r
        if "with_gain_map" in self.options:
            tc.variables["AVIF_ENABLE_EXPERIMENTAL_GAIN_MAP"] = self.options.with_gain_map
        if "with_metav1" in self.options:
            tc.variables["AVIF_ENABLE_EXPERIMENTAL_METAV1"] = self.options.with_metav1
        if "with_sample_transform" in self.options:
            tc.variables["AVIF_ENABLE_EXPERIMENTAL_SAMPLE_TRANSFORM"] = self.options.with_sample_transform
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("libaom-av1", "cmake_file_name", "aom")
        deps.set_property("libaom-av1", "cmake_target_name", "aom")
        deps.set_property("libaom-av1", "cmake_additional_variables_prefixes", ["AOM"])
        if Version(self.version) >= "1.1.0":
            deps.set_property("libyuv", "cmake_target_name", "yuv::yuv")
        deps.generate()
    def _patch_sources(self):
        apply_conandata_patches(self)
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        if Version(self.version) < "1.1.0":
            replace_in_file(self, cmakelists, "find_package(libyuv QUIET)", "find_package(libyuv REQUIRED CONFIG)")
            replace_in_file(self, cmakelists, "${LIBYUV_LIBRARY}", "libyuv::libyuv")
            replace_in_file(self, cmakelists, "find_package(dav1d REQUIRED)", "find_package(dav1d REQUIRED CONFIG)")
            replace_in_file(self, cmakelists, "${DAV1D_LIBRARY}", "dav1d::dav1d")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

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

        self.cpp_info.requires.append("libwebp::sharpyuv")

        self.cpp_info.set_property("cmake_file_name", "libavif")
        self.cpp_info.set_property("cmake_target_name", "avif")
        self.cpp_info.set_property("pkg_config_name", "libavif")

