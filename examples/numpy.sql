SELECT
 range as id,
 np_rand('rand') as numpy_random
FROM range(5)