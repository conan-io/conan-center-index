from conans import ConanFile, tools, CMake
import os, shutil

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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["KANGARU_REVERSE_DESTRUCTION"] = self.options.reverse_destruction
        cmake.definitions["KANGARU_NO_EXCEPTION"] = self.options.no_exception
        cmake.configure(source_folder="kangaru-4.2.4")
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        shutil.rmtree(os.path.join(self.package_folder, "lib"))
        self.copy("*LICENSE*", "licenses")

    def package_id(self):
        self.info.header_only()
    
    def package_info(self):
        self.cpp_info.libs = []
        self.cpp_info.builddirs
