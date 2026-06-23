const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");

// Color Palette — Deep Navy + Electric Blue + White
const C = {
  navy:    "0D1B3E",  // dark bg
  blue:    "1A6EFC",  // primary accent
  cyan:    "3DD6F5",  // secondary accent
  white:   "FFFFFF",
  offWhite:"F0F4FF",
  muted:   "8FA8C8",
  card:    "132044",  // card background on dark slides
  light:   "EFF4FF",  // light slide bg
  lightCard:"FFFFFF",
  darkText:"0D1B3E",
  mutedText:"4A6080",
};

// Icon helper
async function iconToBase64(IconComponent, color = "#FFFFFF", size = 256) {
  const { FaRocket, FaLightbulb, FaChartBar, FaUsers, FaDollarSign,
          FaTrophy, FaRoad, FaHandshake, FaGlobe, FaCheckCircle,
          FaCogs, FaStar, FaBolt } = require("react-icons/fa");
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}

const { FaRocket, FaLightbulb, FaChartBar, FaUsers, FaDollarSign,
        FaTrophy, FaRoad, FaHandshake, FaGlobe, FaCheckCircle,
        FaCogs, FaStar, FaBolt } = require("react-icons/fa");

const makeShadow = () => ({ type:"outer", color:"000000", blur:8, offset:3, angle:45, opacity:0.18 });

