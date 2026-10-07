"""
Menghitung IC, membandingkan frekuensi sebelum/sesudah encode, dan mengestimasi
brute force Vigenere berdasarkan asumsi. Tidak mencoba kunci atau mengukur keamanan.
"""


from math import log10
from .frequency import analyze


def distribution(text):
    data = analyze(text)
    total = data['total']
    # Peluang dua posisi berbeda berisi huruf sama; abaikan selain A-Z.
    data['ic'] = (sum(row['count'] * (row['count'] - 1) for row in data['rows'])
                  / (total * (total - 1))) if total > 1 else None
    return data


def scientific(log_value):
    """Format angka besar/kecil tanpa membuat float melampaui batas."""
    exponent = int(log_value // 1)
    mantissa = 10 ** (log_value - exponent)
    if round(mantissa, 3) >= 10:
        mantissa, exponent = 1, exponent + 1
    return f'{mantissa:.3f} × 10^{exponent}'


def duration_label(log_seconds):
    if log_seconds < 0:
        return 'Kurang dari 1 detik'
    for unit, size in [('tahun', 365.25 * 86400), ('hari', 86400),
                       ('jam', 3600), ('menit', 60), ('detik', 1)]:
        scaled = log_seconds - log10(size)
        if scaled >= 0:
            value = f'{10 ** scaled:,.2f}' if scaled < 9 else scientific(scaled)
            return f'{value} {unit}'


def estimate(length, rate=1000000, seconds=60):
    # Batas input untuk simulator saja; kunci enkripsi tidak dibatasi di sini.
    for value, limit, name in [(length, 1000000, 'Panjang kunci'),
                               (rate, 10**12, 'Kecepatan'),
                               (seconds, 10**12, 'Durasi')]:
        if type(value) is not int or not 1 <= value <= limit:
            raise ValueError(f'{name} harus bilangan bulat 1 sampai {limit}.')
    log_space = length * log10(26)
    # Hindari membuat jutaan digit untuk input kunci sangat panjang.
    exact = 26 ** length if length <= 128 else None
    budget = rate * seconds
    attempts = min(budget, exact) if exact is not None else budget
    log_probability = min(0, log10(attempts) - log_space)
    if exact is not None and attempts == exact:
        percent = '100%'
    elif log_probability + 2 >= -4:
        percent = f'{10 ** (log_probability + 2):.6f}%'
    else:
        percent = scientific(log_probability + 2) + '%'
    average_log = log10((exact + 1) / 2) if exact is not None else log_space - log10(2)
    return {'length': length, 'rate': rate, 'seconds': seconds,
            'key_space': str(exact) if exact is not None else scientific(log_space),
            'key_space_exact': exact is not None, 'attempts': str(attempts),
            'probability': percent,
            'full_time': duration_label(log_space - log10(rate)),
            'average_time': duration_label(average_log - log10(rate))}


def compare(raw_ciphertext, encoded_ciphertext, key_length):
    return {'before': distribution(raw_ciphertext),
            'after': distribution(encoded_ciphertext),
            'vigenere_length': key_length, 'estimate': estimate(key_length)}
