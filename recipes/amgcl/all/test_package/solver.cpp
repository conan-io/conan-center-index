#include <iostream>
#include <string>
#include <random>

#include <boost/program_options.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/range/iterator_range.hpp>
#include <boost/preprocessor/seq/for_each.hpp>


#if defined(SOLVER_BACKEND_VEXCL)
#  include <amgcl/value_type/static_matrix.hpp>
#  include <amgcl/adapter/block_matrix.hpp>
#  include <amgcl/backend/vexcl.hpp>
#  include <amgcl/backend/vexcl_static_matrix.hpp>
   typedef amgcl::backend::vexcl<double> Backend;
#elif defined(SOLVER_BACKEND_VIENNACL)
#  include <amgcl/backend/viennacl.hpp>
   typedef amgcl::backend::viennacl< viennacl::compressed_matrix<double> > Backend;
#elif defined(SOLVER_BACKEND_CUDA)
#  include <amgcl/backend/cuda.hpp>
#  include <amgcl/relaxation/cusparse_ilu0.hpp>
   typedef amgcl::backend::cuda<double> Backend;
#elif defined(SOLVER_BACKEND_EIGEN)
#  include <amgcl/backend/eigen.hpp>
   typedef amgcl::backend::eigen<double> Backend;
#elif defined(SOLVER_BACKEND_BLAZE)
#  include <amgcl/backend/blaze.hpp>
   typedef amgcl::backend::blaze<double> Backend;
#else
#  ifndef SOLVER_BACKEND_BUILTIN
#    define SOLVER_BACKEND_BUILTIN
#  endif
#  include <amgcl/backend/builtin.hpp>
#  include <amgcl/value_type/static_matrix.hpp>
#  include <amgcl/adapter/block_matrix.hpp>
   typedef amgcl::backend::builtin<double> Backend;
#endif

#include <amgcl/relaxation/runtime.hpp>
#include <amgcl/coarsening/runtime.hpp>
#include <amgcl/coarsening/rigid_body_modes.hpp>
#include <amgcl/solver/runtime.hpp>
#include <amgcl/preconditioner/runtime.hpp>
#include <amgcl/make_solver.hpp>
#include <amgcl/amg.hpp>
#include <amgcl/adapter/crs_tuple.hpp>
#include <amgcl/adapter/reorder.hpp>
#include <amgcl/io/mm.hpp>
#include <amgcl/io/binary.hpp>

#include <amgcl/profiler.hpp>

#include "sample_problem.hpp"

#ifndef AMGCL_BLOCK_SIZES
#  define AMGCL_BLOCK_SIZES (3)(4)
#endif

namespace amgcl { profiler<> prof; }
using amgcl::prof;
using amgcl::precondition;

#ifdef SOLVER_BACKEND_BUILTIN
//---------------------------------------------------------------------------
template <int B>
std::tuple<size_t, double> block_solve(
        const boost::property_tree::ptree &prm,
        size_t rows,
        std::vector<ptrdiff_t> const &ptr,
        std::vector<ptrdiff_t> const &col,
        std::vector<double>    const &val,
        std::vector<double>    const &rhs,
        std::vector<double>          &x,
        bool reorder
        )
{
    typedef amgcl::static_matrix<double, B, B> value_type;
    typedef amgcl::static_matrix<double, B, 1> rhs_type;
    typedef amgcl::backend::builtin<value_type> BBackend;

    typedef amgcl::make_solver<
        amgcl::runtime::preconditioner<BBackend>,
        amgcl::runtime::solver::wrapper<BBackend>
        > Solver;

    auto As = std::tie(rows, ptr, col, val);
    auto Ab = amgcl::adapter::block_matrix<value_type>(As);

    std::tuple<size_t, double> info;

    if (reorder) {
        prof.tic("reorder");
        amgcl::adapter::reorder<> perm(Ab);
        prof.toc("reorder");

        prof.tic("setup");
        Solver solve(perm(Ab), prm);
        prof.toc("setup");

        std::cout << solve << std::endl;

        rhs_type const * fptr = reinterpret_cast<rhs_type const *>(&rhs[0]);
        rhs_type       * xptr = reinterpret_cast<rhs_type       *>(&x[0]);

        amgcl::backend::numa_vector<rhs_type> F(perm(amgcl::make_iterator_range(fptr, fptr + rows/B)));
        amgcl::backend::numa_vector<rhs_type> X(perm(amgcl::make_iterator_range(xptr, xptr + rows/B)));

        prof.tic("solve");
        info = solve(F, X);
        prof.toc("solve");

        perm.inverse(X, xptr);
    } else {
        prof.tic("setup");
        Solver solve(Ab, prm);
        prof.toc("setup");

        std::cout << solve << std::endl;

        rhs_type const * fptr = reinterpret_cast<rhs_type const *>(&rhs[0]);
        rhs_type       * xptr = reinterpret_cast<rhs_type       *>(&x[0]);

        amgcl::backend::numa_vector<rhs_type> F(fptr, fptr + rows/B);
        amgcl::backend::numa_vector<rhs_type> X(xptr, xptr + rows/B);

        prof.tic("solve");
        info = solve(F, X);
        prof.toc("solve");

        std::copy(X.data(), X.data() + X.size(), xptr);
    }

    return info;
}
#endif

