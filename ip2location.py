import csv
import ipaddress
from pathlib import Path

CSV_PATH = "IP2LOCATION-LITE-DB3.CSV"
OUTPUT_PATH = "angry_ranges.txt"

def normalize_city(s: str) -> str:
    if s is None:
        return ""
    return s.strip().lower().replace("’", "'").replace("`", "'")

def parse_ip_num(value: str):
    if value is None:
        return None
    v = value.strip().strip('"').strip("'")
    if v == "":
        return None
    try:
        return int(v)
    except ValueError:
        try:
            return int(ipaddress.IPv4Address(v))
        except Exception:
            return None

def merge_ranges(ranges):
    if not ranges:
        return []
    ranges = sorted(ranges, key=lambda x: x[0])
    merged = []
    cur_s, cur_e = ranges[0]
    for s, e in ranges[1:]:
        if s <= cur_e + 1:
            cur_e = max(cur_e, e)
        else:
            merged.append((cur_s, cur_e))
            cur_s, cur_e = s, e
    merged.append((cur_s, cur_e))
    return merged

def main():
    csv_path = Path(CSV_PATH)
    if not csv_path.exists():
        print(f"CSV файл не найден: {csv_path.resolve()}")
        return

    city_input = input("Введите город (так, как он записан в 6-м столбце): ").strip()
    city_input_norm = normalize_city(city_input)

    found_ranges = []

    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 6:
                continue
            city = normalize_city(row[5])
            if city == city_input_norm:
                start_num = parse_ip_num(row[0])
                end_num = parse_ip_num(row[1])
                if start_num is None or end_num is None:
                    continue
                if start_num > end_num:
                    start_num, end_num = end_num, start_num
                found_ranges.append((start_num, end_num))

    if not found_ranges:
        print("Диапазоны для указанного города не найдены.")
        return

    merged = merge_ranges(found_ranges)

    out_path = Path(OUTPUT_PATH)
    with out_path.open("w", encoding="utf-8") as out:
        for s, e in merged:
            s_ip = str(ipaddress.IPv4Address(s))
            e_ip = str(ipaddress.IPv4Address(e))
            out.write(f"{s_ip}-{e_ip}\n")

    print(f"Сохранено {len(merged)} диапазонов в файл: {out_path.resolve()}")

if __name__ == "__main__":
    main()
