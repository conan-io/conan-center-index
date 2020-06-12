#include <iostream>
#include <memory>
#include <boost/di.hpp>

namespace di = boost::di;

class IPrinter {
public:
  virtual ~IPrinter() = default;
  virtual void print() = 0;
};

class Printer : public IPrinter {
  void print() override { std::cout << "Success !\n"; }
};

class PrintCaller {
public:
  explicit PrintCaller(std::unique_ptr<IPrinter> printer) : _printer{std::move(printer)} {}
  void callPrint() { _printer->print(); }
private:
  std::unique_ptr<IPrinter> _printer;
};

int main() {
  const auto injector = di::make_injector(
     di::bind<IPrinter>().to<Printer>()
  );

  auto printCaller = injector.create<PrintCaller>();
  printCaller.callPrint();

  return 0;
}
