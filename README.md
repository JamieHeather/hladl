# hladl
### (HLA downloader)
#### JH @ MGH, 2025

This is a simple CLI to make grabbing specific HLA allele sequences easier. It aims to be similar to [`hladownload`](https://github.com/ramonamerong/hladownload/) but without the more advanced features that offers (although that script appears to be out of action due to `Biopython` version changes since its last update).

Effectively, this script will spit out a cDNA nucleotide or protein amino acid sequence, given an allele identifier and a number of digits resolution. Sequences are grabbed from [the IMGTHLA Github repo](https://github.com/ANHIG/IMGTHLA) and stored locally in a gzippd json, allowing them to be output without a need for later internet connectivity.


### Installation

`hladl` was made with `poetry` and `typer`. It can be installed from PyPI:

```bash
pip install hladl
```

### Usage

Sequences can be downloaded to the installed data directory using `hladl init`. Users specify the *s*equence type (nucleotide, protein, or both) with the `-s` flag, and the HLA allele digit resolution (i.e. 2, 4, 6, or 8 digit, being HLA-X*22:44:66:88) wit the `-d` flag like so:

```bash
# Download nucleotide (cDNA) sequences for 4 digit alleles
hladl init -s nuc -d 4
 
# Download protein (AA) sequences for 2 digit alleles
hladl init -s prot -d 2
```

Sequences can then be output to stdout using the `seq` command:
```bash
hladl seq -a DRA*01:01
hladl seq -a A*02 -s prot -d 2
```

Class I MHC protein sequences can also be automatically trimmed to remove leader and transmembrane/intracellular domains, yielding the extracellular domain, by specifying this in the mode option:

```bash
hladl seq -a A*02:01 -m ecd -s prot
```

Users can also instead choose to produce a FASTA file of the designated allele using the `-om / --output_mode` flag, which saves to the current directory:

```bash
hladl seq -a B*07:02 -om fasta
```


The location of the data directory can be determined using the `dd` command:
```bash
hladl dd

# Will produce something like
/path/to/where/its/saving/stuff
```

#### Notes

* If you run the `hladl seq` script without running the appropriate `hladl init`, it will try to download the appropriate sequences on the fly. 

* While the IMGTHLA repo does also store unspliced genomic DNA files, these are handled slightly different, are much larger files, and frankly I don't need them in my pipelines right now, so they're not yet catered to.

* Pseudogenes and other aberrent length entries in the dataset cannot be used for `ecd` mode.




