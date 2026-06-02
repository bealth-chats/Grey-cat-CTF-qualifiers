import socket
import re
import binascii

def recv_until(sock, suffix):
    data = b""
    while not data.endswith(suffix):
        chunk = sock.recv(1)
        if not chunk:
            break
        data += chunk
    return data

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("challs.nusgreyhats.org", 37167))

    prompt = recv_until(s, b"decrypt: ")
    print(prompt.decode('ascii'))

    match = re.search(r"Encrypted flag: ([0-9a-f]+)", prompt.decode('ascii'))
    if not match:
        print("Failed to find encrypted flag.")
        return

    enc_flag_hex = match.group(1)
    enc_flag = bytes.fromhex(enc_flag_hex)
    blocks = [enc_flag[i:i+16] for i in range(0, len(enc_flag), 16)]

    # 1. Modify the last block to get first 4 blocks
    mod1 = bytearray(enc_flag)
    mod1[-1] ^= 1
    s.sendall(mod1.hex().encode() + b"\n")
    resp1 = recv_until(s, b"decrypt: ").decode('ascii')

    match = re.search(r"Decrypted: (.*)", resp1)
    pt1 = match.group(1).replace("?", "")
    print("PT1:", pt1)

    # 2. Swap the first two blocks to get the last blocks
    if len(blocks) >= 2:
        new_blocks = list(blocks)
        new_blocks[0], new_blocks[1] = new_blocks[1], new_blocks[0]
        payload = b"".join(new_blocks).hex()
        s.sendall(payload.encode() + b"\n")
        resp2 = recv_until(s, b"decrypt: ").decode('ascii')

        match = re.search(r"Decrypted: (.*)", resp2)
        pt2 = match.group(1).replace("?", "")
        print("PT2:", pt2)

        # Combine the two parts.
        # PT1 has block 1, 2, 3, 4 (with length 64 bytes)
        # PT2 has block 3, 4, 5
        # The block 3 and 4 overlap, so we can just concatenate the first 4 blocks and the last block

        # We need to find the overlap or just take the length
        block5 = pt2[-16:]
        flag = pt1[:64] + block5
        print("\nFLAG:", flag)

if __name__ == "__main__":
    main()
