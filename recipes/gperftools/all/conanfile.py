from conans import ConanFile, AutoToolsBuildEnvironment, tools
import functools
import os

from conans import ConanInvalidConfiguration


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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            f"--enable-shared={yes_no(self.options.shared)}",
            f"--enable-static={yes_no(not self.options.shared)}",
        ]
        autotools.configure(args=args, configure_dir=self._source_subfolder)
        autotools.fpic = self.options.get_safe("fPIC", True)
        return autotools

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

