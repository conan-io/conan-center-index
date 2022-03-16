from conans import ConanFile, CMake, tools, errors
import os

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
    tool_requires = ("cmake/3.22.0")
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
        "onetbb:tbbproxy": False,
        "onetbb:tbbmalloc": False,
        "Opus:shared": True,
        "Ogg:shared": True,
        "Vorbis:shared": True,
        "spdlog:header_only": True,
        "vulkan-loader:shared": True,
    }
    cmake = None
    unsupportedOS = ['AIX', 'Android', 'Arduino', 'Emscripten', 'FreeBSD', 'Macos', 'Neutrino', 'SunOS', 'WindowsCE', 'WindowsStore', 'iOS', 'tvOS', 'watchOS']
    unsupportedCompilers = ['gcc', 'intel', 'mcst-lcc', 'qcc', 'sun-cc', 'msvc']

    @property
    def _compilers_minimum_version(self):
        return {
            "clang": "10",
            "Visual Studio": "16"
        }

    @property
    def _source_subfolder(self):
        return "source"

    @property
    def _build_subfolder(self):
        return "artifacts"

    @property
    def _is_static_lib_win(self):
        return str(self.settings.compiler.runtime) in ["MTd", "MT"]

    @property
    def _is_debug_runtime_win(self):
        return str(self.settings.compiler.runtime) in ["MDd", "MTd"]

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    def configure_cmake(self):
        cmakePath = self.deps_env_info["cmake"].CMAKE_ROOT
        if cmakePath:
            if self.settings.os == "Windows":
                cmakePath += "\\bin\\cmake.exe"
            else:
                cmakePath += "/bin/cmake"
            self.output.info(f"Overriding CMake to use version from Conan at: {cmakePath}")
        cmake = CMake(self, cmake_program=cmakePath, parallel=True)
        cmake.definitions["NOVELRT_BUILD_DOCUMENTATION"] = "Off"
        cmake.definitions["NOVELRT_BUILD_TESTS"] = "Off"
        cmake.definitions["NOVELRT_BUILD_SAMPLES"] = "Off"
        cmake.definitions["NOVELRT_BUILD_INTEROP"] = "Off"
        cmake.configure()
        return cmake

    def imports(self):
        if self.settings.os == "Windows":
            self.copy("*.dll", dst="thirdparty", src="bin")
            self.copy("*.dll", dst="thirdparty", src="lib")

    def build(self):
        self.cmake = self.configure_cmake()
        self.cmake.build()

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
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        compiler_version = tools.Version(self.settings.compiler.version)
        if minimum_version and compiler_version < minimum_version:
            raise errors.ConanInvalidConfiguration(f"NovelRT does not support compilation with {self.settings.compiler} {self.settings.compiler.version} as C++ 17 is required.")
        if self.settings.compiler == "clang":
            if compiler_version == 10 and self.settings.compiler.libcxx != "libstdc++11":
                raise errors.ConanInvalidConfiguration(f"Please use libstdc++11 when compiling NovelRT with Clang 10.")
            if self.settings.compiler.libcxx in ["libstdc++", "libstdc++11"] and self.settings.compiler.version == "11":
                 raise errors.ConanInvalidConfiguration("Clang 11 with libstdc++ is not supported due to old libstdc++ missing C++17 support.")
        if self.settings.compiler == "Visual Studio":
            if self._is_debug_runtime_win:
                raise errors.ConanInvalidConfiguration(f"NovelRT does not support debug runtime builds at this time with Visual Studio.")
            if self._is_static_lib_win:
                raise errors.ConanInvalidConfiguration(f"NovelRT does not support static builds at this time with Visual Studio.")
        if self.settings.arch != "x86_64":
            raise errors.ConanInvalidConfiguration(f"NovelRT does not support compilation under {self.settings.arch} architecture at this time.")
