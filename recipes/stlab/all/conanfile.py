from conans import ConanFile, tools
import os

class Stlab(ConanFile):
    name = 'stlab'
    description = 'The Software Technology Lab libraries.'
    url = 'https://github.com/stlab/libraries'
    homepage = 'https://github.com/stlab/libraries'
    author = 'Manu Sanchez and Tim van Deurzen'
    license = 'Boost Software License 1.0'
    topics = 'c++', 'concurrency'

    settings = 'compiler'

    no_copy_source = True
    _source_subfolder = 'source_subfolder'

    requires = 'boost/1.69.0'
    default_options = ('boost:shared=False',
                       'boost:without_chrono=False',
                       'boost:without_system=False',
                       'boost:without_timer=False',
                       'boost:without_test=False',
                       'boost:without_iostreams=True',
                       'boost:without_log=True',
                       'boost:without_regex=True',
                       'boost:without_locale=True',
                       'boost:without_exception=True',
                       'boost:without_filesystem=True',
                       'boost:without_container=True',
                       'boost:without_program_options=True',
                       'boost:without_wave=True',
                       'boost:without_thread=True',
                       'boost:without_graph_parallel=True',
                       'boost:without_context=True',
                       'boost:without_random=True',
                       'boost:without_graph=True',
                       'boost:without_serialization=True',
                       'boost:without_date_time=True',
                       'boost:without_fiber=True',
                       'boost:without_coroutine=True',
                       'boost:without_mpi=True',
                       'boost:without_type_erasure=True',
                       'boost:without_math=True',
                       'boost:without_container=True',
                       'boost:without_log=True',
                       'boost:without_exception=True',
                       'boost:without_python=True',
                       'boost:without_stacktrace=True',
                       'boost:without_atomic=True')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "libraries-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        tools.check_min_cppstd(self, '17')

    def package(self):
        self.copy("*LICENSE", dst="licenses", keep_path=False)
        self.copy("stlab/*", src=self._source_subfolder, dst='include/')

    def package_id(self):
        self.info.header_only()
