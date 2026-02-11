#!/usr/bin/env python3
"""
Prepare presentation files for a given date by extracting and renaming them
from a GradeScope submissions export.
"""

import argparse
import csv
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path


def parse_schedule(tsv_path, target_date):
    """
    Parse the schedule TSV and return presentations for the target date.

    Returns a list of (start_time, student_names) tuples.
    """
    presentations = []

    with open(tsv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)

        # Find the column index for the target date
        date_col = None
        for i, col in enumerate(header):
            if target_date.lower() in col.lower():
                date_col = i
                break

        if date_col is None:
            raise ValueError(f"Date '{target_date}' not found in schedule. Available dates: {header[1:]}")

        for row in reader:
            if len(row) <= date_col:
                continue

            time_slot = row[0].strip()
            students = row[date_col].strip()

            if not students:
                continue

            # Extract start time from slot like "3:30 - 3:40 pm"
            match = re.match(r'(\d+:\d+)', time_slot)
            if match:
                start_time = match.group(1).replace(':', '')
                # Parse student names (comma-separated)
                student_list = [s.strip() for s in students.split(',')]
                presentations.append((start_time, student_list))

    return presentations


def normalize_name(name):
    """Normalize a name for matching: lowercase, remove extra spaces/punctuation."""
    # Replace commas with spaces, collapse multiple spaces, lowercase
    normalized = re.sub(r'[,]+', ' ', name)
    normalized = re.sub(r'\s+', ' ', normalized).strip().lower()
    return normalized


def extract_link_from_response(response_str):
    """Extract URL from the Question 1 Response field."""
    if not response_str:
        return None
    # Look for URLs in the response (format: "1"=>"URL" or similar)
    url_match = re.search(r'https?://[^\s"\'}\]]+', response_str)
    if url_match:
        return url_match.group(0)
    return None


