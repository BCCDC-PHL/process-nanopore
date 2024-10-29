# process-nanopore

# Setup
This pipeline assumes that [dorado](https://github.com/nanoporetech/dorado) is available on the `PATH`. It is known to be compatible with dorado-linux-x64 v0.8.0, and may not be compatible with other versions.

## Usage

```
nextflow run BCCDC-PHL/process-nanopore \
  --run_dir </path/to/nanopore_run>
  --samplesheet </path/to/nanopore_run/sample_sheet.csv>
  --outdir </path/to/nanopore_run/fastq_pass_combined>
```
