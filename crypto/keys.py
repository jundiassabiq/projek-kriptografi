def validate(key):
    """Kunci klasik hanya memakai huruf Latin, tanpa spasi atau angka."""
    if not isinstance(key, str) or not key or any(not ('A' <= c <= 'Z' or 'a' <= c <= 'z') for c in key):
        raise ValueError('Ketiga kunci wajib huruf A–Z/a–z tanpa spasi atau angka.')
    return key.upper()
