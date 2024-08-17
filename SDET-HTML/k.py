import secrets

secret_key = secrets.token_hex(16)  # 16 bytes (128 bits) of randomness
print(secret_key)