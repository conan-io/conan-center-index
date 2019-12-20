from conans import ConanFile, tools, MSBuild
import os


class PthreadWin32Conan(ConanFile):
    name = "pthread-win32"
    description = "Open Source POSIX Threads for Win32"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.sourceware.org/pthreads-win32/"
    topics = ("pthread", "posix", "win32-port", "multithreaded", "thread")
    license = "GNU LGPL"

    # Options may need to change depending on the packaged library.
    settings = {"os": "Windows", "arch": None, "compiler": "Visual Studio", "build_type": None}
    options = {"shared": [True, False]}
    default_options = {'shared': 'False'}
    _source_subfolder = "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
   
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename('pthread-win32-19fd5054b29af1b4e3b3278bfffbb6274c6c89f5', self._source_subfolder)

    def build(self):
        with tools.chdir(self._source_subfolder):
            solution_name = {16: 'pthread.2015.sln',
                             15: 'pthread.2015.sln',
                             14: 'pthread.2015.sln',
                             12: 'pthread.2013.sln'}.get(int(str(self.settings.compiler.version)))
            targets = ['pthread_dll'] if self.options.shared else ['pthread_lib']
            msbuild = MSBuild(self)
            msbuild.build(solution_name, targets=targets, platforms={"x86": "Win32"})

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="pthread.h", dst="include", src=self._source_subfolder)
        self.copy(pattern="sched.h", dst="include", src=self._source_subfolder)
        self.copy(pattern="semaphore.h", dst="include", src=self._source_subfolder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['pthread_dll' if self.options.shared else 'pthread_lib']
        if not self.options.shared:
            self.cpp_info.defines.append('PTW32_STATIC_LIB=1')
