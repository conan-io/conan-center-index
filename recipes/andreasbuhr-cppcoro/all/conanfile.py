import os
import glob
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration

class AndreasbuhrCppCoroConan(ConanFile):
    name = "andreasbuhr-cppcoro"
    description = "A library of C++ coroutine abstractions for the coroutines TS"
    topics = ("conan", "cpp", "async", "coroutines")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/andreasbuhr/cppcoro"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"

    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "10",
            "clang": "8",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        # We can't simply check for C++20, because clang and MSVC support the coroutine TS despite not having labeled (__cplusplus macro) C++20 support
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires coroutine TS support. The current compiler {} {} does not support it.".format(
                    self.name, self.settings.compiler, self.settings.compiler.version))
        
        # Currently clang expects coroutine to be implemented in a certain way (under std::experiemental::), while libstdc++ puts them under std::
        # There are also other inconsistencies, see https://bugs.llvm.org/show_bug.cgi?id=48172
        # This should be removed after both gcc and clang implements the final coroutine TS
        if self.settings.compiler == "clang" and self.settings.compiler.get_safe("libcxx") == "libstdc++":
            raise ConanInvalidConfiguration("{} does not support clang with libstdc++. Use libc++ instead.".format(self.name))

        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("cppcoro-*/")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.cxxflags.append("/await")
        elif self.settings.compiler == "gcc":
            self.cpp_info.cxxflags.append("-fcoroutines")
        elif self.settings.compiler == "clang" or self.settings.compiler == "apple-clang":
            self.cpp_info.cxxflags.append("-fcoroutines-ts")
