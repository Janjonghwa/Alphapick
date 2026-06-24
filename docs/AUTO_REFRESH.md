# KOSPI automatic refresh

AlphaPick's browser requests only the Django API and the Django API reads the
local database.  The external KRX/pykrx call is intentionally performed in a
separate batch job so a visitor cannot make the service slow or exhaust the
public data source.

`pykrx` supplies end-of-day data, not tick-by-tick real-time quotes.  The
recommended policy is therefore a weekday job after the Korean market closes.
The refresh command resolves the *latest completed KOSPI session* first using
the daily OHLCV calendar of Samsung Electronics, a liquid KOSPI bellwether.
This avoids a pykrx index-endpoint encoding issue seen on some Windows
installations. A holiday, weekend, or pre-close execution will therefore use
the latest real trading date instead of pretending that unfinished data is
current.

## One-time setup

Run this once from the project root after creating the backend virtual
environment and applying migrations.

```powershell
cd "C:\Users\SSAFY\Documents\1학기 관통-main-latest"
.\scripts\run_market_refresh.ps1
```

The first full update is intentionally heavy: it downloads approximately 420
calendar days of OHLCV for the KOSPI universe so the application can calculate
EMA200, one-year return, volatility, and the other score inputs.  Let it finish
before opening the app.  It does **not** delete users, watchlists, posts, or
comments.

For a short connection test only:

```powershell
cd backend
.\.venv\Scripts\python.exe manage.py refresh_market_data --limit 5 --skip-fundamentals
```

## Create the Windows scheduled task

Open PowerShell as the same Windows user who runs the project, then run:

```powershell
$project = "C:\Users\SSAFY\Documents\1학기 관통-main-latest"
$action = New-ScheduledTaskAction `
  -Execute "powershell.exe" `
  -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$project\scripts\run_market_refresh.ps1`""
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 4:20PM
Register-ScheduledTask -TaskName "AlphaPick KOSPI Daily Refresh" -Action $action -Trigger $trigger -Description "Updates AlphaPick after KRX close" -Force
```

`4:20 PM` is a safe default after the regular KRX close.  If KRX or pykrx is
delayed, the job fails safely and the prior database remains available; the log
will show the reason.

## Operate and troubleshoot

```powershell
# Run the same task now without waiting for 4:20 PM.
Start-ScheduledTask -TaskName "AlphaPick KOSPI Daily Refresh"

# Check the scheduler state.
Get-ScheduledTaskInfo -TaskName "AlphaPick KOSPI Daily Refresh"

# View today's batch log.
Get-Content "$project\backend\logs\market-refresh-$(Get-Date -Format yyyy-MM-dd).log" -Tail 80

# Remove the task if the project folder is moved.
Unregister-ScheduledTask -TaskName "AlphaPick KOSPI Daily Refresh" -Confirm:$false
```

If the project folder changes, unregister the old task and register it again
with the new absolute path.  Scheduled tasks are machine-specific and are not
stored in Git.
