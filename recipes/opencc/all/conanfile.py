from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class OpenCCConan(ConanFile):
    name = "opencc"
    description = "Open Chinese Convert (OpenCC, 開放中文轉換) is an opensource project for conversions between Traditional Chinese, Simplified Chinese and Japanese Kanji (Shinjitai)"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/BYVoid/OpenCC"
    license = "Apache-2.0"
    topics = ("chinese", "opencc", "conversions")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tools": True,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("marisa/0.2.6")
        self.requires("rapidjson/cci.20220822")
        self.requires("tclap/1.2.5")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["BUILD_TOOLS"] = self.options.tools
        self._cmake.definitions["BUILD_PYTHON"] = False
        self._cmake.definitions["USE_SYSTEM_MARISA"] = True
        self._cmake.definitions["USE_SYSTEM_RAPIDJSON"] = True
        self._cmake.definitions["USE_SYSTEM_TCLAP"] = True

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="LICENSE", dst="licenses",
                  src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rename(os.path.join(self.package_folder, "share"), os.path.join(self.package_folder, "res"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "opencc")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "opencc")
        self.cpp_info.set_property("cmake_target_name", "opencc::opencc")

        self.cpp_info.names["cmake_find_package"] = "opencc"
        self.cpp_info.names["cmake_find_package_multi"] = "opencc"

        self.cpp_info.libs = ["opencc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        self.cpp_info.requires = ["marisa::marisa", "rapidjson::rapidjson", "tclap::tclap"]

        if self.options.tools:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(
                "Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
