from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.43.0"


class ZipConan(ConanFile):
    name = "kuba-zip"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kuba--/zip"
    description = "A portable, simple zip library written in C"
    topics = ("zip", "compression", "c", "miniz", "portable", "hacking")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "-Werror", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        cmake = CMake(self)
        cmake.definitions["CMAKE_DISABLE_TESTING"] = True
        cmake.definitions["ZIP_STATIC_PIC"] = self.options.get_safe("fPIC", True)
        cmake.definitions["ZIP_BUILD_DOCS"] = False
        cmake.configure()
        self._cmake = cmake
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("UNLICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "zip")
        self.cpp_info.set_property("cmake_target_name", "zip::zip")

        self.cpp_info.names["cmake_find_package"] = "zip"
        self.cpp_info.names["cmake_find_package_multi"] = "zip"

        self.cpp_info.libs = ["zip"]
        if self.options.shared:
            self.cpp_info.defines.append("ZIP_SHARED")
