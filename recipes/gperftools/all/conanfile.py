import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class GperftoolsConan(ConanFile):
    name = "gperftools"
    license = "BSD-3-Clause License"
    homepage = "https://github.com/gperftools/gperftools"
    url = "https://github.com/conan-io/conan-center-index"
    description = "gperftools: originally Google Performance Tools"
    topics = ("malloc", "profiler")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": False,
    }
    autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self.autotools is None:
            autotools = AutoToolsBuildEnvironment(self)
            with tools.chdir(self._source_subfolder):
                self.run("autoreconf -fiv")
            default_args = []
            if self.options.shared:
                default_args.append("--disable-static")
            else:
                default_args.append("--disable-shared")
            if self.options.fPIC:
                default_args.append("--with-pic=yes")
            autotools.configure(
                configure_dir=self._source_subfolder,
                args=default_args
            )
            self.autotools = autotools
        return self.autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.components["tcmalloc_and_profiler"].names["cmake_find_package"] = "tcmalloc_and_profiler"
        self.cpp_info.components["tcmalloc_and_profiler"].names["cmake_find_package_multi"] = "tcmalloc_and_profiler"
        self.cpp_info.components["tcmalloc_and_profiler"].libs = ["tcmalloc_and_profiler"]

        self.cpp_info.components["tcmalloc"].names["cmake_find_package"] = "tcmalloc"
        self.cpp_info.components["tcmalloc"].names["cmake_find_package_multi"] = "tcmalloc"
        self.cpp_info.components["tcmalloc"].libs = ["tcmalloc"]

        self.cpp_info.components["profiler"].names["cmake_find_package"] = "profiler"
        self.cpp_info.components["profiler"].names["cmake_find_package_multi"] = "profiler"
        self.cpp_info.components["profiler"].libs = ["profiler"]
        if self.settings.os == 'Linux':
            self.cpp_info.components['tcmalloc_and_profiler'].system_libs.extend(['pthread'])

