#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <string>
#include <fstream>
#include <sstream>
#include <tuple>
#include <unordered_set>
#include <vector>

using Matrix = std::array<std::uint32_t, 32>;
constexpr int N = 32;

static std::uint32_t apply_row(std::uint32_t row, const Matrix& m) {
    std::uint32_t out = 0;
    while (row) {
        const int bit = std::countr_zero(row);
        out ^= m[bit];
        row &= row - 1;
    }
    return out;
}
static Matrix mul(const Matrix& a, const Matrix& b) {
    Matrix out{};
    for (int i = 0; i < N; ++i) out[i] = apply_row(a[i], b);
    return out;
}
static Matrix inv(Matrix a) {
    Matrix out{};
    for (int i = 0; i < N; ++i) out[i] = std::uint32_t{1} << i;
    for (int col = 0; col < N; ++col) {
        int p = col;
        while (p < N && !(a[p] & (std::uint32_t{1} << col))) ++p;
        if (p == N) std::abort();
        std::swap(a[p], a[col]); std::swap(out[p], out[col]);
        for (int i = 0; i < N; ++i) if (i != col && (a[i] & (std::uint32_t{1} << col))) {
            a[i] ^= a[col]; out[i] ^= out[col];
        }
    }
    return out;
}
static bool inv_checked(Matrix a, Matrix& out) {
    out = {};
    for (int i = 0; i < N; ++i) out[i] = std::uint32_t{1} << i;
    for (int col = 0; col < N; ++col) {
        int p = col;
        while (p < N && !(a[p] & (std::uint32_t{1} << col))) ++p;
        if (p == N) return false;
        std::swap(a[p], a[col]); std::swap(out[p], out[col]);
        for (int i = 0; i < N; ++i) if (i != col && (a[i] & (std::uint32_t{1} << col))) {
            a[i] ^= a[col]; out[i] ^= out[col];
        }
    }
    return true;
}
static Matrix xorshift_matrix() {
    Matrix a{};
    for (int src = 0; src < N; ++src) {
        std::uint32_t x = std::uint32_t{1} << src;
        x ^= x >> 13; x ^= x << 17; x ^= x >> 5;
        for (int dst = 0; dst < N; ++dst) a[dst] |= ((x >> dst) & 1U) << src;
    }
    return a;
}
static Matrix identity() {
    Matrix a{}; for (int i = 0; i < N; ++i) a[i] = std::uint32_t{1} << i; return a;
}
struct State { Matrix T, B, C; };
static bool from_T(const Matrix& T, State& out);
static State origin() {
    Matrix A = xorshift_matrix(), T = identity();
    return {T, A, A};
}

static bool load_hex_T(const char* path, State& out) {
    if (!path || !*path) return false;
    std::ifstream stream(path);
    if (!stream) return false;
    std::string text((std::istreambuf_iterator<char>(stream)), {});
    const auto marker = text.find("\"T\"");
    const auto open = marker == std::string::npos ? marker : text.find('[', marker);
    if (open == std::string::npos) return false;
    Matrix T{};
    std::size_t cursor = open + 1;
    for (int i = 0; i < N; ++i) {
        const auto quote = text.find('"', cursor);
        const auto end = quote == std::string::npos ? quote : text.find('"', quote + 1);
        if (end == std::string::npos) return false;
        T[i] = static_cast<std::uint32_t>(std::strtoull(text.substr(quote + 1, end - quote - 1).c_str(), nullptr, 16));
        cursor = end + 1;
    }
    return from_T(T, out);
}
static bool from_T(const Matrix& T, State& out) {
    Matrix ti;
    if (!inv_checked(T, ti)) return false;
    const Matrix A = xorshift_matrix();
    const Matrix C = mul(A, ti);
    out = {T, mul(T, C), C};
    return true;
}
static State random_forest(std::mt19937_64& rng) {
    Matrix T = identity();
    std::array<int,N> parent{}, unit_row{};
    for(int i=0;i<N;++i) parent[i]=unit_row[i]=i;
    auto root = [&](int x) { while(parent[x]!=x)x=parent[x]; return x; };
    const int merges = 8 + int(rng()%24);
    for(int k=0;k<merges;++k) {
        int a,b,ra,rb;
        do { a=int(rng()%N); b=int(rng()%N); ra=root(a); rb=root(b); } while(ra==rb);
        // Convert the second tree's only singleton row into the connecting edge.
        T[unit_row[rb]] = (std::uint32_t{1}<<a) | (std::uint32_t{1}<<b);
        parent[rb]=ra;
    }
    std::shuffle(T.begin(),T.end(),rng);
    State out; if(!from_T(T,out)) std::abort(); return out;
}