#ifdef SOLVER_BACKEND_VEXCL
//---------------------------------------------------------------------------
template <int B>
std::tuple<size_t, double> block_solve(
        const boost::property_tree::ptree &prm,
        size_t rows,
        std::vector<ptrdiff_t> const &ptr,
        std::vector<ptrdiff_t> const &col,
        std::vector<double>    const &val,
        std::vector<double>    const &rhs,
        std::vector<double>          &x,
        bool reorder
        )
{
    typedef amgcl::static_matrix<double, B, B> value_type;
    typedef amgcl::static_matrix<double, B, 1> rhs_type;
    typedef amgcl::backend::vexcl<value_type> BBackend;

    typedef amgcl::make_solver<
        amgcl::runtime::preconditioner<BBackend>,
        amgcl::runtime::solver::wrapper<BBackend>
        > Solver;

    typename BBackend::params bprm;

    vex::Context ctx(vex::Filter::Env);
    std::cout << ctx << std::endl;
    bprm.q = ctx;
    bprm.fast_matrix_setup = prm.get("fast", true);

    vex::scoped_program_header header(ctx,
            amgcl::backend::vexcl_static_matrix_declaration<double,B>());

    auto As = std::tie(rows, ptr, col, val);
    auto Ab = amgcl::adapter::block_matrix<value_type>(As);

    std::tuple<size_t, double> info;

    if (reorder) {
        prof.tic("reorder");
        amgcl::adapter::reorder<> perm(Ab);
        prof.toc("reorder");

        prof.tic("setup");
        Solver solve(perm(Ab), prm, bprm);
        prof.toc("setup");

        std::cout << solve << std::endl;

        rhs_type const * fptr = reinterpret_cast<rhs_type const *>(&rhs[0]);
        rhs_type       * xptr = reinterpret_cast<rhs_type       *>(&x[0]);

        std::vector<rhs_type> tmp(rows / B);

        perm.forward(amgcl::make_iterator_range(fptr, fptr + rows/B), tmp);
        vex::vector<rhs_type> f_b(ctx, tmp);

        perm.forward(amgcl::make_iterator_range(xptr, xptr + rows/B), tmp);
        vex::vector<rhs_type> x_b(ctx, tmp);

        prof.tic("solve");
        info = solve(f_b, x_b);
        prof.toc("solve");

        vex::copy(x_b, tmp);
        perm.inverse(tmp, xptr);
    } else {
        prof.tic("setup");
        Solver solve(Ab, prm, bprm);
        prof.toc("setup");

        std::cout << solve << std::endl;

        rhs_type const * fptr = reinterpret_cast<rhs_type const *>(&rhs[0]);
        rhs_type       * xptr = reinterpret_cast<rhs_type       *>(&x[0]);

        vex::vector<rhs_type> f_b(ctx, rows/B, fptr);
        vex::vector<rhs_type> x_b(ctx, rows/B, xptr);

        prof.tic("solve");
        info = solve(f_b, x_b);
        prof.toc("solve");

        vex::copy(x_b.begin(), x_b.end(), xptr);
    }

    return info;
}
#endif

