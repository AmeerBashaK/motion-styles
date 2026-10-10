# Render every Blender loop to PNG frames, then encode each to an MP4 next to the AE renders.
$ErrorActionPreference = "Continue"
$blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$dir = $PSScriptRoot
$videos = Join-Path (Split-Path $dir) "videos"
Remove-Item Env:PREVIEW_FRAME -ErrorAction SilentlyContinue

$scenes = @{ "04_clay" = "04-clay-3d"; "06_y2k" = "06-y2k-chrome"; "14_isometric" = "14-isometric"; "15_lowpoly" = "15-low-poly" }
foreach ($script in $scenes.Keys | Sort-Object) {
    $name = $scenes[$script]
    $frames = Join-Path $dir "frames\$name"
    if (Test-Path $frames) { Remove-Item -Recurse -Force $frames }
    & $blender -b --factory-startup --python (Join-Path $dir "$script.py") 2>&1 | Select-String -Pattern "Error|Traceback" | Select-Object -First 5
    & ffmpeg -hide_banner -loglevel error -y -framerate 30 -i (Join-Path $frames "f_%04d.png") -c:v libx264 -pix_fmt yuv420p -crf 18 (Join-Path $videos "$name.mp4")
    "$name -> " + (Get-ChildItem $frames -Filter *.png).Count + " frames"
}
