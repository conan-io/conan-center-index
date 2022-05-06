from conans import ConanFile, tools, CMake
import os


class SystemccciConan(ConanFile):
    name = "systemc-cci"
    version = "1.0.0"
    description = """SystemC Configuration, Control and Inspection library"""
    homepage = "https://www.accellera.org/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    topics = ("simulation", "modeling", "esl", "cci")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    requires = "systemc/2.3.3"
    generators = "cmake"
    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        tools.check_min_cppstd(self, "11")
        if self.options.shared:
            del self.options.fPIC


    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("cci-{}".format(self.version), self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        cmake = CMake(self, parallel=True)
        cmake.verbose = True
        cmake.definitions["SYSTEMC_ROOT"] = self.deps_cpp_info["systemc"].rootpath
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("NOTICE", dst="licenses", src=self._source_subfolder)
        src_dir = os.path.join(self._source_subfolder, "src")
        self.copy("*.h", dst="include", src=src_dir)
        self.copy("cci_configuration", dst="include", src=src_dir)
        lib_dir = os.path.join(self._source_subfolder, "lib")
        if self.options.shared:
            self.copy("*.so", dst="lib", src=lib_dir)
        else:
            self.copy("*.a", dst="lib", src=lib_dir)

    def package_info(self):
        self.cpp_info.libs = ["cciapi"]
