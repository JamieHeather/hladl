# -*- coding: utf-8 -*-

import os
import sys

import typer
from typing_extensions import Annotated
from . import download as dl
from . import get_seq as get
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
    # TODO
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
    # TODO tidy up

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
    Output the sequence of a specified HLA allele.
    """

    hla_seq = get.seq(allele, digits, seqtype, mode, output_mode, data_dir)
    if output_mode == 'stdout':
        if hla_seq:
            print(hla_seq)
        else:
            print("Failed to grab the", seqtype, "sequence for", allele, "at", str(digits), "resolution. ")


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
