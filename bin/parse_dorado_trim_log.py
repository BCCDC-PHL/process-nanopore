#!/usr/bin/env python3

import argparse
import csv
import json
import sys

from pathlib import Path


def parse_line(line: str):
    """
    Parse a line of the Dorado trim log file.

    :param line: Line from the Dorado trim log file.
    :type line: str
    :return: Parsed line. Keys: [adapter_primer_name, interval]
    :rtype: dict
    """
    known_intervals = [
        'front',
        'rear'
    ]
    parsed_line = {}
    line_split = line.split()
    adapter_primer_name = line_split[-1]
    parsed_line['adapter_primer_name'] = adapter_primer_name
    interval = line_split[4]
    if interval not in known_intervals:
        # Ideally we'd throw an exception here, but we'll just skip for now.
        # Our counts will be slightly off but it's difficult
        # To handle all of the different cases.
        return None
    
    parsed_line['interval'] = interval

    return parsed_line


def select_adapter_primer_detection_lines(adapter_primer_detection_file: Path):
    """
    Select adapter/primer detection lines from the Dorado trim log file.

    :param adapter_primer_detection_file: Path to the Dorado trim log file.
    :type adapter_primer_detection_file: Path
    :return: Generator of adapter/primer detection lines.
    :rtype: generator
    """
    with open(adapter_primer_detection_file, 'r') as f:
        for line in f:
            if 'Detected' in line:
                line = line.strip()
                # It looks like there may be some multithreading or concurrency issues with the Dorado trim log
                # We occasionally get lines that look like:
                # > Output records written: [2024-10-02 15:30:51.770] [trace] Checking adapter/primer PCR_PSK_rev
                # While most lines look like:
                # [2024-10-02 15:30:51.770] [trace] Detected adapter/primer PCR_PSK_rev in interval rear
                # So we need to remove the "> Output records written: " part.
                if line.startswith('> Output records written: '):
                    line = line[len('> Output records written: '):]
                yield line


def main(args):
    count_by_adapter_primer_by_interval = {
        'front': {},
        'rear': {},
    }
    for line in select_adapter_primer_detection_lines(args.dorado_trim_log):
        parsed_line = parse_line(line)
        if parsed_line is None:
            continue
        adapter_primer_name = parsed_line['adapter_primer_name']
        interval = parsed_line['interval']
        if adapter_primer_name not in count_by_adapter_primer_by_interval[interval]:
            count_by_adapter_primer_by_interval[interval][adapter_primer_name] = 0
        count_by_adapter_primer_by_interval[interval][adapter_primer_name] += 1

    output_fieldnames = []

    if args.library_id:
        output_fieldnames.append('library_id')

    output_fieldnames += [
        'adapter_primer_name',
        'interval',
        'count'
    ]

    writer = csv.DictWriter(sys.stdout, fieldnames=output_fieldnames, dialect='unix', quoting=csv.QUOTE_MINIMAL, extrasaction='ignore')
    writer.writeheader()

    output_lines = []
    for interval, adapter_primer_counts in count_by_adapter_primer_by_interval.items():
        for adapter_primer_name, count in adapter_primer_counts.items():
            output_lines.append({
                'library_id': args.library_id,
                'adapter_primer_name': adapter_primer_name,
                'interval': interval,
                'count': count
            })


    output_lines_sorted = sorted(output_lines, key=lambda x: x['count'], reverse=True)

    for output_line in output_lines_sorted:
        writer.writerow(output_line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse Dorado trim log file.')
    parser.add_argument('--library-id', type=str, help='Library ID.')
    parser.add_argument('dorado_trim_log', type=Path, help='Dorado trim log file.')
    args = parser.parse_args()
    main(args)
