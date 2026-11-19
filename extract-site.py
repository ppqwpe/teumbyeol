import hashlib,io,json,pathlib,zipfile
base=pathlib.Path(__file__).resolve().parent
manifest=json.loads((base/'site-manifest.json').read_text())
parts=[]
for part in manifest['parts']:
    content=(base/part['path']).read_bytes()
    assert len(content)==part['size'] and hashlib.sha256(content).hexdigest()==part['sha256'],part['path']
    parts.append(content)
archive=b''.join(parts)
assert hashlib.sha256(archive).hexdigest()==manifest['archiveSha256']
target=(base/'_site').resolve()
with zipfile.ZipFile(io.BytesIO(archive)) as z:
    for entry in z.infolist():
        dest=(target/entry.filename).resolve()
        assert dest==target or target in dest.parents,'Unsafe archive path'
    assert z.testzip() is None
    z.extractall(target)
assert (target/'index.html').is_file()
(target/'.nojekyll').write_text('')
update_manifest=base/'updates/manifest.json'
if update_manifest.exists():
    update=json.loads(update_manifest.read_text())
    chunks=[]
    for part in update['parts']:
        content=(base/part['path']).read_bytes()
        assert len(content)==part['size'] and hashlib.sha256(content).hexdigest()==part['sha256']
        chunks.append(content)
    content=b''.join(chunks)
    assert hashlib.sha256(content).hexdigest()==update['archiveSha256']
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        for entry in z.infolist():
            dest=(target/entry.filename).resolve()
            assert dest==target or target in dest.parents,'Unsafe update path'
        assert z.testzip() is None
        z.extractall(target)
print('Verified and extracted independent static website and latest update')
