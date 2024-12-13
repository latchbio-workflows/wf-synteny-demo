from latch import map_task
from latch.resources.workflow import workflow
from latch.types.directory import LatchDir, LatchOutputDir
from latch.types.file import LatchFile
from latch.types.metadata import LatchAuthor, LatchMetadata, LatchParameter

from wf.task import preprocess_task, quantify_task, summarize_task

metadata = LatchMetadata(
    display_name="SyntenyAI Workflow",
    author=LatchAuthor(name="LatchBio"),
    parameters={
        "fastq_directory": LatchParameter(
            display_name="FASTQ Directory",
            description="Directory of FASTQ files.",
            batch_table_column=True,
        ),
        "reference_file": LatchParameter(
            display_name="Reference File",
            description="Reference FASTA file.",
            batch_table_column=True,
        ),
        "optional_bool": LatchParameter(
            display_name="Bool Control",
            description="Example of a bool.",
            batch_table_column=True,
        ),
        "output_directory": LatchParameter(
            display_name="Output Directory",
            description="Output directory location.",
            batch_table_column=True,
        ),
    },
)


@workflow(metadata)
def synteny_wf(
    fastq_directory: LatchDir,
    reference_file: LatchFile,
    optional_bool: bool,
    output_directory: LatchOutputDir,
) -> LatchFile:
    # Step 1: Preprocess the input data
    samples = preprocess_task(
        fastq_directory=fastq_directory,
        reference_file=reference_file,
        output_directory=output_directory,
    )

    # Step 2: Quantify samples in parallel
    processed_samples = map_task(quantify_task)(sample=samples)

    # Step 3: Summarize the results
    return summarize_task(
        processed_samples=processed_samples,
        optional_bool=optional_bool,
        output_directory=output_directory,
    )


"""
This workflow demonstrates the use of Latch SDK to create a bioinformatics pipeline.
It processes FASTQ files, performs quantification, and summarizes the results.

Workflow steps:
1. Preprocessing: Prepare input data for parallel processing.
2. Quantification: Process each sample in parallel using map_task.
3. Summarization: Aggregate results from all processed samples.

Args:
    fastq_directory (LatchDir): Directory containing FASTQ files.
    reference_file (LatchFile): Reference file for alignment or quantification.
    optional_bool (bool): Option demo bool.
    output_directory (LatchOutputDir): Directory for saving results.

Returns:
    LatchFile: Summary file of the workflow results.
"""
