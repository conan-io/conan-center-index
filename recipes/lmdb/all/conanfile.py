import os
from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.29.0"


class lmdbConan(ConanFile):
    name = "lmdb"
    license = "OLDAP-2.8"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://symas.com/lmdb/"
    description = "Fast and compat memory-mapped key-value database"
    topics = ("LMDB", "database", "key-value", "memory-mapped")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_robust_mutex": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_robust_mutex": True,
    }
    exports_sources = ["CMakeLists.txt"]
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
        if self.settings.os in ("Linux", "FreeBSD"):
            self.options.enable_robust_mutex = True
        else:
            self.options.enable_robust_mutex = False

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        root = "openldap-LMDB_{}".format(self.version)
        tools.files.rename(self, os.path.join(root, "libraries", "liblmdb"), self._source_subfolder)
        tools.files.rmdir(self, root)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LMDB_ENABLE_ROBUST_MUTEX"] = self.options.enable_robust_mutex
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["lmdb"]
        self.cpp_info.names["pkg_config"] = "lmdb"

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
