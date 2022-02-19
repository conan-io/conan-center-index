from conans import ConanFile, CMake, tools, errors
import sys, os

required_conan_version = ">=1.33.0"


class NovelRTConan(ConanFile):
    name = "novelrt"
    version = "0.0.1"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/novelrt/NovelRT"
    description = "A cross-platform 2D game engine accompanied by a strong toolset for visual novels."
    topics = {"conan", "game", "engine" "gamedev", "visualnovel", "vn"}
    settings = "os", "compiler", "build_type", "arch"
    requires = [
        ("freetype/2.10.1"),
        ("glfw/3.3.2"),
        ("glm/0.9.9.7"),
        ("gtest/1.10.0"),
        ("libsndfile/1.0.30"),
        ("ms-gsl/3.1.0"),
        ("openal/1.21.1"),
        ("onetbb/2021.3.0"),
        ("spdlog/1.8.2"),
        ("vulkan-loader/1.2.182"),
        ("vulkan-memory-allocator/2.3.0")
    ]
    generators = "cmake_find_package", "cmake_paths"
    default_options = {
        "freetype:shared": True,
        "glfw:shared": True,
        "libsndfile:shared": True,
        "openal:shared": True,
        "PNG:shared": True,
        "BZip2:shared": True,
        "flac:shared": True,
        "fmt:shared": True,
        "Opus:shared": True,
        "Ogg:shared": True,
        "Vorbis:shared": True,
        "spdlog:header_only": True,
        "vulkan-loader:shared": True,
    }
    cmake = None
    unsupportedOS = ['AIX', 'Android', 'Arduino', 'Emscripten', 'FreeBSD', 'Macos', 'Neutrino', 'SunOS', 'WindowsCE', 'WindowsStore', 'iOS', 'tvOS', 'watchOS']
    unsupportedCompilers = ['gcc', 'intel', 'mcst-lcc', 'qcc', 'sun-cc']

    @property
    def _source_subfolder(self):
        return "source"

    @property
    def _build_subfolder(self):
        return "artifacts"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["NOVELRT_BUILD_DOCUMENTATION"] = "Off"
        cmake.definitions["NOVELRT_BUILD_TESTS"] = "Off"
        cmake.definitions["NOVELRT_BUILD_SAMPLES"] = "Off"
        cmake.definitions["NOVELRT_BUILD_INTEROP"] = "Off"
        if self.settings.os == 'Windows':
            cmake.generator = "Ninja"
        cmake.configure()
        return cmake

    def imports(self):
        if self.settings.os == "Windows":
            self.copy("*.dll", dst="thirdparty", src="bin")
            self.copy("*.dll", dst="thirdparty", src="lib")

    def build(self):
        self.cmake = self.configure_cmake()
        buildArgs = ['-j']
        self.cmake.build(args=buildArgs)

    def package(self):
        self.copy("*LICENCE.md", dst="licenses", keep_path=False)
        self.copy("include/NovelRT/*.h", dst="", keep_path=True)
        self.copy("*include/NovelRT.h", dst="include", keep_path=False)
        self.copy("*.spv", dst="bin/Resources/Shaders", keep_path=False)
        if self.settings.os == "Windows":
            self.copy("*NovelRT.lib", dst="lib", keep_path=False)
            self.copy("*NovelRT.dll", dst="bin", keep_path=False)
            self.copy("*bz2.dll", dst="bin", keep_path=False)
            self.copy("*FLAC.dll", dst="bin", keep_path=False)
            self.copy("*FLAC++.dll", dst="bin", keep_path=False)
            self.copy("*fmt.dll", dst="bin", keep_path=False)
            self.copy("*freetype.dll", dst="bin", keep_path=False)
            self.copy("*glfw3.dll", dst="bin", keep_path=False)
            self.copy("*ogg.dll", dst="bin", keep_path=False)
            self.copy("*OpenAL32.dll", dst="bin", keep_path=False)
            self.copy("*opus.dll", dst="bin", keep_path=False)
            self.copy("*sndfile.dll", dst="bin", keep_path=False)
            self.copy("*tbb12.dll", dst="bin", keep_path=False)
            self.copy("*tbbmalloc.dll", dst="bin", keep_path=False)
            self.copy("*tbbmalloc_proxy.dll", dst="bin", keep_path=False)
            self.copy("*vorbis.dll", dst="bin", keep_path=False)
            self.copy("*vorbisenc.dll", dst="bin", keep_path=False)
            self.copy("*vorbisfile.dll", dst="bin", keep_path=False)
            self.copy("*vulkan-1.dll", dst="bin", keep_path=False)
        elif self.settings.os == "Linux":
            self.copy("*libNovelRT.so", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = self.collect_libs()

    def validate(self):
        if self.settings.os in self.unsupportedOS:
            raise errors.ConanInvalidConfiguration(f"NovelRT does not support {self.settings.os} at this time.")
        if self.settings.compiler in self.unsupportedCompilers:
            raise errors.ConanInvalidConfiguration(f"NovelRT does not support compilation with {self.settings.compiler} at this time.")
        if self.settings.arch != "x86_64":
            raise errors.ConanInvalidConfiguration(f"NovelRT does not support compilation under {self.settings.arch} architecture at this time.")
