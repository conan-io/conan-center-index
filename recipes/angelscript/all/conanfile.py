from conans import CMake, ConanFile, tools

import os


class AngelScriptConan(ConanFile):
    name = "angelscript"
    license = "Zlib"
    homepage = "http://www.angelcode.com/angelscript"
    url = "https://github.com/conan-io/conan-center-index"
    description = "An extremely flexible cross-platform scripting library designed to allow applications to extend their functionality through external scripts."
    topics = "angelcode", "embedded", "scripting", "language", "compiler", "interpreter"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [False, True],
        "fPIC": [False, True],
        "no_exceptions": [False, True],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "no_exceptions": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(
            args=[
                "-DCMAKE_CXX_STANDARD=11",
                "-DAS_NO_EXCEPTIONS={}".format(self.options.no_exceptions.value),
            ],
            source_folder=os.path.join(self._source_subfolder, "angelscript", "projects", "cmake"),
            build_folder=self._build_subfolder,
        )
        return cmake

    def source(self):
        # Website blocks default user agent string.
        tools.get(
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder,
            headers={"User-Agent": "ConanCenter"},
            strip_root=True,
        )

    def build(self):
        self._configure_cmake().build()

    def package(self):
        self._configure_cmake().install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        header = tools.load(os.path.join(self.package_folder, "include", "angelscript.h"))
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), header[header.find("/*", 1) + 3 : header.find("*/", 1)])

    def package_info(self):
        # FIXME: Missing CMake components 
        self.cpp_info.names["cmake_find_package"] = "Angelscript"
        self.cpp_info.names["cmake_find_package_multi"] = "Angelscript"
        self.cpp_info.components["_angelscript"].names["cmake_find_package"] = "angelscript"
        self.cpp_info.components["_angelscript"].names["cmake_find_package_multi"] = "angelscript"
        postfix = "d" if self.settings.compiler == "Visual Studio" else ""
        self.cpp_info.components["_angelscript"].libs = ["angelscript" + postfix]
        if self.settings.os in ("Linux", "FreeBSD", "SunOS"):
            self.cpp_info.components["_angelscript"].system_libs.append("pthread")
