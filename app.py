from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

COMMODITIES = [
    {
        "name": "Maize",
        "unit": "kg",
        "price_per_unit": 0.42,
        "image": "https://images.unsplash.com/photo-1601599561213-832382fd07ba?auto=format&fit=crop&w=1200&q=80",
        "description": "A staple grain used for flour, animal feed, and household meals.",
    },
    {
        "name": "Beans",
        "unit": "kg",
        "price_per_unit": 1.10,
        "image": "https://images.unsplash.com/photo-1515543904379-3d757afe72e5?auto=format&fit=crop&w=1200&q=80",
        "description": "Protein-rich legumes sold in local markets and cooperatives.",
    },
    {
        "name": "Tomatoes",
        "unit": "crate",
        "price_per_unit": 8.50,
        "image": "https://images.unsplash.com/photo-1546470427-e26264be0b0d?auto=format&fit=crop&w=1200&q=80",
        "description": "Fresh produce harvested for urban markets and food processors.",
    },
    {
        "name": "Coffee",
        "unit": "kg",
        "price_per_unit": 3.75,
        "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1200&q=80",
        "description": "Premium beans prepared for local roasters and export buyers.",
    },
]


def render_page(valuation_results=None, total_value=0.0):
    valuation_results = valuation_results or []

    cards = "".join(
        f"""
        <article class=\"card\">
            <img src=\"{item['image']}\" alt=\"{item['name']}\" />
            <div class=\"card-body\">
                <h3>{item['name']}</h3>
                <p>{item['description']}</p>
                <p class=\"price\">Market price: ${item['price_per_unit']:.2f} / {item['unit']}</p>
            </div>
        </article>
        """
        for item in COMMODITIES
    )

    fields = "".join(
        f"""
        <label for=\"{item['name'].lower()}\">{item['name']} yield ({item['unit']})</label>
        <input type=\"number\" min=\"0\" step=\"0.01\" id=\"{item['name'].lower()}\" name=\"{item['name'].lower()}\" placeholder=\"Enter amount harvested\" />
        """
        for item in COMMODITIES
    )

    results_section = ""
    if valuation_results:
        rows = "".join(
            f"""
            <tr>
                <td>{row['name']}</td>
                <td>{row['quantity']:.2f} {row['unit']}</td>
                <td>${row['price_per_unit']:.2f}</td>
                <td>${row['estimated_value']:.2f}</td>
            </tr>
            """
            for row in valuation_results
        )

        results_section = f"""
        <section class=\"results\">
            <h2>Estimated Earnings</h2>
            <table>
                <thead>
                    <tr>
                        <th>Commodity</th>
                        <th>Yield</th>
                        <th>Unit Price (USD)</th>
                        <th>Estimated Value (USD)</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
                <tfoot>
                    <tr>
                        <td colspan=\"3\">Total Potential Earnings</td>
                        <td>${total_value:.2f}</td>
                    </tr>
                </tfoot>
            </table>
        </section>
        """

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Farmer Inventory & Commodity Value</title>
  <link rel=\"stylesheet\" href=\"/styles.css\" />
</head>
<body>
  <header class=\"hero\">
    <h1>Farmer Inventory Showcase</h1>
    <p>Track your harvested commodities, enter current yields, and estimate your market value instantly.</p>
  </header>

  <main class=\"container\">
    <section>
      <h2>Available Commodities</h2>
      <div class=\"card-grid\">{cards}</div>
    </section>

    <section class=\"calculator\">
      <h2>Yield Value Calculator</h2>
      <form method=\"POST\" action=\"/\">{fields}<button type=\"submit\">Calculate Commodity Value</button></form>
    </section>
    {results_section}
  </main>
</body>
</html>
"""


class FarmerInventoryHandler(BaseHTTPRequestHandler):
    def _send_html(self, content):
        encoded = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_css(self):
        with open("static/styles.css", "r", encoding="utf-8") as css_file:
            content = css_file.read().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/css; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        if self.path == "/styles.css":
            self._send_css()
            return
        self._send_html(render_page())

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_data = self.rfile.read(content_length).decode("utf-8")
        form_data = parse_qs(raw_data)

        valuation_results = []
        total_value = 0.0
        for item in COMMODITIES:
            key = item["name"].lower()
            try:
                quantity = max(float(form_data.get(key, ["0"])[0]), 0.0)
            except ValueError:
                quantity = 0.0

            estimated_value = quantity * item["price_per_unit"]
            total_value += estimated_value
            valuation_results.append(
                {
                    "name": item["name"],
                    "unit": item["unit"],
                    "quantity": quantity,
                    "price_per_unit": item["price_per_unit"],
                    "estimated_value": estimated_value,
                }
            )

        self._send_html(render_page(valuation_results, total_value))


def run_server(host="0.0.0.0", port=5000):
    server = HTTPServer((host, port), FarmerInventoryHandler)
    print(f"Serving Farmer Inventory Showcase at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
