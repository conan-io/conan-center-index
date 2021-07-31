
#include <h5pp/h5pp.h>
#include <iostream>

/*! \brief Prints the content of a vector nicely */
template<typename T>
std::ostream &operator<<(std::ostream &out, const std::vector<T> &v) {
    if(!v.empty()) {
        out << "[ ";
        std::copy(v.begin(), v.end(), std::ostream_iterator<T>(out, " "));
        out << "]";
    }
    return out;
}




template<typename T>
struct has_scalar2 {
    private:
    static constexpr bool test() {
        if constexpr(h5pp::type::sfinae::has_value_type_v<T>)
            return h5pp::type::sfinae::is_Scalar2_v<typename T::value_type>;
        else if constexpr(h5pp::type::sfinae::has_Scalar_v<T>)
            return h5pp::type::sfinae::is_Scalar2_v<typename T::Scalar>;
        else return false;
    }
    public:
    static constexpr bool value = test();
};
template<typename T>
inline constexpr bool has_scalar2_v = has_scalar2<T>::value;


template<typename T>
struct has_scalar3 {
    private:
    static constexpr bool test() {
        if constexpr(h5pp::type::sfinae::has_value_type_v<T>)
            return h5pp::type::sfinae::is_Scalar3_v<typename T::value_type>;
        else if constexpr(h5pp::type::sfinae::has_Scalar_v<T>)
            return h5pp::type::sfinae::is_Scalar3_v<typename T::Scalar>;
        else return false;
    }
    public:
    static constexpr bool value = test();
};
template<typename T>
inline constexpr bool has_scalar3_v = has_scalar3<T>::value;

template<typename T>
struct has_scalarN {
    private:
    static constexpr bool test() {
        return has_scalar2_v<T> or has_scalar3_v<T>;
    }
    public:
    static constexpr bool value = test();
};
template<typename T>
inline constexpr bool has_scalarN_v = has_scalarN<T>::value;


template<typename T>
void compareScalar(const T & lhs, const T & rhs){
    if constexpr(h5pp::type::sfinae::is_Scalar2_v<T>){
        if(lhs.x != rhs.x) throw std::runtime_error("lhs.x != rhs.x");
        if(lhs.y != rhs.y) throw std::runtime_error("lhs.y != rhs.y");
    }else if constexpr(h5pp::type::sfinae::is_Scalar3_v<T>){
        if(lhs.x != rhs.x) throw std::runtime_error("lhs.x != rhs.x");
        if(lhs.y != rhs.y) throw std::runtime_error("lhs.y != rhs.y");
        if(lhs.z != rhs.z) throw std::runtime_error("lhs.z != rhs.z");
    }
}


// Store some dummy data to an hdf5 file

