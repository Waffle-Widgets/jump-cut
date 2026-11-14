# Dismiss a blocking Unreal modal by title. This repo uses git LFS, NOT Unreal source
# control, so "Check Out Assets" must be cancelled, never accepted.
param([int]$EdPid = 12844, [string]$Title = 'Check Out Assets')
Add-Type @'
using System;using System.Runtime.InteropServices;using System.Text;
public class WM{
 [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr l);
 public delegate bool EnumWindowsProc(IntPtr h, IntPtr l);
 [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr h);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr h, out int p);
 [DllImport("user32.dll")] public static extern IntPtr PostMessage(IntPtr h,uint m,IntPtr w,IntPtr l);
 [DllImport("user32.dll")] public static extern bool IsWindow(IntPtr h);
}
'@
$found = [IntPtr]::Zero
$cb = [WM+EnumWindowsProc]{ param($h,$l)
  $p = 0; [void][WM]::GetWindowThreadProcessId($h, [ref]$p)
  if ($p -eq $script:EdPid -and [WM]::IsWindowVisible($h)) {
    $n = [WM]::GetWindowTextLength($h)
    if ($n -gt 0) { $sb = New-Object System.Text.StringBuilder ($n+1); [void][WM]::GetWindowText($h,$sb,$n+1)
      if ($sb.ToString() -eq $script:Title) { $script:found = $h } } }
  return $true }
[void][WM]::EnumWindows($cb, [IntPtr]::Zero)
if ($found -eq [IntPtr]::Zero) { 'no modal'; exit 0 }
[void][WM]::PostMessage($found, 0x0100, [IntPtr]0x1B, [IntPtr]0)   # WM_KEYDOWN  ESC
[void][WM]::PostMessage($found, 0x0101, [IntPtr]0x1B, [IntPtr]0)   # WM_KEYUP    ESC
Start-Sleep -Seconds 3
if ([WM]::IsWindow($found)) { 'STILL OPEN' } else { 'dismissed' }
