#include <memory>
#include <OpenHome/Private/Standard.h>
#include <OpenHome/Buffer.h>
#include <OpenHome/Private/TestFramework.h>
#include <OpenHome/Private/Arch.h>

#include <string>
#include <map>

using namespace OpenHome;
using namespace OpenHome::TestFramework;

class SuiteConstruction : public Suite
{
public:
    SuiteConstruction() : Suite("Buffer Construction Tests") {}
    void Test();
};

void SuiteConstruction::Test()
{
    //1) Create a Brn to a TChar*

    const TChar* str = "MyString";
    Brn ptr1(str);
    TEST(ptr1.Bytes() == strlen(str));

    Brn ptr2(str);
    TEST(ptr2.Bytes() == strlen(str));
    TEST(ptr1 == ptr2);

    //2) Create a stack based Bws
    Bws<10> buf1;
    TEST(buf1 != ptr1);
    TEST(buf1.Bytes() == 0);
    TEST(buf1.MaxBytes() == 10);

    //3) make buf1 equal a replica of str
    buf1.Replace("MyString");
    TEST(buf1.Bytes() == 8);
    TEST(buf1.MaxBytes() == 10);
    //4) ensure that the original and replica are equal
    TEST(ptr1 == buf1);
    TEST(ptr2 == buf1);

    //5) Create another Bws but set it up to copy from the original ptr1
    Bws<11> buf2(5);
    TEST(buf2.Bytes() == 5);
    TEST(buf2.MaxBytes() == 11);
    buf2.Replace(ptr1);
    TEST(ptr1 == buf2);
    TEST(ptr2 == buf2);
    TEST(buf1 == buf2);

    //6) Create a heap based Bws
    Bws<8>* buf3 = new Bws<8>(3);
    TEST(buf3->Bytes() == 3);
    TEST(buf3->MaxBytes() == 8);
    buf3->Replace(ptr2);
    TEST(ptr1 == *buf3);
    TEST(ptr2 == *buf3);
    TEST(buf1 == *buf3);
    TEST(buf2 == *buf3);

    delete buf3;

    //7) Exception test
    //The (void)buf4 just gets rid of compile warning about unused variable
    TEST_THROWS(Bws<4> buf4(5); (void)buf4, AssertionFailed);

    Bws<4> buf5(4);
    TEST(buf5.Bytes() == 4);
    TEST_THROWS(buf5.SetBytes(5), AssertionFailed);
    buf5.SetBytes(0);
    TEST(buf5.Bytes() == 0);

    //8> BytesRemaining()
    Bws<8> buf6;
    TEST(buf6.BytesRemaining() == 8);
    buf6.SetBytes(3);
    TEST(buf6.BytesRemaining() == 5);
    buf6.SetBytes(8);
    TEST(buf6.BytesRemaining() == 0);
}

class SuiteModification : public Suite
{
public:
    SuiteModification() : Suite("Buffer Modification Tests") {}
    void Test();
};

