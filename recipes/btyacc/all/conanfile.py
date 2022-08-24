import functools
import os
import textwrap

from conans import CMake, ConanFile, tools

required_conan_version = ">=1.43.0"


class BtyaccConan(ConanFile):
    name = "btyacc"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ChrisDodd/btyacc"
    description = "Backtracking yacc"
    topics = "yacc", "parser"
    license = "Unlicense"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    generators = "cmake"
    exports_sources = "CMakeLists.txt"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        root = self._source_subfolder
        get_args = self.conan_data["sources"][self.version]
        tools.files.get(self, **get_args, destination=root, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        self._configure_cmake().build()

    @property
    def _variables(self):
        return os.path.join("bin", "conan-official-btyacc-variables.cmake")

    def package(self):
        self.copy("README", "licenses", self._source_subfolder)
        self.copy("README.BYACC", "licenses", self._source_subfolder)
        self._configure_cmake().install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        variables = os.path.join(self.package_folder, self._variables)
        content = textwrap.dedent("""\
            set(BTYACC_EXECUTABLE "${CMAKE_CURRENT_LIST_DIR}/btyacc")
            if(NOT EXISTS "${BTYACC_EXECUTABLE}")
              set(BTYACC_EXECUTABLE "${BTYACC_EXECUTABLE}.exe")
            endif()
        """)
        tools.save(variables, content)

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)
        self.cpp_info.build_modules["cmake"] = [self._variables]
        self.cpp_info.build_modules["cmake_find_package"] = [self._variables]
        self.cpp_info.build_modules["cmake_find_package_multi"] = \
            [self._variables]
        self.cpp_info.builddirs = ["bin"]
