# -*- coding: utf-8 -*-

import textwrap
import os
import gzip
import json
from . import download as dl


def readfq(fastx_file):
    """
    readfq(file):Heng Li's Python implementation of his readfq function
    https://github.com/lh3/readfq/blob/master/readfq.py
    :param fastx_file: opened file containing fastq or fasta reads
    :yield: read id, read sequence, and (where available) read quality scores
    """

    last = None  # this is a buffer keeping the last unprocessed line
    while True:
        if not last:  # the first record or a record following a fastq
            for l in fastx_file:  # search for the start of the next record
                if l[0] in '>@':  # fasta/q header line
                    last = l[:-1]  # save this line
                    break

        if not last:
            break

        name, seqs, last = last[1:], [], None  # This version takes the whole line (post '>')
        for l in fastx_file:  # read the sequence
            if l[0] in '@+>':
                last = l[:-1]
                break
            seqs.append(l[:-1])

        if not last or last[0] != '+':  # this is a fasta record
            yield name, ''.join(seqs), None  # yield a fasta record
            if not last:
                break

        else:  # this is a fastq record
            sequence, leng, seqs = ''.join(seqs), 0, []
            for l in fastx_file:  # read the quality
                seqs.append(l[:-1])
                leng += len(l) - 1
                if leng >= len(sequence):  # have read enough quality
                    last = None
                    yield name, sequence, ''.join(seqs)  # yield a fastq record
                    break

            if last:  # reach EOF before reading enough quality
                yield name, sequence, None  # yield a fasta record instead
                break


def fastafy(gene, seq_line):
    """
    :param gene: Gene symbol, extracted from the read id
    :param seq_line: Total protein primary sequence, extracted from input FASTA/generated by in silico splicing
    :return: An output-compatible FASTA entry ready for writing to file
    """
    return ">" + gene + "\n" + textwrap.fill(seq_line, 60) + "\n"


def trim_gene(digits, full_gene):
    """
    :param digits: int, number of digits to give HLA resolution (2/4/6/8)
    :param full_gene: identifier of full gene/allele, as given in the second space-limited field of the IMGTHLA headers
    :return:
    """
    asterisk_x = full_gene.find('*')
    if asterisk_x == -1:
        raise IOError("Full allele identifier (minus 'HLA-') required, inclusive of asterisk.")
    else:
        return full_gene[:asterisk_x + int(1.5 * digits)]


def check_digits(requested_digits):
    if requested_digits not in [2, 4, 6, 8]:
        raise IOError("The only acceptable value for 'digits' are 2, 4, 6, and 8. ")


def get_data(digits, seqtype, data_dir):
    # TODO docstr

    # Check to see if the relevant data is present
    type_match = '_' + str(digits) + '_' + seqtype
    data_files = [x for x in os.listdir(data_dir) if x.endswith('.json.gz')
                  and type_match in x and 'tags' not in x]

    if not data_files:
        print("Necessary data not detected: downloading. ")
        dl.get_data(seqtype, digits, data_dir)
        data_files = [x for x in os.listdir(data_dir) if x.endswith('.json.gz') and type_match in x]

    # Use the most recent entry
    data_files.sort()
    recent = data_files[-1]
    hla = read_json(os.path.join(data_dir, recent))
    return hla, recent


def save_json(out_path, to_save, print2stdout=True):
    """
    :param out_path: str, path to save JSON to
    :param to_save: dict to save as JSON
    :param print2stdout: bool, detailing whether to print a confirmation after saving
    :return: nothing
    """
    with gzip.open(out_path, 'wt') as out_file:
        json.dump(to_save, out_file)

    if print2stdout:
        print('\tSaved to', out_path)


def read_json(in_path):
    """
    :param in_path: str, path to JSON file to read in
    :return: parsed JSON document
    """
    try:

        with gzip.open(in_path, 'rt') as in_file:
            return json.load(in_file)

    except Exception:
        raise IOError(f"Unable to read in JSON file '{in_path}'.")


modes = ['full', 'ecd']

# Details of the sequences and locations of the relevant domains, based on Uniprot examples
domains = {'signal': {'A': 'MAVMAPRTLLLLLSGALALTQTWA',  # https://www.uniprot.org/uniprotkb/P04439/
                      'B': 'MLVMAPRTVLLLLSAALALTETWA',  # https://www.uniprot.org/uniprotkb/P01889/
                      'C': 'MRVMAPRALLLLLSGGLALTETWA'},  # https://www.uniprot.org/uniprotkb/P10321/
           'transmemb': {'A': 'VGIIAGLVLLGAVITGAVVAAVMW',
                         'B': 'GIVAGLAVLAVVVIGAVVAAVMCR',
                         'C': 'MGIVAGLAVLVVLAVLGAVVTAMMC'}}

domain_locs = {'signal': {'A': '1-24',
                          'B': '1-24',
                          'C': '1-24'},
               'transmemb': {'A': '309-332',
                             'B': '310-333',
                             'C': '309-333'}}

featured_mhci = ['A', 'B', 'C', 'E']
