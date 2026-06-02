14340-YK RNASeq analysis information

2025-09-26

UM Advanced Genomics Core - agc-datateam@umich.edu


The NF-Core RNASeq pipeline was used to perform commonly desired tasks such as QC, trimming, alignment, quantification, etc.

You can find more details about this NF-Core pipeline at the following link:

https://nf-co.re/rnaseq/

There you will find details on the outputs, the process, and many additional details about this pipeline developed by the nf-core community.

We have added a handful of files to these outputs in order to provide additional information, which are detailed here:

- star_rsem/rsem.merged.gene_counts.annot.tsv
  - An annotated version of the gene expression count matrix provided by rsem, where annotation information has been obtained from BiomaRt.
- pipeline_info/ref_source_info_14340-YK.yaml
  - Useful information about the reference files that were used and where they can be downloaded
- pipeline_info/params_14340-YK.yaml
  - A parameters file that mirrors what was used for this analysis
- pipeline_info/samplesheet_14340-YK.csv
  - The samplesheet that mirrors what used for this analysis


** Note: The parameters file and samplesheet have some sections where the text "/path/to/" is a placeholder for the actual path to the resource
