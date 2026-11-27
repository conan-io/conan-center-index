#include <FluentQt/FluentQt.h>

int main()
{
    if (!fluent::textfields::Label::staticMetaObject.inherits(&QLabel::staticMetaObject))
        return 1;

    return Typography::Icons::catalog().isEmpty() ? 1 : 0;
}
