from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.52.0"


class LibtiffConan(ConanFile):
    name = "libtiff"
    description = "Library for Tag Image File Format (TIFF)"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "http://www.simplesystems.org/libtiff"
    topics = ("tiff", "image", "bigtiff", "tagged-image-file-format")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "lzma": [True, False],
        "jpeg": [False, "libjpeg-turbo", "libjpeg"],
        "zlib": [True, False],
        "libdeflate": [True, False],
        "zstd": [True, False],
        "jbig": [True, False],
        "webp": [True, False],
        "cxx":  [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "lzma": True,
        "jpeg": "libjpeg",
        "zlib": True,
        "libdeflate": True,
        "zstd": True,
        "jbig": True,
        "webp": True,
        "cxx":  True,
    }

    @property
    def _has_webp_option(self):
        return Version(self.version) >= "4.0.10"

    @property
    def _has_zstd_option(self):
        return Version(self.version) >= "4.0.10"

    @property
    def _has_libdeflate_option(self):
        return Version(self.version) >= "4.2.0"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_webp_option:
            del self.options.webp
        if not self._has_zstd_option:
            del self.options.zstd
        if not self._has_libdeflate_option:
            del self.options.libdeflate

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        if not self.options.cxx:
            try:
                del self.settings.compiler.libcxx
            except Exception:
                pass
            try:
                del self.settings.compiler.cppstd
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.zlib:
            self.requires("zlib/1.2.12")
        if self.options.get_safe("libdeflate"):
            self.requires("libdeflate/1.12")
        if self.options.lzma:
            self.requires("xz_utils/5.2.5")
        if self.options.jpeg == "libjpeg":
            self.requires("libjpeg/9d")
        if self.options.jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.3")
        if self.options.jbig:
            self.requires("jbig/20160605")
        if self.options.get_safe("zstd"):
            self.requires("zstd/1.5.2")
        if self.options.get_safe("webp"):
            self.requires("libwebp/1.2.3")

    def validate(self):
        if self.info.options.get_safe("libdeflate") and not self.info.options.zlib:
            raise ConanInvalidConfiguration("libtiff:libdeflate=True requires libtiff:zlib=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["lzma"] = self.options.lzma
        tc.variables["jpeg"] = bool(self.options.jpeg)
        tc.variables["jpeg12"] = False
        tc.variables["jbig"] = self.options.jbig
        tc.variables["zlib"] = self.options.zlib
        if self._has_libdeflate_option:
            tc.variables["libdeflate"] = self.options.libdeflate
        if self._has_zstd_option:
            tc.variables["zstd"] = self.options.zstd
        if self._has_webp_option:
            tc.variables["webp"] = self.options.webp
        if Version(self.version) >= "4.3.0":
            tc.variables["lerc"] = False # TODO: add lerc support for libtiff versions >= 4.3.0
        tc.variables["cxx"] = self.options.cxx
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        top_cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        libtiff_cmakelists = os.path.join(self.source_folder, "libtiff", "CMakeLists.txt")

        # Handle libjpeg-turbo
        if self.options.jpeg == "libjpeg-turbo":
            if Version(self.version) < "4.3.0":
                file_find_package_jpeg = top_cmakelists
                file_jpeg_target = top_cmakelists
            else:
                file_find_package_jpeg = os.path.join(self.source_folder, "cmake", "JPEGCodec.cmake")
                file_jpeg_target = libtiff_cmakelists
            jpeg_target = "libjpeg-turbo::jpeg" if self.dependencies["libjpeg-turbo"].options.shared else "libjpeg-turbo::jpeg-static"
            replace_in_file(self, file_find_package_jpeg,
                                  "find_package(JPEG)",
                                  "find_package(libjpeg-turbo REQUIRED CONFIG)\nset(JPEG_FOUND TRUE)")
            replace_in_file(self, file_jpeg_target, "JPEG::JPEG", jpeg_target)

        # Export symbols of tiffxx for msvc shared
        replace_in_file(self, libtiff_cmakelists,
                              "set_target_properties(tiffxx PROPERTIES SOVERSION ${SO_COMPATVERSION})",
                              "set_target_properties(tiffxx PROPERTIES SOVERSION ${SO_COMPATVERSION} WINDOWS_EXPORT_ALL_SYMBOLS ON)")

        # Disable tools, test, contrib, man & html generation
        replace_in_file(self, top_cmakelists,
                              "add_subdirectory(tools)\nadd_subdirectory(test)\nadd_subdirectory(contrib)\nadd_subdirectory(build)\n"
                              "add_subdirectory(man)\nadd_subdirectory(html)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYRIGHT", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"), ignore_case=True, keep_path=False)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "TIFF")
        self.cpp_info.set_property("cmake_target_name", "TIFF::TIFF")
        self.cpp_info.set_property("pkg_config_name", f"libtiff-{Version(self.version).major}")
        suffix = "d" if is_msvc(self) and self.settings.build_type == "Debug" else ""
        if self.options.cxx:
            self.cpp_info.libs.append(f"tiffxx{suffix}")
        self.cpp_info.libs.append(f"tiff{suffix}")
        if self.settings.os in ["Linux", "Android", "FreeBSD", "SunOS", "AIX"]:
            self.cpp_info.system_libs.append("m")

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "TIFF"
        self.cpp_info.names["cmake_find_package_multi"] = "TIFF"
        self.cpp_info.names["pkg_config"] = f"libtiff-{Version(self.version).major}"
