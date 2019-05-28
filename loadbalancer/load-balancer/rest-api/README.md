# Dependencies REST-API
See [requirments.txt](src/requriments.txt)\
But summary:\
`python3.6`\
`pip`\
`Flask-RESTful`

TODO: Hardcoded filepaths/names
TODO: Hardcoded port

## Usage
`http://URL/`

`http://URL/halog/2`
where 2 is a number of number of logs you want to get. Example below.







## Examples
`http://URL/halog/2`
```angular2html
{
    "http-in/server-0": [
        {
            "timestamp": "2018-10-20-14:05:00.790",
            "1xx": 0,
            "2xx": 0,
            "3xx": 0,
            "4xx": 7,
            "5xx": 0,
            "other": 0,
            "tot_req": 7,
            "req_ok": 7,
            "pct_ok": "100.0",
            "avg_ct": 7,
            "avg_rt": 7,
            "ms_since_last_entry": 5017,
            "percentile": {
                "95.0": [
                    {
                        "UNKWN COL(idx:2)": 28,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 92,
                        "UNKWN COL(idx:5)": 92,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 212
                    }
                ],
                "98.0": [
                    {
                        "UNKWN COL(idx:2)": 29,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 92,
                        "UNKWN COL(idx:5)": 94,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 215
                    }
                ],
                "99.0": [
                    {
                        "UNKWN COL(idx:2)": 29,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 92,
                        "UNKWN COL(idx:5)": 94,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 215
                    }
                ],
                "99.9": [
                    {
                        "UNKWN COL(idx:2)": 29,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 92,
                        "UNKWN COL(idx:5)": 94,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 215
                    }
                ],
                "100.0": [
                    {
                        "UNKWN COL(idx:2)": 30,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 92,
                        "UNKWN COL(idx:5)": 97,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 219
                    }
                ]
            }
        },
        {
            "timestamp": "2018-10-20-14:05:05.808",
            "1xx": 0,
            "2xx": 0,
            "3xx": 0,
            "4xx": 8,
            "5xx": 0,
            "other": 0,
            "tot_req": 8,
            "req_ok": 8,
            "pct_ok": "100.0",
            "avg_ct": 7,
            "avg_rt": 8,
            "ms_since_last_entry": 5018,
            "percentile": {
                "95.0": [
                    {
                        "UNKWN COL(idx:2)": 28,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 91,
                        "UNKWN COL(idx:5)": 93,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 212
                    }
                ],
                "98.0": [
                    {
                        "UNKWN COL(idx:2)": 29,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 91,
                        "UNKWN COL(idx:5)": 96,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 216
                    }
                ],
                "99.0": [
                    {
                        "UNKWN COL(idx:2)": 29,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 91,
                        "UNKWN COL(idx:5)": 96,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 216
                    }
                ],
                "99.9": [
                    {
                        "UNKWN COL(idx:2)": 29,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 91,
                        "UNKWN COL(idx:5)": 96,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 216
                    }
                ],
                "100.0": [
                    {
                        "UNKWN COL(idx:2)": 30,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 96,
                        "UNKWN COL(idx:5)": 98,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 224
                    }
                ]
            }
        }
    ],
    "http-in/server-1": [
        {
            "timestamp": "2018-10-20-14:05:00.790",
            "1xx": 0,
            "2xx": 0,
            "3xx": 23,
            "4xx": 0,
            "5xx": 0,
            "other": 0,
            "tot_req": 23,
            "req_ok": 23,
            "pct_ok": "100.0",
            "avg_ct": 90,
            "avg_rt": 91,
            "ms_since_last_entry": 5017,
            "percentile": {
                "95.0": [
                    {
                        "UNKWN COL(idx:2)": 28,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 92,
                        "UNKWN COL(idx:5)": 92,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 212
                    }
                ],
                "98.0": [
                    {
                        "UNKWN COL(idx:2)": 29,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 92,
                        "UNKWN COL(idx:5)": 94,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 215
                    }
                ],
                "99.0": [
                    {
                        "UNKWN COL(idx:2)": 29,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 92,
                        "UNKWN COL(idx:5)": 94,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 215
                    }
                ],
                "99.9": [
                    {
                        "UNKWN COL(idx:2)": 29,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 92,
                        "UNKWN COL(idx:5)": 94,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 215
                    }
                ],
                "100.0": [
                    {
                        "UNKWN COL(idx:2)": 30,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 92,
                        "UNKWN COL(idx:5)": 97,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 219
                    }
                ]
            }
        },
        {
            "timestamp": "2018-10-20-14:05:05.808",
            "1xx": 0,
            "2xx": 0,
            "3xx": 22,
            "4xx": 0,
            "5xx": 0,
            "other": 0,
            "tot_req": 22,
            "req_ok": 22,
            "pct_ok": "100.0",
            "avg_ct": 90,
            "avg_rt": 91,
            "ms_since_last_entry": 5018,
            "percentile": {
                "95.0": [
                    {
                        "UNKWN COL(idx:2)": 28,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 91,
                        "UNKWN COL(idx:5)": 93,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 212
                    }
                ],
                "98.0": [
                    {
                        "UNKWN COL(idx:2)": 29,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 91,
                        "UNKWN COL(idx:5)": 96,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 216
                    }
                ],
                "99.0": [
                    {
                        "UNKWN COL(idx:2)": 29,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 91,
                        "UNKWN COL(idx:5)": 96,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 216
                    }
                ],
                "99.9": [
                    {
                        "UNKWN COL(idx:2)": 29,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 91,
                        "UNKWN COL(idx:5)": 96,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 216
                    }
                ],
                "100.0": [
                    {
                        "UNKWN COL(idx:2)": 30,
                        "UNKWN COL(idx:3)": 0,
                        "UNKWN COL(idx:4)": 96,
                        "UNKWN COL(idx:5)": 98,
                        "UNKWN COL(idx:6)": 0,
                        "sum": 224
                    }
                ]
            }
        }
    ]
}
```