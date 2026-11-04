#include <optim.hpp>

struct ll_data_t
{
    optim::ColVec_t Y;
    optim::Mat_t X;
};

double ll_fn(const optim::ColVec_t& vals_inp, optim::ColVec_t* grad_out, void* opt_data)
{
    return 0.0;
}

int main()
{
    int n_dim = 5;
    int n_samp = 40;
    ll_data_t opt_data;
    opt_data.Y = optim::ColVec_t(n_samp);
    opt_data.X = optim::Mat_t(n_samp, n_dim);
    optim::ColVec_t x(n_samp);
    optim::algo_settings_t settings;
    bool success = optim::gd(x, ll_fn, &opt_data, settings);
}
