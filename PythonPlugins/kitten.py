from VDB_Client.VBD_Client import VBD_Client, VBD_vlType as func, single_call

import time

cat = """\
               )\._.,--....,'``.
 .b--.        /;   _.. \   _\  (`._ ,.
`=,-,-'~~~   `----(,_..'--(,_..'`-.;.'
"""

with VBD_Client() as client:
    old_text = client.call(func["VBD_GetActiveText"]).replace(b"\x00", b"")
    client.call(func["VBD_SetActiveText"], param3=cat.encode())
    time.sleep(5)
    old_text = client.call(func["VBD_SetActiveText"], param3=old_text)