def parse_metadata(metadata_path):
    """
    Parse the submission metadata CSV.

    Returns a dict mapping normalized name -> (display_name, submission_id)
    Also returns reverse lookups for flexible matching.
    Also returns a dict mapping submission_id -> link (if any).
    """
    student_to_submission = {}
    normalized_lookup = {}
    submission_links = {}

    with open(metadata_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            first_name = row.get('First Name', '').strip()
            last_name = row.get('Last Name', '').strip()
            submission_id = row.get('Submission ID', '').strip()
            response = row.get('Question 1 Response', '')

            if first_name and last_name and submission_id:
                full_name = f"{first_name} {last_name}"
                student_to_submission[full_name] = submission_id

                # Add normalized version for flexible matching
                normalized = normalize_name(full_name)
                normalized_lookup[normalized] = (full_name, submission_id)

                # Also add "Last First" order for matching
                reversed_name = normalize_name(f"{last_name} {first_name}")
                if reversed_name not in normalized_lookup:
                    normalized_lookup[reversed_name] = (full_name, submission_id)

                # Extract link if present
                link = extract_link_from_response(response)
                if link and submission_id not in submission_links:
                    submission_links[submission_id] = link

    return student_to_submission, normalized_lookup, submission_links


def normalize_date(date_str):
    """Convert date string to a normalized format for filenames."""
    # Remove day name if present, keep just the date part
    # e.g., "Feb 10" -> "Feb10"
    parts = date_str.split()
    # Filter out day names
    date_parts = [p for p in parts if p.lower() not in ['mon', 'tue', 'wed', 'thur', 'thu', 'fri', 'sat', 'sun']]
    return ''.join(date_parts)


def main():
    parser = argparse.ArgumentParser(
        description='Prepare presentation files for a given date.'
    )
    parser.add_argument('input_dir', help='Input directory containing .tsv and submissions.zip')
    parser.add_argument('date', help='Date string to match (e.g., "Feb 10")')
    parser.add_argument('output_dir', help='Output directory for renamed presentation files')

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    target_date = args.date

    # Find the TSV file
    tsv_files = list(input_dir.glob('*.tsv'))
    if not tsv_files:
        raise FileNotFoundError(f"No .tsv file found in {input_dir}")
    tsv_path = tsv_files[0]

    # Find the submissions.zip
    zip_path = input_dir / 'submissions.zip'
    if not zip_path.exists():
        raise FileNotFoundError(f"submissions.zip not found in {input_dir}")

    # Parse the schedule
    presentations = parse_schedule(tsv_path, target_date)
    print(f"Found {len(presentations)} presentation slots for '{target_date}'")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract zip to temp directory and process
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(temp_path)

        # Find the export directory
        export_dirs = list(temp_path.glob('assignment_*_export'))
        if not export_dirs:
            raise FileNotFoundError("No assignment export directory found in zip")
        export_dir = export_dirs[0]

        # Parse metadata
        metadata_path = export_dir / 'submission_metadata.csv'
        if not metadata_path.exists():
            raise FileNotFoundError("submission_metadata.csv not found in zip")

        student_to_submission, normalized_lookup, submission_links = parse_metadata(metadata_path)

        # Normalize date for filename
        date_normalized = normalize_date(target_date)

        # Collect all scheduled students for this date (normalized for matching)
        scheduled_students = set()
        scheduled_students_normalized = set()
        for _, student_list in presentations:
            for student in student_list:
                scheduled_students.add(student)
                scheduled_students_normalized.add(normalize_name(student))

        # Report submissions that don't match any scheduled student
        unmatched_submissions = []
        for student_name, submission_id in student_to_submission.items():
            normalized = normalize_name(student_name)
            if student_name not in scheduled_students and normalized not in scheduled_students_normalized:
                unmatched_submissions.append((student_name, submission_id))

        if unmatched_submissions:
            print(f"\nSubmissions not matching any student scheduled for '{target_date}':")
            for student_name, submission_id in sorted(unmatched_submissions):
                print(f"  - {student_name} (submission {submission_id})")
            print()

        # Process each presentation
        for start_time, student_list in presentations:
            # Find submission for any student in the group
            submission_id = None
            matched_student = None

            for student in student_list:
                # Try exact match first
                if student in student_to_submission:
                    submission_id = student_to_submission[student]
                    matched_student = student
                    break
                # Try normalized match
                normalized = normalize_name(student)
                if normalized in normalized_lookup:
                    matched_student, submission_id = normalized_lookup[normalized]
                    break

            if not submission_id:
                print(f"  Warning: No submission found for {student_list}")
                continue

            # Find submission directory
            submission_dir = export_dir / f'submission_{submission_id}'
            student_name = student_list[0].replace(' ', '_')
            has_files = submission_dir.exists() and any(submission_dir.iterdir())

            if has_files:
                # Copy all files from submission
                for file_path in submission_dir.iterdir():
                    if file_path.is_file():
                        # Create new filename: DATE-STARTTIME-STUDENTNAME-ORIGINALFILENAME
                        original_name = file_path.name

                        new_name = f"{date_normalized}-{start_time}-{student_name}-{original_name}"
                        dest_path = output_dir / new_name

                        shutil.copy2(file_path, dest_path)
                        print(f"  Created: {new_name}")
            elif submission_id in submission_links:
                # No files, but there's a link - create an HTML redirect
                link = submission_links[submission_id]
                html_name = f"{date_normalized}-{start_time}-{student_name}-slides.html"
                html_path = output_dir / html_name
                html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url={link}">
    <title>Redirecting to slides...</title>
</head>
<body>
    <p>Redirecting to <a href="{link}">{link}</a></p>
</body>
</html>
'''
                html_path.write_text(html_content)
                print(f"  Created: {html_name} (link to external slides)")
            else:
                print(f"  Warning: No files or link found for {matched_student}")

    print(f"\nDone! Files written to {output_dir}")


if __name__ == '__main__':
    main()
