#! /usr/bin/env python
"""Freeze importlib for use as the implementation of import."""
import marshal


header = """/* Auto-generated by Python/freeze_importlib.py */"""


def main(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as input_file:
        source = input_file.read()

    code = compile(source, '<frozen importlib._bootstrap>', 'exec')

    lines = [header]
    lines.append('unsigned char _Py_M__importlib[] = {')
    data = marshal.dumps(code)
    # Code from Tools/freeze/makefreeze.py:writecode()
    for i in range(0, len(data), 16):
        line = ['    ']
        for c in data[i:i+16]:
            line.append('%d,' % c)
        lines.append(''.join(line))
    lines.append('};\n')
    with open(output_path, 'w') as output_file:
        output_file.write('\n'.join(lines))
        output_file.write('\u0000')


if __name__ == '__main__':
    import sys

    args = sys.argv[1:]
    if len(args) != 2:
        print('Need to specify input and output file paths', file=sys.stderr)
        sys.exit(1)

    main(*args)
