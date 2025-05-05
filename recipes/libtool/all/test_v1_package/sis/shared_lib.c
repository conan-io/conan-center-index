int
static_function(int);

int
shared_function(int arg) {
    return static_function(arg) + 1337;
}
