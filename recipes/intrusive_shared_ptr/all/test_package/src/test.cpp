#include <intrusive_shared_ptr/intrusive_shared_ptr.h>


struct counted { mutable int count = 1; };

struct counted_traits
{
    static void add_ref(const counted * c) noexcept { ++c->count; }

    static void sub_ref(const counted * c) noexcept { 
        if (--c->count == 0)
            delete c;
    }
};

using counted_ptr = isptr::intrusive_shared_ptr<counted, counted_traits>;


int main() {
    auto p = counted_ptr::ref(new counted);
}
