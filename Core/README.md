# Loadwrap - k6 Wrapper

## Run Test
```bash
python cli.py run config/sample_config.json --report html
```

## Example Config
```json
{
  "duration": "30s",
  "vus": 5,
  "scenarios": [
    {
      "name": "Get Users",
      "method": "GET",
      "url": "https://jsonplaceholder.typicode.com/users",
      "expectedStatus": 200
    }
  ]
}
```
# K6loadPOC
