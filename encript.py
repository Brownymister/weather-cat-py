import sys


def main(text, shift):
    encrypted_message = ""
    for char in text:
        if char.isalpha() or char.isdigit():
            ascii_offset = ord('a') if char.islower() else ord('A')
            if char.isdigit():
                encrypted_digit = str((int(char) + shift) % 10)
            else:
                encrypted_char = chr((ord(char) - ascii_offset + shift) % 26 +
                                     ascii_offset)
            encrypted_message += encrypted_digit if char.isdigit(
            ) else encrypted_char
        else:
            encrypted_message += char  # Keep non-letter and non-digit characters unchanged
    return encrypted_message




if __name__ == "__main__":
    shift = int(sys.argv[2])
    print(main(sys.argv[1], shift))
