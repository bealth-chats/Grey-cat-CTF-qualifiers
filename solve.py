import json

def main():
    with open('dist-AE-no-S/output.txt', 'r') as f:
        data = json.load(f)

    zero_ct = int(data['zero']['ct'], 16)

    A = []
    for pair in data['basis_pairs']:
        pt = int(pair['pt'], 16)
        ct = int(pair['ct'], 16)
        A.append(ct ^ zero_ct)

    def solve_block(target_ct_hex):
        target_ct = int(target_ct_hex, 16)
        target = target_ct ^ zero_ct

        mat = []
        for row in range(128):
            mat_row = []
            for col in range(128):
                mat_row.append((A[col] >> (127 - row)) & 1)
            mat_row.append((target >> (127 - row)) & 1)
            mat.append(mat_row)

        for i in range(128):
            pivot = -1
            for j in range(i, 128):
                if mat[j][i] == 1:
                    pivot = j
                    break
            if pivot == -1:
                raise Exception("Matrix not invertible at index " + str(i))

            mat[i], mat[pivot] = mat[pivot], mat[i]

            for j in range(128):
                if j != i and mat[j][i] == 1:
                    for k in range(i, 129):
                        mat[j][k] ^= mat[i][k]

        x = 0
        for i in range(128):
            x = (x << 1) | mat[i][128]

        return int.to_bytes(x, 16, 'big')

    flag_ct = data['flag_ct']
    blocks = [flag_ct[i:i+32] for i in range(0, len(flag_ct), 32)]

    pt = b""
    for block in blocks:
        pt += solve_block(block)

    print("Decrypted:", pt)

if __name__ == '__main__':
    main()
