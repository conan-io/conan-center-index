from conans import ConanFile, CMake, tools
import os

class CoinLemonConan(ConanFile):
    name = "coin-lemon"
    license = "Boost 1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://lemon.cs.elte.hu"
    description = "LEMON stands for Library for Efficient Modeling and Optimization in Networks."
    topics = ("data structures", "algorithms", "graphs", "network")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

        self.copy("*.h", dst=os.path.join("include", "lemon"), src=os.path.join(self._source_subfolder, "lemon"))
        self.copy("config.h", dst=os.path.join("include", "lemon"), src="lemon")

        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so*", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["emon"]
        self.cpp_info.filenames["cmake_find_package"] = "coin-lemon"
        self.cpp_info.filenames["cmake_find_package_multi"] = "coin-lemon"
