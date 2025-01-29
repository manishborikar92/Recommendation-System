import secrets

def generate_secure_key(length=32):
    """Generate a secure random string with the given length."""
    return secrets.token_urlsafe(length)

# Generate secrets
jwt_secret = generate_secure_key(40)  # At least 32 chars
otp_secret = generate_secure_key(40)  # At least 32 chars

# Write to SECRET.txt file
with open("SECRET.txt", "w") as env_file:
    env_file.write(f"JWT_SECRET={jwt_secret}\n")
    env_file.write(f"OTP_SECRET={otp_secret}\n")

print("SECRET.txt file has been generated with secure secrets!")
