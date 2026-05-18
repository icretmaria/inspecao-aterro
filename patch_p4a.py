import subprocess

r = subprocess.run(['grep', '-rl', 'minimum supported NDK', '/home/user/.venv/'],
                   capture_output=True, text=True)

for f in r.stdout.strip().split('\n'):
    if not f.strip():
        continue
    print(f'Arquivo: {f}')
    lines = open(f).readlines()
    new_lines = list(lines)
    for i, line in enumerate(lines):
        if 'minimum supported NDK' in line:
            print(f'  Encontrado na linha {i}: {line.rstrip()}')
            for j in range(i, max(0, i-5), -1):
                if 'raise' in lines[j]:
                    paren = 0
                    k = j
                    while k < min(i+5, len(lines)):
                        paren += lines[k].count('(') - lines[k].count(')')
                        new_lines[k] = '# PATCHED: ' + lines[k]
                        if paren <= 0 and k > j:
                            break
                        k += 1
                    break
    new_content = ''.join(new_lines)
    if new_content != ''.join(lines):
        open(f, 'w').write(new_content)
        print('  Corrigido!')
    else:
        for i, line in enumerate(lines):
            if 'ndk' in line.lower() or 'minimum' in line.lower() or 'raise' in line.lower():
                print(f'  {i}: {repr(line[:100])}')
