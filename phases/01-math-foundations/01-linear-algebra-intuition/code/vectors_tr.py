# Orijinal: https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/01-linear-algebra-intuition/code/vectors.py
# Bu dosya, orijinal kodun Türkçe çevrilmiş versiyonudur.

class Vector:
    def __init__(self, components):
        self.components = list(components)
        self.dim = len(self.components)

    def __add__(self, other):
        return Vector([a + b for a, b in zip(self.components, other.components)])

    def __sub__(self, other):
        return Vector([a - b for a, b in zip(self.components, other.components)])

    def __mul__(self, scalar):
        return Vector([x * scalar for x in self.components])

    def dot(self, other):
        return sum(a * b for a, b in zip(self.components, other.components))

    def magnitude(self):
        return sum(x**2 for x in self.components) ** 0.5

    def normalize(self):
        mag = self.magnitude()
        return Vector([x / mag for x in self.components])

    def cosine_similarity(self, other):
        return self.dot(other) / (self.magnitude() * other.magnitude())

    def angle_between(self, other):
        import math
        cos_theta = self.cosine_similarity(other)
        cos_theta = max(-1.0, min(1.0, cos_theta))
        return math.degrees(math.acos(cos_theta))

    def project_onto(self, other):
        scalar = self.dot(other) / other.dot(other)
        return Vector([scalar * x for x in other.components])

    def __repr__(self):
        return f"Vector({self.components})"


def is_independent(vectors):
    n = len(vectors)
    if n == 0:
        return True
    dim = vectors[0].dim
    rows = [v.components[:] for v in vectors]
    rank = 0
    for col in range(dim):
        pivot = None
        for row in range(rank, len(rows)):
            if abs(rows[row][col]) > 1e-10:
                pivot = row
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][col]
        rows[rank] = [x / scale for x in rows[rank]]
        for row in range(len(rows)):
            if row != rank and abs(rows[row][col]) > 1e-10:
                factor = rows[row][col]
                rows[row] = [rows[row][j] - factor * rows[rank][j] for j in range(dim)]
        rank += 1
    return rank == n


def gram_schmidt(vectors):
    orthonormal = []
    for v in vectors:
        w = v
        for u in orthonormal:
            proj = w.project_onto(u)
            w = w - proj
        if w.magnitude() < 1e-10:
            continue
        orthonormal.append(w.normalize())
    return orthonormal


class Matrix:
    def __init__(self, rows):
        self.rows = [list(row) for row in rows]
        self.shape = (len(self.rows), len(self.rows[0]))

    def __matmul__(self, other):
        if isinstance(other, Vector):
            return Vector([
                sum(self.rows[i][j] * other.components[j] for j in range(self.shape[1]))
                for i in range(self.shape[0])
            ])
        rows = []
        for i in range(self.shape[0]):
            row = []
            for j in range(other.shape[1]):
                row.append(sum(
                    self.rows[i][k] * other.rows[k][j]
                    for k in range(self.shape[1])
                ))
            rows.append(row)
        return Matrix(rows)

    def transpose(self):
        return Matrix([
            [self.rows[j][i] for j in range(self.shape[0])]
            for i in range(self.shape[1])
        ])

    def rank(self):
        rows = [row[:] for row in self.rows]
        m, n = self.shape
        r = 0
        for col in range(n):
            pivot = None
            for row in range(r, m):
                if abs(rows[row][col]) > 1e-10:
                    pivot = row
                    break
            if pivot is None:
                continue
            rows[r], rows[pivot] = rows[pivot], rows[r]
            scale = rows[r][col]
            rows[r] = [x / scale for x in rows[r]]
            for row in range(m):
                if row != r and abs(rows[row][col]) > 1e-10:
                    factor = rows[row][col]
                    rows[row] = [rows[row][j] - factor * rows[r][j] for j in range(n)]
            r += 1
        return r

    def __repr__(self):
        return f"Matrix({self.rows})"


