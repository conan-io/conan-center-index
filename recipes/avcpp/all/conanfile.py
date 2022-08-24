import os
from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import functools

required_conan_version = ">=1.43.0"

class AvcppConan(ConanFile):
    name = "avcpp"
    description = "C++ wrapper for FFmpeg"
    topics = ("ffmpeg", "cpp")
    license = "LGPL-2.1", "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/h4tr3d/avcpp/"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False], 
        "shared": [True, False],
    }
    default_options = {
        "fPIC": True, 
        "shared": False,
    }
    generators = "cmake", "cmake_find_package_multi"


    @property
    def _compiler_required_cpp17(self):
        return {
            "Visual Studio": "16",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12.0",
        }

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

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, "17")

        minimum_version = self._compiler_required_cpp17.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{0} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))

    def requirements(self):
        self.requires("ffmpeg/5.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["AV_ENABLE_SHARED"] = self.options.shared
        cmake.definitions["AV_ENABLE_STATIC"] = not self.options.shared
        cmake.definitions["AV_BUILD_EXAMPLES"] = False
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        target_name = "avcpp" if self.options.shared else "avcpp-static"

        self.cpp_info.set_property("cmake_file_name", "avcpp")
        self.cpp_info.set_property("cmake_target_name", "avcpp::{}".format(target_name))

        self.cpp_info.filenames["cmake_find_package"] = "avcpp"
        self.cpp_info.filenames["cmake_find_package_multi"] = "avcpp"
        self.cpp_info.names["cmake_find_package"] = "avcpp"
        self.cpp_info.names["cmake_find_package_multi"] = "avcpp"

        self.cpp_info.components["AvCpp"].names["cmake_find_package"] = target_name
        self.cpp_info.components["AvCpp"].names["cmake_find_package_multi"] = target_name
        self.cpp_info.components["AvCpp"].set_property("cmake_target_name", "avcpp::{}".format(target_name))
        self.cpp_info.components["AvCpp"].libs = ["avcpp", ]
        self.cpp_info.components["AvCpp"].requires = ["ffmpeg::ffmpeg", ]
