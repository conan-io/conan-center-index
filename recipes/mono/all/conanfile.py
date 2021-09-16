from conans import AutoToolsBuildEnvironment, ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os
import yaml
import math

required_conan_version = ">=1.33.0"


class MonoConan(ConanFile):
    name = "mono"
    description = "Mono open source ECMA CLI, C# and .NET implementation."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.mono-project.com/"
    license = ("MIT", "BSD-3-Clause", "Apache-2.0")
    exports_sources = "patches/**"
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config"
    topics = "dotnet", "mono", "csharp", "runtime", "compiler"
    # options = {
    #     "with-sgen": ["yes", "no"],
    #     "with-libgc": ["included", "none"],
    #     "enable-cooperative-suspend": [True, False],
    #     #"with-tls": ["__thread", "pthread", ""], #Review needed added ""
    #     "with-sigaltstack": ["yes", "no"],
    #     "with-static_mono": ["yes", "no"],
    #     "with-xen-opt": ["yes", "no"],
    #     "with-large-heap": ["yes", "no"],
    #     "enable-small-config": ["yes", "no"],
    #     "with-ikvm-native": ["yes", "no"],
    #     "with-profile4": ["yes", "no"],
    #     "with-libgdiplus": ["installed", "sibling"], #or <path> ?
    #     # "enable-minimal": ["aot", "attach", "com", "debug", "decimal", "full_messages",
    #     #                     "generics", "jit", "large_code", "logging", "pinvoke", "portability", "profiler",
    #     #                     "reflection_emit", "reflection_emit_save", "shadow_copy", "simd", "ssa", []], #How ?????!! added []
    #     "enable-llvm": [True, False],
    #     "enable-big-arrays": [True, False],
    #     "enable-parallel-mark": [True, False],
    #     "enable-dtrace": [True, False],
    #     "disable-dev-random": [True, False],
    #     "with-csc": ["roslyn", "mcs", "default"],
    #     "enable-nacl": [True, False],
    #     "enable-wasm": [True, False],
    # }
    # default_options = {
    #     "with-sgen": "no",
    #     "with-libgc": "none",
    #     "enable-cooperative-suspend": False, #recheck this
    #     #"with-tls": "", #This value is typically pre-configured and there is no need to set it, unless you are trying to debug a problem
    #     "with-sigaltstack": "no",
    #     "with-static_mono": "yes",
    #     "with-xen-opt": "yes",
    #     "with-large-heap": "no",
    #     "enable-small-config": "no",
    #     "with-ikvm-native": "yes",
    #     "with-profile4": "yes",
    #     "with-libgdiplus": "installed",
    #     #"enable-minimal" : [],
    #     "enable-llvm": False,
    #     "enable-big-arrays": False,
    #     "enable-parallel-mark": False,
    #     "enable-dtrace": False,
    #     "disable-dev-random": False,
    #     "with-csc": "default",
    #     "enable-nacl": False,
    #     "enable-wasm": False,
    # }


    @property
    def _minimum_compilers_version(self):
        # requires C++11
        return {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "9"
        }


    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("mono cannot be built on Windows")

    def configure(self):
        # C++ minimum standard required
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("C++11 support required. Your compiler is unknown. Assuming it supports C++11.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("C++11 support required, which your compiler does not support.")

    def requirements(self):
        self.requires("zlib/1.2.11")

    def build_requirements(self):
        self.build_requires("m4/1.4.18")
        self.build_requires("libtool/2.4.6")

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _source_subfolder_with_root(self):
        return os.path.join("source_subfolder", "mono-" + self.version)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=False)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder_with_root):
            self.run("./autogen.sh --prefix={}".format(self.package_folder), run_environment=True)
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        with tools.chdir(self._source_subfolder_with_root):
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "mono"
        self.cpp_info.names["cmake_find_package_multi"] = "mono"
        self.cpp_info.names["pkg_config"] = "mono"
        self.cpp_info.libs = tools.collect_libs(self)


        # from https://stackoverflow.com/a/50374000
        self.env_info.MONO_TLS_PROVIDER = "legacy"

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

