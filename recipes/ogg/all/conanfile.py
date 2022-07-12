from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.43.0"


class OggConan(ConanFile):
    name = "ogg"
    description = "The OGG library"
    topics = ("ogg", "codec", "audio", "lossless")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xiph/ogg"
    license = "BSD-2-Clause"

    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"
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
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        # Generate a relocatable shared lib on Macos
        self._cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("COPYING", src=self._source_subfolder, dst="licenses", keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Ogg")
        self.cpp_info.set_property("cmake_target_name", "Ogg::ogg")
        self.cpp_info.set_property("pkg_config_name", "ogg")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["ogglib"].libs = ["ogg"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Ogg"
        self.cpp_info.names["cmake_find_package_multi"] = "Ogg"
        self.cpp_info.components["ogglib"].names["cmake_find_package"] = "ogg"
        self.cpp_info.components["ogglib"].names["cmake_find_package_multi"] = "ogg"
        self.cpp_info.components["ogglib"].set_property("cmake_target_name", "Ogg::ogg")
        self.cpp_info.components["ogglib"].set_property("pkg_config_name", "ogg")
