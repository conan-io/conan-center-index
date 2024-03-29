#include <inspurcloud/oss/OssClient.h>
#include <list>
#include <memory>
#include <fstream>
using namespace InspurCloud::OSS;


int main(void)
{
    /*初始化OSS账号信息*/

    std::string AccessKeyId = "AccessKeyId";
    std::string AccessKeySecret = "AccessKeySecret";
    std::string Endpoint = "Endpoint";
    std::string BucketName = "bucketname";

    /*初始化网络等资源*/
    InitializeSdk();

    ClientConfiguration conf;
    OssClient client(Endpoint, AccessKeyId, AccessKeySecret, conf);

    /*指定新创建bucket的名称、存储类型和ACL*/
    CreateBucketRequest request(BucketName, StorageClass::IA, CannedAccessControlList::PublicReadWrite);
    request.SetRegion("cn-north-3");
    /*创建bucket*/
    auto outcome = client.CreateBucket(request);

    if (!outcome.isSuccess()) {
        /* 异常处理 */
        std::cout << "CreateBucket fail" <<
                  ",code:" << outcome.error().Code() <<
                  ",message:" << outcome.error().Message() <<
                  ",requestId:" << outcome.error().RequestId() << std::endl;
        ShutdownSdk();
        return 0;
    }

    /*释放网络等资源*/
    ShutdownSdk();
    return 0;
}
