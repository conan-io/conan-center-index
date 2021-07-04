from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class DiscountConan(ConanFile):
    name = "discount"
    description = "DISCOUNT is a implementation of John Gruber & Aaron Swartz's Markdown markup language."
    license = "BSD-3-Clause"
    topics = ("discount", "markdown")
    homepage = "http://www.pell.portland.or.us/~orc/Code/discount"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["DISCOUNT_MAKE_INSTALL"] = True
        self._cmake.definitions["DISCOUNT_INSTALL_SAMPLES"] = False
        self._cmake.definitions["DISCOUNT_ONLY_LIBRARY"] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYRIGHT", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "discount"
        self.cpp_info.names["cmake_find_package_multi"] = "discount"
        self.cpp_info.names["pkg_config"] = "libmarkdown"
        self.cpp_info.components["_discount"].names["cmake_find_package"] = "libmarkdown"
        self.cpp_info.components["_discount"].names["cmake_find_package_multi"] = "libmarkdown"
        self.cpp_info.components["_discount"].names["pkg_config"] = "libmarkdown"
        self.cpp_info.components["_discount"].libs = ["markdown"]
