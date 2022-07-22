from conan import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd

import functools
import os
from packaging.version import Version

required_conan_version = ">=1.33.0"


class OpenGrmConan(ConanFile):
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
            raise ConanInvalidConfiguration('Using %s with GCC requires "compiler.libcxx=libstdc++11"' % self.name)
        elif self.settings.compiler == "clang" and self.settings.compiler.libcxx not in ["libstdc++11", "libc++"]:
            raise ConanInvalidConfiguration('Using %s with Clang requires either "compiler.libcxx=libstdc++11"'
                                            ' or "compiler.libcxx=libc++"' % self.name)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--with-pic={}".format(yes_no(self.options.get_safe("fPIC", True))),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-bin={}".format(yes_no(self.options.enable_bin)),
            "LIBS=-lpthread",
        ]
        autotools.configure(args=args, configure_dir=self._source_subfolder)
        return autotools

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenGrm")
        self.cpp_info.set_property("cmake_target_name", "OpenGrm::OpenGrm")
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.names["cmake_find_package"] = "OpenGrm"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenGrm"

        self.cpp_info.libs = ["thrax"]

        if self.options.enable_bin:
            bindir = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment var: {}".format(bindir))
            self.env_info.PATH.append(bindir)

        self.cpp_info.system_libs = ["pthread", "dl", "m"]
