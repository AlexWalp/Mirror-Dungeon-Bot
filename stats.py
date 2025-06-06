import re
from collections import defaultdict

file = "game.log"

def parse_floors(log_file):
    with open(log_file, "r") as f:
        lines = f.readlines()

    floors = defaultdict(list)
    current_floor = None

    for line in lines:
        match = re.search(r"Floor (\d+)", line)
        if match:
            current_floor = int(match.group(1))
            continue

        if current_floor is not None:
            floors[current_floor].append(line)

    return floors

def time_between_actions(lines, word1, word2, start_line=0):
    time1, time2 = None, None
    last_index = start_line

    for i in range(start_line, len(lines)):
        line = lines[i]
        parts = line.split(" - ")
        if len(parts) < 2:
            continue

        timestamp_str = parts[0]
        timestamp = timestamp_str.replace(",", ".")

        if word1 in line and time1 is None:
            time1 = timestamp

        if word2 in line and time1 is not None:
            time2 = timestamp
            last_index = i + 1
            break

    if time1 and time2:
        h1, m1, s1 = map(float, time1.split(" ")[1].split(":"))
        h2, m2, s2 = map(float, time2.split(" ")[1].split(":"))
        return (h2 * 3600 + m2 * 60 + s2) - (h1 * 3600 + m1 * 60 + s1), last_index

    return None, last_index

def av_time(lines, word1, word2):
    total_time = 0
    count = 0
    start_line = 0

    while True:
        time_diff, start_line = time_between_actions(lines, word1, word2, start_line)
        if time_diff is None:
            break

        total_time += time_diff
        count += 1

    avg = total_time / count if count > 0 else 0
    return avg, count

def format_time(seconds):
    seconds = seconds or 0
    minutes = int(seconds // 60)
    sec = int(seconds % 60)
    return f"{minutes}:{sec:02d}"

def parse_runs(lines):
    run_times = []
    failed_time = 0
    failure_count = 0

    current_run_start = None

    for i, line in enumerate(lines):
        if "Iteration" in line:
            timestamp = get_timestamp(line)
            current_run_start = timestamp
        elif "Completed" in line and current_run_start is not None:
            run_end = get_timestamp(line)
            run_times.append(run_end - current_run_start)
            current_run_start = None
        elif "Failed" in line and current_run_start is not None:
            run_end = get_timestamp(line)
            failed_time += run_end - current_run_start
            failure_count += 1
            current_run_start = None

    return run_times, failed_time, failure_count

def get_timestamp(line):
    parts = line.split(" - ")
    if len(parts) < 2:
        return 0
    timestamp_str = parts[0].replace(",", ".")
    h, m, s = map(float, timestamp_str.split(" ")[1].split(":"))
    return h * 3600 + m * 60 + s

def floor_total_times(lines):
    floors = {}
    current_floor = None
    floor_start_time = None
    for i, line in enumerate(lines):
        match = re.search(r"Floor (\d+)", line)
        if match:
            if current_floor is not None and floor_start_time is not None:
                floor_end_time = get_timestamp(line)
                if current_floor not in floors:
                    floors[current_floor] = []
                floors[current_floor].append(floor_end_time - floor_start_time)
            current_floor = int(match.group(1))
            floor_start_time = get_timestamp(line)
        elif "Iteration" in line or "Completed" in line or "Failed" in line:
            if current_floor is not None and floor_start_time is not None:
                end_time = get_timestamp(line)
                if current_floor not in floors:
                    floors[current_floor] = []
                floors[current_floor].append(end_time - floor_start_time)
                current_floor = None
                floor_start_time = None
    return floors


def export():
    import csv
    with open("dungeon_stats.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # 1. Floor Fight Statistics
        writer.writerow(["Floor Fight Statistics"])
        writer.writerow(["Floor", "Fight Type", "Avg Time", "Count"])
        for floor in sorted(floors_data.keys()):
            lines_floor = floors_data[floor]
            for fight in fight_types:
                avg, count = av_time(lines_floor, fight, "over")
                writer.writerow([floor, fight, format_time(avg), count])

        writer.writerow([])

        # 2. Floor Time Summary
        writer.writerow(["Floor Time Summary"])
        writer.writerow(["Floor", "Avg Time", "Count"])
        for floor in sorted(floor_times.keys()):
            total = sum(floor_times[floor])
            avg = total / len(floor_times[floor])
            writer.writerow([floor, format_time(avg), len(floor_times[floor])])

        writer.writerow([])

        # 3. Run Summary
        writer.writerow(["Run Summary"])
        writer.writerow(["Successful Runs", "Avg Run Time", "Failed Runs", "Total Time Wasted"])
        writer.writerow([len(run_times), format_time(avg_run_time), failed_count, format_time(failed_total_time)])
    print("\nSuccessfully exported to dungeon_stats.csv")


if __name__ == "__main__":
    with open(file, "r") as f:
        lines = f.readlines()

    floors_data = parse_floors(file)
    fight_types = ["Normal", "Focused", "Risky", "Miniboss", "Boss"]

    print("📊 Floor Fight Statistics", end="")
    for floor in sorted(floors_data.keys()):
        print(f"\n🧱 Floor {floor}")
        lines_floor = floors_data[floor]
        print(f"{'Type':<9} | {'Avg Time':^10} | {'Count':^5}")
        print("-" * 32)
        for fight in fight_types:
            avg, count = av_time(lines_floor, fight, "over")
            print(f"{fight:<9} | {format_time(avg):^10} | {count:^5}")

    print("\n📦 Floor Time Summary")
    print(f"{'Floor':^6}| {'Avg Time':^8} | {'Count':^5}")
    print("-" * 26)
    floor_times = floor_total_times(lines)
    for floor in sorted(floor_times.keys()):
        total = sum(floor_times[floor])
        avg = total / len(floor_times[floor])
        print(f"{floor:^6}| {format_time(avg):^8} | {len(floor_times[floor]):^5}")

    print("\n🏁 Run Summary")
    run_times, failed_total_time, failed_count = parse_runs(lines)
    avg_run_time = sum(run_times) / len(run_times) if run_times else 0
    print(f"{'Successful Runs':^15} | {'Avg Run Time':^12} | {'Failed Runs':^11} | {'Total Time Wasted':^17} ")
    print("-" * 64)
    print(f"{len(run_times):^15} | {format_time(avg_run_time):^12} | {failed_count:^11} | {format_time(failed_total_time):^17}")
    #export()