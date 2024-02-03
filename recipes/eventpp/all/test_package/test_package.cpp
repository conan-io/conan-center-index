#include <eventpp/callbacklist.h>

int main(void) {
    eventpp::CallbackList<void (const int, const bool)> callbackList;

    callbackList.append([](const int i, const bool b) {
        (void) i;
        (void) b;
    });

    callbackList(1, true);
    
    return 0;
}
