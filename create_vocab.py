import argparse
import leipzig_corpora


special_tokens = ["[PAD]\n", "[unused1]\n", "[unused2]\n", "[unused3]\n", "[unused4]\n", "[unused5]\n", "[unused6]\n", "[unused7]\n", "[unused8]\n", "[unused9]\n", "[UNK]\n", "[CLS]\n", "[SEP]\n", "[MASK]\n"]


def download_corpora(langs, size, year, dir):
    corpora = leipzig_corpora.Leipzig()
    corpora.download_all(dir, langs, size=size, year=year)


def main():
    parser = argparse.ArgumentParser(description="creating new vocab file")
    parser.add_argument("--langs",    
                        nargs='+',
                        required=True, 
                        help="Languages make vocab from")
    parser.add_argument("--size",  
                        type=str,
                        required=False, 
                        default='100K',
                        help="Size of vocab to download")
    parser.add_argument("--year",  
                        type=str,
                        required=False, 
                        default='2021',
                        help="Year of vocab to download")
    parser.add_argument("--dir",
                        type=str,
                        required=False, 
                        default='data',
                        help="Output dir")
    parser.add_argument("-o",
                        type=str,
                        required=False, 
                        default='vocab.txt',
                        help="Output dir")

    args = parser.parse_args()
    download_corpora(args.langs, args.size, args.year, args.dir)
    vocab = set()
    for lang in args.langs:
        filepath = f"{args.dir}/{lang}.{args.size}.txt"
        with open(filepath, "r") as f:
            for line in f:
                vocab.add(line.lower())
    
    sorted_vocab = sorted(list(vocab))

    with open(f"{args.dir}/{args.o}", "w") as f:
        f.writelines(special_tokens)
        f.writelines(sorted_vocab)


if __name__ == "__main__":
    main()
