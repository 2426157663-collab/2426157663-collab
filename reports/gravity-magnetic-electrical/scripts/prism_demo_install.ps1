$shell = New-Object -ComObject WScript.Shell
$null = $shell.AppActivate("GreenGoose Setup")
Start-Sleep -Milliseconds 800
$shell.SendKeys("0000000000000000000000000")
Start-Sleep -Milliseconds 500
$shell.SendKeys("{ENTER}")
