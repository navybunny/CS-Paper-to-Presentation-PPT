param(
 [Parameter(Mandatory=$true)][string]$InputPath,
 [Parameter(Mandatory=$true)][string]$OutputDirectory,
 [int[]]$Slides=@()
)
$ErrorActionPreference='Stop'
$source=(Resolve-Path -LiteralPath $InputPath).Path
$dest=[System.IO.Path]::GetFullPath($OutputDirectory)
$skillRoot=[System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
if($dest -eq $skillRoot -or $dest.StartsWith($skillRoot+[System.IO.Path]::DirectorySeparatorChar,[System.StringComparison]::OrdinalIgnoreCase)) {
 throw 'Render outputs must be in the task directory, not the installed skill.'
}
if(Test-Path -LiteralPath $dest) {
 if((Get-ChildItem -LiteralPath $dest -Force | Measure-Object).Count -gt 0) {throw 'Output directory must be new or empty.'}
}else {New-Item -ItemType Directory -Path $dest | Out-Null}
$app=$null
$deck=$null
try {
 $app=New-Object -ComObject PowerPoint.Application
 $deck=$app.Presentations.Open($source,-1,0,0)
 foreach($n in $Slides) {if($n -lt 1 -or $n -gt $deck.Slides.Count) {throw "Invalid slide number: $n"}}
 for($n=1;$n -le $deck.Slides.Count;$n++) {
  if($Slides.Count -eq 0 -or $n -in $Slides) {
   $deck.Slides.Item($n).Export((Join-Path $dest ('slide-'+$n.ToString('00')+'.png')),'PNG',1280,720)
  }
 }
 Write-Output ('Rendered read-only source: '+$deck.Slides.Count+' total slides')
}finally {
 if($null -ne $deck) {$deck.Close();[System.Runtime.InteropServices.Marshal]::ReleaseComObject($deck)|Out-Null}
 if($null -ne $app) {[System.Runtime.InteropServices.Marshal]::ReleaseComObject($app)|Out-Null}
}
