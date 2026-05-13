exports.handler = async function(event) {

  const API = "https://trafi2.stat.fi/PXWeb/api/v1/fi/TraFi/TraFi__Kaytettyna_maahantuodut/040_yksmaah_tau_104.px";

  // All Finnish special chars as unicode escapes to avoid encoding issues
  // K\u00e4ytt\u00f6\u00f6nottovuosi = Käyttöönottovuosi
  // K\u00e4ytt\u00f6voima = Käyttövoima
  // Yhteens\u00e4 = Yhteensä

  const query = {
    query: [
      {
        code: "Merkki",
        selection: { filter: "item", values: ["Volkswagen"] }
      },
      {
        code: "K\u00e4ytt\u00f6\u00f6nottovuosi",
        selection: { filter: "item", values: ["2024"] }
      },
      {
        code: "K\u00e4ytt\u00f6voima",
        selection: { filter: "item", values: ["Yhteens\u00e4"] }
      },
      {
        code: "Kuukausi",
        selection: { filter: "item", values: ["2024M01", "2024M02", "2024M03"] }
      }
    ],
    response: { format: "json" }
  };

  try {
    const resp = await fetch(API, {
      method: "POST",
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json"
      },
      body: JSON.stringify(query)
    });

    const text = await resp.text();

    return {
      statusCode: resp.status,
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "Access-Control-Allow-Origin": "*"
      },
      body: text
    };

  } catch(e) {
    return {
      statusCode: 500,
      headers: { "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify({ error: e.message })
    };
  }
};