void SuiteModification::Test()
{
    Bws<8> buf1;
    TEST(buf1.Bytes() == 0);
    TEST(buf1.MaxBytes() == 8);
    TEST_THROWS(buf1.SetBytes(9), AssertionFailed);
    TEST(buf1.Bytes() == 0);
    TEST(buf1.MaxBytes() == 8);
    buf1.SetBytes(4);
    TEST(buf1.Bytes() == 4);
    TEST(buf1.MaxBytes() == 8);
    buf1.SetBytes(8);
    TEST(buf1.Bytes() == 8);
    TEST(buf1.MaxBytes() == 8);

    Bws<12> buf2;
    TEST(buf2.Bytes() == 0);
    TEST(buf2.MaxBytes() == 12);

    //Compare two empty buffers
    buf1.SetBytes(0);
    TEST(buf1 == buf2);
    TEST(!(buf1 != buf2));

    buf1.Replace("AString");
    TEST(buf1.Bytes() == 7);
    buf1.SetBytes(0);
    TEST(buf1.Bytes() == 0);

    TEST(buf1 == buf2);

    //Append a char
    buf1.SetBytes(7);
    TEST(buf1.Bytes() == 7);
    buf1.Append('1');
    TEST(buf1.Bytes() == 8);

    TEST_THROWS(buf1.Append('2'), AssertionFailed);
    TEST(buf1.Bytes() == 8);
    TEST(!buf1.TryAppend('2'));
    buf1.SetBytes(7);
    TEST(buf1.TryAppend('1'));

    //Append a TChar*
    buf1.SetBytes(0);
    buf1.Append("B");
    TEST(buf1.Bytes() == 1);
    buf1.SetBytes(7);
    buf2.Replace("BString");
    TEST(buf1 == buf2);
    buf2.Append('1');
    buf1.SetBytes(8);
    TEST(buf1 == buf2); //Bwstring1 == Bwstring1
    TEST(!buf1.TryAppend("2"));
    buf1.SetBytes(7);
    TEST(buf1.TryAppend("2"));


    //Append a B
    buf1.SetBytes(0);
    buf1.Append("Another");
    buf2.SetBytes(0);
    buf2.Append(buf1);
    TEST(buf1 == buf2);
    TEST(buf1.Bytes() == 7);
    TEST(buf2.Bytes() == 7);
    buf2.SetBytes(0);
    TEST(buf2.TryAppend(buf1));
    buf2.SetBytes(6);
    TEST(!buf2.TryAppend(buf1));


    //Append a TByte*
    buf1.SetBytes(0);
    TByte byte[10] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
    buf1.Append(byte, 8);
    TEST(buf1.Bytes() == 8);
    TEST(buf1.MaxBytes() == 8);
    TEST_THROWS(buf1.Append(byte, 8), AssertionFailed);
    TEST(memcmp(buf1.Ptr(), byte, 8)==0);

    buf2.SetBytes(0);
    buf2.Append(byte, 8);
    TEST(buf2.Bytes() == 8);
    TEST(buf2.MaxBytes() == 12);
    TEST(buf1 == buf2);
    TEST(!buf1.TryAppend(byte, 8));
    buf1.SetBytes(0);
    TEST(buf1.TryAppend(byte, 8));

    //Filling
    buf1.SetBytes(5);
    buf1.Fill(0xde);
    TEST(buf1.Bytes() == 5);
    TByte byte1[5] = {0xde, 0xde, 0xde, 0xde, 0xde};
    buf2.Replace(byte1, 5);
    TEST(buf1 == buf2);

    TByte byte2[12] = {0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0};
    buf1.FillZ();
    TEST(buf1.Bytes() == 5);
    buf2.Replace(byte2,5);
    TEST(buf1 == buf2);
    TEST(buf2.Bytes() == 5);
}

class SuiteElements : public Suite
{
public:
    SuiteElements() : Suite("Buffer Element Access Tests") {}
    void Test();
};

void SuiteElements::Test()
{
    //1) element access on constant buffers
    const TChar* str = "FirstString";
    Brn bptr(str);
    TEST(bptr.Bytes() == 11);

    TEST(bptr[0] == 'F');
    TEST(bptr[0] == bptr.At(0));
    TEST(bptr[1] == 'i');
    TEST(bptr[1] == bptr.At(1));
    TEST(bptr[10] == 'g');
    TEST(bptr[10] == bptr.At(10));
    TEST_THROWS(bptr[11], AssertionFailed);
    TEST_THROWS(bptr.At(11), AssertionFailed);

    //2) element access on modifable buffers
    Bws<15> buf("AnotherString");
    TEST(buf.Bytes() == 13);
    TEST(buf[0] == 'A');
    TEST(buf[1] == 'n');
    TEST(buf[11] == 'n');
    TEST(buf[12] == 'g');
    TEST_THROWS(buf[13], AssertionFailed);
    TEST_THROWS(buf[14], AssertionFailed);
    TEST_THROWS(buf[15], AssertionFailed);
    TEST_THROWS(buf[16], AssertionFailed);

    buf[0] = 'B';
    TEST(buf[0] == 'B');

    buf[1] = 0x99;
    TEST(buf[1] == 0x99);

    TEST_THROWS(buf[13] = 0x90, AssertionFailed);

    //3) access elements of a const Bwx

    const Bws<16> b("something");
    TEST(b.At(0) == 's');
    TEST(b[0] == 's');
}

class SuiteHeap : public Suite
{
public:
    SuiteHeap() : Suite("Buffer tests for Bwh"){}
    void Test();
};

