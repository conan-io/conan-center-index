#include <memory>
#include <OpenHome/Net/Core/OhNet.h>
#include <OpenHome/Av/KvpStore.h>

using namespace OpenHome;
using namespace OpenHome::Av;

class RamStore : public IStaticDataSource
{
public:
    RamStore(const Brx& aImageFileName);
    virtual ~RamStore();
private: // from IStaticDataSource
    void LoadStaticData(IStoreLoaderStatic& aLoader) override;
private:
    Brhz iImageFileName;
};

RamStore::RamStore(const Brx& aImageFileName)
    : iImageFileName(aImageFileName)
{
}

RamStore::~RamStore() {}

void RamStore::LoadStaticData(IStoreLoaderStatic& aLoader)
{
    aLoader.AddStaticItem(StaticDataKey::kBufManufacturerName, "OpenHome");
    aLoader.AddStaticItem(StaticDataKey::kBufManufacturerInfo, "insert oh info here...");
    aLoader.AddStaticItem(StaticDataKey::kBufManufacturerUrl, "http://www.openhome.org");
    aLoader.AddStaticItem(StaticDataKey::kBufManufacturerImageUrl, "http://wiki.openhome.org/mediawiki/skins/openhome/images/logo.png");
    aLoader.AddStaticItem(StaticDataKey::kBufModelName, "OpenHome Media Player (test)");
    aLoader.AddStaticItem(StaticDataKey::kBufModelInfo, "Test implementation of ohMediaPlayer");
    aLoader.AddStaticItem(StaticDataKey::kBufModelUrl, "http://wiki.openhome.org/wiki/OhMedia");
    aLoader.AddStaticItem(StaticDataKey::kBufModelImageUrl, iImageFileName.CString());
}

int main()
{
    RamStore* ramStore = new RamStore(Brx::Empty());

    delete ramStore;
}
