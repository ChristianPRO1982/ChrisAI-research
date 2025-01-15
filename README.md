# ChrisAI-research
Tool for generating a newsletter on AI research.

## .ENV format

```dotenv
DEBUG=2 # 0: off, 1: on, 2: on with debug messages, 3: on with only SQL queries

FOLDER_PATH="thesis"
PREFIX="thesis_"

# HAL
QUERY="intelligence+artificielle"
ROWS="10000" # 10000 is the maximum
FQ="submittedDate_tdate:[NOW-3MONTHS/DAY%20TO%20NOW/HOUR]" # last 3 months
# FQ="submittedDateY_i:[2000%20TO%202013]" # 2000 to 2013
```
