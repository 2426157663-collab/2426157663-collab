$shell = New-Object -ComObject WScript.Shell
$null = $shell.AppActivate("GreenGoose Setup")
Start-Sleep -Milliseconds 800
$shell.SendKeys("{ENTER}")
