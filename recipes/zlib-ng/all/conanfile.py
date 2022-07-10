from conans import CMake, tools
from conan import ConanFile
from conans.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
import os
import functools

equired_conan_version = ">=1.33.0"

class ZlibNgConan(ConanFile):
    name = "zlib-ng"
    description = "zlib data compression library for the next generation systems"
    topics = ("zlib", "compression")
    license ="Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zlib-ng/zlib-ng/"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt"]
    options = {"shared": [True, False],
               "zlib_compat": [True, False],
               "with_gzfileop": [True, False],
               "with_optim": [True, False],
               "with_new_strategies": [True, False],
               "with_native_instructions": [True, False],
               "fPIC": [True, False]}
    default_options = {"shared": False,
                       "zlib_compat": False,
                       "with_gzfileop": True,
                       "with_optim": False,
                       "with_new_strategies": True,
                       "with_native_instructions": False,
                       "fPIC": True}
    generators = "cmake",

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
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def validate(self):
        if self.options.zlib_compat and not self.options.with_gzfileop:
            raise ConanInvalidConfiguration("The option 'with_gzfileop' must be True when 'zlib_compat' is True.")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ZLIB_ENABLE_TESTS"] = False
        cmake.definitions["ZLIB_COMPAT"] = self.options.zlib_compat
        cmake.definitions["WITH_GZFILEOP"] = self.options.with_gzfileop
        cmake.definitions["WITH_OPTIM"] = self.options.with_optim
        cmake.definitions["WITH_NEW_STRATEGIES"] = self.options.with_new_strategies
        cmake.definitions["WITH_NATIVE_INSTRUCTIONS"] = self.options.with_native_instructions

        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        #FIXME: CMake targets are https://github.com/zlib-ng/zlib-ng/blob/29fd4672a2279a0368be936d7cd44d013d009fae/CMakeLists.txt#L914
        suffix = "" if self.options.zlib_compat else "-ng"
        self.cpp_info.names["pkg_config"] = "zlib" + suffix
        if self.settings.os == "Windows":
            # The library name of zlib-ng is complicated in zlib-ng>=2.0.4:
            # https://github.com/zlib-ng/zlib-ng/blob/2.0.4/CMakeLists.txt#L994-L1016
            base = "zlib" if is_msvc(self) or tools.Version(self.version) < "2.0.4" or self.options.shared else "z"
            static_flag = "static" if is_msvc(self) and not self.options.shared and tools.Version(self.version) >= "2.0.4" else ""
            build_type = "d" if self.settings.build_type == "Debug" else ""
            self.cpp_info.libs = ["{}{}{}{}".format(base, static_flag, suffix, build_type)]
        else:
            self.cpp_info.libs = ["z{}".format(suffix)]
        if self.options.zlib_compat:
            self.cpp_info.defines.append("ZLIB_COMPAT")
        if self.options.with_gzfileop:
            self.cpp_info.defines.append("WITH_GZFILEOP")
        if not self.options.with_new_strategies:
            self.cpp_info.defines.extend(["NO_QUICK_STRATEGY", "NO_MEDIUM_STRATEGY"])
