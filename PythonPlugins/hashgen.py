from VDB_Client.VBD_Client import VBD_Client, VBD_vlType as func

import pefile
from hashlib import md5, sha256, sha1
import time

def gethash_from_blob(blob, cryptofun = md5):
    hashsum = "-"
    try:
        hashsum = cryptofun(blob).hexdigest()
        return hashsum
    except Exception as e:
        pass
    return hashsum

with VBD_Client() as cli:
    old_text = cli.call(func["VBD_GetActiveText"]).replace(b"\x00", b"").decode()
    file_path = cli.call(func["VBD_GetFileName"]).replace(b"\x00", b"").decode()
    print(file_path)
    if not file_path:
        print("Project is not opened!")
        time.sleep(5)
        exit()
    with open(file_path, 'rb') as f:
        filedata = f.read()

    try:
        p = pefile.PE(data=filedata)
        imphash = p.get_imphash()
    except:
        imphash = False

    file_md5 = gethash_from_blob(filedata)
    file_sha1 = gethash_from_blob(filedata, sha1)
    file_sha256 = gethash_from_blob(filedata, sha256)

    ans = []
    if imphash:
        ans.append(f'imphash\t\t{imphash}') # pretty useless, but...
    ans.append(f'MD5\t\t{file_md5}')
    ans.append(f'SHA1\t\t{file_sha1}')
    ans.append(f'SHA256\t\t{file_sha256}')

    overlay_offset = p.get_overlay_data_start_offset()
    if overlay_offset:
        ans.append(f"Overlay! Offset: {overlay_offset}")

    ans.append("\n\n")
    cli.call(func["VBD_SetActiveText"], param3=(
         "\n".join(ans).encode() + old_text.encode()
                                                )
             )

