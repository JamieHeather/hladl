# -*- coding: utf-8 -*-

import os
import sys

import typer
from typing_extensions import Annotated
from . import download as dl
from . import get_seq as get
from . import infer_allele
from . import __version__
from . import hladlfunctions as fxn

# Ensure correct importlib-resources function imported
if sys.version_info < (3, 9):
    import importlib_resources                              # PyPI
else:
    import importlib.resources as importlib_resources       # importlib.resources


app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})


data_files = importlib_resources.files("hladldata")
data_dir = os.path.dirname(str(data_files / '__init__.py'))


@app.callback()
def callback():
    """
    hladl: a command line tool for getting HLA sequences
    """


@app.command()
def init(seqtype: Annotated[str, typer.Option("--seqtype", "-s",
            help="Type of sequence to download: gen, nuc, prot, or all.")] = 'all',
         digits: Annotated[int, typer.Option("--digits", "-d",
            help="Digit length to download at: 2, 4, 6.")] = 4,
         ):
    """
    Initialise the tool by automatically downloading the HLA data from https://github.com/ANHIG/IMGTHLA
    """

    dl.get_data(seqtype, digits, data_dir)


@app.command()
def seq(allele: Annotated[str, typer.Option("--allele", "-a",
                  help="Allele to download, in the format [ABC]*XX:XX, with the appropriate number of digits.")],
        digits: Annotated[int, typer.Option("--digits", "-d",
                  help="Digit length to download at: 2, 4, 6.")] = 4,
        seqtype: Annotated[str, typer.Option("--seqtype", "-s",
                  help="Type of sequence to download: nuc or prot")] = 'prot',  # TODO add gen?
        mode: Annotated[str, typer.Option('-m', '--mode',
                  help="hladl mode: full (regular), ecd (extracellular domain")] = 'full',
        output_mode: Annotated[str, typer.Option('-om', '--output_mode',
                  help="Output mode: stdout (terminal), fa (FASTA)")] = 'stdout',
        ):
    """
    Output the sequence of a specified HLA allele
    """

    hla_seq = get.seq(allele, digits, seqtype, mode, output_mode, data_dir)
    if output_mode == 'stdout':
        if hla_seq:
            print(hla_seq)
        else:
            print("Failed to grab the", seqtype, "sequence for", allele, "at", str(digits), "resolution. ")



@app.command()
def infer(seq: str,
          digits: Annotated[int, typer.Option("--digits", "-d",
                  help="Digit length to download at: 2, 4, 6.")] = 4,
          seqtype: Annotated[str, typer.Option("--seqtype", "-s",
                  help="Type of sequence to download: nuc or prot")] = 'prot',
          # TODO add gen?
          hla_loci: Annotated[str, typer.Option("--hla_loci", "-L",
                help='Comma-delimited list of IMGTHLA-formatted gene prefixes'
                     ' (before the *)')] = ','.join(fxn.featured_mhci),
          output_mode: Annotated[str, typer.Option("--output_mode", "-om",
                 help="Output mode: stdout (terminal), fa (FASTA)")] = 'stdout',
          lower_len: Annotated[int, typer.Option("--lower_len", "-l",
                 help="Lower length limit of allele product (amino acids) to filter. 0 = no filter.")] = 350,
          upper_len: Annotated[int, typer.Option("--upper_len", "-u",
                 help="Upper length limit of allele product (amino acids) to filter. 0 = no filter.")] = 380,
          window_len: Annotated[int, typer.Option("--window_len", "-wl",
                 help="Sliding window length .")] = 20):
    """
    Given an HLA sequence, infer what allele(s) it could be derived from
    """

    inferred_alleles, tag_count = infer_allele.infer(seq, digits, seqtype, hla_loci, data_dir, lower_len, upper_len, window_len)

    if output_mode.lower() == 'stdout':
        print(f"Detected top-matching alleles: {inferred_alleles}")
        print(f"Number of tags per hit: {tag_count}")



@app.command()
def dd():
    """
    Print the location of the hladl data directory
    """
    print(data_dir)
    return data_dir


@app.command()
def version():
    """
    Print the hladl package version
    """
    print(__version__)
