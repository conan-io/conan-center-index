from conans import ConanFile, AutoToolsBuildEnvironment, tools, RunEnvironment
import os
import shutil


class MesaGluConan(ConanFile):
    name = "mesa-glu"
    description = "Mesa OpenGL Utility library"
    topics = ("conan", "mesa", "glu", "opengl", "graphics")
    url = "https://github.com/bincrafters/conan-mesa-glu"
    homepage = "https://gitlab.freedesktop.org/mesa/glu"
    license = "SGI-B-2.0"
    generators = "pkg_config"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _source_subfolder = "source_subfolder"
    _autotools = None

    requires = (
        "mesa/19.3.1@bincrafters/stable"
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "glu-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            for package in self.deps_cpp_info.deps:
                lib_path = self.deps_cpp_info[package].rootpath
                for dirpath, _, filenames in os.walk(lib_path):
                   for filename in filenames:
                       if filename.endswith('.pc'):
                            shutil.copyfile(os.path.join(dirpath, filename), filename)
                            tools.replace_prefix_in_pc_file(filename, lib_path)
            args = ["--enable-shared", "--disable-static"] if self.options.shared else ["--enable-static", "--disable-shared"]
            self._autotools = AutoToolsBuildEnvironment(self)
            self._autotools.configure(configure_dir=self._source_subfolder,
                                      pkg_config_paths=self.build_folder,
                                      args=args)
        return self._autotools

    def build(self):
        with tools.environment_append(RunEnvironment(self).vars):
            autotools = self._configure_autotools()
            autotools.make()

    def _extract_license(self):
        contents = tools.load(os.path.join("source_subfolder", "include", "GL", "glu.h"))
        license_contents = contents[2:contents.find("*/", 1)]
        tools.save("LICENSE", license_contents)

    def package(self):
        self._extract_license()
        self.copy(pattern="LICENSE", dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
