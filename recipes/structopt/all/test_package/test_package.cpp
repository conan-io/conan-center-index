#include <structopt/app.hpp>

// Copied from structopt/samples/demo

struct Options {
  // positional argument
  //   e.g., ./main <file>
  std::string config_file;

  // optional argument
  //   e.g., -b "192.168.5.3"
  //   e.g., --bind_address "192.168.5.3"
  // The long option can be passed in kebab case
  //   e.g., --bind-address "192.168.5.3"
  std::optional<std::string> bind_address;

  // Use `std::optional<bool>` and provide a default value.
  // Now you have a flag!
  //   e.g., -v
  //   e.g., --verbose
  // Passing this flag will set this
  // value to (!default_value), i.e., true
  std::optional<bool> verbose = false;

  // structopt also support defining enum classes
  // The argument (string) will be converted (if possible)
  // into the equivalent enum value
  //   e.g., --log-level debug
  //   e.g., -l error
  enum class LogLevel { debug, info, warn, error, critical };
  std::optional<LogLevel> log_level = LogLevel::info;

  // Here, structopt will check for `-u` or `--user`
  // and parse the next 2 arguments into an `std::pair`
  std::optional<std::pair<std::string, std::string>> user;

  // You can use containers like std::vector
  // to save variadic arguments of some type
  std::vector<std::string> files;
};
STRUCTOPT(Options, config_file, bind_address, verbose, log_level, user, files);

int main(int argc, char *argv[]) {

  try {
    const auto args = std::vector<std::string>{"./main", "config_2.csv", "--bind-address", "192.168.7.3",
					       "-log-level", "debug", "file1.txt", "file2.txt", "file3.txt",
					       "file4.txt", "--user", "John Doe", "john.doe@foo.com"};
    auto options = structopt::app("my_app").parse<Options>(args);

    // Print out parsed arguments:

    std::cout << "config_file  = " << options.config_file << "\n";
    std::cout << "bind_address = " << options.bind_address.value_or("not provided")
              << "\n";
    std::cout << "verbose      = " << std::boolalpha << options.verbose.value() << "\n";
    std::cout << "log_level    = " << static_cast<int>(options.log_level.value()) << "\n";
    if (options.user.has_value())
      std::cout << "user         = " << options.user.value().first << "<"
                << options.user.value().second << ">\n";
    else
      std::cout << "user         = "
                << "not provided\n";
    std::cout << "files        = { ";
    std::copy(options.files.begin(), options.files.end(),
              std::ostream_iterator<std::string>(std::cout, " "));
    std::cout << "}" << std::endl;

  } catch (structopt::exception &e) {
    std::cout << e.what() << "\n";
    std::cout << e.help();
  }
}
