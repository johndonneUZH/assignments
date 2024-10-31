import csv, sys
from datetime import datetime
from time import perf_counter
from prettytable import PrettyTable
from collections import defaultdict

def summary_stats(trace_file):
    summary_calls = defaultdict(dict)

    with open(trace_file, newline="") as f:
        reader = csv.reader(f)
        next(reader) # Skip the header row
        for row in reader:
            call_id, timestamp, func_name, event_type = row

            # Initialize entry for func_name if not already present
            if func_name not in summary_calls:
                summary_calls[func_name] = {}

            # Handle "start" events by storing start time for each call_id
            if event_type == "start":
                summary_calls[func_name][call_id] = {"start_time": timestamp, "end_time": None}

            # Handle "stop" events by updating end time for each call_id
            elif event_type == "stop":
                if call_id not in summary_calls[func_name]:
                    raise ValueError(f"Start event not found for call ID {call_id} of function {func_name}")
                summary_calls[func_name][call_id]["end_time"] = timestamp

    return summary_calls

from datetime import datetime

def calculate_stats(calls):
    stats = []
    for func_name, logs in calls.items():
        total_time = 0
        num_calls = 0

        for log in logs.values():  # Iterate over each call log entry
            if log["end_time"] is not None:
                datetime_format = "%Y-%m-%d %H:%M:%S.%f"
                start_time = datetime.strptime(log["start_time"], datetime_format)
                end_time = datetime.strptime(log["end_time"], datetime_format)
                
                # Calculate time difference in milliseconds
                time_diff_ms = (end_time - start_time).total_seconds() * 1000
                total_time += time_diff_ms
                num_calls += 1

        if num_calls > 0:
            avrg_time = total_time / num_calls  # Average time in milliseconds
            stats.append((func_name, num_calls, f'{total_time:.3f}', f'{avrg_time:.3f}'))

    return stats


def display_stats(stats):
    table = PrettyTable(["Function Name", "Num. of calls", "Total Time (ms)", "Average Time (ms)"])
    for stat in stats:
        table.add_row(stat)
    print(table)

def main():
    assert len(sys.argv) == 2, "Usage: python reporting.py <trace_file>"
    try:
        trace_file = sys.argv[1]
        calls = summary_stats(trace_file)
        stats = calculate_stats(calls)
        display_stats(stats)
    
    except Exception as e:
        raise e

if __name__ == "__main__":
    main()


                

