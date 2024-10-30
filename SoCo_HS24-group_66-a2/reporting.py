import csv, sys
from datetime import datetime
from time import perf_counter


def summary_stats(trace_file):
    summary_calls = {}
    with open(trace_file, mode = "r", newline ="") as f:
        reader = csv.reader(f)
        next(reader) #skip header
        for row in reader:
            call_id, timestamp, func_name, event_type = row

            if func_name not in summary_calls:
                summary_calls[func_name] = []
            
            if event_type == "start":
                summary_calls[func_name].append({"id": call_id, "start_time": perf_counter(), "end_time":None})
            elif event_type == "stop":
                 for call in summary_calls[func_name]: 
                    if call["id"] == call_id and call["end_time"] is None:
                        call["end_time"] = perf_counter()
                        break #only one end per id
    return summary_calls

def calculate_stats(calls):
    stats = {}
    for func_name, entries in calls.items():
        total_time = 0.0
        num_calls = 0

        for entry in entries:
            if entry["end_time"] is not None:
                
                total_time += (entry["end_time"] - entry["start_time"])*1000.0  #display in ms
                num_calls += 1

        if num_calls > 0:
            avrg_time = float(total_time /num_calls)
            stats[func_name] =[func_name, num_calls, total_time, avrg_time]

    return list(stats.values()) #so duplicates are eliminated

def display_stats(stats):
    print("\n| Function Name | Num. of calls | Total Time (ms) | Average Time (ms)|")
    print("|--------------------------------------------------------------------|")
    for stat in stats:
        print(f"|{stat[0]:<15}|{stat[1]:<15}|{stat[2]:<17.3f}|{stat[3]:<18.3f}|")

def main():
    if len(sys.argv) != 2:  #Usage: python reporting.py <trace_file>
        print("Arguments are wrong")
        sys.exit(1)     #prevents running code faultly

    try:
        trace_file = sys.argv[1]
        calls = summary_stats(trace_file)
        stats = calculate_stats(calls)
        display_stats(stats)
    except FileNotFoundError:   #if file is not found
        print("Error: Trace file not found")
        sys.exit(1)     
    except Exception as e:
        print("Error occurred")
        sys.exit(1)     #if something else happens

if __name__ == "__main__":
    main()


                

