import conan
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import AutotoolsDeps, AutotoolsToolchain, Autotools
from conans.tools import Version, check_min_cppstd, remove_files_by_mask

import functools
import os
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

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 17)
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
        conan.tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @staticmethod
    def _yes_no(v):
        return "yes" if v else "no"

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            conan.tools.files.patch(**patch)

    def generate(self):
        tc = AutotoolsDeps(self)
        tc.generate()
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            f"--enable-bin={self._yes_no(self.options.enable_bin)}",
            "LIBS=-lpthread",
        ])
        tc.make_args.append("-j1")
        tc.generate()

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure(build_script_folder=self._source_subfolder)
        autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        autotools = Autotools(self)
        autotools.install()

        conan.tools.files.rmdir(self, Path(self.package_folder) / "share")
        remove_files_by_mask(Path(self.package_folder) / "lib", "*.la")

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
