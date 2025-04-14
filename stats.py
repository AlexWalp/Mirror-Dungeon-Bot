file = "game.log"


def time_between_actions(log_file, word1, word2, start_line=0):
    with open(log_file, "r") as file:
        lines = file.readlines()
    
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


def av_time(log_file, word1, word2):
    total_time = 0
    count = 0
    start_line = 0

    while True:
        time_diff, start_line = time_between_actions(log_file, word1, word2, start_line)
        if time_diff is None:
            break

        total_time += time_diff
        count += 1

    return total_time / count if count > 0 else None


def format_time(seconds):
    minutes = int(seconds // 60)
    sec = int(seconds % 60)
    return f"{minutes}:{sec:02d}"


if __name__ == "__main__":
    print("Average time for human fight  :", int(av_time(file, "human", "over") or 0), "s")
    print("Average time for focused fight:", int(av_time(file, "focus", "over") or 0), "s")
    print("Average time for risk fight   :", int(av_time(file, "risk", "over") or 0), "s")
    print("Average time for dungeon      :", format_time(av_time(file, "Iteration", "Completed")))