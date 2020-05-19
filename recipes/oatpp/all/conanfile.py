from conans import ConanFile, CMake, tools
import os


class OatppConan(ConanFile):
    name = "oatpp"
    version = "1.0.0"
    description = "Modern Web Framework for C++"
    homepage = "https://github.com/zeromq/cppzmq"
    license = "Apache License 2.0"
    topics = ("conan", "oat++", "oatpp", "web-framework")
    url = "https://github.com/conan-io/conan-center-index"
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _source_subfolder = "source_subfolder"
    _cmake = None

    @property
    def _full_source_subfolder(self):
        return os.path.join(self.source_folder, self._source_subfolder)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("oatpp-{0}".format(self.version), self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build(self):
        cmake = self._configure_cmake()
        cmake.build(target="oatpp")
        cmake.build(target="oatpp-test")
        cmake.install()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["OATPP_BUILD_TESTS"] = False
        self._cmake.definitions["CMAKE_INSTALL_PREFIX"] = os.path.join(
            self.build_folder, "__dist"
        )
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def package(self):
        # copy headers
        self.copy(
            "*",
            src="__dist/include/oatpp-{version}/oatpp"
                .format(version=self.version),
            dst="include",
        )

        # copy libraries
        self.copy(
            "*",
            src="__dist/lib/oatpp-{version}".format(version=self.version),
            dst="lib",
            keep_path=False,
        )

        self.copy(
            "LICENSE",
            src=self._full_source_subfolder,
            dst="licenses",
            keep_path=False
        )

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
