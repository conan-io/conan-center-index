from conans import ConanFile, tools, CMake
import os

class KangaruConan(ConanFile):
    name = "kangaru"
    description = "A dependency injection container for C++11, C++14 and later"
    license = "MIT"
    topics = ("conan", "gracicot", "kangaru", "DI", "IoC", "inversion of control")
    homepage = "https://github.com/gracicot/kangaru/wiki"
    url = "https://github.com/conan-io/conan-center-index"
    options = {"reverse_destruction": [True, False],
                "no_exception": [True, False]}
    default_options = {"reverse_destruction": True,
                        "no_exception": False}
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["KANGARU_REVERSE_DESTRUCTION"] = self.options.reverse_destruction
        cmake.definitions["KANGARU_NO_EXCEPTION"] = self.options.no_exception
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib"))
        self.copy(os.path.join(self._source_subfolder, "LICENSE"), "licenses")
