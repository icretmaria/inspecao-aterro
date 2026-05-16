import glob, re
for f in glob.glob('/home/user/.venv/lib/*/site-packages/pythonforandroid/*.py'):
    try:
        txt = open(f).read()
        if 'MIN_NDK_API' in txt:
            new_txt = re.sub(r'MIN_NDK_API\s*=\s*\d+', 'MIN_NDK_API = 1', txt)
            if new_txt != txt:
                open(f, 'w').write(new_txt)
                print('Patched:', f)
    except Exception as e:
        print('Erro:', e)
