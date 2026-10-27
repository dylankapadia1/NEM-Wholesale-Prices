# Downloads AEMO 5-minute price and demand CSVs: 5 regions x 60 months (Oct 2021 - Sep 2026).
# Run from the repo root: powershell -ExecutionPolicy Bypass -File scripts\download_aemo.ps1
# Re-run it to retry failures: files already downloaded are skipped.

$out = Join-Path $PSScriptRoot "..\data\aemo_price_demand"
New-Item -ItemType Directory -Force $out | Out-Null

$regions = 'NSW1','QLD1','VIC1','SA1','TAS1'
$start = Get-Date '2021-10-01'

for ($m = 0; $m -lt 60; $m++) {
    $ym = $start.AddMonths($m).ToString('yyyyMM')
    foreach ($r in $regions) {
        $file = "PRICE_AND_DEMAND_${ym}_${r}.csv"
        $dest = Join-Path $out $file
        if (Test-Path $dest) { continue }   # skip files you already have
        $url = "https://www.aemo.com.au/aemo/data/nem/priceanddemand/$file"
        try {
            Invoke-WebRequest -Uri $url -OutFile $dest -UserAgent 'Mozilla/5.0' -ErrorAction Stop
        } catch {
            Write-Warning "Failed: $file"
        }
        Start-Sleep -Milliseconds 300   # be polite to AEMO's server
    }
}
"Files downloaded: " + (Get-ChildItem $out -Filter *.csv).Count
