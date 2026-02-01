# Web Content Monitoring Script

## Features
- Monitor content changes of specified URL webpages
- Detect change types including: added, deleted, modified
- Monitoring scope includes: JS code, CSS styles, images, text content, and all other elements
- Use SQLite database to store historical data and change records
- Simple and clear display of change results

## Dependencies
- Python 3.x
- No external dependencies (using Python standard library)

## Installation
No external dependencies required, can run with Python standard library.

## Usage

### Direct Execution
```bash
python web_monitor.py --url <url>
```

Example:
```bash
python web_monitor.py --url https://example.com
```

### Using Configuration File
Configure monitoring addresses in `config.json`:
```json
{
    "lark_webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx",
    "monitor_urls": [
        "https://example.com",
        "https://example.org"
    ]
}
```

Then run:
```bash
python web_monitor.py
```

### Using Entry File
```bash
python main.py
```

## Scheduled Execution Configuration

### Using crontab for Scheduled Execution

1. Open crontab configuration:
```bash
crontab -e
```

2. Add scheduled task (execute every 5 minutes):
```bash
*/5 * * * * cd /path/to/monitor_page && python main.py >> monitor.log 2>&1
```

### crontab Configuration Explanation

- `*/5 * * * *` - Execute every 5 minutes
- `cd /path/to/monitor_page` - Switch to script directory
- `python main.py` - Execute monitoring script
- `>> monitor.log 2>&1` - Redirect output to log file

### Common Time Configurations

- Every 1 minute: `* * * * *`
- Every 5 minutes: `*/5 * * * *`
- Every 10 minutes: `*/10 * * * *`
- Every 15 minutes: `*/15 * * * *`
- Every 30 minutes: `*/30 * * * *`
- Every hour: `0 * * * *`
- Every day: `0 0 * * *`

## Working Principle
1. On first run, the script creates an SQLite database and stores initial webpage content
2. On subsequent runs, the script compares current webpage content with historical records
3. When changes are detected, it records change types and content, and displays them in the console
4. Supported change types:
   - scripts_added: New JS code added
   - scripts_removed: JS code removed
   - styles_added: New CSS styles added
   - styles_removed: CSS styles removed
   - images_added: New images added
   - images_removed: Images removed
   - text_modified: Text content modified
5. When changes are detected, it sends Lark notifications (if Webhook URL is configured)

## Database Structure
- `web_pages` table: Stores webpage URL, last content hash, last content, and last check time
- `changes` table: Stores change records, including URL, change type, change content, and change time

## Example Output
```
=== Detected Changes (https://example.com) ===
Change Type: scripts_added
Change Content: Added: https://example.com/new-script.js
---
Change Type: text_modified
Change Content: Text content changed
---
```