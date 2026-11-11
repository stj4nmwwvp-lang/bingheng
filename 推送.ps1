# 冰衡 · 一键推送到 GitHub
#
# 用法：
#   1. 先在 GitHub 上建一个空仓库（不要勾选 README / .gitignore / license）
#      名字建议：bingheng
#   2. 双击本文件，按提示粘贴仓库地址（形如 https://github.com/你的用户名/bingheng.git）
#   3. 浏览器会弹出 GitHub 登录/授权，点「Authorize」即可
#
# 之后想更新，再双击一次就行（会跳过已配置的步骤）。

$ErrorActionPreference = "Stop"
$env:PATH = "C:\Program Files\Git\cmd;" + $env:PATH
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "  冰衡 · 推送到 GitHub" -ForegroundColor Cyan
Write-Host "  ─────────────────────────────" -ForegroundColor DarkGray
Write-Host ""

# 1) 检查有没有远程仓库
$remote = $null
try { $remote = (git remote get-url origin 2>$null) } catch { }

if (-not $remote) {
    Write-Host "  请粘贴你刚建好的仓库地址，例如：" -ForegroundColor Yellow
    Write-Host "  https://github.com/yourname/bingheng.git" -ForegroundColor DarkGray
    Write-Host ""
    $remote = Read-Host "  仓库地址"

    if ([string]::IsNullOrWhiteSpace($remote)) {
        Write-Host "  没有输入地址，退出。" -ForegroundColor Red
        Read-Host "按回车关闭"
        exit 1
    }
    if ($remote -notmatch '^https://github\.com/.+/.+') {
        Write-Host "  地址格式不对，应该是 https://github.com/用户名/仓库名.git" -ForegroundColor Red
        Read-Host "按回车关闭"
        exit 1
    }
    git remote add origin $remote
    Write-Host "  已关联远程仓库。" -ForegroundColor Green
}

Write-Host ""
Write-Host "  正在推送…浏览器如果弹窗，请点 Authorize 授权。" -ForegroundColor Yellow
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    $web = ($remote -replace '\.git$','') -replace '^https://github\.com/','https://github.com/'
    Write-Host ""
    Write-Host "  推送成功。" -ForegroundColor Green
    Write-Host "  仓库地址：$web" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "  推送失败。常见原因：" -ForegroundColor Red
    Write-Host "    · 仓库地址写错了（要把 https://github.com/用户名/仓库名.git 完整粘进来）" -ForegroundColor DarkGray
    Write-Host "    · 建仓库时勾了 README，导致远程已有内容。删掉仓库重建一个空的即可。" -ForegroundColor DarkGray
    Write-Host "    · 浏览器没完成授权，再双击一次试试" -ForegroundColor DarkGray
}

Write-Host ""
Read-Host "按回车关闭"
