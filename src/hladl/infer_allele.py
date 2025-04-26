# -*- coding: utf-8 -*-

from acora import AcoraBuilder
import collections as coll
import os
from . import hladlfunctions as fxn


def build_trie(sequence_list):
    """
    :param sequence_list: A list of DNA sequences (tags) to search for
    :return: An Aho-Corasick trie, which can be used to search sequences downstream with all of the listed tags
    """

    trie_builder = AcoraBuilder()
    for sequence in sequence_list:
        trie_builder.add(sequence)

    return trie_builder.build()


def get_trie_data(num_digits, seq_type, hla_dir, gene_prefixes, lower, higher, slide_len):
    """
    Generate the necessary tag files for easy loading for AC trie generation,
        saving to or loading from hladl data dir as needed
    :param num_digits: int, resolution of HLA allele number (2/4/6/8)
    :param seq_type: str, sequence type as per IMGTHLA (gen, nuc, prot)
    :param hla_dir: str, path to hladl data directory
    :param gene_prefixes: list of str, detailing IMGTLA pre-asterisk gene identifiers
    :param lower: int, lower length limit of sequence allowed (in amino acids)
    :param higher: int, upper length limit of sequence allowed (in amino acids)
    :param slide_len: int, length of sliding window to use for overlapping tags
    :return: AC trie generated from tags built from the appropriate data set
    """
    hla, data_file = fxn.get_data(num_digits, seq_type, hla_dir)

    # If the tags exist, read them in...
    tag_file = os.path.join(hla_dir, data_file[:data_file.index('.json')] + '_tags.json.gz')

    if os.path.isfile(tag_file):
        tags2hla = fxn.read_json(tag_file)

    # ... Otherwise, let's make a fresh set
    else:
        kept_alleles = coll.defaultdict(str)

        if lower == 0 and higher == 0:
            len_check = False
        else:
            len_check = True
            if seq_type == 'nuc':
                lower *= 3
                higher *= 3

        # Filter down to just the wanted MHC genes / lengths
        for allele in hla:

            if allele.split('*')[0] not in gene_prefixes:
                continue

            if len_check:
                len_seq = len(hla[allele])
                if lower:
                    if len_seq < lower:
                        continue
                if higher:
                    if len_seq > higher:
                        continue

            # Otherwise keep and use
            kept_alleles[allele] = hla[allele]

        # Then make sliding windows
        tags2hla = coll.defaultdict(list)
        for allele in kept_alleles:
            hla_seq = kept_alleles[allele]

            # Take sliding windows across the full length genes, overlapping by half their length
            for i in range(0, len(hla_seq) - slide_len + 1, int(slide_len / 2)):
                slide = hla_seq[i:i + slide_len]
                if len(slide) == slide_len:
                    tags2hla[slide].append(allele)

        # Then save that (to speed up repeat inferences with the same parameters
        fxn.save_json(tag_file, tags2hla)

    # Return a trie of that, and the
    return build_trie(list(tags2hla.keys())), tags2hla


def infer_hla_allele(pot_hla_seq, search_trie, tags2hla):
    """
    :param pot_hla_seq: str, nucleotide or amino acid sequence that (maybe) contains an HLA seq
    :param search_trie: Aho-Corasick object, detailing the appropriate trie to search HLA strings
    :param tags2hla: dict describing which HLA genes are covered by a specific tag sequence
    :return: 2 items: list of str detailing top scoring alleles (sorted alphabetically), & int of their  tag count
    """

    pot_hla_seq = pot_hla_seq.upper()
    matches = search_trie.findall(pot_hla_seq)
    if matches:
        all_matching_alleles = coll.Counter(flatten([tags2hla[x[0]] for x in matches])).most_common()
        highest_score = all_matching_alleles[0][1]
        most_common = [x for x in all_matching_alleles if x[1] == highest_score]
        most_common_alleles = [x[0] for x in most_common]
        most_common_alleles.sort()
        return most_common_alleles, highest_score

    else:
        return '', ''


def flatten(list_of_lists):
    """
    :param list_of_lists: pretty well described in the name here
    :return: flattened list of items within parent lists
    """
    return [x for xs in list_of_lists for x in xs]


def infer(seq, digits, seqtype, hla_loci, data_dir, lower_len, higher_len, window_len):
    """
    :param seq: str, nucletide or amino acid to try to identify an HLA allele in
    :param digits: int, resolution of HLA allele number (2/4/6/8)
    :param seqtype: str, sequence type as per IMGTHLA (gen, nuc, prot)
    :param hla_loci: list of str, detailing IMGTLA pre-asterisk gene identifiers
    :param data_dir: str, path to hladl data directory
    :param lower_len: int, lower length limit of sequence allowed (in amino acids)
    :param higher_len: int, upper length limit of sequence allowed (in amino acids)
    :param window_len: int, length of sliding window to use for overlapping tags
    :return: 2 items: list of str of inferred alleles, and int of # of tags they matched
    """

    # Get the relevant data, and search the sequence
    hla_loci = hla_loci.split(',')
    trie, tags = get_trie_data(digits, seqtype, data_dir, hla_loci, lower_len, higher_len, window_len)

    # TODO add automatic sequence type checks?
    inferred_alleles, tag_count = infer_hla_allele(seq, trie, tags)

    return inferred_alleles, tag_count