template<typename WriteType, typename ReadType = WriteType>
void test_h5pp(h5pp::File & file, const WriteType & writeData, std::string_view dsetpath, std::string tag = ""){
    if(tag.empty()) tag = dsetpath;
    h5pp::logger::log->info("Writing {}",tag);
    file.writeDataset(writeData,dsetpath);
    h5pp::logger::log->debug("Reading {}",tag);
    auto readData = file.readDataset<ReadType>(dsetpath);
    if constexpr(h5pp::type::sfinae::is_Scalar2_v<ReadType> or h5pp::type::sfinae::is_Scalar3_v<ReadType>) {
        compareScalar(writeData,readData);
    }
    else if constexpr (has_scalarN_v<ReadType>){
        if(writeData.size()!= readData.size()) throw std::runtime_error("Size mismatch in ScalarN container");
        if constexpr(h5pp::type::sfinae::is_eigen_matrix_v<ReadType>)
            for(size_t j = 0; j < static_cast<size_t>(writeData.cols()); j++)
                for(size_t i = 0; i < static_cast<size_t>(writeData.rows()); i++) compareScalar(writeData(i,j),readData(i,j));
        else
            for(size_t i = 0; i < static_cast<size_t>(writeData.size()); i++) compareScalar(writeData[i],readData[i]);
    }
//#if defined(H5PP_EIGEN3)
    else if constexpr(h5pp::type::sfinae::is_eigen_tensor_v<WriteType> and h5pp::type::sfinae::is_eigen_tensor_v<ReadType>){
        Eigen::Map<const Eigen::Matrix<typename WriteType::Scalar, Eigen::Dynamic,1>> tensorMap(writeData.data(), writeData.size());
        Eigen::Map<const Eigen::Matrix<typename ReadType::Scalar, Eigen::Dynamic,1>> tensorMapRead(readData.data(), readData.size());
        if(tensorMap != tensorMapRead){
            if constexpr (WriteType::NumIndices == 4){
                for(int i = 0; i < writeData.dimension(0); i++)
                    for(int j = 0; j < writeData.dimension(1); j++)
                        for(int k = 0; k < writeData.dimension(2); k++) {
                            for(int l = 0; l < writeData.dimension(3); l++)
                                h5pp::print("[{} {} {} {}]: {} == {}",i,j,k,l,writeData(i, j, k, l),readData(i, j, k, l));
                            h5pp::print("\n");
                        }
            }
            if constexpr (WriteType::NumIndices == 3){
                for(int i = 0; i < writeData.dimension(0); i++)
                    for(int j = 0; j < writeData.dimension(1); j++)
                        for(int k = 0; k < writeData.dimension(2); k++) {
                                h5pp::print("[{} {} {}]: {} == {}",i,j,k,writeData(i, j, k),readData(i, j, k));
                            h5pp::print("\n");
                        }
            }
            throw std::runtime_error("tensor written != tensor read");
        }
    }
//#endif
    else{
        if(writeData != readData){
            if constexpr (h5pp::type::sfinae::is_streamable_v<WriteType> and h5pp::type::sfinae::is_streamable_v<ReadType>)
                std::cerr << "Wrote: \n" << writeData << "\n" << "Read: \n" << readData << std::endl;
            throw std::runtime_error("Data mismatch: Write != Read");

        }
    }

    h5pp::logger::log->debug("Success");
}

template<auto size, typename WriteType, typename ReadType = WriteType,typename DimsType = int>
void test_h5pp(h5pp::File & file, const WriteType * writeData, const DimsType & dims, std::string_view dsetpath, std::string tag = ""){
    if(tag.empty()) tag = dsetpath;
    h5pp::logger::log->info("Writing {}",tag);
    file.writeDataset(writeData,dsetpath,dims);
    h5pp::logger::log->debug("Reading {}",tag);
    auto * readData = new ReadType[size];
    file.readDataset(readData,dsetpath,dims);
    for(size_t i = 0; i < size; i++){
        if(writeData[i] != readData[i]){
            for(size_t j = 0; j < size; j++){
                if constexpr (h5pp::type::sfinae::is_streamable_v<WriteType> and h5pp::type::sfinae::is_streamable_v<ReadType>)
                    std::cerr << "Wrote [" << j << "]: " << writeData[j] << " | Read [" << j << "]: " << readData[j] << std::endl;
            }
            throw std::runtime_error("Data mismatch: Write != Read");
        }
    }

    delete [] readData;
    h5pp::logger::log->debug("Success");
}





