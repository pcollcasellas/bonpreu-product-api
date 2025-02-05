from bs4 import BeautifulSoup


def parse_nutritional_data_table(html):
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")
    if not table:
        return None

    rows = table.find_all("tr")

    headers = ["productNutritionalValue", "productNutritionalQuantity"]
    data = [[td.get_text(strip=True) for td in row.find_all("td")] for row in rows]

    if headers:
        return [dict(zip(headers, row)) for row in data]
    else:
        return data  # Return as a list of lists if headers are not present
