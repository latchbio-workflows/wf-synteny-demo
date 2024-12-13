import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd
from latch.resources.tasks import (
    large_gpu_task,
    large_task,
    medium_task,
    small_gpu_task,
    small_task,
    v100_x1_task,
    v100_x4_task,
    v100_x8_task,
)
from latch.types.directory import LatchDir, LatchOutputDir
from latch.types.file import LatchFile

sys.stdout.reconfigure(line_buffering=True)


@dataclass
class Sample:
    """Represents a sample with associated data and processing parameters."""

    identifier: str
    forward_read: LatchFile
    reverse_read: LatchFile
    reference_file: LatchFile
    outdir: str


"""
Latch Task Decorators

CPU-only Tasks:
@small_task: 2 CPUs, 4 GB memory
@medium_task: 32 CPUs, 128 GB memory
@large_task: 96 CPUs, 192 GB memory

GPU-enabled Tasks:
@small_gpu_task: 8 CPUs, 32 GB memory, 1 GPU (24 GB VRAM, 9,216 CUDA cores)
@large_gpu_task: 31 CPUs, 120 GB memory, 1 GPU (24 GB VRAM, 9,216 CUDA cores)

V100 GPU Tasks:
@v100_x1_task: 1 NVIDIA V100 GPU
@v100_x4_task: 4 NVIDIA V100 GPUs
@v100_x8_task: 8 NVIDIA V100 GPUs
"""


@small_task
def preprocess_task(
    fastq_directory: LatchDir,
    reference_file: LatchFile,
    output_directory: LatchOutputDir,
) -> List[Sample]:
    print(f"pandas version: {pd.__version__}")

    subprocess.run(
        [
            "blastn",
            "-version",
        ],
        check=True,
    )

    """Preprocesses input data and creates a list of Sample objects."""
    sample_sets = []
    fastq_files = {}

    # Group FASTQ files by sample name
    for file in fastq_directory.iterdir():
        if isinstance(file, LatchFile):
            file_name = file.remote_path.split("/")[-1]
            if "_R1" in file_name or "_R2" in file_name:
                sample_name = file_name.split("_R")[0]
                read_type = "R1" if "_R1" in file_name else "R2"
                fastq_files.setdefault(sample_name, {})[read_type] = file

    # Create Sample objects for each pair of FASTQ files
    for sample_name, files in fastq_files.items():
        if files.get("R1") and files.get("R2"):
            sample_sets.append(
                Sample(
                    identifier=sample_name,
                    forward_read=files["R1"],
                    reverse_read=files["R2"],
                    reference_file=reference_file,
                    outdir=output_directory.remote_path,  # This saves the Latch location for outputs
                )
            )

    print(sample_sets)

    return sample_sets


@small_task
def quantify_task(sample: Sample) -> LatchFile:
    """Performs a simple operation on a given sample and writes results to a file."""
    # Downloads LatchFiles to workflow environment with the .local_path call
    forward_read_local_path = Path(sample.forward_read.local_path)
    reverse_read_local_path = Path(sample.reverse_read.local_path)

    # Create output file in the workflow environment
    output_filename = f"task_{sample.identifier}.txt"
    output_path = Path("/root") / output_filename

    # Write input file paths to the output file
    with open(output_path, "w") as file:
        file.write(f"Forward read: {forward_read_local_path}\n")
        file.write(f"Reverse read: {reverse_read_local_path}\n")

    print(f"Information written to {output_path}")

    # Return the output file as a LatchFile at the needed location
    return LatchFile(
        path=str(output_path), remote_path=f"{sample.outdir}/{output_filename}"
    )


@small_task
def summarize_task(
    processed_samples: List[LatchFile],
    optional_bool: bool,
    output_directory: LatchOutputDir,
) -> LatchFile:
    """Creates a summary of processed samples by listing their filenames."""
    # Create a summary file
    summary_filename = "processed_samples_list.txt"
    summary_path = Path("/root") / summary_filename

    with open(summary_path, "w") as summary_file:
        summary_file.write("List of Processed Sample Files\n")
        summary_file.write("==============================\n")
        summary_file.write(f"Bool was {optional_bool}\n\n")
        for sample in processed_samples:
            summary_file.write(f"{sample.remote_path}\n")
        summary_file.write(
            f"\nTotal number of processed samples: {len(processed_samples)}\n"
        )

    print(f"Summary list written to {summary_path}")

    # Return the summary file as a LatchFile
    return LatchFile(
        path=str(summary_path),
        remote_path=f"{output_directory.remote_path}/{summary_filename}",
    )