if __name__ == "__main__":
    print("=== Vektörler ===")
    a = Vector([1, 2, 3])
    b = Vector([4, 5, 6])
    print(f"a = {a}")
    print(f"b = {b}")
    print(f"a + b = {a + b}")
    print(f"a - b = {a - b}")
    print(f"a * 3 = {a * 3}")
    print(f"a · b = {a.dot(b)}")
    print(f"|a| = {a.magnitude():.4f}")
    print(f"â (normalize edilmiş) = {a.normalize()}")
    print(f"kosinüs_benzerliği(a, b) = {a.cosine_similarity(b):.4f}")

    print("\n=== Matrisler ===")
    rotation_90 = Matrix([[0, -1], [1, 0]])
    point = Vector([3, 1])
    rotated = rotation_90 @ point
    print(f"{point} noktasını 90° döndür → {rotated}")

    print("\n=== Vektörler Arası Açı ===")
    v1 = Vector([1, 0])
    v2 = Vector([0, 1])
    v3 = Vector([1, 1])
    print(f"{v1} ile {v2} arasındaki açı: {v1.angle_between(v2):.1f} derece")
    print(f"{v1} ile {v3} arasındaki açı: {v1.angle_between(v3):.1f} derece")
    print(f"{v1} ile {v1} arasındaki açı: {v1.angle_between(v1):.1f} derece")

    print("\n=== Projeksiyon ===")
    a = Vector([3, 4])
    b = Vector([1, 0])
    proj = a.project_onto(b)
    residual = a - proj
    print(f"a = {a}")
    print(f"b = {b}")
    print(f"proj_b(a) = {proj}")
    print(f"artık = {residual}")
    print(f"artık · b = {residual.dot(b):.6f}")

    print("\n=== Doğrusal Bağımsızlık ===")
    e1 = Vector([1, 0, 0])
    e2 = Vector([0, 1, 0])
    e3 = Vector([0, 0, 1])
    dep = Vector([2, 1, 0])
    print(f"{{e1, e2, e3}} bağımsız: {is_independent([e1, e2, e3])}")
    print(f"{{e1, e2, 2*e1+e2}} bağımsız: {is_independent([e1, e2, dep])}")

    print("\n=== Gram-Schmidt Ortoğonalleştirme ===")
    u1 = Vector([1, 1, 0])
    u2 = Vector([1, 0, 1])
    u3 = Vector([0, 1, 1])
    basis = gram_schmidt([u1, u2, u3])
    for i, vec in enumerate(basis):
        print(f"u{i+1} = {vec}")
    print(f"u1 · u2 = {basis[0].dot(basis[1]):.6f}")
    print(f"u1 · u3 = {basis[0].dot(basis[2]):.6f}")
    print(f"u2 · u3 = {basis[1].dot(basis[2]):.6f}")
    for i, vec in enumerate(basis):
        print(f"|u{i+1}| = {vec.magnitude():.6f}")

    print("\n=== Matris Derecesi ===")
    full_rank = Matrix([[1, 0], [0, 1]])
    rank_deficient = Matrix([[1, 2], [2, 4]])
    rectangular = Matrix([[1, 0, 0], [0, 1, 0]])
    print(f"Birim 2x2 derecesi: {full_rank.rank()}")
    print(f"[[1,2],[2,4]] derecesi: {rank_deficient.rank()}")
    print(f"[[1,0,0],[0,1,0]] derecesi: {rectangular.rank()}")

    print("\n=== Sinir Ağı Katmanı (Matris × Vektör) ===")
    import random
    random.seed(42)
    weights = Matrix([[random.gauss(0, 0.1) for _ in range(3)] for _ in range(2)])
    input_vec = Vector([1.0, 0.5, -0.3])
    output = weights @ input_vec
    print(f"Girdi (3B):  {input_vec}")
    print(f"Çıktı (2B): {output}")
    print("^ Bu, bir sinir ağı katmanının tam olarak yaptığı şeydir.")
