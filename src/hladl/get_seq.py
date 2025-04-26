# -*- coding: utf-8 -*-

from . import hladlfunctions as fxn


def seq(allele, digits, seqtype, mode, output_mode, data_dir):
    """
    :param allele: str, IMGTHLA format of HLA gene to produce
    :param digits: int, resolution of HLA allele number (2/4/6/8)
    :param seqtype: str, sequence type as per IMGTHLA (gen, nuc, prot)
    :param mode: str, mode describing sequences sought
    :param output_mode: str, describing how to output the results
    :param data_dir: str, path to hladl data directory
    :return: depends on mode: may return str of pulled allele, or save to file as requested
    """

    # Check input parameters
    fxn.check_digits(digits)
    if '*' not in allele:
        raise IOError("HLA allele ID should be the gene name minus 'HLA-': it requires the asterisk.")
    elif len(allele[allele.index('*'):]) != int(digits * 1.5):
        raise IOError("Requested allele length is not compatible with the requested digit resolution.")

    mode = mode.lower()
    if mode not in fxn.modes:
        raise IOError(f"Requested mode ({mode}) is not a recognised mode ({fxn.modes}).")

    if mode == 'ecd' and (seqtype == 'nuc' or allele[0] not in fxn.featured_mhci):
        raise IOError("The extracellular domain mode is currently only configured"
                      " to work with classical MHC-I protein sequences.")

    # Get the relevant data
    hla, data_file = fxn.get_data(digits, seqtype, data_dir)

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
