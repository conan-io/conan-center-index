import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration


class DarknetConan(ConanFile):
    name = "darknet"
    license = "YOLO"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://pjreddie.com/darknet/"
    description = "Darknet is a neural network frameworks written in C"
    topics = ("darknet", "neural network", "deep learning")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_opencv": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_opencv": False,
    }
    exports_sources = ['patches/*']
    generators = "pkg_config"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _lib_to_compile(self):
        if not self.options.shared:
            return "$(ALIB)"
        else:
            return "$(SLIB)"

    @property
    def _shared_lib_extension(self):
        if self.settings.os == "Macos":
            return ".dylib"
        else:
            return ".so"

    def _patch_sources(self):
        for patch in self.conan_data["patches"].get(self.version, []):
            tools.files.patch(self, **patch)
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "Makefile"),
            "SLIB=libdarknet.so",
            "SLIB=libdarknet" + self._shared_lib_extension
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "Makefile"),
            "all: obj backup results $(SLIB) $(ALIB) $(EXEC)",
            "all: obj backup results " + self._lib_to_compile
        )

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("This library is not compatible with Windows")

    def requirements(self):
        if self.options.with_opencv:
            self.requires("opencv/2.4.13.7")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder,
                  strip_root=True)

    def build(self):
        self._patch_sources()
        with tools.chdir(self._source_subfolder):
            with tools.environment_append({"PKG_CONFIG_PATH": self.build_folder}):
                args = ["OPENCV={}".format("1" if self.options.with_opencv else "0")]
                env_build = AutoToolsBuildEnvironment(self)
                env_build.fpic = self.options.get_safe("fPIC", True)
                env_build.make(args=args)

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["darknet"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m", "pthread"]
        if tools.stdcpp_library(self):
            self.cpp_info.system_libs.append(tools.stdcpp_library(self))
