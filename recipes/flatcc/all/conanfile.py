import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

class FlatccConan(ConanFile):
    name = "flatcc"
    description = "C language binding for Flatbuffers, an efficient cross platform serialization library"
    topics = "conan", "flatbuffers", "serialization"
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
    default_options = { "shared": True,
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
    no_copy_source = True


    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            raise ConanInvalidConfiguration("Building flatcc with MinGW is not supported")

    def config_options(self):
        if self.settings.compiler == "Visual Studio":
            #Building flatcc shared libs with Visual Studio is broken
            del self.options.shared
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["BUILD_SHARED_LIBS"] = False
        else:
            cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["FLATCC_PORTABLE"] = self.options.portable
        cmake.definitions["FLATCC_GNU_POSIX_MEMALIGN"] = self.options.gnu_posix_memalign
        cmake.definitions["FLATCC_RTONLY"] = self.options.runtime_lib_only
        cmake.definitions["FLATCC_INSTALL"] = True
        cmake.definitions["FLATCC_COVERAGE"] = False
        cmake.definitions["FLATCC_DEBUG_VERIFY"] = self.options.verify_assert
        cmake.definitions["FLATCC_TRACE_VERIFY"] = self.options.verify_trace
        cmake.definitions["FLATCC_REFLECTION"] = self.options.reflection
        cmake.definitions["FLATCC_NATIVE_OPTIM"] = self.options.native_optim
        cmake.definitions["FLATCC_FAST_DOUBLE"] = self.options.fast_double
        cmake.definitions["FLATCC_IGNORE_CONST_COND"]= self.options.ignore_const_condition
        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))
        cmake.build()
        cmake.install()

    def package(self):
        # Copy license file
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.PATH.append(bin_path)
        if not self.options.runtime_lib_only:
            self.cpp_info.libs.append("flatcc")
        self.cpp_info.libs.append("flatccrt")
        self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
