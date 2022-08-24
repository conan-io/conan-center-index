from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class BlissConan(ConanFile):
    name = "bliss"
    description = "bliss is an open source tool for computing automorphism groups and canonical forms of graphs. "
    topics = "conan", "bliss", "automorphism", "group", "graph"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://users.aalto.fi/~tjunttil/bliss"
    license = "GPL-3-or-later", "LGPL-3-or-later"
    settings = "arch", "os", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_exact_int": [False, "gmp", "mpir"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_exact_int": False,
    }
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"

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
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if self.options.with_exact_int == "gmp":
            self.requires("gmp/6.2.0")
        elif self.options.with_exact_int == "mpir":
            self.requires("mpir/3.0.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < "15":
            raise ConanInvalidConfiguration("bliss doesn't support Visual Studio < 2017")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["USE_GMP"] = self.options.with_exact_int != False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("COPYING.LESSER", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["bliss" if self.options.shared else "bliss_static"]
        self.cpp_info.includedirs.append(os.path.join("include", "bliss"))
        if self.options.with_exact_int != False:
            self.cpp_info.defines = ["BLISS_USE_GMP"]
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.cxxflags.append("/permissive-")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