//---------------------------------------------------------------------------
std::tuple<size_t, double> scalar_solve(
        const boost::property_tree::ptree &prm,
        size_t rows,
        std::vector<ptrdiff_t> const &ptr,
        std::vector<ptrdiff_t> const &col,
        std::vector<double>    const &val,
        std::vector<double>    const &rhs,
        std::vector<double>          &x,
        bool reorder
        )
{
    Backend::params bprm;

#if defined(SOLVER_BACKEND_VEXCL)
    vex::Context ctx(vex::Filter::Env);
    std::cout << ctx << std::endl;
    bprm.q = ctx;
#elif defined(SOLVER_BACKEND_VIENNACL)
    std::cout
        << viennacl::ocl::current_device().name()
        << " (" << viennacl::ocl::current_device().vendor() << ")\n\n";
#elif defined(SOLVER_BACKEND_CUDA)
    cusparseCreate(&bprm.cusparse_handle);
    {
        int dev;
        cudaGetDevice(&dev);

        cudaDeviceProp prop;
        cudaGetDeviceProperties(&prop, dev);
        std::cout << prop.name << std::endl << std::endl;
    }
#endif

    typedef amgcl::make_solver<
        amgcl::runtime::preconditioner<Backend>,
        amgcl::runtime::solver::wrapper<Backend>
        > Solver;

    std::tuple<size_t, double> info;

    if (reorder) {
        prof.tic("reorder");
        amgcl::adapter::reorder<> perm(std::tie(rows, ptr, col, val));
        prof.toc("reorder");

        prof.tic("setup");
        Solver solve(perm(std::tie(rows, ptr, col, val)), prm, bprm);
        prof.toc("setup");

        std::cout << solve << std::endl;

        std::vector<double> tmp(rows);

        perm.forward(rhs, tmp);
        auto f_b = Backend::copy_vector(tmp, bprm);

        perm.forward(x, tmp);
        auto x_b = Backend::copy_vector(tmp, bprm);

        prof.tic("solve");
        info = solve(*f_b, *x_b);
        prof.toc("solve");

#if defined(SOLVER_BACKEND_VEXCL)
        vex::copy(*x_b, tmp);
#elif defined(SOLVER_BACKEND_VIENNACL)
        viennacl::fast_copy(*x_b, tmp);
#elif defined(SOLVER_BACKEND_CUDA)
        thrust::copy(x_b->begin(), x_b->end(), tmp.begin());
#else
        std::copy(&(*x_b)[0], &(*x_b)[0] + rows, &tmp[0]);
#endif

        perm.inverse(tmp, x);
    } else {
        prof.tic("setup");
        Solver solve(std::tie(rows, ptr, col, val), prm, bprm);
        prof.toc("setup");

        std::cout << solve << std::endl;

        auto f_b = Backend::copy_vector(rhs, bprm);
        auto x_b = Backend::copy_vector(x,   bprm);

        prof.tic("solve");
        info = solve(*f_b, *x_b);
        prof.toc("solve");

#if defined(SOLVER_BACKEND_VEXCL)
        vex::copy(*x_b, x);
#elif defined(SOLVER_BACKEND_VIENNACL)
        viennacl::fast_copy(*x_b, x);
#elif defined(SOLVER_BACKEND_CUDA)
        thrust::copy(x_b->begin(), x_b->end(), x.begin());
#else
        std::copy(&(*x_b)[0], &(*x_b)[0] + rows, &x[0]);
#endif
    }

    return info;
}

#define AMGCL_CALL_BLOCK_SOLVER(z, data, B)                                    \
  case B:                                                                      \
    return block_solve<B>(prm, rows, ptr, col, val, rhs, x, reorder);

//---------------------------------------------------------------------------
std::tuple<size_t, double> solve(
        const boost::property_tree::ptree &prm,
        size_t rows,
        std::vector<ptrdiff_t> const &ptr,
        std::vector<ptrdiff_t> const &col,
        std::vector<double>    const &val,
        std::vector<double>    const &rhs,
        std::vector<double>          &x,
        int block_size,
        bool reorder
        )
{
    switch (block_size) {
        case 1:
            return scalar_solve(prm, rows, ptr, col, val, rhs, x, reorder);
#if defined(SOLVER_BACKEND_BUILTIN) || defined(SOLVER_BACKEND_VEXCL)
        BOOST_PP_SEQ_FOR_EACH(AMGCL_CALL_BLOCK_SOLVER, ~, AMGCL_BLOCK_SIZES)
#endif
        default:
            precondition(false, "Unsupported block size");
            return std::make_tuple(0, 0.0);
    }
}

