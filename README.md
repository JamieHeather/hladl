# hladl
### (HLA downloader)
#### JH @ MGH, 2025

[![PyPI - Version](https://img.shields.io/pypi/v/hladl?color=%239467bd)](https://pypi.org/project/hladl/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


This is a simple CLI to make grabbing specific HLA allele sequences easier. It aims to be similar to [`hladownload`](https://github.com/ramonamerong/hladownload/) but without the more advanced features that offers (although that script appears to be out of action due to `Biopython` version changes since its last update).

Effectively, this script will spit out a cDNA nucleotide or protein amino acid sequence, given an allele identifier and a number of digits resolution. Sequences are grabbed from [the IPD-IMGT/HLA Github repo](https://github.com/ANHIG/IMGTHLA) (as [is available through the EBI](https://www.ebi.ac.uk/ipd/imgt/hla/)) and stored locally in a gzippd json, allowing them to be output without a need for later internet connectivity.


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

### Importing `hladl` for use inside other scripts

The major case use I wanted `hladl` for is to import in other scripts, to allow for easy in-line grabbing of HLA sequences. It can be done by simple importing the relevant components and calling the `seq` function:

```bash
from hladl.get_seq import seq
from hladl.main import data_dir

seq1 = seq('A*02:01', 4, 'prot', 'ecd', 'stdout', data_dir)
print(seq1)
GSHSMRYFFTSVSRPGRGEPRFIAVGYVDDTQFVRFDSDAASQRMEPRAPWIEQEGPEYWDGETRKVKAHSQTHRVDLGTLRGYYNQSEAGSHTVQRMYGCDVGSDWRFLRGYHQYAYDGKDYIALKEDLRSWTAADMAAQTTKHKWEAAHVAEQLRAYLEGTCVEWLRRYLENGKETLQRTDAPKTHMTHHAVSDHEATLRCWALSFYPAEITLTWQRDGEDQTQDTELVETRPAGDGTFQKWAAVVVPSGQEQRYTCHVQHEGLPKPLTLRWEPSSQPTIPI

seq2 = seq('B*08:01', 4, 'nuc', 'full', 'stdout', data_dir)
print(seq2)
ATGCTGGTCATGGCGCCCCGAACCGTCCTCCTGCTGCTCTCGGCGGCCCTGGCCCTGACCGAGACCTGGGCCGGCTCCCACTCCATGAGGTATTTCGACACCGCCATGTCCCGGCCCGGCCGCGGGGAGCCCCGCTTCATCTCAGTGGGCTACGTGGACGACACGCAGTTCGTGAGGTTCGACAGCGACGCCGCGAGTCCGAGAGAGGAGCCGCGGGCGCCGTGGATAGAGCAGGAGGGGCCGGAGTATTGGGACCGGAACACACAGATCTTCAAGACCAACACACAGACTGACCGAGAGAGCCTGCGGAACCTGCGCGGCTACTACAACCAGAGCGAGGCCGGGTCTCACACCCTCCAGAGCATGTACGGCTGCGACGTGGGGCCGGACGGGCGCCTCCTCCGCGGGCATAACCAGTACGCCTACGACGGCAAGGATTACATCGCCCTGAACGAGGACCTGCGCTCCTGGACCGCGGCGGACACCGCGGCTCAGATCACCCAGCGCAAGTGGGAGGCGGCCCGTGTGGCGGAGCAGGACAGAGCCTACCTGGAGGGCACGTGCGTGGAGTGGCTCCGCAGATACCTGGAGAACGGGAAGGACACGCTGGAGCGCGCGGACCCCCCAAAGACACACGTGACCCACCACCCCATCTCTGACCATGAGGCCACCCTGAGGTGCTGGGCCCTGGGCTTCTACCCTGCGGAGATCACACTGACCTGGCAGCGGGATGGCGAGGACCAAACTCAGGACACTGAGCTTGTGGAGACCAGACCAGCAGGAGATAGAACCTTCCAGAAGTGGGCAGCTGTGGTGGTGCCTTCTGGAGAAGAGCAGAGATACACATGCCATGTACAGCATGAGGGGCTGCCGAAGCCCCTCACCCTGAGATGGGAGCCGTCTTCCCAGTCCACCGTCCCCATCGTGGGCATTGTTGCTGGCCTGGCTGTCCTAGCAGTTGTGGTCATCGGAGCTGTGGTCGCTGCTGTGATGTGTAGGAGGAAGAGCTCAGGTGGAAAAGGAGGGAGCTACTCTCAGGCTGCGTGCAGCGACAGTGCCCAGGGCTCTGATGTGTCTCTCACAGCTTGA
```

### Data licensing and information

This tool doesn't host or distribute any of the IPD-IMGT/HLA data, it just facilitates its download and distribution from that resource. Nor am I affiliated with them in any way.

The IMGTHLA data [is hosted on their Github repo](https://github.com/ANHIG/IMGTHLA), under a [Creative Commons Attribution-NoDerivs License](https://github.com/ANHIG/IMGTHLA/blob/Latest/LICENCE.md), meaning that users "are free to copy, distribute, display and make commercial use of the databases in all legislations", providing suitable attribution is provided. 

For further details on the data, please see the following publications:

* Barker D, Maccari G, Georgiou X, Cooper M, Flicek P, Robinson J, Marsh SGE The IPD-IMGT/HLA Database Nucleic Acids Research(2023), 51(D1): D948-D955
* Robinson J, Barker D, Marsh SGE 25 years of the IPD-IMGT/HLA Database. HLA(2024),103(6): e15549
* Robinson J, Malik A, Parham P, Bodmer JG, Marsh SGE: IMGT/HLA - a sequence database for the human major histocompatibility complex Tissue Antigens (2000), 55:280-287