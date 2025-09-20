import json
import os

# Environment variable substitution helpers

def _replace_env_in_value(value):
    if not isinstance(value, str):
        return value
    result = ""
    i = 0
    while i < len(value):
        if value[i] == '$' and i + 1 < len(value) and value[i + 1] == '{':
            j = i + 2
            while j < len(value) and value[j] != '}':
                j += 1
            if j < len(value) and value[j] == '}':
                var_name = value[i + 2:j]
                result += os.environ.get(var_name, "")
                i = j + 1
                continue
        result += value[i]
        i += 1
    return result


def _replace_env_recursively(obj):
    if isinstance(obj, dict):
        return {k: _replace_env_recursively(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_replace_env_recursively(v) for v in obj]
    return _replace_env_in_value(obj)


def generate_k6_script(config_file, output_file="scripts/load_test.js"):
    with open(config_file) as f:
        config = json.load(f)

    # Resolve environment variables in the config
    config = _replace_env_recursively(config)

    vus = config.get("vus", 5)
    duration = config.get("duration", "10s")
    scenarios = config.get("scenarios", [])
    base_url = config.get("baseUrl")
    stages = config.get("stages")  # e.g., [{"duration":"10s","target":10}]
    thresholds = config.get("thresholds")  # e.g., {"http_req_duration": ["p(95)<500"]}
    global_tags = config.get("tags")  # e.g., {"env":"poc"}
    default_sleep = config.get("sleep", 1)
    data_file = config.get("dataFile")  # optional: CSV file path

    # Build k6 options
    options_obj = {}
    if stages:
        options_obj["stages"] = stages
    else:
        options_obj["vus"] = vus
        options_obj["duration"] = duration
    if thresholds:
        options_obj["thresholds"] = thresholds
    if global_tags:
        options_obj["tags"] = global_tags

    options_json = json.dumps(options_obj)

    # Imports and optional data loader
    script_parts = []
    script_parts.append("import http from 'k6/http';")
    script_parts.append("import { check, sleep } from 'k6';")

    data_loader_code = ""
    if data_file:
        # path used by k6 open() should be relative to the script location
        rel_path = os.path.relpath(data_file, start=os.path.dirname(output_file) or ".")
        data_loader_code = f"""
import {{ SharedArray }} from 'k6/data';
const csvData = new SharedArray('csvData', function() {{
  const text = open('{rel_path}');
  const lines = text.split('\n').filter(l => l.trim().length > 0);
  if (lines.length == 0) return [];
  const headers = lines.shift().split(',').map(h => h.trim());
  return lines.map(line => {{
    const vals = line.split(',');
    const obj = {{}};
    for (let i = 0; i < headers.length; i++) {{
      obj[headers[i]] = (vals[i] !== undefined ? String(vals[i]).trim() : '');
    }}
    return obj;
  }});
}});
"""
        script_parts.append(data_loader_code)

    # Helpers injected into k6 script: JSON path getter and simple template {{key}}
    helpers_code = """
function getByPath(obj, path) {
  try {
    return path.split('.').reduce((o, k) => (o && (k in o)) ? o[k] : undefined, obj);
  } catch (e) {
    return undefined;
  }
}

function tpl(str, row) {
  if (str === undefined || str === null) return '';
  return String(str).replace(/\{\{(\w+)\}\}/g, function(_, k) {
    return row && row[k] !== undefined ? String(row[k]) : '';
  });
}
"""
    script_parts.append(helpers_code)

    # Options
    script_parts.append(f"export let options = {options_json};\n")

    # Start default function
    script_parts.append("export default function () {\n")
    if data_file:
        script_parts.append("  const row = (typeof csvData !== 'undefined' && csvData.length) ? csvData[__ITER % csvData.length] : null;\n")
    else:
        script_parts.append("  const row = null;\n")

    for sc in scenarios:
        name = sc["name"]
        method = sc["method"].upper()
        url = sc["url"]
        expected = sc.get("expectedStatus", 200)
        headers = sc.get("headers", {})
        body = sc.get("body")
        scenario_tags = sc.get("tags", {})
        scenario_sleep = sc.get("sleep", default_sleep)
        json_checks = sc.get("jsonChecks", [])  # list of { path: 'data.id', equals: 123 }

        # Resolve URL against baseUrl if relative
        final_url = url
        if base_url and not (url.startswith("http://") or url.startswith("https://")):
            if url.startswith("/"):
                final_url = base_url.rstrip("/") + url
            else:
                final_url = base_url.rstrip("/") + "/" + url

        headers_json_str = json.dumps(headers)
        tags_json = json.dumps(scenario_tags)

        # Build JSON checks code
        checks_lines = ""
        for jc in json_checks:
            path_expr = jc.get("path")
            if not path_expr:
                continue
            equals_val = json.dumps(jc.get("equals"))
            checks_lines += (
                f"      check(j, {{ '{name} json {path_expr} equals': () => getByPath(j, '{path_expr}') === {equals_val} }});\n"
            )

        if method == "GET":
            script_parts.append(f"""
  {{
    const url = tpl('{final_url}', row);
    let headers = JSON.parse('{headers_json_str}');
    for (let k in headers) {{ headers[k] = tpl(headers[k], row); }}
    let res = http.get(url, {{ headers: headers, tags: {tags_json} }});
    check(res, {{ '{name} status is {expected}': (r) => r.status === {expected} }});
    try {{
      const j = res.json();
{checks_lines}    }} catch (_) {{}}
  }}
  sleep({scenario_sleep});
""")
        else:
            js_body = json.dumps(body) if body else "{}"
            # We template the stringified body at runtime
            script_parts.append(f"""
  {{
    const url = tpl('{final_url}', row);
    let headers = JSON.parse('{headers_json_str}');
    for (let k in headers) {{ headers[k] = tpl(headers[k], row); }}
    const bodyTpl = tpl({json.dumps(js_body)}, row);
    let payload = bodyTpl;
    let res = http.request('{method}', url, payload, {{ headers: headers, tags: {tags_json} }});
    check(res, {{ '{name} status is {expected}': (r) => r.status === {expected} }});
    try {{
      const j = res.json();
{checks_lines}    }} catch (_) {{}}
  }}
  sleep({scenario_sleep});
""")

    # Close default function
    script_parts.append("}\n")

    script = "\n".join(script_parts)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        f.write(script)
    print(f"✅ Stronger k6 script generated: {output_file}")
