#include <sel.hpp>

#include <iostream>

int main() {
  sel::Value ctx = sel::Value::none();
  ctx.set("QTY", sel::Value::num("3"));
  ctx.set("PRICE", sel::Value::num("19.99"));

  const sel::Program rule = sel::compile(R"(IF(QTY * PRICE > 50.00, "over", "ok"))");
  std::cout << "rule   = " << rule.run(ctx).as_text() << "\n";
  std::cout << "exact  = " << sel::evaluate("0.10 + 0.20").as_text() << "\n";

  try {
    sel::evaluate(R"(IF(1, "a", "b"))");
  } catch (const sel::SelError& e) {
    std::cout << "error  = " << e.code() << "\n";
  }
  return 0;
}