// Left multiply T by an elementary row shear.  Update B= T A T^-1 and
// C=A T^-1 without recomputing an inverse.
static void shear(State& s, int dst, int src) {
    const auto db = std::uint32_t{1} << dst;
    const auto sb = std::uint32_t{1} << src;
    s.T[dst] ^= s.T[src];
    for (auto& row : s.B) if (row & db) row ^= sb;
    s.B[dst] ^= s.B[src];
    for (auto& row : s.C) if (row & db) row ^= sb;
}
// Row permutation T'=P T.  This is useful because it keeps every T row
// sparse while exploring arbitrary output-coordinate assignments.
static void swap_rows(State& s, int a, int b) {
    if (a == b) return;
    std::swap(s.T[a], s.T[b]);
    std::swap(s.B[a], s.B[b]);
    const auto ba = std::uint32_t{1} << a, bb = std::uint32_t{1} << b;
    for (auto& row : s.B) {
        const bool xa = row & ba, xb = row & bb;
        if (xa != xb) row ^= ba | bb;
    }
    for (auto& row : s.C) {
        const bool xa = row & ba, xb = row & bb;
        if (xa != xb) row ^= ba | bb;
    }
}
static std::uint64_t hash_matrix(const Matrix& a) {
    std::uint64_t h = 0x9e3779b97f4a7c15ULL;
    for (auto x : a) { h ^= x + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2); h ^= h >> 29; }
    return h;
}
static bool sparse_T(const Matrix& t) {
    for (auto x : t) if (!x || std::popcount(x) > 2) return false;
    return true;
}
struct Cover {
    int xor_count = 1000;
    int pair_count = 0;
    int finals = 0;
    std::vector<std::uint32_t> pairs;
};
static bool has(const std::vector<std::uint32_t>& v, std::uint32_t x) {
    return std::find(v.begin(), v.end(), x) != v.end();
}
static std::vector<std::array<std::uint32_t,2>> options(std::uint32_t row) {
    std::vector<int> b;
    for (auto x = row; x; x &= x - 1) b.push_back(std::countr_zero(x));
    std::vector<std::array<std::uint32_t,2>> out;
    if (b.size() == 3) for (int lone : b) out.push_back({row ^ (std::uint32_t{1} << lone), 0});
    if (b.size() == 4) {
        auto u = [&](int i) { return std::uint32_t{1} << b[i]; };
        out.push_back({u(0)|u(1),u(2)|u(3)});
        out.push_back({u(0)|u(2),u(1)|u(3)});
        out.push_back({u(0)|u(3),u(1)|u(2)});
    }
    return out;
}
static Cover greedy_cover(const State& s) {
    std::vector<std::uint32_t> targets;
    for (const auto* m : {&s.B, &s.C}) for (auto x : *m) if (!has(targets,x)) targets.push_back(x);
    Cover c;
    std::vector<std::uint32_t> finals;
    for (auto x : targets) {
        const int w = std::popcount(x);
        if (!w || w > 4) return c;
        if (w == 2) c.pairs.push_back(x); else if (w >= 3) finals.push_back(x);
    }
    auto covered = [&](std::uint32_t row, const std::vector<std::uint32_t>& p) {
        for (auto q : options(row)) if (has(p,q[0]) && (!q[1] || has(p,q[1]))) return true;
        return false;
    };
    std::sort(c.pairs.begin(), c.pairs.end()); c.pairs.erase(std::unique(c.pairs.begin(),c.pairs.end()),c.pairs.end());
    while (true) {
        std::vector<std::uint32_t> unmet;
        for (auto x : finals) if (!covered(x,c.pairs)) unmet.push_back(x);
        if (unmet.empty()) break;
        double best_ratio=-1; int best_gain=-1,best_size=9; std::array<std::uint32_t,2> best{};
        for (auto row : unmet) for (auto q : options(row)) {
            int add = (!has(c.pairs,q[0])) + (q[1] && !has(c.pairs,q[1]));
            if (!add) continue;
            auto p=c.pairs; p.push_back(q[0]); if(q[1])p.push_back(q[1]);
            int gain=0; for(auto y:unmet) gain += covered(y,p);
            double ratio=double(gain)/add;
            if (std::tuple(ratio,gain,-add,~q[0],~q[1]) >
                std::tuple(best_ratio,best_gain,-best_size,~best[0],~best[1])) {
                best_ratio=ratio;best_gain=gain;best_size=add;best=q;
            }
        }
        if (best_size==9) return c;
        c.pairs.push_back(best[0]); if(best[1])c.pairs.push_back(best[1]);
        std::sort(c.pairs.begin(),c.pairs.end()); c.pairs.erase(std::unique(c.pairs.begin(),c.pairs.end()),c.pairs.end());
    }
    // Remove optional unused pair nodes.
    for (auto it=c.pairs.rbegin();it!=c.pairs.rend();) {
        bool required=has(targets,*it); if (!required) {
            auto p=c.pairs; p.erase(std::find(p.begin(),p.end(),*it)); bool ok=true; for(auto y:finals)ok&=covered(y,p);
            if(ok){c.pairs=std::move(p);it=c.pairs.rbegin();continue;}
        } ++it;
    }
    c.pair_count=(int)c.pairs.size(); c.finals=(int)finals.size(); c.xor_count=c.pair_count+c.finals; return c;
}
struct Score { int bad=0, excess=0, sq=0, maxw=0, total=0, t2=0; };
static Score score(const State& s) {
    Score z;
    for(auto x:s.T) { int w=std::popcount(x); z.t2 += w==2; }
    for(const auto* m:{&s.B,&s.C}) for(auto x:*m){int w=std::popcount(x);z.maxw=std::max(z.maxw,w);z.total+=w;int e=std::max(0,w-4);z.excess+=e;z.sq+=e*e;z.bad+=w>4;}
    return z;
}
static auto score_key(const Score& z) {
    return std::tuple(z.bad, z.excess, z.sq, z.maxw, z.total, z.t2);
}
static double energy(const Score& z, const Cover* c) {
    double e = z.bad*260.0 + z.sq*25.0 + z.excess*4.0 + z.total*0.02 + z.t2*0.2;
    if(c && c->xor_count<1000) e += c->xor_count*2.0;
    return e;
}
static void emit(std::uint64_t step,const State&s,const Score&z,const Cover&c) {
    const auto A = xorshift_matrix();
    if (!sparse_T(s.T) || mul(s.C,s.T) != A || mul(s.T,s.C) != s.B) std::abort();
    std::printf("{\"step\":%llu,\"hash\":\"%016llx\",\"t2\":%d,\"bad\":%d,\"excess\":%d,\"linear_excess\":%d,\"squared_excess\":%d,\"max\":%d,\"total_weight\":%d,\"xor\":%d,\"T\":[",(unsigned long long)step,(unsigned long long)hash_matrix(s.T),z.t2,z.bad,z.excess,z.excess,z.sq,z.maxw,z.total,c.xor_count);
    for(int i=0;i<N;++i)std::printf("%s\"%08x\"",i?",":"",s.T[i]); std::printf("],\"B\":[");
    for(int i=0;i<N;++i)std::printf("%s\"%08x\"",i?",":"",s.B[i]); std::printf("],\"C\":[");
    for(int i=0;i<N;++i)std::printf("%s\"%08x\"",i?",":"",s.C[i]); std::printf("],\"pairs\":[");
    for(size_t i=0;i<c.pairs.size();++i)std::printf("%s\"%08x\"",i?",":"",c.pairs[i]); std::printf("]}\n"); std::fflush(stdout);
}
int main(int argc,char**argv){
    std::uint64_t seed=argc>1?std::strtoull(argv[1],nullptr,0):0x9e3779ULL;
    std::uint64_t steps=argc>2?std::strtoull(argv[2],nullptr,0):10000000ULL;
    std::uint64_t restart=argc>3?std::strtoull(argv[3],nullptr,0):250000ULL;
    std::mt19937_64 rng(seed); State start;
    const bool have_start = argc > 4 && load_hex_T(argv[4], start);
    State cur=have_start ? start : random_forest(rng); Score cs=score(cur); Cover cc=greedy_cover(cur); double ce=energy(cs,&cc);
    int best_obj=1000; Score best_frontier=cs; emit(0,cur,cs,cc);
    std::unordered_set<std::uint64_t> seen; seen.reserve(100000);
    for(std::uint64_t step=1;step<=steps;++step){
        if(restart && step%restart==0){cur=(have_start && (rng()&1)) ? start : random_forest(rng);cs=score(cur);cc=greedy_cover(cur);ce=energy(cs,&cc);}
        State cand=cur; int a=(int)(rng()%N), b=(int)(rng()%(N-1)); b += b>=a;
        const int kind=int(rng()%10);
        if(kind<2) swap_rows(cand,a,b);
        else if(kind<7) { if(std::popcount(cand.T[a]^cand.T[b])>2) continue; shear(cand,a,b); }
        else {
            Matrix nt=cand.T;
            if(rng()&1) nt[a]=std::uint32_t{1}<<(rng()%N);
            else {int x=int(rng()%N),y=int(rng()%(N-1));y+=y>=x;nt[a]=(std::uint32_t{1}<<x)|(std::uint32_t{1}<<y);}
            if(!from_T(nt,cand)) continue;
        }
        if(!sparse_T(cand.T)) continue;
        Score ns=score(cand); Cover nc=greedy_cover(cand); double ne=energy(ns,&nc);
        if(ns.bad==0 && nc.xor_count<1000){int obj=3*(nc.xor_count+ns.t2); if(obj<best_obj){best_obj=obj;emit(step,cand,ns,nc);}}
        if(score_key(ns)<score_key(best_frontier)){best_frontier=ns;emit(step,cand,ns,nc);}
        const double phase=restart?double(step%restart)/restart:double(step)/steps;
        const double temp=80.0*std::pow(0.0002,phase)+0.2;
        const double draw=double(rng()>>11)*(1.0/9007199254740992.0);
        if(ne<=ce || draw<std::exp((ce-ne)/temp)){cur=std::move(cand);cs=ns;cc=std::move(nc);ce=ne;}
    }
    std::fprintf(stderr,"summary seed=%llu steps=%llu best_obj=%d best_bad=%d best_linear_excess=%d best_squared_excess=%d best_max=%d best_total=%d best_t2=%d\n",
        (unsigned long long)seed,(unsigned long long)steps,best_obj,best_frontier.bad,
        best_frontier.excess,best_frontier.sq,best_frontier.maxw,best_frontier.total,best_frontier.t2);
    return 0;
}
