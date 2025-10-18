import secrets
alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
key_gen = (secrets.choice(alphabet) for _ in range(90))
key = ''.join(key_gen)  # هنا نحول الـ generator لسلسلة نصية
print(key)