void SuiteHeap::Test()
{
    {
    Bwh buf(10);
    TEST(buf.Bytes() == 0);
    TEST(buf.MaxBytes() == 10);
    buf.Replace("MyString1");
    TEST(buf.Bytes() == 9);
    Bws<10> buf1("MyString1");
    TEST(buf == buf1);
    }

    {
    Bwh buf(10, 20);
    TEST(buf.Bytes() == 10);
    TEST(buf.MaxBytes() == 20);
    }

    //TChar* constructor
    {
    Bwh buf("MyStringLonger");
    TEST(buf.Bytes() == 14);
    TEST(buf.MaxBytes() == 14);
    TEST(memcmp(buf.Ptr(), "MyStringLonger", buf.Bytes())==0);
    }

    //TByte* constructor
    {
    TByte byte[6] = {0xa,0xb,0xc,0xd,0xe,0xf};
    Bwh buf(byte, 6);
    TEST(buf.Bytes() == 6);
    TEST(buf.MaxBytes() == 6);
    TEST(memcmp(buf.Ptr(), byte, buf.Bytes()) == 0);
    }

    //Replace Constructors
    {
    //Replace from const BC&
    Bws<11> buf("MyStaticBuf");
    TEST(buf.Bytes() == 11);
    TEST(buf.MaxBytes() == 11);
    Bwh buf1(buf);
    TEST(buf1 == buf);
    //ensure we preformed a deep copy.
    TEST(buf1.Ptr() != buf.Ptr());

    //Replace from const Bwh&
    Bwh buf2(buf1);
    TEST(buf1 == buf);
    //ensure we preformed a deep copy.
    TEST(buf1.Ptr() != buf.Ptr());
    }

    {
    Bwh buf("My stack string to heap string");
    TEST(buf.Bytes() == 30);
    TEST(buf.MaxBytes() == 30);
    TEST(memcmp(buf.Ptr(), "My stack string to heap string", buf.Bytes())==0);
    }

    {
    Bws<10> buf("String");
    Bwh heap(buf);
    TEST(heap.Bytes() == 6);
    TEST(heap.MaxBytes() == 6);
    TEST(buf == heap);
    TEST(buf.Ptr() != heap.Ptr());
    }

    {
    Bwh first("First");
    Bwh second(first);
    TEST(second.Bytes() == 5);
    TEST(second.MaxBytes() == 5);
    TEST(first == second);
    TEST(first.Ptr() != second.Ptr());

    Bwh another("Another");
    TEST_THROWS(second.Replace(another), AssertionFailed);
    TEST(second.Bytes() == 5);
    TEST(second.MaxBytes() == 5);
    TEST(another.Bytes() == 7);
    TEST(another.MaxBytes() == 7);
    }

    {
    Bwh larger("larger");
    TEST(larger.Bytes() == 6);
    TEST(larger.MaxBytes() == 6);
    Bwh small("small");
    TEST(small.Bytes() == 5);
    TEST(small.MaxBytes() == 5);

    larger.Replace(small);
    TEST(larger.Bytes() == 5);
    TEST(larger.MaxBytes() == 6);
    TEST(larger == small);
    }

    {
    Bwh src("stuff");
    Bwh trg;
    TEST(src.Bytes() == 5);
    TEST(trg.Bytes() == 0);
    TEST(src.Ptr() != NULL);
    TEST(trg.Ptr() == NULL);
    src.TransferTo(trg);
    TEST(src.Bytes() == 0);
    TEST(trg.Bytes() == 5);
    TEST(src.Ptr() == NULL);
    TEST(trg.Ptr() != NULL);
    }

    {
    Bwh lhs("left");
    Bwh rhs("right");
    TEST(lhs == Brn("left"));
    TEST(rhs == Brn("right"));
    lhs.Swap(rhs);
    TEST(rhs == Brn("left"));
    TEST(lhs == Brn("right"));
    }
}

class SuiteSplit : public Suite
{
public:
    SuiteSplit() : Suite("Splits and Records") {}
    void Test();
};

