#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

include { dorado_trim } from './modules/process_nanopore.nf'


workflow {
    ch_samplesheet = Channel.fromPath(params.samplesheet)
    ch_alias_by_barcode = ch_samplesheet.splitCsv(header: true, sep: ',').map{ it -> [it['alias'], it['barcode']] }
    ch_run_dir = Channel.fromPath(params.run_dir).filter{ it -> it.isDirectory() }

    main:

    dorado_trim(ch_alias_by_barcode.combine(ch_run_dir))

    ch_trimming_counts = dorado_trim.out.trimmed_adapter_primer_counts

    ch_trimming_counts.map{ it -> it[2] }.collectFile(keepHeader: true, newLine: true, name: 'trimming_summary.csv', storeDir: params.outdir)
}
