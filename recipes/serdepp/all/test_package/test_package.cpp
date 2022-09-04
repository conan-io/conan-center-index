#include <iostream>
#include <sstream>
#include <serdepp/serializer.hpp>
#include <serdepp/adaptor/sstream.hpp>
class test {
public:
    template<class Context>
    constexpr static void serde(Context& context, test& value) {
        using Self = test;
        serde::serde_struct(context, value)
            (&Self::str, "str")  // or .field(&Self::str, "str")
            (&Self::i,   "i")    // or .field(&Self::i , "i")
            (&Self::vec, "vec"); // or .field(&Self::vec, "vec")
    }
private:
    std::string str;
    int i;
    std::vector<std::string> vec;
};

int main()
{
    test t;
}
