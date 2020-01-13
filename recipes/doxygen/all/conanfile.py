from conans import ConanFile, tools, CMake
import os

class DoxygenConan(ConanFile):
    name = "doxygen"
    description = "A documentation system for C/C++"
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-2.0"
    homepage = "http://www.doxygen.nl/"
    settings = "os_build", "arch_build"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("libiconv/1.15")

    def build_requirements(self):
        if not tools.which("flex"):
            self.build_requires("flex/2.6.4@bincrafters/stable")

        if not tools.which("bison"):
            self.build_requires("bison/3.3.2@bincrafters/stable")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=os.path.join(self.source_folder, self._source_subfolder))

        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.path.append(bin_path)