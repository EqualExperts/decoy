SELECT
    range as id,
    np_rand('randint', [0, 10])
FROM range(1)