async function buildDeck() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.title = "Startup Pitch Demo Template";

  // ─────────────────────────────────────────────
  // SLIDE 1: TITLE SLIDE (dark)
  // ─────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };

    // Big gradient circle decoration (right side)
    s.addShape(pres.shapes.OVAL, { x:6.5, y:-1.2, w:5.5, h:5.5,
      fill:{ color:C.blue, transparency:75 }, line:{ color:C.blue, transparency:60, width:1 } });
    s.addShape(pres.shapes.OVAL, { x:7.5, y:2.5, w:3.5, h:3.5,
      fill:{ color:C.cyan, transparency:82 }, line:{ color:C.cyan, transparency:70, width:1 } });

    // Small decorative dots
    for (let i=0;i<5;i++) {
      s.addShape(pres.shapes.OVAL, { x:0.3+i*0.22, y:5.1, w:0.08, h:0.08,
        fill:{ color:C.blue, transparency: i%2===0?0:50 }, line:{ color:"000000", transparency:100 } });
    }

    // Logo placeholder circle
    s.addShape(pres.shapes.OVAL, { x:0.55, y:0.55, w:1.0, h:1.0,
      fill:{ color:C.blue }, line:{ color:C.cyan, width:2 } });
    s.addText("LOGO", { x:0.55, y:0.55, w:1.0, h:1.0,
      fontSize:10, color:C.white, bold:true, align:"center", valign:"middle" });

    // Startup Name
    s.addText("Your Startup Name", {
      x:0.55, y:1.85, w:6.5, h:1.1,
      fontSize:44, color:C.white, bold:true, align:"left", margin:0,
    });

    // Tagline
    s.addText("One powerful line that captures what you do", {
      x:0.55, y:3.05, w:6.2, h:0.55,
      fontSize:18, color:C.cyan, italic:true, align:"left", margin:0,
    });

    // Thin separator
    s.addShape(pres.shapes.RECTANGLE, { x:0.55, y:3.72, w:2.5, h:0.04,
      fill:{ color:C.blue }, line:{ color:"000000", transparency:100 } });

    // Event label
    s.addText("Startup Pitch Competition  •  2025", {
      x:0.55, y:3.9, w:5, h:0.4,
      fontSize:12, color:C.muted, align:"left", margin:0,
    });

    // Bottom instruction badge
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:0.55, y:4.85, w:4.5, h:0.55,
      fill:{ color:C.card }, line:{ color:C.blue, width:1 }, rectRadius:0.08 });
    s.addText("📋  Replace all placeholder text with your startup's details", {
      x:0.55, y:4.85, w:4.5, h:0.55,
      fontSize:11, color:C.muted, align:"center", valign:"middle",
    });
  }

  // ─────────────────────────────────────────────
  // SLIDE 2: PROBLEM (light bg)
  // ─────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.light };

    // Header band
    s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:10, h:1.1,
      fill:{ color:C.navy }, line:{ color:"000000", transparency:100 } });
    s.addText("02", { x:0.4, y:0, w:0.8, h:1.1,
      fontSize:28, color:C.blue, bold:true, align:"center", valign:"middle", margin:0 });
    s.addText("THE PROBLEM", { x:1.1, y:0, w:5, h:1.1,
      fontSize:22, color:C.white, bold:true, align:"left", valign:"middle", margin:0 });

    const iconData = await iconToBase64(FaLightbulb, "#1A6EFC", 256);
    s.addImage({ data: iconData, x:9.2, y:0.25, w:0.55, h:0.55 });

    // Three problem cards
    const cards = [
      { title:"What's the Problem?", body:"Describe the core pain point or gap in the market that your startup addresses. Be specific and compelling.", icon: FaLightbulb },
      { title:"Who Faces It?",       body:"Define your target audience — their demographics, behaviors, and why this problem is especially painful for them.", icon: FaUsers },
      { title:"Why Does It Matter?", body:"Quantify the impact. How much time, money, or opportunity is lost? Use data or relatable examples here.", icon: FaChartBar },
    ];

    for (let i=0; i<3; i++) {
      const cx = 0.4 + i*3.2;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:cx, y:1.35, w:2.9, h:3.85,
        fill:{ color:C.lightCard }, line:{ color:"E0E8FF", width:1.5 }, rectRadius:0.12,
        shadow: makeShadow() });

      // Icon circle
      s.addShape(pres.shapes.OVAL, { x:cx+0.3, y:1.6, w:0.7, h:0.7,
        fill:{ color:C.navy }, line:{ color:"000000", transparency:100 } });

      const ic = await iconToBase64(cards[i].icon, "#1A6EFC", 256);
      s.addImage({ data:ic, x:cx+0.38, y:1.68, w:0.54, h:0.54 });

      s.addText(cards[i].title, { x:cx+0.15, y:2.45, w:2.6, h:0.55,
        fontSize:13, color:C.darkText, bold:true, align:"center", margin:0 });
      s.addText(cards[i].body, { x:cx+0.15, y:3.05, w:2.6, h:2.0,
        fontSize:11, color:C.mutedText, align:"left", valign:"top", margin:0 });
    }

    // Bottom tip
    s.addText("💡  Tip: Use a real story or statistic to make the problem feel urgent.", {
      x:0.4, y:5.2, w:9.2, h:0.35, fontSize:10, color:C.mutedText, align:"left", margin:0 });
  }

  // ─────────────────────────────────────────────
  // SLIDE 3: SOLUTION (dark)
  // ─────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };

    s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:10, h:1.1,
      fill:{ color:C.card }, line:{ color:"000000", transparency:100 } });
    s.addText("03", { x:0.4, y:0, w:0.8, h:1.1,
      fontSize:28, color:C.cyan, bold:true, align:"center", valign:"middle", margin:0 });
    s.addText("OUR SOLUTION", { x:1.1, y:0, w:5, h:1.1,
      fontSize:22, color:C.white, bold:true, align:"left", valign:"middle", margin:0 });

    const ic = await iconToBase64(FaRocket, "#3DD6F5", 256);
    s.addImage({ data:ic, x:9.1, y:0.22, w:0.6, h:0.6 });

    // Left: description column
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:0.4, y:1.35, w:4.3, h:3.8,
      fill:{ color:C.card }, line:{ color:C.blue, width:1.5 }, rectRadius:0.12 });

    s.addText("Your Solution", { x:0.65, y:1.6, w:3.8, h:0.5,
      fontSize:18, color:C.cyan, bold:true, align:"left", margin:0 });
    s.addText([
      { text: "Proposed Solution\n", options:{ bold:true, color:C.white, fontSize:12 } },
      { text: "Describe in 2–3 sentences how your product or service works and how it directly addresses the problem you identified.\n\n", options:{ color:C.muted, fontSize:11 } },
      { text: "How It Solves the Problem\n", options:{ bold:true, color:C.white, fontSize:12 } },
      { text: "Explain the mechanism — what makes this approach effective where others have failed?\n\n", options:{ color:C.muted, fontSize:11 } },
      { text: "Main Benefits\n", options:{ bold:true, color:C.white, fontSize:12 } },
      { text: "List the top 2–3 outcomes your users will experience.", options:{ color:C.muted, fontSize:11 } },
    ], { x:0.65, y:2.2, w:3.8, h:2.75, align:"left", valign:"top", margin:0 });

    // Right: 3 benefit cards
    const benefits = [
      { label:"Benefit 1", desc:"Speed, cost, convenience — pick your top win", color:C.blue },
      { label:"Benefit 2", desc:"Second strongest outcome for your customers", color:C.cyan },
      { label:"Benefit 3", desc:"Longer-term or strategic advantage gained", color:"7C3AED" },
    ];
    for (let i=0;i<3;i++) {
      const cy = 1.35 + i*1.3;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:5.1, y:cy, w:4.5, h:1.1,
        fill:{ color:C.card }, line:{ color:benefits[i].color, width:1.5 }, rectRadius:0.1 });
      s.addShape(pres.shapes.OVAL, { x:5.25, y:cy+0.2, w:0.65, h:0.65,
        fill:{ color:benefits[i].color, transparency:20 }, line:{ color:"000000", transparency:100 } });
      const icBenefit = await iconToBase64(FaCheckCircle, "#"+benefits[i].color, 256);
      s.addImage({ data:icBenefit, x:5.32, y:cy+0.27, w:0.51, h:0.51 });
      s.addText(benefits[i].label, { x:6.05, y:cy+0.1, w:3.3, h:0.4,
        fontSize:13, color:C.white, bold:true, align:"left", margin:0 });
      s.addText(benefits[i].desc, { x:6.05, y:cy+0.52, w:3.3, h:0.45,
        fontSize:11, color:C.muted, align:"left", margin:0 });
    }
    // 4th card placeholder
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:5.1, y:4.25, w:4.5, h:0.85,
      fill:{ color:C.card }, line:{ color:C.muted, width:1, dashType:"dash" }, rectRadius:0.1 });
    s.addText("+ Add more benefits as needed", { x:5.1, y:4.25, w:4.5, h:0.85,
      fontSize:11, color:C.muted, italic:true, align:"center", valign:"middle" });
  }

  // ─────────────────────────────────────────────
  // SLIDE 4: PRODUCT DEMO / FEATURES (light)
  // ─────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.light };

    s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:10, h:1.1,
      fill:{ color:C.navy }, line:{ color:"000000", transparency:100 } });
    s.addText("04", { x:0.4, y:0, w:0.8, h:1.1,
      fontSize:28, color:C.blue, bold:true, align:"center", valign:"middle", margin:0 });
    s.addText("PRODUCT DEMO & FEATURES", { x:1.1, y:0, w:7, h:1.1,
      fontSize:22, color:C.white, bold:true, align:"left", valign:"middle", margin:0 });

    // Screenshot placeholder
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:0.4, y:1.35, w:5.2, h:3.85,
      fill:{ color:"D6E4FF" }, line:{ color:C.blue, width:1.5 }, rectRadius:0.15,
      shadow: makeShadow() });
    s.addText("[ Screenshot / Prototype / Workflow Diagram ]", {
      x:0.4, y:2.9, w:5.2, h:0.8, fontSize:13, color:C.mutedText,
      italic:true, align:"center", valign:"middle",
    });
    s.addText("Replace with your actual product screenshot or mockup", {
      x:0.4, y:3.7, w:5.2, h:0.5, fontSize:10, color:C.muted, align:"center" });

    // Feature list
    const features = ["Feature 1 — Core capability", "Feature 2 — Key differentiator",
                      "Feature 3 — User experience highlight", "Feature 4 — Integration / platform",
                      "Feature 5 — Data / analytics / reporting"];
    for (let i=0;i<5;i++) {
      const fy = 1.35 + i*0.77;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:5.9, y:fy, w:3.7, h:0.65,
        fill:{ color:C.lightCard }, line:{ color:"CBD5E1", width:1 }, rectRadius:0.08,
        shadow: { type:"outer", color:"000000", blur:4, offset:1, angle:45, opacity:0.08 } });
      s.addShape(pres.shapes.OVAL, { x:6.08, y:fy+0.1, w:0.42, h:0.42,
        fill:{ color:C.blue }, line:{ color:"000000", transparency:100 } });
      s.addText(String(i+1), { x:6.08, y:fy+0.1, w:0.42, h:0.42,
        fontSize:12, color:C.white, bold:true, align:"center", valign:"middle" });
      s.addText(features[i], { x:6.6, y:fy+0.08, w:2.8, h:0.5,
        fontSize:12, color:C.darkText, align:"left", valign:"middle", margin:0 });
    }
  }

  // ─────────────────────────────────────────────
  // SLIDE 5: TARGET MARKET (dark)
  // ─────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };

    s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:10, h:1.1,
      fill:{ color:C.card }, line:{ color:"000000", transparency:100 } });
    s.addText("05", { x:0.4, y:0, w:0.8, h:1.1,
      fontSize:28, color:C.cyan, bold:true, align:"center", valign:"middle", margin:0 });
    s.addText("TARGET MARKET", { x:1.1, y:0, w:5, h:1.1,
      fontSize:22, color:C.white, bold:true, align:"left", valign:"middle", margin:0 });

    const icGlobe = await iconToBase64(FaGlobe, "#3DD6F5", 256);
    s.addImage({ data:icGlobe, x:9.1, y:0.22, w:0.6, h:0.6 });

    // Big TAM number
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:0.4, y:1.35, w:9.2, h:1.35,
      fill:{ color:C.card }, line:{ color:C.blue, width:1 }, rectRadius:0.12 });
    s.addText("$XX Billion", { x:0.6, y:1.45, w:4, h:1.1,
      fontSize:40, color:C.cyan, bold:true, align:"center", valign:"middle", margin:0 });
    s.addText("Approximate Total Addressable Market (TAM)", {
      x:0.6, y:2.2, w:4, h:0.4, fontSize:11, color:C.muted, align:"center", margin:0 });
    s.addShape(pres.shapes.RECTANGLE, { x:4.85, y:1.6, w:0.04, h:0.9,
      fill:{ color:C.blue, transparency:40 }, line:{ color:"000000", transparency:100 } });
    s.addText([
      { text:"Who are your customers? ", options:{ bold:true, color:C.white, fontSize:12 } },
      { text:"B2B / B2C / Both — describe their industry, role, or demographic.", options:{ color:C.muted, fontSize:11 } },
    ], { x:5.1, y:1.45, w:4.3, h:1.1, align:"left", valign:"middle", margin:0 });

    // Three market segments
    const segs = [
      { icon: FaUsers, label:"Primary Segment", desc:"Describe your earliest adopters and ideal customer profile (ICP)." },
      { icon: FaChartBar, label:"Market Size", desc:"SAM / SOM breakdown. Even rough numbers show you've done the research." },
      { icon: FaStar, label:"Potential Users", desc:"Estimate total number of users or businesses who could benefit globally." },
    ];
    for (let i=0;i<3;i++) {
      const cx = 0.4 + i*3.2;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:cx, y:2.9, w:2.9, h:2.35,
        fill:{ color:C.card }, line:{ color:C.muted, width:1 }, rectRadius:0.1 });
      const icSeg = await iconToBase64(segs[i].icon, "#1A6EFC", 256);
      s.addImage({ data:icSeg, x:cx+0.15, y:3.1, w:0.45, h:0.45 });
      s.addText(segs[i].label, { x:cx+0.7, y:3.05, w:2.0, h:0.55,
        fontSize:13, color:C.white, bold:true, align:"left", margin:0 });
      s.addText(segs[i].desc, { x:cx+0.15, y:3.65, w:2.6, h:1.45,
        fontSize:11, color:C.muted, align:"left", valign:"top", margin:0 });
    }
  }

  // ─────────────────────────────────────────────
  // SLIDE 6: BUSINESS MODEL (light)
  // ─────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.light };

    s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:10, h:1.1,
      fill:{ color:C.navy }, line:{ color:"000000", transparency:100 } });
    s.addText("06", { x:0.4, y:0, w:0.8, h:1.1,
      fontSize:28, color:C.blue, bold:true, align:"center", valign:"middle", margin:0 });
    s.addText("BUSINESS MODEL", { x:1.1, y:0, w:5, h:1.1,
      fontSize:22, color:C.white, bold:true, align:"left", valign:"middle", margin:0 });

    const icDollar = await iconToBase64(FaDollarSign, "#FFFFFF", 256);
    s.addImage({ data:icDollar, x:9.1, y:0.2, w:0.6, h:0.65 });

    const streams = [
      { title:"Revenue Stream", sub:"How you earn money", body:"SaaS subscription, one-time payment, marketplace commission, licensing, etc. Be explicit about your primary model.", icon:FaDollarSign, color:C.blue },
      { title:"Pricing Tiers", sub:"Plans & packages", body:"Free / Starter / Pro / Enterprise tiers. Show price points if known — even rough numbers show you've thought this through.", icon:FaStar, color:"7C3AED" },
      { title:"Other Sources", sub:"Additional income", body:"Advertising, partnerships, data insights, professional services, grants, or government contracts.", icon:FaBolt, color:C.cyan },
    ];

    for (let i=0;i<3;i++) {
      const cx = 0.4 + i*3.2;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:cx, y:1.35, w:2.9, h:4.0,
        fill:{ color:C.lightCard }, line:{ color:"CBD5E1", width:1.5 }, rectRadius:0.12,
        shadow: makeShadow() });

      // Colored top tag
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:cx, y:1.35, w:2.9, h:0.55,
        fill:{ color:streams[i].color }, line:{ color:"000000", transparency:100 }, rectRadius:0.12 });
      // Mask bottom of top tag to make flat bottom corners
      s.addShape(pres.shapes.RECTANGLE, { x:cx, y:1.7, w:2.9, h:0.2,
        fill:{ color:streams[i].color }, line:{ color:"000000", transparency:100 } });

      s.addText(streams[i].title, { x:cx+0.15, y:1.38, w:2.6, h:0.5,
        fontSize:13, color:C.white, bold:true, align:"center", valign:"middle", margin:0 });

      const icStream = await iconToBase64(streams[i].icon, "#"+String(streams[i].color), 256);
      s.addShape(pres.shapes.OVAL, { x:cx+1.05, y:1.85, w:0.8, h:0.8,
        fill:{ color:C.offWhite }, line:{ color:"CBD5E1", width:1 } });
      s.addImage({ data:icStream, x:cx+1.15, y:1.95, w:0.6, h:0.6 });

      s.addText(streams[i].sub, { x:cx+0.15, y:2.75, w:2.6, h:0.4,
        fontSize:12, color:C.darkText, bold:true, align:"center", margin:0 });
      s.addText(streams[i].body, { x:cx+0.15, y:3.2, w:2.6, h:1.9,
        fontSize:11, color:C.mutedText, align:"left", valign:"top", margin:0 });
    }
  }

  // ─────────────────────────────────────────────
  // SLIDE 7: COMPETITIVE ADVANTAGE (dark)
  // ─────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };

    s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:10, h:1.1,
      fill:{ color:C.card }, line:{ color:"000000", transparency:100 } });
    s.addText("07", { x:0.4, y:0, w:0.8, h:1.1,
      fontSize:28, color:C.cyan, bold:true, align:"center", valign:"middle", margin:0 });
    s.addText("COMPETITIVE ADVANTAGE", { x:1.1, y:0, w:7, h:1.1,
      fontSize:22, color:C.white, bold:true, align:"left", valign:"middle", margin:0 });

    const icTrophy = await iconToBase64(FaTrophy, "#3DD6F5", 256);
    s.addImage({ data:icTrophy, x:9.1, y:0.22, w:0.6, h:0.6 });

    // Competition table
    const headers = ["Feature / Criteria", "Competitor A", "Competitor B", "Your Startup ✦"];
    const rows = [
      ["Core Functionality",       "✓",  "✓",  "✓"],
      ["Ease of Use",               "✗",  "Limited",  "✓"],
      ["Pricing",                   "High", "Medium", "Competitive"],
      ["AI / Automation",           "✗",  "✗",  "✓"],
      ["Customer Support",          "Basic","Basic","24/7 Dedicated"],
    ];

    // Header row
    const colWidths = [3.0, 1.8, 1.8, 2.2];
    const colStarts = [0.4, 3.4, 5.2, 7.0];
    headers.forEach((h, i) => {
      const isLast = i === 3;
      s.addShape(pres.shapes.RECTANGLE, { x:colStarts[i], y:1.35, w:colWidths[i]-0.05, h:0.55,
        fill:{ color: isLast ? C.blue : C.card }, line:{ color:"000000", transparency:100 } });
      s.addText(h, { x:colStarts[i]+0.1, y:1.35, w:colWidths[i]-0.2, h:0.55,
        fontSize:12, color:isLast ? C.white : C.cyan, bold:true, align:"center", valign:"middle", margin:0 });
    });

    rows.forEach((row, ri) => {
      const ry = 1.9 + ri * 0.62;
      const bg = ri%2===0 ? C.card : C.navy;
      row.forEach((cell, ci) => {
        const isLast = ci === 3;
        s.addShape(pres.shapes.RECTANGLE, { x:colStarts[ci], y:ry, w:colWidths[ci]-0.05, h:0.57,
          fill:{ color: isLast ? "0A2E6A" : bg }, line:{ color:"000000", transparency:100 } });
        const cellColor = isLast ? C.cyan : (cell==="✓"?C.cyan : cell==="✗"?"FF4444" : C.white);
        s.addText(cell, { x:colStarts[ci]+0.05, y:ry, w:colWidths[ci]-0.15, h:0.57,
          fontSize:12, color:cellColor, bold:isLast, align:"center", valign:"middle", margin:0 });
      });
    });

    // Why choose you
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:0.4, y:5.0, w:9.2, h:0.45,
      fill:{ color:C.blue, transparency:85 }, line:{ color:C.blue, width:1 }, rectRadius:0.06 });
    s.addText("💡  Your edge: Summarize in one line why customers will choose you over everything else.", {
      x:0.4, y:5.0, w:9.2, h:0.45, fontSize:11, color:C.white, align:"center", valign:"middle" });
  }

  // ─────────────────────────────────────────────
  // SLIDE 8: ROADMAP (light)
  // ─────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.light };

    s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:10, h:1.1,
      fill:{ color:C.navy }, line:{ color:"000000", transparency:100 } });
    s.addText("08", { x:0.4, y:0, w:0.8, h:1.1,
      fontSize:28, color:C.blue, bold:true, align:"center", valign:"middle", margin:0 });
    s.addText("ROADMAP & FUTURE PLANS", { x:1.1, y:0, w:7, h:1.1,
      fontSize:22, color:C.white, bold:true, align:"left", valign:"middle", margin:0 });

    const icRoad = await iconToBase64(FaRoad, "#FFFFFF", 256);
    s.addImage({ data:icRoad, x:9.05, y:0.2, w:0.65, h:0.65 });

    // Timeline horizontal line
    s.addShape(pres.shapes.RECTANGLE, { x:0.7, y:3.0, w:8.8, h:0.06,
      fill:{ color:C.blue, transparency:30 }, line:{ color:"000000", transparency:100 } });

    const phases = [
      { label:"Phase 1", timeframe:"Now – 3 Months", color:C.blue, items:["MVP launch","Beta testing","First 50 users","Core feature set"] },
      { label:"Phase 2", timeframe:"3 – 9 Months",   color:"7C3AED", items:["Public launch","Paid customers","Team hiring","Feature expansion"] },
      { label:"Phase 3", timeframe:"9 – 24 Months",  color:C.cyan,   items:["Geographic expansion","Enterprise tier","Partnerships","Series A"] },
    ];

    for (let i=0;i<3;i++) {
      const cx = 0.7 + i*3.1;

      // Circle on timeline
      s.addShape(pres.shapes.OVAL, { x:cx+0.85, y:2.73, w:0.55, h:0.55,
        fill:{ color:phases[i].color }, line:{ color:C.white, width:2 } });
      s.addText(String(i+1), { x:cx+0.85, y:2.73, w:0.55, h:0.55,
        fontSize:14, color:C.white, bold:true, align:"center", valign:"middle" });

      // Top label
      s.addText(phases[i].label, { x:cx, y:1.35, w:2.8, h:0.45,
        fontSize:15, color:phases[i].color, bold:true, align:"center", margin:0 });
      s.addText(phases[i].timeframe, { x:cx, y:1.8, w:2.8, h:0.35,
        fontSize:11, color:C.mutedText, align:"center", margin:0 });

      // Connector
      s.addShape(pres.shapes.RECTANGLE, { x:cx+1.07, y:2.15, w:0.04, h:0.62,
        fill:{ color:phases[i].color, transparency:40 }, line:{ color:"000000", transparency:100 } });

      // Bottom cards
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:cx, y:3.35, w:2.8, h:1.95,
        fill:{ color:C.lightCard }, line:{ color:"CBD5E1", width:1.2 }, rectRadius:0.1,
        shadow: { type:"outer", color:"000000", blur:5, offset:2, angle:45, opacity:0.1 } });

      const textItems = phases[i].items.map((it, j) => ({
        text: it + (j < phases[i].items.length-1 ? "\n" : ""),
        options:{ bullet:true, color:C.darkText, fontSize:12 }
      }));
      s.addText(textItems, { x:cx+0.2, y:3.45, w:2.45, h:1.75,
        align:"left", valign:"top", margin:0, paraSpaceAfter:3 });
    }
  }

  // ─────────────────────────────────────────────
  // SLIDE 9: TEAM & CLOSING (dark)
  // ─────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };

    // Decorative circle
    s.addShape(pres.shapes.OVAL, { x:6.0, y:3.5, w:5.5, h:5.5,
      fill:{ color:C.blue, transparency:88 }, line:{ color:"000000", transparency:100 } });
    s.addShape(pres.shapes.OVAL, { x:-1.5, y:-1.0, w:4.5, h:4.5,
      fill:{ color:C.cyan, transparency:90 }, line:{ color:"000000", transparency:100 } });

    s.addShape(pres.shapes.RECTANGLE, { x:0, y:0, w:10, h:1.1,
      fill:{ color:C.card }, line:{ color:"000000", transparency:100 } });
    s.addText("09", { x:0.4, y:0, w:0.8, h:1.1,
      fontSize:28, color:C.cyan, bold:true, align:"center", valign:"middle", margin:0 });
    s.addText("TEAM & CLOSING", { x:1.1, y:0, w:5, h:1.1,
      fontSize:22, color:C.white, bold:true, align:"left", valign:"middle", margin:0 });

    // Team section
    s.addText("Meet the Team", { x:0.4, y:1.25, w:4.5, h:0.45,
      fontSize:16, color:C.cyan, bold:true, align:"left", margin:0 });

    const members = [
      { name:"Name, Co-Founder & CEO", role:"Background in [industry]. Previously at X.", avatar:"F17" },
      { name:"Name, Co-Founder & CTO", role:"Engineering lead. Built X. Expertise in Y.", avatar:"F18" },
      { name:"Name, Head of Design",   role:"UX specialist. Designed products used by 1M+ users.", avatar:"F19" },
      { name:"Name, Marketing Lead",   role:"Growth hacker. Scaled [startup] from 0 to 100K users.", avatar:"F20" },
    ];

    for (let i=0;i<4;i++) {
      const row = Math.floor(i/2), col = i%2;
      const cx = 0.4 + col*2.2;
      const cy = 1.8 + row*1.3;

      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:cx, y:cy, w:2.0, h:1.1,
        fill:{ color:C.card }, line:{ color:C.muted, width:0.5 }, rectRadius:0.1 });
      s.addShape(pres.shapes.OVAL, { x:cx+0.1, y:cy+0.15, w:0.75, h:0.75,
        fill:{ color:C.blue, transparency:20 }, line:{ color:C.cyan, width:1.5 } });
      s.addText("👤", { x:cx+0.1, y:cy+0.15, w:0.75, h:0.75,
        fontSize:20, align:"center", valign:"middle" });
      s.addText(members[i].name, { x:cx+0.92, y:cy+0.08, w:0.95, h:0.45,
        fontSize:9, color:C.white, bold:true, align:"left", margin:0 });
      s.addText(members[i].role, { x:cx+0.92, y:cy+0.52, w:0.95, h:0.45,
        fontSize:8, color:C.muted, align:"left", margin:0 });
    }

    // Thank you block
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:4.9, y:1.25, w:4.8, h:3.9,
      fill:{ color:C.card }, line:{ color:C.blue, width:1.5 }, rectRadius:0.15 });

    const icRocket = await iconToBase64(FaRocket, "#1A6EFC", 256);
    s.addImage({ data:icRocket, x:6.8, y:1.55, w:0.8, h:0.8 });

    s.addText("Thank You!", {
      x:4.9, y:2.4, w:4.8, h:0.75,
      fontSize:34, color:C.white, bold:true, align:"center", margin:0 });
    s.addText("We're excited about what we're building.\nLet's connect and make it happen.", {
      x:5.1, y:3.2, w:4.4, h:0.75,
      fontSize:13, color:C.muted, align:"center", margin:0 });

    s.addText("📧  hello@yourstartup.com", { x:5.1, y:4.05, w:4.4, h:0.35,
      fontSize:12, color:C.cyan, align:"center", margin:0 });
    s.addText("🌐  www.yourstartup.com", { x:5.1, y:4.4, w:4.4, h:0.35,
      fontSize:12, color:C.cyan, align:"center", margin:0 });

    // Bottom strip
    s.addShape(pres.shapes.RECTANGLE, { x:0, y:5.25, w:10, h:0.38,
      fill:{ color:C.card }, line:{ color:"000000", transparency:100 } });
    s.addText("Startup Pitch Competition 2025  •  Confidential & Proprietary", {
      x:0, y:5.25, w:10, h:0.38, fontSize:10, color:C.muted, align:"center", valign:"middle" });
  }

  await pres.writeFile({ fileName: "/home/claude/startup_pitch_demo.pptx" });
  console.log("✅ Deck written!");
}

buildDeck().catch(console.error);