void SuiteSplit::Test()
{
    {
    Bws<20> a("0123456789ABCDEFGHIJ");
    Bws<20> aa("0123456789ABCDEFGHIJ");
    aa.SetBytes(1);
    Brn b = a.Split(0,1);
    TEST(b.Bytes() == 1);
    TEST(b == aa);

    b.Set(a.Split(0,2));
    aa.SetBytes(2);
    TEST(b.Bytes() == 2);
    TEST(b == aa);

    b.Set(a.Split(0,19));
    aa.SetBytes(19);
    TEST(b.Bytes() == 19);
    TEST(b == aa);

    b.Set(a.Split(0,20));
    aa.SetBytes(20);
    TEST(b.Bytes() == 20);
    TEST(b == aa);
    TEST(b == a);

    b.Set(a.Split(19,1));
    Bws<2> aaa("J");
    aaa.SetBytes(1);
    TEST(b.Bytes() == 1);
    TEST(b == aaa);

    TEST_THROWS(a.Split(19,2), AssertionFailed);

    b.Set(a.Split(5,5));
    Bws<5> aaaa("56789");
    TEST(b.Bytes() == 5);
    TEST(b == aaaa);

    b.Set(a.Split(20));
    TEST(b.Bytes() == 0);
    TEST(b == Brx::Empty());

    b.Set(a.Split(19));
    TEST(b.Bytes() == 1);
    TEST(b == aaa);

    b.Set(a.Split(1));
    TEST(b.Bytes() == 19);
    TEST(b == aa.Split(1, 19));

    b.Set(a.Split(0));
    TEST(b.Bytes() == 20);
    TEST(b == aa.Split(0, 20));

    TEST_THROWS(a.Split(21), AssertionFailed);
    }

    {
    const TByte a[10] = { 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF,
                            0x1A, 0x2B, 0x3C, 0x4D };
    Brn b(a,10);
    }
}

class SuiteGrow : public Suite
{
public:
    SuiteGrow() : Suite("Growing Bwh's") {}
    void Test();
};

void SuiteGrow::Test()
{
    //Test normal growing (new max bytes is larger than current)
    {
    Bwh d("My String");
    Bws<9> e(d);
    TEST(d.Bytes() == 9);
    TEST(d.MaxBytes() == 9);
    TEST_THROWS(d.Replace("My String1"), AssertionFailed);

    d.Grow(10);
    TEST(d.Bytes() == 9);
    TEST(d.MaxBytes() == 10);
    TEST(d == e);
    }

    //Test no change growing (new max bytes is less than or equal to current)
    {
    Bwh d("New string");
    TEST(d.Bytes() == 10);
    TEST(d.MaxBytes() == 10);
    d.Grow(8);
    //Nothing changes
    TEST(d.Bytes() == 10);
    TEST(d.MaxBytes() == 10);
    }

    //Test corner case (new max bytes is less than 4 -- gets rounded up to 4)
    {
    Bwh d;
    TEST(d.Bytes() == 0);
    TEST(d.MaxBytes() == 0);
    Bws<10> e((TUint)0);
    TEST(e.Bytes() == 0);
    TEST(e.MaxBytes() == 10);
    TEST(d == e);

    d.Grow(3);
    TEST(d.Bytes() == 0);
    TEST(d.MaxBytes() == 4); // Minimum growth size of 4
    e.Replace("A St");
    d.Replace("A St");
    TEST(d.Bytes() == 4);
    TEST(d.MaxBytes() == 4);
    TEST(e.Bytes() == 4);
    TEST(e.MaxBytes() == 10);
    TEST(d == e);
    }
}

class SuiteZeroBytes : public Suite
{
public:
    SuiteZeroBytes() : Suite("Zero byte sized buffers") {}
    void Test();
};

void SuiteZeroBytes::Test()
{
    Bws<8> z(6);
    TEST(Brx::Empty() != z);
    z.SetBytes(0);
    TEST(Brx::Empty() == z);
    TEST(Brx::Empty().Bytes() == 0);

    Brn brn(z);
    TEST(brn == Brx::Empty());
    z.SetBytes(4);
    Brn brn1(z);
    TEST(brn1 != Brx::Empty());

    Brn brn2;
    TEST(brn2 == Brx::Empty());
    brn2.Set(z);
    TEST(brn2 != Brx::Empty());

    Bwh d;
    TEST(d == Brx::Empty());
    d.Grow(10);
    TEST(d.Bytes() == 0);
    TEST(d == Brx::Empty());
}

class SuiteTestBwn : public Suite
{
public:
    SuiteTestBwn() : Suite("Bwn Test Suite") {}
    void Test();
};

