#include <jinja2cpp/template.h>
#include <iostream>

int main()
{
    std::string source = R"(
{{ ("Hello", 'world') | join }}!!!
{{ ("Hello", 'world') | join(', ') }}!!!
{{ ("Hello", 'world') | join(d = '; ') }}!!!
{{ ("Hello", 'world') | join(d = '; ') | lower }}!!!)";

    jinja2::Template tpl;
    tpl.Load(source);

    std::string result = tpl.RenderAsString(jinja2::ValuesMap()).value();
    std::cout << result << "\n";
}
