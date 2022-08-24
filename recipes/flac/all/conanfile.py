from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


class FlacConan(ConanFile):
    name = "flac"
    description = "Free Lossless Audio Codec"
    topics = ("flac", "codec", "audio", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xiph/flac"
    license = ("BSD-3-Clause", "GPL-2.0-or-later", "LPGL-2.1-or-later", "GFDL-1.2")

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
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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

    def requirements(self):
        self.requires("ogg/1.3.5")

    def build_requirements(self):
        if self.settings.arch in ["x86", "x86_64"]:
            self.build_requires("nasm/2.15.05")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_DOCS"] = False
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="COPYING.*", dst="licenses", src=self._source_subfolder, keep_path=False)
        self.copy(pattern="*.h", dst=os.path.join("include", "share"), src=os.path.join(self._source_subfolder, "include", "share"), keep_path=False)
        self.copy(pattern="*.h", dst=os.path.join("include", "share", "grabbag"),
                  src=os.path.join(self._source_subfolder, "include", "share", "grabbag"), keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "flac")

        self.cpp_info.components["libflac"].set_property("cmake_target_name", "FLAC::FLAC")
        self.cpp_info.components["libflac"].set_property("pkg_config_name", "flac")
        self.cpp_info.components["libflac"].libs = ["FLAC"]
        self.cpp_info.components["libflac"].requires = ["ogg::ogg"]

        self.cpp_info.components["libflac++"].set_property("cmake_target_name", "FLAC::FLAC++")
        self.cpp_info.components["libflac++"].set_property("pkg_config_name", "flac++")
        self.cpp_info.components["libflac++"].libs = ["FLAC++"]
        self.cpp_info.components["libflac++"].requires = ["libflac"]
        if not self.options.shared:
            self.cpp_info.components["libflac"].defines = ["FLAC__NO_DLL"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["libflac"].system_libs += ["m"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "flac"
        self.cpp_info.filenames["cmake_find_package_multi"] = "flac"
        self.cpp_info.names["cmake_find_package"] = "FLAC"
        self.cpp_info.names["cmake_find_package_multi"] = "FLAC"
        self.cpp_info.components["libflac"].names["cmake_find_package"] = "FLAC"
        self.cpp_info.components["libflac"].names["cmake_find_package_multi"] = "FLAC"
        self.cpp_info.components["libflac++"].names["cmake_find_package"] = "FLAC++"
        self.cpp_info.components["libflac++"].names["cmake_find_package_multi"] = "FLAC++"
