# pylint: skip-file
from conan.tools.files import rename
from conans import ConanFile, CMake, tools
import functools
import os

required_conan_version = ">=1.43.0"

class SAILConan(ConanFile):
    name = "sail"
    description = "The missing small and fast image decoding library for humans (not for machines)"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sail.software"
    topics = ( "image", "encoding", "decoding", "graphics" )
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "thread_safe": [True, False],
        "with_avif": [True, False],
        "with_gif": [True, False],
        "with_jpeg2000": [True, False],
        "with_jpeg": [True, False],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_webp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "thread_safe": True,
        "with_avif": True,
        "with_gif": True,
        "with_jpeg2000": True,
        "with_jpeg": True,
        "with_png": True,
        "with_tiff": True,
        "with_webp": True,
    }
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "src"

    @property
    def _build_subfolder(self):
        return "build"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    # Probably will not be needed in Conan 2.x
    def validate(self):
        if self.options.with_avif and tools.cross_building(self):
            raise ConanInvalidConfiguration("Cross-building is not implemented due to dependencies (dav1d)")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_avif:
            self.requires("libavif/0.9.3")
        if self.options.with_gif:
            self.requires("giflib/5.2.1")
        if self.options.with_jpeg2000:
            self.requires("jasper/2.0.33")
        if self.options.with_jpeg:
            self.requires("libjpeg/9d")
        if self.options.with_png:
            self.requires("libpng/1.6.37")
        if self.options.with_tiff:
            self.requires("libtiff/4.3.0")
        if self.options.with_webp:
            self.requires("libwebp/1.2.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        except_codecs = []

        if not self.options.with_avif:
            except_codecs.append("AVIF")
        if not self.options.with_gif:
            except_codecs.append("GIF")
        if not self.options.with_jpeg2000:
            except_codecs.append("JPEG2000")
        if not self.options.with_jpeg:
            except_codecs.append("JPEG")
        if not self.options.with_png:
            except_codecs.append("PNG")
        if not self.options.with_tiff:
            except_codecs.append("TIFF")
        if not self.options.with_webp:
            except_codecs.append("WEBP")

        cmake = CMake(self)
        cmake.definitions["SAIL_BUILD_APPS"] = False
        cmake.definitions["SAIL_BUILD_EXAMPLES"] = False
        cmake.definitions["SAIL_BUILD_TESTS"] = False
        cmake.definitions["SAIL_COMBINE_CODECS"] = True
        cmake.definitions["SAIL_EXCEPT_CODECS"] = ";".join(except_codecs)
        cmake.definitions["SAIL_INSTALL_PDB"] = False
        cmake.definitions["SAIL_THREAD_SAFE"] = self.options.thread_safe
        cmake.configure(build_folder=self._build_subfolder)

        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt",       src=self._source_subfolder, dst="licenses")
        self.copy("LICENSE.INIH.txt",  src=self._source_subfolder, dst="licenses")
        self.copy("LICENSE.MUNIT.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        # Remove CMake and pkg-config rules
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        # Move icons
        rename(self, os.path.join(self.package_folder, "share"),
                     os.path.join(self.package_folder, "res"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Sail")

        self.cpp_info.filenames["cmake_find_package"]       = "Sail"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Sail"
        self.cpp_info.names["cmake_find_package"]           = "SAIL"
        self.cpp_info.names["cmake_find_package_multi"]     = "SAIL"

        self.cpp_info.components["sail-common"].set_property("cmake_target_name", "SAIL::SailCommon")
        self.cpp_info.components["sail-common"].set_property("pkg_config_name", "libsail-common")
        self.cpp_info.components["sail-common"].names["cmake_find_package"]       = "SailCommon"
        self.cpp_info.components["sail-common"].names["cmake_find_package_multi"] = "SailCommon"
        self.cpp_info.components["sail-common"].includedirs = ["include/sail"]
        self.cpp_info.components["sail-common"].libs = ["sail-common"]

        self.cpp_info.components["sail-codecs"].set_property("cmake_target_name", "SAIL::SailCodecs")
        self.cpp_info.components["sail-codecs"].names["cmake_find_package"]       = "SailCodecs"
        self.cpp_info.components["sail-codecs"].names["cmake_find_package_multi"] = "SailCodecs"
        self.cpp_info.components["sail-codecs"].libs = ["sail-codecs"]
        self.cpp_info.components["sail-codecs"].requires = ["sail-common"]
        if self.options.with_avif:
            self.cpp_info.components["sail-codecs"].requires.append("libavif::libavif")
        if self.options.with_gif:
            self.cpp_info.components["sail-codecs"].requires.append("giflib::giflib")
        if self.options.with_jpeg2000:
            self.cpp_info.components["sail-codecs"].requires.append("jasper::jasper")
        if self.options.with_jpeg:
            self.cpp_info.components["sail-codecs"].requires.append("libjpeg::libjpeg")
        if self.options.with_png:
            self.cpp_info.components["sail-codecs"].requires.append("libpng::libpng")
        if self.options.with_tiff:
            self.cpp_info.components["sail-codecs"].requires.append("libtiff::libtiff")
        if self.options.with_webp:
            self.cpp_info.components["sail-codecs"].requires.append("libwebp::libwebp")

        self.cpp_info.components["libsail"].set_property("cmake_target_name", "SAIL::Sail")
        self.cpp_info.components["libsail"].set_property("pkg_config_name", "libsail")
        self.cpp_info.components["libsail"].names["cmake_find_package"] = "Sail"
        self.cpp_info.components["libsail"].names["cmake_find_package_multi"] = "Sail"
        self.cpp_info.components["libsail"].libs = ["sail"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libsail"].system_libs.append("dl")
            if self.options.thread_safe:
                self.cpp_info.components["libsail"].system_libs.append("pthread")
        self.cpp_info.components["libsail"].requires = ["sail-common", "sail-codecs"]

        self.cpp_info.components["sail-manip"].set_property("cmake_target_name", "SAIL::SailManip")
        self.cpp_info.components["sail-manip"].set_property("pkg_config_name", "libsail-manip")
        self.cpp_info.components["sail-manip"].names["cmake_find_package"]       = "SailManip"
        self.cpp_info.components["sail-manip"].names["cmake_find_package_multi"] = "SailManip"
        self.cpp_info.components["sail-manip"].libs = ["sail-manip"]
        self.cpp_info.components["sail-manip"].requires = ["sail-common"]

        self.cpp_info.components["sail-c++"].set_property("cmake_target_name", "SAIL::SailC++")
        self.cpp_info.components["sail-c++"].set_property("pkg_config_name", "libsail-c++")
        self.cpp_info.components["sail-c++"].names["cmake_find_package"]       = "SailC++"
        self.cpp_info.components["sail-c++"].names["cmake_find_package_multi"] = "SailC++"
        self.cpp_info.components["sail-c++"].libs = ["sail-c++"]
        self.cpp_info.components["sail-c++"].requires = ["libsail", "sail-manip"]
