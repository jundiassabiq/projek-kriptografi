def analyze(text):
    # Hitung sendiri, tanpa library statistik/kriptanalisis.
    counts = {chr(65 + i): 0 for i in range(26)}
    for char in text:
        if 'A' <= char <= 'Z' or 'a' <= char <= 'z':
            counts[char.upper()] += 1
    total = sum(counts.values())
    rows = [{'letter': letter, 'count': count,
             'percent': round(count * 100 / total, 2) if total else 0}
            for letter, count in counts.items()]
    rows.sort(key=lambda row: (-row['count'], row['letter']))
    return {'total': total, 'rows': rows}
