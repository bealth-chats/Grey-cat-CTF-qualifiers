const http = require('http');

function decodeStamp(stamp, traceId) {
  try {
    const encoded = atob(stamp);
    const parts = String(traceId || "").split("-");
    const seed = parts.length >= 3 ? parts[1] : "";
    const index = Number(parts.length >= 3 ? parts[2] : 0) - 1;
    const keyBase = seed.split("").reduce((sum, ch) => sum + ch.charCodeAt(0), 0) + Math.max(0, index) * 17;
    let output = "";

    for (let i = 0; i < encoded.length; i += 1) {
      const code = encoded.charCodeAt(i) ^ ((keyBase + i * 13) & 0xff);
      output += String.fromCharCode(code);
    }

    return output;
  } catch (error) {
    return null;
  }
}

async function solve() {
  const bootstrapRes = await fetch("http://challs.nusgreyhats.org:34467/api/bootstrap");
  const bootstrapData = await bootstrapRes.json();
  const session = bootstrapRes.headers.get('set-cookie');

  let tick = 0;
  let score = 0;
  let speed = 7;
  let lastReportTick = -24;
  let headers = session ? { "Cookie": session.split(';')[0] } : {};
  let flagFragments = [];
  let ghostIdx = 0;

  while (score < bootstrapData.fastPhaseScore + 4000) {
    tick += 1;
    score += 0.24 * speed;
    speed = Math.min(28, 7 + score / 180);

    if (tick - lastReportTick >= 24) {
      lastReportTick = tick;
      await fetch(`http://challs.nusgreyhats.org:34467/api/run?score=${Math.floor(score)}&tick=${tick}&state=running`, { headers });
    }

    if (score >= bootstrapData.fastPhaseScore && tick % 50 === 0) {
      const lane = ghostIdx % 2;
      const res = await fetch(`http://challs.nusgreyhats.org:34467/api/ghost?score=${Math.floor(score)}&lane=${lane}`, {
        headers: { ...headers, "X-Runner-Debug": "trace" }
      });
      const data = await res.json();
      if (data.stamp) {
          const decoded = decodeStamp(data.stamp, data.traceId);
          if (!flagFragments.includes(decoded)) {
             flagFragments.push(decoded);
             console.log(`Score ${score}, Lane ${lane}: ${decoded}`);
          }
          ghostIdx++;
      }
    }
  }

  console.log("Decoded ghosts:", flagFragments);
}

solve().catch(console.error);
