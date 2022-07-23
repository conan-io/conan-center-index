import conan
from conan.errors import ConanInvalidConfiguration
from conans import AutoToolsBuildEnvironment
from conans.tools import Version

import functools
import os
import glob
from pathlib import Path

required_conan_version = ">=1.49.0"


class OpenGrmConan(conan.ConanFile):
    name = "opengrm"
    description = "The OpenGrm Thrax tools compile grammars expressed as regular expressions and context-dependent rewrite rules into weighted finite-state transducers."
    topics = ("fst", "wfst", "opengrm", "thrax")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.opengrm.org/twiki/bin/view/GRM/Thrax"
    license = "Apache-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_bin": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_bin": True,
    }

    def requirements(self):
        self.requires("openfst/1.8.2")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        self.options["openfst"].enable_grm = True

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("OpenGrm is only supported on linux")

        if not self.options["openfst"].enable_grm:
            raise ConanInvalidConfiguration("OpenGrm requires OpenFst with enable_grm enabled.")

        compilers = {
            "gcc": "8",
            "clang": "7",
        }

        minimum_compiler = compilers.get(str(self.settings.compiler))
        if minimum_compiler:
            if Version(self.settings.compiler.version) < minimum_compiler:
                raise ConanInvalidConfiguration(f"{self.name} requires c++17, which your compiler does not support.")
        else:
            self.output.warn(f"{self.name} requires c++17, but this compiler is unknown to this recipe. Assuming your compiler supports c++17.")

        # Check stdlib ABI compatibility
        if self.settings.compiler == "gcc" and self.settings.compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration(f'Using {self.name} with GCC requires "compiler.libcxx=libstdc++11"')
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx not in ["libstdc++11", "libc++"]:
            raise ConanInvalidConfiguration(f'Using {self.name} with Clang requires either "compiler.libcxx=libstdc++11"'
                                            ' or "compiler.libcxx=libc++"')

    def source(self):
        conan.tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @staticmethod
    def _yes_no(v):
        return "yes" if v else "no"

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self)
        args = [
            f"--with-pic={self._yes_no(self.options.get_safe('fPIC', True))}",
            f"--enable-shared={self._yes_no(self.options.shared)}",
            f"--enable-static={self._yes_no(not self.options.shared)}",
            f"--enable-bin={self._yes_no(self.options.enable_bin)}",
            "LIBS=-lpthread",
        ]
        autotools.configure(args=args, configure_dir=self._source_subfolder)
        return autotools

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            conan.tools.files.patch(**patch)

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        conan.tools.files.rmdir(self, Path(self.package_folder) / "share")
        for f in glob.glob(Path(self.package_folder) / "lib" / "*.la"):
            os.remove(f)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenGrm")
        self.cpp_info.set_property("cmake_target_name", "OpenGrm::OpenGrm")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.names["cmake_find_package"] = "OpenGrm"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenGrm"

        self.cpp_info.libs = ["thrax"]

        if self.options.enable_bin:
            bindir = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment var: {bindir}")
            self.env_info.PATH.append(bindir)

        self.cpp_info.system_libs = ["pthread", "dl", "m"]