void SuiteTestBwn::Test()
{
    //1) Create a Bwn.

    TByte fakeBuff1[] = "abcdefgh";
    TUint fakeBuffLen1    = 8;
    TUint fakeBuffMaxLen1 = 8;

    TByte fakeBuff2[] = "ijklm";
    TUint fakeBuffLen2    = 5;
    TUint fakeBuffMaxLen2 = 5;

    // Test the constructors.
    // fail on maxBytes
    // the '; (void)bwn4' just shuts the compiler up about unused variables
    TEST_THROWS( Bwn bwn4( fakeBuff1, fakeBuffMaxLen1, fakeBuffMaxLen1-1 ); (void)bwn4, AssertionFailed );

    Bwn bwn1( fakeBuff1, (TUint)strlen((const TChar *)fakeBuff1), fakeBuffMaxLen1 );                    // create a bwn.
    Bwn bwn2( fakeBuff1, (TUint)strlen((const TChar *)fakeBuff1), fakeBuffMaxLen1 );                    // and another...

    TEST( bwn1.Equals( bwn2 ) == true );                                                        // Ensure Set works.
    bwn2.Set( fakeBuff2, (TUint)strlen((const TChar *)fakeBuff2), fakeBuffMaxLen2 );                    // test Set.
    TEST( bwn1.Equals( bwn2 ) == false );                                                       // Ensure Set works.

    TEST( bwn1.Ptr() == fakeBuff1 );
    TEST( bwn1.Bytes() == fakeBuffLen1 );
    TEST( bwn1.MaxBytes() == fakeBuffMaxLen1 );

    TEST( bwn2.Ptr() == fakeBuff2 );
    TEST( bwn2.Bytes() == fakeBuffLen2 );
    TEST( bwn2.MaxBytes() == fakeBuffMaxLen2 );
}

class SuiteBrh : public Suite
{
public:
    SuiteBrh() : Suite("Brh Test Suite") {}
    void Test();
};

void SuiteBrh::Test()
{
    Brh brh;
    TEST(brh.Ptr() == NULL);
    TEST(brh.Bytes() == 0);
    Brn blah("blah");
    brh.Set(blah);
    TEST(brh.Equals(blah));
    Brh brh2(blah);
    TEST(brh2.Equals(blah));
    TEST(brh2.Equals(brh));
    Brh brh3("foo");
    TEST(brh3.Bytes() == 3);
    brh3.Set("qwerty");
    TEST(brh3.Bytes() == 6);
    brh3.Set(brh2.Ptr(), brh2.Bytes());
    TEST(brh3.Equals(brh2));
    TEST(brh3.Equals(blah));

    Brhz brhz;
    TEST(brhz.Ptr() == NULL);
    TEST(brhz.Bytes() == 0);
    brhz.Set(blah);
    TEST(brhz.Equals(blah));
    TEST(strlen((const char*)brhz.Ptr()) == 4);
    TEST(strcmp((const char*)brhz.Ptr(), brhz.CString()) == 0);
    TEST(brhz.Bytes() == 4);
    Brhz brhz2(blah);
    TEST(brhz2.Equals(blah));
    TEST(brhz2.Equals(brh2));
    Brhz brhz3("foo");
    TEST(strlen(brhz3.CString()) == 3);
    TEST(strcmp("foo", brhz3.CString()) == 0);
    TEST(brhz3.Bytes() == 3);
    brhz3.Set("qwerty");
    TEST(strlen(brhz3.CString()) == 6);
    TEST(brhz3.Bytes() == 6);
    brhz3.Set(brh2.Ptr(), brh2.Bytes());
    TEST(brhz3.Equals(brh2));
    TEST(brhz3.Equals(blah));
}

class SuiteBufferCmp : public Suite
{
public:
    SuiteBufferCmp() : Suite("SuiteBufferCmp Test Suite") {}
    void Test();
private:
    class Register
    {
    public:
        Register(const TChar* aName, TInt aValue) : iName(aName), iValue(aValue) {}
        const Brx& Name() const { return iName; }
        TInt Value() const { return iValue; }
    private:
        Brh iName;
        TInt iValue;
    };
};