int main() {
    using cplx = std::complex<double>;

    static_assert(h5pp::type::sfinae::has_data<std::vector<double>>() and
                  "Compile time type-checker failed. Could not properly detect class member data. Check that you are using a supported compiler!");

    std::string outputFilename = "test_package.h5";
    size_t      logLevel       = 2;
    h5pp::File  file(outputFilename, H5F_ACC_TRUNC | H5F_ACC_RDWR, logLevel);

    // Generate dummy data
    std::vector<int> emptyVector;
    std::string stringDummy = "Dummy string with spaces";
    std::complex<float> cplxFloat(1, 1);
    std::vector<double> vectorDouble = {1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,  0.0, 0.0, 1.0, 0.0,  0.0, 0.0, 0.0,  0.0, 1.0, 0.0, 0.0,
                                        1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0, 1.0};
    std::vector<cplx> vectorComplex = {{-0.191154, 0.326211}, {0.964728, -0.712335}, {-0.0351791, -0.10264}, {0.177544, 0.99999}};
    auto *cStyleDoubleArray = new double[10];
    for(size_t i = 0; i < 10; i++) cStyleDoubleArray[i] = static_cast<double>(i);

    struct Field2 {
        double x;
        double y;
    };
    struct Field3 {
        double x;
        double y;
        double z;
    };
    Field2 field2{0.53, 0.45};
    Field3 field3{0.54, 0.56, 0.58};
    std::vector<Field2> field2vector(10);
    for(size_t i = 0; i < field2vector.size(); i++) {
        field2vector[i].x = 2.3 * i;
        field2vector[i].y = 20.5 * i;
    }
    std::vector<Field3> field3vector(10);
    for(size_t i = 0; i < field3vector.size(); i++) {
        field3vector[i].x = 2.3 * i;
        field3vector[i].y = 20.5 * i;
        field3vector[i].z = 200.9 * i;
    }
#ifdef H5PP_EIGEN3
    Eigen::MatrixXd matrixDouble = Eigen::MatrixXd::Random(3,2);
    Eigen::Matrix<size_t, 3, 2, Eigen::RowMajor> matrixSizeTRowMajor = Eigen::Matrix<size_t, 3, 2, Eigen::RowMajor>::Random(3,2);
    Eigen::Tensor<cplx, 4> tensorComplex(2, 3, 2, 3);
    tensorComplex.setRandom();
    Eigen::Tensor<double, 3> tensorDoubleRowMajor(2, 3, 4);
    tensorDoubleRowMajor.setRandom();

    Eigen::Matrix<Field2, Eigen::Dynamic, Eigen::Dynamic> field2Matrix(10, 10);
    for(int row = 0; row < field2Matrix.rows(); row++)
        for(int col = 0; col < field2Matrix.cols(); col++) field2Matrix(row, col) = {static_cast<double>(row), static_cast<double>(col)};

    Eigen::Map<Eigen::VectorXd>                vectorMapDouble(vectorDouble.data(), (long) vectorDouble.size());
    Eigen::Map<Eigen::MatrixXd>                matrixMapDouble(matrixDouble.data(), matrixDouble.rows(), matrixDouble.cols());
    Eigen::TensorMap<Eigen::Tensor<double, 2>> tensorMapDouble(matrixDouble.data(), matrixDouble.rows(), matrixDouble.cols());
    Eigen::MatrixXd vectorMatrix = Eigen::MatrixXd::Random(10,1);
#endif


    // Test reading and writing dummy data
    test_h5pp(file,emptyVector,"emptyVector");
    test_h5pp(file,stringDummy,"stringDummy");
    test_h5pp(file,cplxFloat,"cplxFloat");
    test_h5pp(file,vectorDouble,"vectorDouble");
    test_h5pp(file,vectorComplex,"vectorComplex");
    test_h5pp<10,double>(file,cStyleDoubleArray,10,"cStyleDoubleArray");
    delete[] cStyleDoubleArray;
    test_h5pp(file,field2,"field2");
    test_h5pp(file,field3,"field3");
    test_h5pp(file,field2vector,"field2vector");
    test_h5pp(file,field3vector,"field3vector");

#ifdef H5PP_EIGEN3
    test_h5pp(file,matrixDouble,"matrixDouble");
    test_h5pp(file,matrixSizeTRowMajor,"matrixSizeTRowMajor");
    test_h5pp(file,tensorComplex,"tensorComplex");
    test_h5pp(file,tensorDoubleRowMajor,"tensorDoubleRowMajor");
    test_h5pp(file,field2Matrix,"field2Matrix");
    test_h5pp<Eigen::Map<Eigen::VectorXd>               ,Eigen::VectorXd>(file,vectorMapDouble,"vectorMapDouble");
    test_h5pp<Eigen::Map<Eigen::MatrixXd>               ,Eigen::MatrixXd>(file,matrixMapDouble,"matrixMapDouble");
    test_h5pp<Eigen::TensorMap<Eigen::Tensor<double, 2>>,Eigen::Tensor<double, 2> >(file,tensorMapDouble,"tensorMapDouble");
    test_h5pp<Eigen::MatrixXd, Eigen::VectorXd>(file,vectorMatrix,"vectorMatrix");
#endif

    auto foundLinksInRoot = file.findDatasets();
    for(auto &link : foundLinksInRoot) h5pp::logger::log->info("Found Link: {}", link);

    return 0;
}
