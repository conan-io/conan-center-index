#include <argparse/argparse.hpp>

#include <iostream>

int main(int argc, char *argv[]) {
  argparse::ArgumentParser program("test_package");

  program.add_argument("square")
    .help("display the square of a given integer")
    .action([](const std::string& value) { return std::stoi(value); });

  try {
    program.parse_args(argc, argv);
  }
  catch (const std::runtime_error& err) {
    std::cout << err.what() << std::endl;
    std::cout << program;
    return 0;
  }

  auto input = program.get<int>("square");
  std::cout << (input * input) << std::endl;

  return 0;
}
