#include <bid_conf.h>
#include <bid_functions.h>

static constexpr auto IN {"12345678901234567"};
static constexpr auto ROUNDING {BID_ROUNDING_DOWN};
static constexpr auto EXPECTED_FLAGS {BID_INEXACT_EXCEPTION};
static constexpr BID_UINT64 EXPECTED_OUT {3595107070531779264};

static constexpr int check(BID_UINT64 out, _IDEC_flags flags) {
    if (flags != EXPECTED_FLAGS)
        return 1;
    if (out != EXPECTED_OUT)
        return 1;
    return 0;
}

#if DECIMAL_CALL_BY_REFERENCE && DECIMAL_GLOBAL_ROUNDING && DECIMAL_GLOBAL_EXCEPTION_FLAGS
int main () {
    _IDEC_glbround = ROUNDING;
    BID_UINT64 out{};
    bid64_from_string(&out, const_cast<char *>(IN));
    return check(out, _IDEC_glbflags);
}
#endif

#if DECIMAL_CALL_BY_REFERENCE && DECIMAL_GLOBAL_ROUNDING && !DECIMAL_GLOBAL_EXCEPTION_FLAGS
int main () {
    _IDEC_glbround = ROUNDING;
    _IDEC_flags flags{};
    BID_UINT64 out{};
    bid64_from_string(&out, const_cast<char *>(IN), &flags);
    return check(out, flags);
}
#endif

#if DECIMAL_CALL_BY_REFERENCE && !DECIMAL_GLOBAL_ROUNDING && DECIMAL_GLOBAL_EXCEPTION_FLAGS
int main () {
    _IDEC_round round{ROUNDING};
    BID_UINT64 out{};
    bid64_from_string(&out, const_cast<char *>(IN), &round);
    return check(out, _IDEC_glbflags);
}
#endif

#if DECIMAL_CALL_BY_REFERENCE && !DECIMAL_GLOBAL_ROUNDING && !DECIMAL_GLOBAL_EXCEPTION_FLAGS
int main () {
    _IDEC_round round{ROUNDING};
    _IDEC_flags flags{};
    BID_UINT64 out{};
    bid64_from_string(&out, const_cast<char *>(IN), &round, &flags);
    return check(out, flags);
}
#endif

#if !DECIMAL_CALL_BY_REFERENCE && DECIMAL_GLOBAL_ROUNDING && DECIMAL_GLOBAL_EXCEPTION_FLAGS
int main() {
    _IDEC_glbround = ROUNDING;
    BID_UINT64 out = bid64_from_string(const_cast<char *>(IN));
    return check(out, _IDEC_glbflags);
}
#endif

#if !DECIMAL_CALL_BY_REFERENCE && DECIMAL_GLOBAL_ROUNDING && !DECIMAL_GLOBAL_EXCEPTION_FLAGS
int main() {
    _IDEC_glbround = ROUNDING;
    _IDEC_flags flags{};
    BID_UINT64 out = bid64_from_string(const_cast<char *>(IN), &flags);
    return check(out, flags);
}
#endif

#if !DECIMAL_CALL_BY_REFERENCE && !DECIMAL_GLOBAL_ROUNDING && DECIMAL_GLOBAL_EXCEPTION_FLAGS
int main() {
    _IDEC_round round{ROUNDING};
    BID_UINT64 out = bid64_from_string(const_cast<char *>(IN), round);
    return check(out, _IDEC_glbflags);
}
#endif

#if !DECIMAL_CALL_BY_REFERENCE && !DECIMAL_GLOBAL_ROUNDING && !DECIMAL_GLOBAL_EXCEPTION_FLAGS
int main() {
    _IDEC_round round{ROUNDING};
    _IDEC_flags flags{};
    BID_UINT64 out = bid64_from_string(const_cast<char *>(IN), round, &flags);
    return check(out, flags);
}
#endif
