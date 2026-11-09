Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class WindowTools {
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@

Get-Process WindowsTerminal -ErrorAction SilentlyContinue |
    ForEach-Object { [WindowTools]::ShowWindow($_.MainWindowHandle, 6) | Out-Null }
