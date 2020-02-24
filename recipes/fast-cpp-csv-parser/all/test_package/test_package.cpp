#include <csv.h>

#include <iostream>
#include <string>

int main(int argc, char **argv) {
  if (argc < 2) {
    std::cerr << "Need at least one argument\n";
    return 1;
  }

  io::CSVReader<3> in(argv[1]);
  in.read_header(io::ignore_extra_column, "First Name", "Last Name", "Age");
  std::string first_name; std::string last_name; double age;
  while (in.read_row(first_name, last_name, age)) {
    std::cout << first_name << " " << last_name << " " << age << '\n';
  }

  return 0;
}
