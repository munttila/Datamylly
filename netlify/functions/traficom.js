exports.handler = async function(event) {

  const BASE = "https://trafi2.stat.fi/PXWeb/api/v1/fi/TraFi/TraFi__Kaytettyna_maahantuodut/040_yksmaah_tau_104.px";

  const results = {};

  // Test 1: GET metadata
  try {
    const r = await fetch(BASE, { method: "GET" });
    const txt = await r.text();
    results.test1_GET_metadata = {
      status: r.status,
      body: txt.slice(0, 1000)
    };
  } catch(e) { results.test1_GET_metadata = { error: e.message }; }

  // Test 2: POST with ALL 4 variables including required ones
  try {
    const r = await fetch(BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: [
          { code: "Merkki",              selection: { filter: "item", values: ["Volkswagen"] } },
          { code: "K\u00e4ytt\u00f6\u00f6nottovuosi", selection: { filter: "item", values: ["2024"] } },
          { code: "K\u00e4ytt\u00f6voima",       selection: { filter: "item", values: ["Yhteens\u00e4"] } },
          { code: "Kuukausi",            selection: { filter: "item", values: ["2024M01"] } }
        ],
        response: { format: "json" }
      })
    });
    const txt = await r.text();
    results.test2_POST_all4_fi = { status: r.status, body: txt.slice(0, 500) };
  } catch(e) { results.test2_POST_all4_fi = { error: e.message }; }

  // Test 3: POST with top(1) filter to get any data
  try {
    const r = await fetch(BASE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: [
          { code: "Merkki",              selection: { filter: "top", values: ["1"] } },
          { code: "K\u00e4ytt\u00f6\u00f6nottovuosi", selection: { filter: "top", values: ["1"] } },
          { code: "K\u00e4ytt\u00f6voima",       selection: { filter: "top", values: ["1"] } },
          { code: "Kuukausi",            selection: { filter: "top", values: ["1"] } }
        ],
        response: { format: "json" }
      })
    });
    const txt = await r.text();
    results.test3_POST_top1 = { status: r.status, body: txt.slice(0, 1000) };
  } catch(e) { results.test3_POST_top1 = { error: e.message }; }

  // Test 4: English endpoint GET
  try {
    const r = await fetch(
      "https://trafi2.stat.fi/PXWeb/api/v1/en/TraFi/TraFi__Kaytettyna_maahantuodut/040_yksmaah_tau_104.px",
      { method: "GET" }
    );
    const txt = await r.text();
    results.test4_EN_GET = { status: r.status, body: txt.slice(0, 1000) };
  } catch(e) { results.test4_EN_GET = { error: e.message }; }

  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    body: JSON.stringify(results, null, 2)
  };
};
