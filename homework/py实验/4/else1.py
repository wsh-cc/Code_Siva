L = [
    ('Bob', 75),
    ('Adam', 92),
    ('Bart', 66),
    ('Lisa', 88),
    ('Sophia', 96),
    ('Andy', 83)
]

result = sorted(L, key=lambda x: x[1], reverse=True)

print(result)