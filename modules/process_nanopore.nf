process dorado_trim {

    tag { sample_id + " / " + barcode }

    publishDir "${params.outdir}", pattern: "${sample_id}_${barcode}_RL.fastq.gz", mode: 'copy'
    
    input:
    tuple val(alias), val(barcode), path(run_dir)

    output:
    tuple val(sample_id), val(barcode), path("${sample_id}_${barcode}_RL.fastq.gz"), emit: fastq
    tuple val(sample_id), val(barcode), path("${sample_id}_dorado_trim.log"), emit: log
    tuple val(sample_id), val(barcode), path("${sample_id}_trimmed_adapter_primer_counts.csv"), emit: trimmed_adapter_primer_counts

    script:
    sample_id = alias.split("_")[0]
    """
    for fastq in ${run_dir}/fastq_pass/${alias}/*fastq.gz; do
    dorado trim \
	--threads ${task.cpus} \
	-vv \
	--emit-fastq \
	\${fastq} \
	>> ${sample_id}_${barcode}_RL.fastq \
	2>> ${sample_id}_dorado_trim.log
    done

    gzip ${sample_id}_${barcode}_RL.fastq

    parse_dorado_trim_log.py --library-id ${sample_id} ${sample_id}_dorado_trim.log > ${sample_id}_trimmed_adapter_primer_counts.csv
    """
}
