from conans import ConanFile, CMake, tools
import functools
import os

required_conan_version = ">=1.33.0"


class CppcheckConan(ConanFile):
    name = "cppcheck"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/danmar/cppcheck"
    topics = ("cpp check", "static analyzer")
    description = "Cppcheck is an analysis tool for C/C++ code."
    license = "GPL-3.0-or-later"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_z3": [True, False],
        "have_rules": [True, False]
        }
    default_options = {
        "with_z3": True,
        "have_rules": True
        }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "${CMAKE_SOURCE_DIR}",
                              "${PROJECT_SOURCE_DIR}")
        tools.replace_in_file(os.path.join(self._source_subfolder, "tools", "CMakeLists.txt"),
                              "${CMAKE_SOURCE_DIR}",
                              "${PROJECT_SOURCE_DIR}")
        tools.replace_in_file(os.path.join(self._source_subfolder, "tools", "CMakeLists.txt"),
                              "${CMAKE_BINARY_DIR}",
                              "${PROJECT_BINARY_DIR}")
        tools.replace_in_file(os.path.join(self._source_subfolder, "cli", "CMakeLists.txt"),
                              "RUNTIME DESTINATION ${CMAKE_INSTALL_FULL_BINDIR}",
                              "DESTINATION ${CMAKE_INSTALL_FULL_BINDIR}")

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def requirements(self):
        if self.options.with_z3:
            self.requires("z3/4.10.2")
        if self.options.have_rules:
            self.requires("pcre/8.45")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["USE_Z3"] = self.options.with_z3
        cmake.definitions["HAVE_RULES"] = self.options.have_rules
        cmake.definitions["USE_MATCHCOMPILER"] = "Auto"
        cmake.definitions["ENABLE_OSS_FUZZ"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst=os.path.join("bin","cfg"), src=os.path.join(self._source_subfolder,"cfg"))
        self.copy("cppcheck-htmlreport", dst=os.path.join("bin"), src=os.path.join(self._source_subfolder,"htmlreport"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        bin_folder = os.path.join(self.package_folder, "bin")
        self.output.info("Append %s to environment variable PATH" % bin_folder)
        self.env_info.PATH.append(bin_folder)
        # This is required to run the python script on windows, as we cannot simply add it to the PATH
        self.env_info.CPPCHECK_HTMLREPORT = os.path.join(bin_folder, "cppcheck-htmlreport")
