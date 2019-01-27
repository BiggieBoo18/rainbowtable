import hashlib
import itertools
import random

from tqdm import tqdm

class RainbowTable(object):
    NUM   = "0123456789"
    LOWER = "abcdefghijklmnopqrstuvwxyz"
    UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __init__(self, func_hash, char_type, char_length, chain_length, n_chains):
        self.func_hash    = self.md5 if func_hash=="md5" else self.sha1
        self.char_type    = char_type
        self.chars        = {i:c for i, c in enumerate(char_type)}
        self.char_length  = char_length
        self.chain_length = chain_length
        self.n_chains     = n_chains
        self.rainbowtable = []
        if self.char_length>16:
            print("Please char_length must be 16 or less.")
            exit(1)

    def md5(self, p):
        return hashlib.md5(p.encode()).hexdigest()

    def sha1(self, p):
        return hashlib.sha1(p.encode()).hexdigest()

    def reduction(self, h, i):
        p = ""
        i = int(h, 16)+i
        while i:
            p += self.chars[i%len(self.char_type)]
            i //= len(self.char_type)
        return p[:self.char_length]

    def chain(self, p):
        ch = []
        for i in range(self.chain_length):
            ch.extend([p, self.func_hash(p)]) # plain + hash
            p     = rt.reduction(ch[-1], i) # reduction plain
        ch.append(p)
        return ch

    def rainbow_table(self, path):
        fp = open(path, "w")
        p = itertools.product(self.char_type, repeat=self.char_length) # product all patern in char_type
        for i, s in enumerate(tqdm(p), start=1):
            s = "".join(s)
            chain = self.chain(s)
            # self.rainbowtable.append([chain[0], chain[-1]]) # append only chain head and chain tail
            fp.writelines(" ".join([chain[0], chain[-1]]))
            fp.write("\n") # write format: "head_chain tail_chain\n"
            if self.n_chains and i>=self.n_chains: # continue if n_chains==0 or i<n_chains, n_chains==0 is all patern
                break
        fp.close()

    def match_tail(self, p):
        for chain in self.rainbowtable:
            if chain[1]==p:
                return chain
        return False

    def decode(self, t):
        if not self.rainbowtable:
            return False
        for i in range(self.chain_length-1, -1, -1): # column
            p = self.reduction(t, i) # to plain
            for j in range((self.chain_length-1)-i): # loop diff from tail
                h = self.func_hash(p)
                p = self.reduction(h, i+j+1)
            matched_chain = self.match_tail(p)
            if matched_chain:
                break
        if not matched_chain:
            return False
        matched_chain = self.chain(matched_chain[0])
        return matched_chain[matched_chain.index(t)-1]

    def read_table(self, path):
        fp = open(path, "r")
        self.rainbowtable = [s.strip().split(" ") for s in fp.readlines()] # read format: "head_chain tail_chain\n"
        fp.close()

if __name__ == "__main__":
    # p = "password"
    p = "aaaaaaaa"

    rt = RainbowTable(func_hash="md5",
                      char_type=RainbowTable.NUM+RainbowTable.LOWER,
                      char_length=8,
                      chain_length=1000,
                      n_chains=2821109907455//2)

    ch = rt.chain(p)
    rt.rainbow_table("sample.rt")
    rt.read_table("sample.rt")
    print("decoded =", rt.decode(rt.md5(p)))
