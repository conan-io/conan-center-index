import os
import glob
from conans import ConanFile, CMake, tools


class AstcCodecConan(ConanFile):
    name = "astc-codec"
    description = " A software ASTC decoder implementation which supports the ASTC LDR profile"
    homepage = "https://github.com/google/astc-codec"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    topics = ("conan", "astc", "codec")
    settings = "os", "compiler", "arch", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    exports_sources = "CMakeLists.txt"
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
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("astc-codec-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["OPTION_ASTC_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.lib", src=os.path.join(self._build_subfolder, "lib"), dst="lib", keep_path=False)
        self.copy("*.dll", src=os.path.join(self._build_subfolder, "bin"), dst="bin", keep_path=False)
        self.copy("*.exe", src=os.path.join(self._build_subfolder, "bin"), dst="bin", keep_path=False)
        self.copy("*.so*", src=os.path.join(self._build_subfolder, "lib"), dst="lib", keep_path=False, symlinks=True)
        self.copy("*.dylib", src=os.path.join(self._build_subfolder, "lib"), dst="lib", keep_path=False)
        self.copy("*.a", src=os.path.join(self._build_subfolder, "lib"), dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