//---------------------------------------------------------------------------
int main(int argc, char *argv[]) {
    namespace po = boost::program_options;
    namespace io = amgcl::io;

    using amgcl::prof;
    using std::vector;
    using std::string;

    po::options_description desc("Options");

    desc.add_options()
        ("help,h", "Show this help.")
        ("prm-file,P",
         po::value<string>(),
         "Parameter file in json format. "
        )
        (
         "prm,p",
         po::value< vector<string> >()->multitoken(),
         "Parameters specified as name=value pairs. "
         "May be provided multiple times. Examples:\n"
         "  -p solver.tol=1e-3\n"
         "  -p precond.coarse_enough=300"
        )
        ("matrix,A",
         po::value<string>(),
         "System matrix in the MatrixMarket format. "
         "When not specified, solves a Poisson problem in 3D unit cube. "
        )
        (
         "rhs,f",
         po::value<string>(),
         "The RHS vector in the MatrixMarket format. "
         "When omitted, a vector of ones is used by default. "
         "Should only be provided together with a system matrix. "
        )
        (
         "f0",
         po::bool_switch()->default_value(false),
         "Use zero RHS vector. Implies --random-initial and solver.ns_search=true"
        )
        (
         "f1",
         po::bool_switch()->default_value(false),
         "Set RHS = Ax where x = 1"
        )
        (
         "null,N",
         po::value<string>(),
         "The near null-space vectors in the MatrixMarket format. "
         "Should be a dense matrix of size N*M, where N is the number of "
         "unknowns, and M is the number of null-space vectors. "
         "Should only be provided together with a system matrix. "
        )
        (
         "coords,C",
         po::value<string>(),
         "Coordinate matrix where number of rows corresponds to the number of grid nodes "
         "and the number of columns corresponds to the problem dimensionality (2 or 3). "
         "Will be used to construct near null-space vectors as rigid body modes. "
         "Should only be provided together with a system matrix. "
        )
        (
         "binary,B",
         po::bool_switch()->default_value(false),
         "When specified, treat input files as binary instead of as MatrixMarket. "
         "It is assumed the files were converted to binary format with mm2bin utility. "
        )
        (
         "scale,s",
         po::bool_switch()->default_value(false),
         "Scale the matrix so that the diagonal is unit. "
        )
        (
         "block-size,b",
         po::value<int>()->default_value(1),
         "The block size of the system matrix. "
         "When specified, the system matrix is assumed to have block-wise structure. "
         "This usually is the case for problems in elasticity, structural mechanics, "
         "for coupled systems of PDE (such as Navier-Stokes equations), etc. "
        )
        (
         "size,n",
         po::value<int>()->default_value(32),
         "The size of the Poisson problem to solve when no system matrix is given. "
         "Specified as number of grid nodes along each dimension of a unit cube. "
         "The resulting system will have n*n*n unknowns. "
        )
        (
         "anisotropy,a",
         po::value<double>()->default_value(1.0),
         "The anisotropy value for the generated Poisson value. "
         "Used to determine problem scaling along X, Y, and Z axes: "
         "hy = hx * a, hz = hy * a."
        )
        (
         "single-level,1",
         po::bool_switch()->default_value(false),
         "When specified, the AMG hierarchy is not constructed. "
         "Instead, the problem is solved using a single-level smoother as preconditioner. "
        )
        (
         "reorder,r",
         po::bool_switch()->default_value(false),
         "When specified, the matrix will be reordered to improve cache-locality"
        )
        (
         "initial,x",
         po::value<double>()->default_value(0),
         "Value to use as initial approximation. "
        )
        (
         "random-initial",
         po::bool_switch()->default_value(false),
         "Use random initial approximation. "
        )
        (
         "output,o",
         po::value<string>(),
         "Output file. Will be saved in the MatrixMarket format. "
         "When omitted, the solution is not saved. "
        )
        ;

    po::positional_options_description p;
    p.add("prm", -1);

    po::variables_map vm;
    po::store(po::command_line_parser(argc, argv).options(desc).positional(p).run(), vm);
    po::notify(vm);

    if (vm.count("help")) {
        std::cout << desc << std::endl;
        return 0;
    }

    for (int i = 0; i < argc; ++i) {
        if (i) std::cout << " ";
        std::cout << argv[i];
    }
    std::cout << std::endl;

    boost::property_tree::ptree prm;
    if (vm.count("prm-file")) {
        read_json(vm["prm-file"].as<string>(), prm);
    }

    if (vm.count("prm")) {
        for(const string &v : vm["prm"].as<vector<string> >()) {
            amgcl::put(prm, v);
        }
    }

    size_t rows, nv = 0;
    vector<ptrdiff_t> ptr, col;
    vector<double> val, rhs, null, x;

    if (vm.count("matrix")) {
        auto t = prof.scoped_tic("reading");

        string Afile  = vm["matrix"].as<string>();
        bool   binary = vm["binary"].as<bool>();

        if (binary) {
            io::read_crs(Afile, rows, ptr, col, val);
        } else {
            size_t cols;
            std::tie(rows, cols) = io::mm_reader(Afile)(ptr, col, val);
            precondition(rows == cols, "Non-square system matrix");
        }

        if (vm.count("rhs")) {
            string bfile = vm["rhs"].as<string>();

            size_t n, m;

            if (binary) {
                io::read_dense(bfile, n, m, rhs);
            } else {
                std::tie(n, m) = io::mm_reader(bfile)(rhs);
            }

            precondition(n == rows && m == 1, "The RHS vector has wrong size");
        } else if (vm["f1"].as<bool>()) {
            rhs.resize(rows);
            for(size_t i = 0; i < rows; ++i) {
                double s = 0;
                for(ptrdiff_t j = ptr[i], e = ptr[i+1]; j < e; ++j)
                    s += val[j];
                rhs[i] = s;
            }
        } else {
            rhs.resize(rows, vm["f0"].as<bool>() ? 0.0 : 1.0);
        }

        if (vm.count("null")) {
            string nfile = vm["null"].as<string>();

            size_t m;

            if (binary) {
                io::read_dense(nfile, m, nv, null);
            } else {
                std::tie(m, nv) = io::mm_reader(nfile)(null);
            }

            precondition(m == rows, "Near null-space vectors have wrong size");
        } else if (vm.count("coords")) {
            string cfile = vm["coords"].as<string>();
            std::vector<double> coo;

            size_t m, ndim;

            if (binary) {
                io::read_dense(cfile, m, ndim, coo);
            } else {
                std::tie(m, ndim) = io::mm_reader(cfile)(coo);
            }

            precondition(m * ndim == rows && (ndim == 2 || ndim == 3), "Coordinate matrix has wrong size");

            nv = amgcl::coarsening::rigid_body_modes(ndim, coo, null);
        }

        if (nv) {
            prm.put("precond.coarsening.nullspace.cols", nv);
            prm.put("precond.coarsening.nullspace.rows", rows);
            prm.put("precond.coarsening.nullspace.B",    &null[0]);
        }
    } else {
        auto t = prof.scoped_tic("assembling");
        rows = sample_problem(vm["size"].as<int>(), val, col, ptr, rhs, vm["anisotropy"].as<double>());
    }

    if (vm["scale"].as<bool>()) {
        std::vector<double> dia(rows, 1.0);

        for (ptrdiff_t i = 0; i < static_cast<ptrdiff_t>(rows); ++i) {
            double d = 1.0;
            for(ptrdiff_t j = ptr[i], e = ptr[i+1]; j < e; ++j) {
                if (col[j] == i) {
                    d = 1 / sqrt(val[j]);
                }
            }
            if (!std::isnan(d)) dia[i] = d;
        }

        for (ptrdiff_t i = 0; i < static_cast<ptrdiff_t>(rows); ++i) {
            rhs[i] *= dia[i];
            for(ptrdiff_t j = ptr[i], e = ptr[i+1]; j < e; ++j) {
                val[j] *= dia[i] * dia[col[j]];
            }
        }
    }

    x.resize(rows, vm["initial"].as<double>());
    if (vm["random-initial"].as<bool>() || vm["f0"].as<bool>()) {
        std::mt19937 rng;
        std::uniform_real_distribution<double> rnd(-1, 1);
        for(auto &v : x) v = rnd(rng);
    }

    if (vm["f0"].as<bool>()) {
        prm.put("solver.ns_search", true);
    }

    size_t iters;
    double error;

    int block_size = vm["block-size"].as<int>();

    if (vm["single-level"].as<bool>())
        prm.put("precond.class", "relaxation");

    std::tie(iters, error) = solve(
            prm, rows, ptr, col, val, rhs, x,
            block_size, vm["reorder"].as<bool>());

    if (vm.count("output")) {
        auto t = prof.scoped_tic("write");
        amgcl::io::mm_write(vm["output"].as<string>(), &x[0], x.size());
    }

    std::cout << "Iterations: " << iters << std::endl
              << "Error:      " << error << std::endl
              << prof << std::endl;
}
