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
    settings = "os", "compiler"
    topics = "dotnet", "mono", "csharp", "runtime", "compiler"

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
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder_with_root)
        with tools.chdir(self._source_subfolder_with_root):
            autotools = self._configure_autotools()
            autotools.install()

        # The scripts in the bin folder all have absolute paths. Replace them with the MONO_CONAN_ROOT_DIR environment variable
        # which is set in the package_info step
        # The find code before sed is filtering to only replace in text files and skip binary files
        # Source: https://stackoverflow.com/a/13659891

        # Not sure why, but this command fails on Macos
        if self.settings.os != "Macos":
            self.run('find {2} -type f -exec grep -Iq . {{}} \\; -print | xargs sed -i "s@{0}/@{1}/@g" '.format(self.package_folder, "\\${MONO_CONAN_ROOT_DIR}", os.path.join(self.package_folder, "bin")))

        tools.rmdir(os.path.join(self.package_folder, "share"))
        # Note: the etc folder is needed, otherwise some of the mono scripts do not properly work
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pdb")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "mono"
        self.cpp_info.names["cmake_find_package_multi"] = "mono"
        self.cpp_info.names["pkg_config"] = "mono"
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.resdirs = ["etc"]

        # This variable is required within the mono scripts in mono/bin folder
        self.env_info.MONO_CONAN_ROOT_DIR = self.package_folder

        # The cert-sync script is requiring MONO_CONAN_ROOT_DIR
        env = {"MONO_CONAN_ROOT_DIR": self.package_folder}
        with tools.environment_append(env):
            # See https://github.com/mono/mono/issues/12406#issuecomment-453998125
            self.run("{} --user --quiet /etc/ssl/certs/ca-certificates.crt".format(os.path.join(self.package_folder, "bin", "cert-sync")))

        # from https://stackoverflow.com/a/50374000
        self.env_info.MONO_TLS_PROVIDER = "legacy"

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

