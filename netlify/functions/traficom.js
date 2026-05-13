exports.handler = async function(event) {

  const API = "https://trafi2.stat.fi/PXWeb/api/v1/fi/TraFi/TraFi__Kaytettyna_maahantuodut/040_yksmaah_tau_104.px";

  // Minimal possible query - just one brand, one year, one month, no fuel filter
  const query = {
    query: [
      { code: "Merkki",   selection: { filter: "item", values: ["Volkswagen"] } },
      { code: "Kuukausi", selection: { filter: "item", values: ["2024M01"] } }
    ],
    response: { format: "json" }
  };

  const bodyStr = JSON.stringify(query);

  try {
    const resp = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: bodyStr
    });

    const text = await resp.text();

    // Return everything for debugging
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify({
        traficom_status: resp.status,
        traficom_statustext: resp.statusText,
        query_sent: query,
        body_sent: bodyStr,
        traficom_response: text.slice(0, 2000)
      }, null, 2)
    };

  } catch(e) {
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      body: JSON.stringify({ fetch_error: e.message, stack: e.stack })
    };
  }
};
