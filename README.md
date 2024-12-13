# SyntenyAI Demo Workflow

This workflow demonstrates the use of the Latch SDK to create a bioinformatics pipeline. It processes FASTQ files, performs quantification, and summarizes the results.

## Workflow Steps

1. Preprocessing: Prepare input data for parallel processing.
2. Quantification: Process each sample in parallel using map_task.
3. Summarization: Aggregate results from all processed samples.

## Inputs

- fastq_directory (LatchDir): Directory containing FASTQ files.
- reference_file (LatchFile): Reference file for alignment or quantification.
- optional_bool (bool): Optional demo flag.
- output_directory (LatchOutputDir): Directory for saving results.

## Latch Guide

This repository includes comments and notes to explain its functionality. Useful pointers to get started:

- The Dockerfile determines the environment in which the workflow runs.
- The __init__.py file defines parameters, execution flow, metadata, etc.
- Other Python files are regular Python files with Latch task decorators.
- The version file contains the workflow's version.
- LatchFile, LatchDir, etc., are used in this workflow to demonstrate data manipulation within the workflow environment.

To push code to the Latch Platform when complete, run:

latch workspace

latch register .

with the Latch CLI in the terminal.

## Useful Links

- https://wiki.latch.bio/docs/getting-started/quick-start
- https://wiki.latch.bio/docs/getting-started/authorizing-your-own-workflow
- https://wiki.latch.bio/data/data-command-line
- https://wiki.latch.bio/workflows/sdk/defining-a-workflow/defining-cloud-resources#defining-cloud-resources
