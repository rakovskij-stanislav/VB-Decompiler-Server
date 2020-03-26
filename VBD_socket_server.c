/* Source template by: VBDecC.c

	Exapmle of usage VB Decompiler API
	Internal API wrappers are in VBDecPDK.h, don't forget to include this file.

	Support Unicode & ANSI build (uncomment _UNICODE to build Unicode version)

	(C) 2006 by Jupiter
*/

/*
VDB_socket_server

Allows you to use VB Decompiler API from Python, Java, etc without dll creation.

Can be used for investigation optimizations, printing additional information.

(c) Rakovskij Stanislav, 2020 - 2077
*/

/* Only used stuff */
#define	WIN32_LEAN_AND_MEAN

#undef	_UNICODE
#include	<windows.h>
#include	<winuser.h>
#include	<tchar.h>

#include <string.h>
#include	"VBDecPDK.h"
#include	"vcruntime_string.h"
#include <stdio.h>

#include    <winsock2.h>
#include    <ws2tcpip.h>



#pragma comment (lib, "ws2_32.lib")



VBDEC_API	VBDecompilerPluginName	(HWND hWndVBDec, HWND hRichEd, LPSTR sBuffer, DWORD lpResVBD1);
VBDEC_API	VBDecompilerPluginLoad	(HWND hWndVBDec, HWND hRichEd, LPSTR sBuffer, FARPROC VBDecModEngine);



/* Name of the Module - displayed in Plugins menu */
TCHAR	*sModuleName="### VBD Socket Server ###";
/* Module Handle */
HANDLE	hInst;


/*
Module EntryPoint. Nothing special.
*/
BOOL	APIENTRY	DllMain	(HANDLE hModule, DWORD  fdwReason, LPVOID lpReserved)
{
    switch (fdwReason)
	{
		case DLL_PROCESS_ATTACH:
			hInst=hModule;
		case DLL_THREAD_ATTACH:
		case DLL_THREAD_DETACH:
		case DLL_PROCESS_DETACH:
			break;
    }
    return TRUE;
}


VBDEC_API	VBDecompilerPluginName	(HWND hWndVBDec, HWND hRichEd, LPSTR sBuffer, DWORD lpResVBD1)
{
	strcpy(sBuffer,sModuleName);
	return	TRUE;
}



VBDEC_API	VBDecompilerPluginLoad	(HWND hWndVBDec, HWND hRichEd, LPSTR sBuffer, FARPROC VBDecModEngine)
{
	TCHAR	*pStr;
	/*
	Initialize module.
	Save address of VB decompiler CallBack in VBDecInit.
	This must be first call in your function to verify that we got correct address.
	*/
	if (!(VBDecInit(VBDecModEngine)))
	{
		return	FALSE;
	}

	MessageBox(hWndVBDec, "Run your plugin and press OK (Port 6868).", sModuleName, MB_OK + MB_ICONINFORMATION);
	

	WSADATA WsaData;
	int err = WSAStartup(0x0101, &WsaData);
	if (err == SOCKET_ERROR)
	{
		MessageBox(hWndVBDec, "Error on socket opening", sModuleName, MB_OK + MB_ICONINFORMATION);
		return 1;
	}

	SOCKET s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

	SOCKADDR_IN sin;
	sin.sin_family = AF_INET;
	sin.sin_port = htons(6868);
	sin.sin_addr.s_addr = INADDR_ANY;

	struct SOCKADDR_IN* addr;
	int addrlen;

	err = bind(s, (LPSOCKADDR)&sin, sizeof(sin));

	err = listen(s, 1);

	SOCKADDR_IN from;
	int fromlen = sizeof(from);
	SOCKET s1 = accept(s, NULL, NULL);

	char RecvBuffer[4096];
	memset(&RecvBuffer, 0, 4096);

	int buf_len = recv(s1, RecvBuffer, sizeof(RecvBuffer), 0);
	while (buf_len != SOCKET_ERROR)
	{
		if (strcmp(&RecvBuffer, "VBD")==0) {

			char *res;
            // получаем результат выполнения функи
			res = VBDecGate(((DWORD*)RecvBuffer)[1], ((DWORD*)RecvBuffer)[2], ((DWORD*)RecvBuffer)[3], RecvBuffer + 16);
			memset(&RecvBuffer, 0, 4096);
			// отправляем его обратно

			// глупая проверка "адрес или код возврата"
			if ((int)res < 1024) 
			{ 
				send(s1, (DWORD)res, 4, MSG_DONTROUTE);
			}
			else
			{
				size_t res_len = wcslen(res) * 2;
				send(s1, res, res_len, MSG_DONTROUTE);
			}
			send(s1, "\x00\x00\x00\x00", 4, MSG_DONTROUTE);

		}
		if (strcmp(&RecvBuffer, "END") == 0) {
			send(s1, "\x01\x00\x00\x00", 4, MSG_DONTROUTE);
			break;
		}
		buf_len = recv(s1, RecvBuffer, sizeof(RecvBuffer), 0);
	}
	closesocket(s);
	
	//SetVBDecVal(sNewData, VBD_SetVBProject,0,0); // работает
	//SetVBDecVal(sNewData, VBD_SetStatusBarText,0,0); // не работает
	//SetVBDecVal(sNewData, VBD_UpdateAll,0,0); // todo: по факту функу обновления можно посылать после любой отработки плагина
	return	TRUE;

}