void SuiteBufferCmp::Test()
{
    typedef std::map<Brn,Register*,BufferCmp> Map;
    Map map;
    Register* r = new Register("Register0", 3);
    Brn name(r->Name());
    (void)map.insert(std::pair<Brn,Register*>(name, r));
    r = new Register("Register1", 4);
    name.Set(r->Name());
    (void)map.insert(std::pair<Brn,Register*>(name, r));
    r = new Register("Register2", 5);
    name.Set(r->Name());
    (void)map.insert(std::pair<Brn,Register*>(name, r));
    r = new Register("Register5", 8);
    name.Set(r->Name());
    (void)map.insert(std::pair<Brn,Register*>(name, r));
    r = new Register("Register7", 10);
    name.Set(r->Name());
    (void)map.insert(std::pair<Brn,Register*>(name, r));
    r = new Register("Register3", 6);
    name.Set(r->Name());
    (void)map.insert(std::pair<Brn,Register*>(name, r));
    r = new Register("Register6", 9);
    name.Set(r->Name());
    (void)map.insert(std::pair<Brn,Register*>(name, r));
    r = new Register("Register4", 7);
    name.Set(r->Name());
    (void)map.insert(std::pair<Brn,Register*>(name, r));

    Brn key("Register5");
    Map::iterator it = map.find(key);
    TEST(it != map.end());
    TEST(it->second->Value() == 8);
    key.Set("Register1");
    it = map.find(key);
    TEST(it != map.end());
    TEST(it->second->Value() == 4);
    key.Set("Register7");
    it = map.find(key);
    TEST(it != map.end());
    TEST(it->second->Value() == 10);
    key.Set("Register6");
    it = map.find(key);
    TEST(it != map.end());
    TEST(it->second->Value() == 9);
    key.Set("Register3");
    it = map.find(key);
    TEST(it != map.end());
    TEST(it->second->Value() == 6);
    key.Set("Register0");
    it = map.find(key);
    TEST(it != map.end());
    TEST(it->second->Value() == 3);
    key.Set("Register4");
    it = map.find(key);
    TEST(it != map.end());
    TEST(it->second->Value() == 7);
    key.Set("Register2");
    it = map.find(key);
    TEST(it != map.end());
    TEST(it->second->Value() == 5);

    it = map.begin();
    TEST(it != map.end());
    TEST(it->second->Name() == Brn("Register0"));
    TEST(it->second->Value() == 3);
    it++;
    TEST(it != map.end());
    TEST(it->second->Name() == Brn("Register1"));
    TEST(it->second->Value() == 4);
    it++;
    TEST(it != map.end());
    TEST(it->second->Name() == Brn("Register2"));
    TEST(it->second->Value() == 5);
    it++;
    TEST(it != map.end());
    TEST(it->second->Name() == Brn("Register3"));
    TEST(it->second->Value() == 6);
    it++;
    TEST(it != map.end());
    TEST(it->second->Name() == Brn("Register4"));
    TEST(it->second->Value() == 7);
    it++;
    TEST(it != map.end());
    TEST(it->second->Name() == Brn("Register5"));
    TEST(it->second->Value() == 8);
    it++;
    TEST(it != map.end());
    TEST(it->second->Name() == Brn("Register6"));
    TEST(it->second->Value() == 9);
    it++;
    TEST(it != map.end());
    TEST(it->second->Name() == Brn("Register7"));
    TEST(it->second->Value() == 10);
    it++;
    TEST(it == map.end());

    it = map.begin();
    while (it != map.end()) {
        delete it->second;
        it++;
    }
}

void TestBuffer()
{
    Runner runner("Binary Buffer Testing");
    runner.Add(new SuiteConstruction());
    runner.Add(new SuiteModification());
    runner.Add(new SuiteElements());
    runner.Add(new SuiteHeap());
    runner.Add(new SuiteSplit());
    runner.Add(new SuiteGrow());
    runner.Add(new SuiteZeroBytes());
    runner.Add(new SuiteTestBwn());
    runner.Add(new SuiteBrh());
    runner.Add(new SuiteBufferCmp());
    runner.Run();
}

void OpenHome::TestFramework::Runner::Main(TInt /*aArgc*/, TChar* /*aArgv*/[], Net::InitialisationParams* aInitParams)
{
    Net::UpnpLibrary::InitialiseMinimal(aInitParams);
    TestBuffer();
    delete aInitParams;
    Net::UpnpLibrary::Close();
}
