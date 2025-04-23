# -*- coding: utf-8 -*-

import os
import gzip
import json
from . import hladlfunctions as fxn
from . import download as dl


def seq(allele, digits, seqtype, mode, output_mode, data_dir):

    # Check input parameters
    fxn.check_digits(digits)
    if '*' not in allele:
        raise IOError("HLA allele ID should be the gene name minus 'HLA-': it requires the asterisk.")
    elif len(allele[allele.index('*'):]) != int(digits * 1.5):
        raise IOError("Requested allele length is not compatible with the requested digit resolution.")

    mode = mode.lower()
    if mode not in fxn.modes:
        raise IOError(f"Requested mode ({mode}) is not a recognised mode ({fxn.modes}).")

    if mode == 'ecd' and (seqtype == 'nuc' or allele[0] not in ['A', 'B', 'C']):
        raise IOError("The extracellular domain mode is currently only configured"
                      " to work with classical MHC-I protein sequences.")

    # Check to see if the relevant data is present
    type_match = '_' + str(digits) + '_' + seqtype
    data_files = [x for x in os.listdir(data_dir) if x.endswith('.json.gz') and type_match in x]

    if not data_files:
        print("Necessary data not detected: downloading. ")
        dl.get_data(seqtype, digits, data_dir)
        data_files = [x for x in os.listdir(data_dir) if x.endswith('.json.gz') and type_match in x]

    # Use the most recent entry
    data_files.sort()
    recent = data_files[-1]

    hla_file = os.path.join(data_dir, recent)
    with gzip.open(hla_file, 'rt') as in_file:
        hla = json.load(in_file)

    if allele not in hla:
        raise IOError("Allele not present in HLA dictionary.")
    else:
        hla_seq = hla[allele]

    # Trim off leader and trans-membrane/intracellular portions if requested
    if mode == 'ecd':
        hla_len = len(hla_seq)
        if hla_len < 350 or hla_len > 380:
            raise IOError(f"Unable to extract extracellular domain, sequence an unexpected length ({hla_len} AA).")
        hla_seq = hla_seq[24:308]
        # TODO make smarter? PWMs?

    if output_mode == 'stdout':
        return hla_seq
    elif output_mode == 'fasta':
        out_str = fxn.fastafy(allele, hla_seq)
        out_name = allele.replace('*', '').replace(':', '-') + '.fasta'
        with open(out_name, 'w') as out_file:
            out_file.write(out_str)
