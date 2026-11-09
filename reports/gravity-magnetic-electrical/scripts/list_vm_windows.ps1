Get-Process |
    Where-Object { $_.MainWindowTitle } |
    Select-Object ProcessName, Id, MainWindowHandle, MainWindowTitle |
    Format-Table -AutoSize |
    Out-File -Encoding utf8 C:\lab\windows.txt
