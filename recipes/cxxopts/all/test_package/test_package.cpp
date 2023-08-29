#include <iostream>
#include <cxxopts.hpp>

int main(int argc, char* argv[])
{
	cxxopts::Options options { "test_package", "The example program to test cxxopts package" };

	options.add_options()
		("h,help", "Print help")
		("f,foo", "Option foo", cxxopts::value<int>()->default_value("10"))
		("b,bar", "Option bar", cxxopts::value<std::string>())
		("z,baz", "Option baz", cxxopts::value<bool>()->implicit_value("true"))
	#ifdef CXXOPTS_USE_UNICODE
		("q,qux", u8"Option qux with non-ascii description: 你好", cxxopts::value<std::string>())
	#endif
	;

	try {
		// cxxopts versions before 2.x.x had a slightly different interface of options parsing
		// This preprocessor block allows to use one recipe and test package
		// for both 1.x.x and 2.x.x releases
	#ifdef CXXOPTS__VERSION_MAJOR
		auto result = options.parse(argc, argv);
	#else
		options.parse(argc, argv);
		auto result = options;
	#endif

		if (result.count("help")) {
			std::cout << options.help({ "", "Group" }) << std::endl;
			return 0;
		}

		if (result.count("foo")) {
			std::cout << "foo:" << result["foo"].as<int>() << std::endl;
		}

		if (result.count("bar")) {
			std::cout << "bar:" << result["bar"].as<std::string>() << std::endl;
		}

		if (result.count("baz")) {
			std::cout << "baz:" << result["baz"].as<bool>() << std::endl;
		}
	#ifdef CXXOPTS_USE_UNICODE
		if (result.count("qux")) {
			std::cout << "qux:" << result["qux"].as<std::string>() << std::endl;
		}
	#endif
	}
	#ifdef CXXOPTS_OLD_EXCEPTIONS
	catch (const cxxopts::OptionException& e) {
		std::cout << "error parsing options: " << e.what() << std::endl;
		return 1;
	}
	#else
	catch (const cxxopts::exceptions::exception& e) {
		std::cout << "error parsing options: " << e.what() << std::endl;
		return 1;
	}
	#endif

	return 0;
}
