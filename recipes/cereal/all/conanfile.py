import os

from conans import ConanFile, CMake, tools


class CerealConan(ConanFile):
    name = "cereal"
    description = "Serialization header-only library for C++11."
    license = "BSD-3-Clause"
    topics = ("conan", "cereal", "header-only", "serialization", "cpp11")
    homepage = "https://github.com/USCiLab/cereal"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {"thread_safe": [True, False]}
    default_options = {"thread_safe": False}
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = CMake(self)
        cmake.definitions["JUST_INSTALL_CEREAL"] = True
        cmake.configure()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        self._create_module_official_cmake_targets(
            os.path.join(self.package_folder, self._module_folder, self._module_file),
            [{"official": "cereal", "namespaced": "cereal::cereal"}]
        )

    @staticmethod
    def _create_module_official_cmake_targets(module_file, targets):
        content = ""
        for target in targets:
            content += (
                "if(TARGET {namespaced} AND NOT TARGET {official})\n"
                "    add_library({official} INTERFACE IMPORTED)\n"
                "    target_link_libraries({official} INTERFACE {namespaced})\n"
                "endif()\n"
            ).format(official=target["official"], namespaced=target["namespaced"])
        tools.save(module_file, content)

    @property
    def _module_folder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return "conan-official-{}-targets.cmake".format(self.name)

    def package_info(self):
        self.cpp_info.builddirs = [self._module_folder]
        self.cpp_info.build_modules = [os.path.join(self._module_folder, self._module_file)]
        if self.options.thread_safe:
            self.cpp_info.defines = ["CEREAL_THREAD_SAFE=1"]
            if self.settings.os == "Linux":
                self.cpp_info.system_libs.append("pthread")
