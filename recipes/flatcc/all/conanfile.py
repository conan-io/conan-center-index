import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

class FlatccConan(ConanFile):
    name = "flatcc"
    description = "C language binding for Flatbuffers, an efficient cross platform serialization library"
    topics = ("conan", "flatbuffers", "serialization")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dvidelabs/flatcc"
    license = "Apache-2.0"
    options = { "shared": [True, False],
                "fPIC": [True, False],
                "portable": [True, False],
                "gnu_posix_memalign": [True, False],
                "runtime_lib_only": [True, False],
                "verify_assert": [True, False],
                "verify_trace": [True, False],
                "reflection": [True, False],
                "native_optim": [True, False],
                "fast_double": [True, False],
                "ignore_const_condition": [True, False],
    }
    default_options = { "shared": False,
                        "fPIC": True,
                        "portable": False,
                        "gnu_posix_memalign": True,
                        "runtime_lib_only": False,
                        "verify_assert": False,
                        "verify_trace": False,
                        "reflection": True,
                        "native_optim": False,
                        "fast_double": False,
                        "ignore_const_condition": False
    }
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]

    _cmake = None


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio" and self.options.shared:
                #Building flatcc shared libs with Visual Studio is broken
                raise ConanInvalidConfiguration("Building flatcc libraries shared is not supported")
            if self.settings.compiler == "gcc":
                raise ConanInvalidConfiguration("Building flatcc with MinGW is not supported")
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["FLATCC_PORTABLE"] = self.options.portable
            self._cmake.definitions["FLATCC_GNU_POSIX_MEMALIGN"] = self.options.gnu_posix_memalign
            self._cmake.definitions["FLATCC_RTONLY"] = self.options.runtime_lib_only
            self._cmake.definitions["FLATCC_INSTALL"] = True
            self._cmake.definitions["FLATCC_COVERAGE"] = False
            self._cmake.definitions["FLATCC_DEBUG_VERIFY"] = self.options.verify_assert
            self._cmake.definitions["FLATCC_TRACE_VERIFY"] = self.options.verify_trace
            self._cmake.definitions["FLATCC_REFLECTION"] = self.options.reflection
            self._cmake.definitions["FLATCC_NATIVE_OPTIM"] = self.options.native_optim
            self._cmake.definitions["FLATCC_FAST_DOUBLE"] = self.options.fast_double
            self._cmake.definitions["FLATCC_IGNORE_CONST_COND"] = self.options.ignore_const_condition
            self._cmake.definitions["FLATCC_TEST"] = False
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()


    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        if self.settings.build_type == "Debug" and not tools.os_info.is_windows:
            debug_suffix = "_d" if self.settings.build_type == "Debug" else ""
            os.rename(os.path.join(self.package_folder, "bin", "flatcc%s" % debug_suffix),
                      os.path.join(self.package_folder, "bin", "flatcc"))
        # Copy license file
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.PATH.append(bin_path)
        debug_suffix = "_d" if self.settings.build_type == "Debug" else ""
        if not self.options.runtime_lib_only:
            self.cpp_info.libs.append("flatcc%s" % debug_suffix)
        self.cpp_info.libs.append("flatccrt%s" % debug_suffix)
