# -*- coding: utf-8 -*-

import requests
import json
import gzip
import os
import collections as coll
from . import hladlfunctions as fxn

data_url_base = 'https://raw.githubusercontent.com/ANHIG/IMGTHLA/refs/heads/Latest/fasta/hla_REPLACE.fasta'
release_url = 'https://raw.githubusercontent.com/ANHIG/IMGTHLA/refs/heads/Latest/release_version.txt'


def get_data(seqs, digits, data_dir):

    seqs = seqs.lower()
    if seqs not in ['nuc', 'prot', 'all']:
        raise IOError("Sequence type needs to be one of "
                      "'gen' (gDNA), 'nuc' (cDNA)', 'prot' (AA), or 'all' (get all 3). ")
    if seqs == 'all':
        seqs = ['nuc', 'prot']
    else:
        seqs = [seqs]

    fxn.check_digits(digits)

    # Grab release info first
    response = requests.get(release_url, headers={})
    if response.status_code == 200:
        release_dat = response.text.split('\n')
        release_line = [x for x in release_dat if 'version:' in x]
        if len(release_line) == 1:
            release = release_line[0].split(' ')[-1]
        else:
            raise IOError("Unable to identify release # from repo!")

    out_prefix = release + '_' + str(digits) + '_'

    print(f"Downloading reference data ('{seqs}'), at {digits} digit annotation, saving files to:")
    # Then grab the corresponding file(s)
    for seq in seqs:
        url = data_url_base.replace('REPLACE', seq)

        response = requests.get(url, headers={})
        if response.status_code == 200:
            data = response.content.decode()

            raw_path = os.path.join(data_dir, out_prefix + seq + '.fasta.gz')
            with gzip.open(raw_path, 'wt') as ref_file:
                ref_file.write(data)

            # Then read that file in
            hla_dict = coll.defaultdict(str)
            with gzip.open(raw_path, 'rt') as ref_file:
                for fa_header, fa_seq, fa_null in fxn.readfq(ref_file):
                    full_gene = fa_header.split(' ')[1]
                    gene = fxn.trim_gene(digits, full_gene)

                    # Only take one sequence per allele at the requested resolution
                    if gene not in hla_dict:
                        hla_dict[gene] = fa_seq

            # Then write that out that dict for later use
            processed_path = os.path.join(data_dir, out_prefix + seq + '.json.gz')
            with gzip.open(processed_path, 'wt') as json_file:
                json.dump(hla_dict, json_file)

            print('\t' + processed_path)

        else:
            raise ConnectionError("Unable to reach the ANHIG/IMGTHLA Github repo!")

    print("Successfully completed hladl init!")
