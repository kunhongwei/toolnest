import json, time, os, jwt, requests
key = json.loads(base64.b64decode(os.environ["GA4_KEY"]))
now = int(time.time())
assertion = jwt.encode({"iss": key["client_email"], "scope":"https://www.googleapis.com/auth/analytics.readonly",
  "aud":"https://oauth2.googleapis.com/token","iat":now,"exp":now+3500}, key["private_key"], algorithm="RS256")
tok = requests.post("https://oauth2.googleapis.com/token",
  data={"grant_type":"urn:ietf:params:oauth:grant-type:jwt-bearer","assertion":assertion}, timeout=30).json()["access_token"]
H = {"Authorization": f"Bearer {tok}"}
def run(dims, mets, days):
    r = requests.post("https://analyticsdata.googleapis.com/v1beta/properties/559360917:runReport",
      headers=H, json={"dateRanges":[{"startDate":f"{days}daysAgo","endDate":"today"}],
      "dimensions":[{"name":d} for d in dims], "metrics":[{"name":m} for m in mets],
      "orderBys":[{"desc":True,"metric":{"metricName":mets[0]}}], "limit":15}, timeout=30)
    return r.json().get("rows", [])
report = {
  "generated": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
  "last7": {
    "daily": run(["date"], ["activeUsers","screenPageViews"], 7),
    "pages": run(["pagePath"], ["screenPageViews","activeUsers"], 7),
    "countries": run(["country"], ["activeUsers"], 7),
    "events": run(["eventName"], ["eventCount"], 7),
    "sources": run(["sessionDefaultChannelGroup"], ["sessions"], 7),
  },
  "last30": {
    "pages": run(["pagePath"], ["screenPageViews"], 30),
    "countries": run(["country"], ["activeUsers"], 30),
  },
}
with open("ga4-report.json","w") as f: json.dump(report, f, indent=1)
print("report written")
