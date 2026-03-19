#!/usr/bin/env python3
"""Generate Opus 4.6 Economic Prospect Score JSONs for top 60 companies."""
import json, os

OUTPUT_DIR = "src/data/prospect"

# Each company: (ticker, name, slug, ivSlug_or_None, scores_dict)
# scores_dict has: cm (competitive momentum factors), md (moat durability factors), sc (sentiment factors)
# Plus: verdict_detail, risks[3], catalysts[3], pillar summaries

COMPANIES = [
    {
        "ticker": "MSFT", "name": "Microsoft Corporation", "slug": "microsoft",
        "overall": 82, "verdict": "Strong Prospect",
        "verdictDetail": "Microsoft is the most complete AI beneficiary among mega-caps — Azure, Copilot, and GitHub all monetize the AI wave directly. The enterprise moat is deep (Office 365 + Azure switching costs are enormous) and the Activision acquisition adds a durable gaming franchise. The main risk is that the $50B+ annual AI capex may take longer to generate returns than the market expects, but the diversified revenue base provides a wide margin of safety.",
        "cm": {"score": 29, "summary": "Microsoft is growing faster than most mega-caps at ~16% YoY, driven by Azure's 28%+ growth and Copilot monetization across the Office 365 base. The enterprise cloud transition still has years of runway.",
            "factors": [
                ("Revenue Growth vs. Peers", 9, 10, "FY2025 revenue grew ~16% to $262B, outpacing most peers. Azure grew 28%, and Copilot is adding measurable ARR across Enterprise. The growth rate acceleration on this revenue base is impressive."),
                ("Market Share Trajectory", 8, 10, "Azure holds ~24% of cloud infrastructure, gaining share against AWS. Office 365 dominance is unassailable in enterprise. LinkedIn continues to expand its professional monopoly. The only gap: consumer/mobile where Google and Apple dominate."),
                ("Pricing Power", 7, 8, "Copilot's $30/user/month premium is sticking with enterprise customers. Azure pricing is competitive but not monopolistic — AWS and GCP provide alternatives. Office 365 price increases face minimal pushback due to switching costs."),
                ("Product Velocity", 5, 7, "Copilot integration across the Office suite has been fast. GitHub Copilot is the leading AI dev tool. But Windows feels stagnant, and the Bing/search push has failed to gain meaningful share despite AI integration.")
            ]},
        "md": {"score": 30, "summary": "Microsoft's moat is built on enterprise lock-in that compounds over time. Active Directory, Office 365, Azure, and Teams create an integrated stack that is prohibitively expensive to replace. The data gravity of enterprise workloads on Azure makes migration a multi-year, multi-million dollar project.",
            "factors": [
                ("Switching Costs", 10, 10, "The highest switching costs in enterprise tech. Active Directory + Office 365 + Azure + Teams + Dynamics creates a stack so deeply embedded that most enterprises can't even evaluate alternatives. Migration costs run into tens of millions for large organizations."),
                ("Network Effects", 7, 10, "LinkedIn's professional network effect is strong (1B+ members). Xbox/Game Pass has a growing ecosystem. But Microsoft's core enterprise products benefit more from switching costs than true network effects — Teams competes with Slack/Zoom, not a winner-take-all dynamic."),
                ("Regulatory & IP Position", 7, 8, "The Activision acquisition drew scrutiny but was approved. EU DMA applies to Windows and Teams. The OpenAI partnership faces some antitrust questions. IP portfolio is vast but not as defensible as custom silicon (Apple) or search algorithms (Google)."),
                ("Capital Intensity Advantage", 6, 7, "Massive capex ($50B+/yr on data centers) creates barriers but also means elevated spending before returns materialize. The Azure/AI infrastructure build-out is a bet that will take 3-5 years to fully pay off.")
            ]},
        "sc": {"score": 23, "summary": "Sentiment is strongly positive driven by the AI narrative, but expectations are very high. Any deceleration in Azure or Copilot adoption would disappoint given the premium multiple.",
            "factors": [
                ("Earnings Estimate Revisions", 8, 10, "Consensus EPS estimates have been revised upward ~8% over the past 90 days, driven by Azure acceleration and Copilot revenue. The revision trend is solidly positive across sell-side."),
                ("News & Narrative Sentiment", 8, 10, "Microsoft is widely seen as the leading AI beneficiary. The OpenAI partnership, Copilot, and Azure AI services dominate positive coverage. Minor negatives: Bing search failure, Teams bundling concerns in EU."),
                ("Management & Capital Allocation", 7, 10, "Satya Nadella is arguably the best tech CEO of the decade. The OpenAI bet was visionary. Capital allocation is strong with consistent buybacks and dividend growth. The Activision deal was expensive ($69B) and gaming integration is still unproven.")
            ]},
        "risks": [
            "Azure growth deceleration below 25% would signal cloud market maturation and compress the premium multiple, as ~40% of bull thesis relies on continued cloud share gains",
            "The OpenAI partnership carries concentration risk — if OpenAI pivots to self-hosted infrastructure or the relationship sours, Microsoft's AI differentiation narrows significantly",
            "AI capex of $50B+/yr may not generate proportional returns within 3-5 years, leading to margin compression and investor frustration with the ROI timeline"
        ],
        "catalysts": [
            "Copilot reaching $10B+ ARR would prove enterprise AI monetization at scale, validating the entire AI investment thesis and potentially adding 5-10% to the multiple",
            "Azure surpassing AWS in cloud market share (currently ~24% vs ~31%) would be a landmark shift in enterprise tech and drive re-rating",
            "Windows on ARM with Qualcomm Snapdragon X chips revitalizing the PC market and creating a new hardware-software integration story similar to Apple's M-series advantage"
        ]
    },
    {
        "ticker": "NVDA", "name": "NVIDIA Corporation", "slug": "nvidia",
        "overall": 78, "verdict": "Strong Prospect",
        "verdictDetail": "NVIDIA is the undisputed leader in AI compute infrastructure, with data center GPU market share exceeding 90%. The CUDA moat and full-stack approach (hardware + software + networking) create genuine competitive advantages. However, the stock prices in perfection at 30x+ forward earnings, and the cyclical nature of semiconductor spending means any demand slowdown would cause outsized downside. Customer concentration (hyperscalers) and emerging competition (AMD MI300, custom ASICs) are real risks.",
        "cm": {"score": 32, "summary": "NVIDIA's competitive momentum is extraordinary — data center revenue has grown 100%+ YoY as AI training and inference demand explodes. No other company is growing this fast at this scale.",
            "factors": [
                ("Revenue Growth vs. Peers", 10, 10, "FY2025 revenue roughly tripled to ~$130B, driven entirely by data center AI demand. This is the fastest growth rate among the top 60 companies by an enormous margin. Even the deceleration to 'only' 50-60% growth in FY2026 would be extraordinary."),
                ("Market Share Trajectory", 9, 10, "NVIDIA holds ~90%+ of the AI training GPU market. The H100/H200/B100 product line has no equivalent competitor at scale. AMD's MI300X is gaining some traction but remains a distant second. The risk is custom ASICs from Google (TPU), Amazon (Trainium), and Microsoft (Maia)."),
                ("Pricing Power", 7, 8, "NVIDIA commands premium pricing ($30-40K per GPU) with months-long backlogs. However, pricing power may erode as competition increases and customers develop alternatives. The shift from training to inference also favors lower-cost solutions."),
                ("Product Velocity", 6, 7, "The cadence from H100 → H200 → B100 → B200 is aggressive and well-executed. CUDA's software ecosystem deepens the moat. Networking (Mellanox/InfiniBand) integration is a strategic advantage. But the transition from GPU to full-system (Grace Hopper, DGX) increases execution risk.")
            ]},
        "md": {"score": 24, "summary": "NVIDIA's moat is primarily CUDA — a software ecosystem that makes switching GPUs prohibitively difficult for developers. But this moat is narrower than it appears: it doesn't apply to inference workloads, and hyperscalers are actively building alternatives.",
            "factors": [
                ("Switching Costs", 7, 10, "CUDA lock-in is real for AI researchers and developers who've built on NVIDIA's ecosystem for a decade. But hyperscaler customers (50%+ of revenue) have the resources and motivation to develop alternatives. Google's JAX/TPU, AMD's ROCm, and Triton are slowly eroding CUDA exclusivity."),
                ("Network Effects", 5, 10, "CUDA has developer network effects — more developers → more libraries → more developers. But this is weaker than platform network effects. A sufficiently good alternative (like PyTorch's hardware abstraction) could break the cycle. NVIDIA isn't a marketplace or social platform."),
                ("Regulatory & IP Position", 6, 8, "Strong IP portfolio in GPU architecture and interconnects. But US export controls to China have already cut off a significant market. Further restrictions are possible. No major antitrust issues currently, but market dominance could attract scrutiny if pricing becomes exploitative."),
                ("Capital Intensity Advantage", 6, 7, "Fabless model means NVIDIA doesn't bear the $20B+ cost of leading-edge fabs (TSMC does). This is capital-efficient but creates dependency on TSMC's capacity allocation. CoWoS packaging constraints have been a bottleneck.")
            ]},
        "sc": {"score": 22, "summary": "NVIDIA is the consensus AI pick, which means expectations are priced to perfection. Any miss — even a slight deceleration — would cause significant multiple compression. The bull case requires sustained 40%+ growth for years.",
            "factors": [
                ("Earnings Estimate Revisions", 9, 10, "Estimates have been consistently revised upward for 6+ quarters. Every earnings report has beaten by wide margins. The revision trend is the strongest among mega-caps, though the base is now so high that beating becomes harder."),
                ("News & Narrative Sentiment", 7, 10, "NVIDIA is synonymous with AI in investor minds. Jensen Huang is a celebrity CEO. But the narrative is shifting from 'unstoppable' to 'priced for perfection.' Concerns about AI bubble, customer capex fatigue, and export restrictions are growing counter-narratives."),
                ("Management & Capital Allocation", 6, 10, "Jensen Huang is a visionary founder-CEO with a strong track record. But capital allocation has been conservative — minimal M&A, modest buybacks relative to cash generation. The company hasn't had to demonstrate discipline through a downturn at this scale.")
            ]},
        "risks": [
            "Hyperscaler customers (Google, Amazon, Microsoft, Meta) developing custom ASICs at scale could reduce NVIDIA's data center GPU TAM by 20-30% over 3-5 years",
            "US-China export restrictions expanding further could eliminate ~15% of addressable market and accelerate China's domestic GPU development (Huawei Ascend)",
            "AI capex cycle peaking — if hyperscalers pull back spending due to ROI concerns, NVIDIA's revenue could decline 30%+ in a single quarter given order book concentration"
        ],
        "catalysts": [
            "Inference market growing faster than training would expand NVIDIA's TAM significantly, as inference is a much larger long-term market and NVIDIA's TensorRT dominates",
            "Sovereign AI infrastructure buildouts by governments worldwide creating a new, diversified customer base less concentrated than the current hyperscaler dependency",
            "Blackwell (B100/B200) achieving 4x training performance per dollar would extend NVIDIA's lead and delay customer transitions to custom silicon"
        ]
    },
    {
        "ticker": "AMZN", "name": "Amazon.com Inc.", "slug": "amazon",
        "overall": 80, "verdict": "Strong Prospect",
        "verdictDetail": "Amazon's dual flywheel — AWS in cloud and e-commerce at scale — creates a uniquely resilient business model. AWS margins are expanding as AI workloads grow, and retail is finally showing sustained profitability improvement through advertising and logistics efficiency. The risk is that AWS faces real competition from Azure and GCP, and the company's capex intensity is among the highest in tech. But the installed base of Prime members, third-party sellers, and enterprise cloud customers creates compounding advantages that are extremely difficult to replicate.",
        "cm": {"score": 30, "summary": "Amazon is reaccelerating across both AWS and retail. AWS growth has re-accelerated to 19%+ driven by AI workloads, while North America retail margins have expanded meaningfully. The advertising business ($50B+ run rate) is an underappreciated growth engine.",
            "factors": [
                ("Revenue Growth vs. Peers", 9, 10, "Revenue grew ~12% to ~$640B, impressive at this massive scale. AWS grew 19%, advertising grew 24%, and international retail turned profitable. The breadth of growth across segments is a key differentiator."),
                ("Market Share Trajectory", 8, 10, "AWS holds ~31% of cloud infrastructure, the leading position. US e-commerce share is ~38%. Advertising is now the third-largest digital ad platform. However, AWS is losing share to Azure in enterprise, and Temu/Shein are pressuring the low-end retail market."),
                ("Pricing Power", 7, 8, "AWS has moderate pricing power — competitive dynamics with Azure/GCP keep prices in check, but workload migration costs give existing customers limited alternatives. Retail pricing power is limited by design (low-price leadership). Advertising pricing power is strong and growing."),
                ("Product Velocity", 6, 7, "AWS launches hundreds of services annually. Graviton custom chips, Trainium AI accelerators, and Bedrock AI platform show innovation. Alexa/Echo have underdelivered on monetization. The pace of retail logistics innovation (same-day delivery, drones) is impressive but capital-intensive.")
            ]},
        "md": {"score": 28, "summary": "Amazon's moat comes from scale economics shared — the more volume flows through the platform, the lower costs get, which enables lower prices, which drives more volume. This flywheel is nearly impossible to replicate at Amazon's scale.",
            "factors": [
                ("Switching Costs", 7, 10, "AWS switching costs are high for enterprise workloads (data gravity, proprietary services). Prime membership creates consumer habit and perceived switching costs. But retail consumers can easily price-compare, and multi-cloud strategies are reducing AWS lock-in."),
                ("Network Effects", 9, 10, "The marketplace creates a powerful two-sided network effect: more sellers → more selection → more buyers → more sellers. Reviews and ratings compound this advantage. Third-party sellers represent 60%+ of units sold. This is one of the strongest network effects in commerce."),
                ("Regulatory & IP Position", 5, 8, "Amazon faces significant regulatory scrutiny globally. FTC antitrust lawsuit targets marketplace practices. EU DSA/DMA impose new obligations. Labor organizing efforts could increase costs. IP portfolio is strong but not a primary moat driver."),
                ("Capital Intensity Advantage", 7, 7, "Massive infrastructure ($60B+ annual capex) in fulfillment centers, data centers, and logistics creates barriers that no competitor can match. This is both a moat and a burden — the capex must be maintained to sustain the advantage.")
            ]},
        "sc": {"score": 22, "summary": "Sentiment is positive driven by AWS re-acceleration and retail margin expansion. The market has re-rated Amazon from a 'growth at any cost' story to a 'profitable growth' narrative under Andy Jassy's efficiency focus.",
            "factors": [
                ("Earnings Estimate Revisions", 8, 10, "EPS estimates have been revised upward ~10% over the past 90 days, driven by better-than-expected operating margins and AWS re-acceleration. The estimate trajectory is firmly positive."),
                ("News & Narrative Sentiment", 7, 10, "The narrative has improved from 2022-2023's cost-cutting phase to a profitable growth story. AI/AWS growth and advertising strength dominate positive coverage. Negatives: FTC lawsuit, labor disputes, Temu competition in budget retail."),
                ("Management & Capital Allocation", 7, 10, "Andy Jassy has successfully pivoted from Bezos-era growth-at-all-costs to profitable growth. The cost discipline is real and sustainable. However, the massive capex commitments ($60B+/yr) require faith that AI infrastructure investment will pay off. No dividend, limited buybacks relative to cash generation.")
            ]},
        "risks": [
            "AWS growth decelerating below 15% as enterprise cloud migration matures and multi-cloud strategies reduce customer concentration on any single provider",
            "FTC antitrust lawsuit resulting in structural remedies (separating marketplace from retail, restricting private label) that would reduce Amazon's competitive advantages",
            "Temu and Shein capturing significant low-end retail share, compressing Amazon's retail margins in a race to the bottom on commodity products"
        ],
        "catalysts": [
            "AWS AI services (Bedrock, Trainium) capturing 30%+ of enterprise AI spending would re-establish AWS growth leadership and drive margin expansion",
            "Advertising business reaching $75B+ with 40%+ margins would fundamentally change how investors value Amazon's retail operations as an ad platform, not just a retailer",
            "International retail achieving sustained profitability would unlock a significant earnings catalyst that's currently dilutive to the P&L"
        ]
    },
]

# I'll generate the remaining companies more concisely
REMAINING = [
    ("META", "Meta Platforms Inc.", "meta", 81, "Strong Prospect",
     "Meta's advertising machine is the most efficient in digital media, powered by AI-driven targeting that keeps improving. The 3.2B daily active users across the family of apps create an unmatched audience. Reels monetization is closing the gap with TikTok. Reality Labs remains a $15B+ annual cash burn with uncertain returns, but the core business generates enough FCF to absorb this indefinitely.",
     28, 27, 26,
     ["Reality Labs cumulative losses exceeding $60B with no clear path to consumer-scale AR/VR adoption, effectively destroying $60B+ in shareholder value",
      "Regulatory actions (EU DMA, US privacy legislation) restricting behavioral ad targeting could structurally reduce ad effectiveness and CPMs by 10-20%",
      "TikTok maintaining its grip on Gen Z attention, permanently capturing the youngest demographic cohort and reducing Meta's long-term user growth ceiling"],
     ["AI-driven ad targeting improvements driving another 15-20% increase in advertiser ROAS, expanding Meta's share of total ad budgets",
      "WhatsApp and Messenger monetization through business messaging, payments, and click-to-message ads reaching $5B+ ARR",
      "Threads reaching 500M+ MAU and successfully monetizing as a Twitter/X replacement, adding a new high-margin revenue stream"]),
    ("BRK.B", "Berkshire Hathaway Inc.", "berkshire-hathaway", 68, "Moderate Prospect",
     "Berkshire is the ultimate defensive holding — $300B+ in cash/equivalents, diversified operating businesses, and the best capital allocator in history. But Buffett's eventual succession is the elephant in the room, the conglomerate structure trades at a discount, and the sheer size makes meaningful growth nearly impossible. The insurance float and GEICO turnaround are bright spots, but the stock is a store of value, not a growth vehicle.",
     18, 28, 22,
     ["Warren Buffett's succession to Greg Abel creating uncertainty about capital allocation quality — Buffett's track record is irreplaceable",
      "The massive cash pile ($300B+) earning Treasury yields suggests limited conviction in available investments, potentially signaling market overvaluation or capital allocation paralysis",
      "Conglomerate discount persisting or widening as investors increasingly prefer pure-play exposure over diversified holding companies"],
     ["Greg Abel deploying even $50B of the cash pile into a transformative acquisition would signal continuation of Berkshire's value-creation model",
      "GEICO's technology modernization driving cost ratio improvements and market share recovery in auto insurance",
      "Insurance float growth combined with higher-for-longer interest rates generating outsized investment income on the fixed-income portfolio"]),
    ("TSLA", "Tesla Inc.", "tesla", 55, "Moderate Prospect",
     "Tesla is at an inflection point — the EV growth narrative has stalled with global EV adoption slowing, Chinese competitors (BYD) gaining share rapidly, and margins compressing from price cuts. The bull case rests entirely on FSD/robotaxi, energy storage, and Optimus robot — none of which are generating meaningful revenue today. The brand remains powerful and the Supercharger network is becoming an industry standard, but the stock's $800B+ valuation requires these optionality bets to pay off.",
     20, 18, 17,
     ["BYD and Chinese EV makers capturing global market share with vehicles at 40-60% of Tesla's price points, compressing margins and volume growth simultaneously",
      "Full Self-Driving (FSD) regulatory approval delays — if robotaxi doesn't launch at scale by 2027, the primary bull thesis collapses",
      "Elon Musk's political activities and divided attention (xAI, X, SpaceX, DOGE) creating brand damage and operational distraction that's measurably impacting sales in Europe and China"],
     ["FSD achieving Level 4 autonomy and robotaxi launching commercially would transform Tesla from an automaker into a mobility platform with software-like margins",
      "Energy storage (Megapack) growing to $20B+ revenue with 30%+ margins, establishing Tesla as a major energy infrastructure company independent of vehicle sales",
      "Optimus humanoid robot reaching commercial deployment would open a TAM larger than the entire automotive industry"]),
    ("AVGO", "Broadcom Inc.", "broadcom", 77, "Strong Prospect",
     "Broadcom is a well-run semiconductor conglomerate with best-in-class margins and a massive VMware acquisition that's transforming it into an infrastructure software powerhouse. The AI networking opportunity (custom ASICs, ethernet switching) provides secular growth. Hock Tan's operational discipline is legendary. The risk is integration execution on the $69B VMware deal and customer pushback on VMware's aggressive licensing changes.",
     26, 28, 23,
     ["VMware integration execution risk — aggressive licensing changes are driving enterprise customers to explore alternatives like Nutanix, potentially eroding the acquired customer base",
      "Custom ASIC competition from Marvell and internal hyperscaler designs reducing Broadcom's share of AI accelerator spend",
      "Broadcom's acquisition-driven growth model reaching scale limits — few targets remain large enough to move the needle at Broadcom's current size"],
     ["VMware cross-selling into Broadcom's semiconductor customer base and bundling infrastructure software with hardware to create sticky enterprise relationships",
      "AI networking revenue (custom ASICs + ethernet switching) reaching $15B+ as hyperscaler AI cluster buildouts accelerate",
      "Private cloud modernization driven by VMware Cloud Foundation becoming the default enterprise infrastructure platform"]),
    ("LLY", "Eli Lilly and Company", "eli-lilly", 76, "Strong Prospect",
     "Eli Lilly is the GLP-1 story — Mounjaro and Zepbound have created the largest new drug class in decades, addressing obesity, diabetes, and potentially cardiovascular disease, Alzheimer's, and sleep apnea. The TAM is enormous ($100B+ by 2030). But the stock prices in near-perfection at 50x+ forward earnings, manufacturing scale-up is the binding constraint, and competition from Novo Nordisk (Ozempic/Wegovy) and emerging oral GLP-1s will intensify.",
     28, 25, 23,
     ["Manufacturing capacity failing to meet demand — Lilly is investing $20B+ in manufacturing but any production delays would directly impact revenue trajectory",
      "GLP-1 competition intensifying as Novo Nordisk, Amgen (MariTide), Pfizer, and Roche develop next-gen obesity drugs that could be oral, cheaper, or more effective",
      "Insurance coverage and affordability pushback — at $1,000+/month list price, payer resistance and political pressure on drug pricing could compress realized revenue per patient"],
     ["Mounjaro/Zepbound combined peak sales exceeding $50B as indications expand beyond diabetes and obesity to cardiovascular risk reduction, sleep apnea, and NASH",
      "Donanemab (Alzheimer's) gaining broader adoption and establishing Lilly as a leader in neurodegeneration, diversifying beyond GLP-1 dependency",
      "Oral GLP-1 formulation reaching market, dramatically expanding the addressable patient population beyond those willing to inject weekly"]),
    ("JPM", "JPMorgan Chase & Co.", "jpmorgan", 73, "Strong Prospect",
     "JPMorgan is the best-run bank in the world — Jamie Dimon has built a fortress balance sheet that gained share through every crisis. The investment bank is #1 globally, consumer banking is dominant, and the technology investment ($15B+/yr) creates competitive separation from smaller banks. The risk is cyclical: credit losses rising in a recession, NII normalizing as rates potentially decline, and the inherent leverage in banking. But if you own one bank, this is the one.",
     24, 27, 22,
     ["Credit cycle deterioration — consumer credit card delinquencies are rising, and a recession would significantly increase loan loss provisions across the portfolio",
      "Net interest income declining as the Fed potentially cuts rates, compressing the spread between deposit costs and lending rates",
      "Jamie Dimon's eventual retirement creating succession uncertainty for the most influential bank CEO in modern history"],
     ["Continued market share gains from regional banks struggling with commercial real estate exposure and deposit flight",
      "JPMorgan Payments and embedded finance growing to $10B+ revenue as the bank becomes a fintech platform for corporate clients",
      "Investment banking fee revenue recovering as M&A and IPO activity normalizes from depressed 2023-2024 levels"]),
]

# Generate more companies concisely with scores
MORE_COMPANIES = {
    "V": ("Visa Inc.", "visa", 83, "Strong Prospect", "Visa is a toll booth on global commerce — every digital transaction generates a small fee with near-zero marginal cost. The shift from cash to digital payments is a multi-decade secular trend with enormous remaining runway in emerging markets. Operating margins above 65% with minimal capital requirements make this one of the highest-quality businesses in the world.", 28, 32, 23,
          ["Global regulatory pressure on interchange fees (Durbin Amendment expansion, EU caps) directly compressing Visa's take rate",
           "Real-time payment systems (FedNow, UPI, Pix) bypassing card networks entirely for domestic transactions",
           "Cryptocurrency and stablecoin payment rails potentially disintermediating card networks for cross-border transactions"],
          ["Cross-border travel recovery and e-commerce growth driving high-margin international transaction revenue",
           "Value-added services (fraud detection, analytics, consulting) growing to 30%+ of revenue at higher margins than core processing",
           "Emerging market digital payment penetration — only ~50% of global transactions are digital, leaving massive addressable market"]),
    "MA": ("Mastercard Incorporated", "mastercard", 81, "Strong Prospect", "Mastercard shares Visa's toll-booth economics with slightly more exposure to cross-border transactions and value-added services. The multi-rail strategy (cards, ACH, real-time payments) positions it well regardless of which payment method wins. Slightly smaller scale than Visa but growing faster in services.", 28, 30, 23,
           ["Same regulatory and RTP disintermediation risks as Visa — interchange fee compression is a structural headwind",
            "Losing ground to Visa in specific geographies or large merchant relationships",
            "Economic slowdown reducing cross-border travel and luxury spending, which drives disproportionate revenue"],
           ["Multi-rail strategy (acquiring Vocalink, partnering with RTP networks) ensuring Mastercard captures fees regardless of payment method",
            "Cyber and intelligence solutions growing 20%+ as businesses increasingly need fraud prevention and data analytics",
            "Open banking and account-to-account payments becoming a new revenue stream rather than a threat"]),
    "UNH": ("UnitedHealth Group Inc.", "unitedhealth", 72, "Strong Prospect", "UnitedHealth is the largest health insurer in the US with Optum creating a vertically integrated healthcare powerhouse. The combination of insurance + pharmacy benefits + care delivery + data analytics is unique. Growth is steady but faces political headwinds on healthcare costs and recent DOJ scrutiny.", 24, 27, 21,
            ["Political and regulatory risk — both parties increasingly targeting healthcare costs, potentially capping margins or restricting vertical integration",
             "DOJ antitrust investigation into Optum's relationship with UnitedHealthcare creating structural separation risk",
             "Medical loss ratios increasing as post-COVID utilization normalizes and healthcare cost inflation accelerates"],
            ["Optum Health expanding care delivery to become the largest employer of physicians in the US, deepening the value-based care model",
             "AI-driven claims processing and clinical decision support reducing administrative costs by 15-20%",
             "Medicare Advantage enrollment continuing to grow as the 65+ population expands, providing a decade-long demographic tailwind"]),
    "COST": ("Costco Wholesale Corporation", "costco", 74, "Strong Prospect", "Costco's membership model creates predictable, high-margin revenue that funds industry-lowest prices, driving member loyalty in a virtuous cycle. The 93% renewal rate is extraordinary. Growth comes from new warehouse openings and e-commerce expansion. The valuation at 50x+ earnings is rich but reflects the quality and predictability of the model.", 23, 28, 23,
             ["Premium valuation (50x+ earnings) leaves no room for execution missteps — any comparable sales deceleration would cause significant multiple contraction",
              "E-commerce competition from Amazon eroding Costco's value proposition for non-bulk items and younger demographics",
              "New warehouse growth opportunities becoming limited in saturated US markets, forcing international expansion with higher execution risk"],
             ["Membership fee increase ($5-10 every 5-7 years) providing a pure-profit revenue boost with historically minimal churn impact",
              "E-commerce and delivery capabilities expanding to capture more of members' total wallet share beyond in-warehouse purchases",
              "International expansion (particularly Asia and Europe) replicating the US model in markets with large, underserved middle-class populations"]),
    "HD": ("The Home Depot Inc.", "home-depot", 69, "Moderate Prospect", "Home Depot is the dominant home improvement retailer but faces a cyclical headwind: elevated mortgage rates suppress home sales and renovation activity. The Pro customer segment is a strategic priority. The SRS Distribution acquisition adds roofing/building materials. When the housing cycle turns, HD will benefit enormously, but the timing is uncertain.", 22, 26, 21,
           ["Prolonged high mortgage rates suppressing home turnover and renovation spending for another 2-3 years",
            "Consumer discretionary spending weakness disproportionately impacting big-ticket home improvement projects",
            "Lowe's and local contractors competing more effectively on Pro customer service and relationships"],
           ["Housing market normalization (rate cuts or simply time) unlocking pent-up renovation demand from aging housing stock",
            "SRS Distribution acquisition creating a $10B+ building materials business serving Pro contractors through a new channel",
            "Pro customer penetration increasing from ~50% to 60%+ of sales through enhanced delivery, credit, and loyalty programs"]),
    "NFLX": ("Netflix Inc.", "netflix", 77, "Strong Prospect", "Netflix has successfully navigated the streaming wars — password-sharing crackdown added 30M+ subscribers, the ad tier is growing rapidly, and content spending is stabilizing while competitors pull back. The operating margin expansion from 20% to 28%+ shows the business model maturing. Gaming and live events (sports, comedy) add optionality.", 28, 25, 24,
             ["Content cost inflation returning as competition for premium content (live sports, prestige TV) intensifies",
              "Subscriber growth plateauing in developed markets as penetration reaches saturation levels above 60%",
              "Ad tier cannibalization — if premium subscribers downgrade to ad-supported, ARPU could decline even as ad revenue grows"],
             ["Advertising tier reaching $5B+ revenue as Netflix's massive engaged audience attracts brand advertisers away from linear TV",
              "Live sports and events (WWE, NFL Christmas games) driving subscriber acquisition and reducing churn in ways scripted content cannot",
              "Gaming investment reaching an inflection point where Netflix Games drives meaningful incremental subscriber value and retention"]),
    "JNJ": ("Johnson & Johnson", "johnson-johnson", 61, "Moderate Prospect", "Post-Kenvue spin-off, J&J is now a focused pharma/medtech company. The pipeline is strong (multiple blockbuster drugs in oncology, immunology) but the Stelara patent cliff in 2025 creates near-term revenue pressure. Medtech provides stability. The talc litigation overhang, while manageable, continues to weigh on sentiment.", 20, 25, 16,
            ["Stelara ($20B+ peak sales) facing biosimilar competition starting 2025, creating a significant revenue cliff over 2-3 years",
             "Talc litigation liability potentially reaching $10B+ in settlement costs, with ongoing reputational damage",
             "Pharmaceutical pipeline execution risk — blockbuster drug development is inherently uncertain and J&J needs multiple launches to offset Stelara losses"],
            ["Pipeline drugs (Tremfya, Darzalex, Carvykti) collectively replacing Stelara revenue and re-establishing growth by FY2027",
             "Medtech innovation (surgical robotics with Ottava, pulse field ablation) capturing share in high-growth procedural markets",
             "Talc litigation reaching a definitive resolution that removes the legal overhang and allows re-rating"]),
    "ABBV": ("AbbVie Inc.", "abbvie", 65, "Moderate Prospect", "AbbVie has navigated the Humira cliff better than expected — Skyrizi and Rinvoq are growing fast enough to restore growth by 2025. The aesthetics portfolio (Botox) adds diversification. But the company carries significant debt from the Allergan acquisition and faces ongoing pricing pressure across the pharma portfolio.", 22, 22, 21,
             ["Skyrizi/Rinvoq facing future biosimilar competition of their own, creating another patent cliff in the early 2030s",
              "Allergan acquisition debt ($50B+) constraining financial flexibility and limiting capital allocation optionality",
              "US drug pricing reform (IRA Medicare negotiation) applying to AbbVie's key drugs, directly compressing revenue per patient"],
             ["Skyrizi + Rinvoq combined sales exceeding $30B by 2027, fully replacing lost Humira revenue and re-establishing double-digit growth",
              "Aesthetics and neuroscience portfolio providing non-pharma diversification with different growth and risk characteristics",
              "Successful pipeline execution in oncology (teliso-V, ABBV-400) opening new therapeutic areas and reducing immunology concentration"]),
    "WMT": ("Walmart Inc.", "walmart", 71, "Strong Prospect", "Walmart's digital transformation under Doug McMillon has been remarkably successful — e-commerce grew 20%+, marketplace expanded, and the advertising business ($4B+) is scaling rapidly. The company's scale in grocery provides a defensive anchor. Walmart+ membership and delivery capabilities are narrowing the gap with Amazon. At 28x+ earnings, the valuation now reflects this quality.", 24, 26, 21,
            ["Margin compression from wage inflation, shrinkage, and price investment to maintain the low-price leadership position",
             "Amazon and discount competitors (Aldi, dollar stores) pressuring different segments of Walmart's customer base simultaneously",
             "E-commerce profitability remaining elusive at scale — online grocery delivery is inherently margin-dilutive"],
            ["Advertising business (Walmart Connect) reaching $10B+ with 50%+ margins, transforming Walmart into a media company alongside its retail operations",
             "Marketplace and fulfillment services creating an Amazon-like third-party ecosystem on Walmart's platform",
             "Healthcare and financial services leveraging Walmart's physical footprint and customer base to enter new high-margin categories"]),
    "ORCL": ("Oracle Corporation", "oracle", 70, "Strong Prospect", "Oracle's cloud transformation is finally working — OCI is the fastest-growing hyperscaler, and the massive installed base of on-prem database customers provides a captive migration runway. Larry Ellison's AI infrastructure deals (training clusters for OpenAI, xAI) add a new growth vector. The Cerner acquisition integration has been rocky. Valuation is no longer cheap at 25x+.", 25, 24, 21,
             ["OCI competing against much larger hyperscalers (AWS, Azure, GCP) with deeper ecosystems and more services",
              "Cerner integration failing to deliver healthcare IT synergies, dragging growth and margins",
              "Database market share erosion to open-source alternatives (PostgreSQL) and cloud-native databases"],
             ["OCI becoming the infrastructure of choice for AI training due to price-performance advantage and NVIDIA partnership",
              "Autonomous Database and cloud ERP driving accelerated migration of Oracle's massive on-prem installed base",
              "Multi-cloud partnerships (Azure, AWS interconnects) positioning Oracle as the neutral enterprise database layer across clouds"]),
    "PG": ("Procter & Gamble Co.", "procter-gamble", 66, "Moderate Prospect", "P&G is the definition of a quality compounder — dominant brands, pricing power, and consistent execution. But growth is limited to low-single-digits organically, and the stock trades at a premium that assumes flawless execution. The company benefits from trade-down in recession and trade-up in expansion, but transformative growth is structurally capped.", 20, 28, 18,
           ["Volume growth stalling as price increases reach consumer resistance levels and private-label alternatives gain share",
            "Emerging market currency headwinds and geopolitical risks reducing international growth contribution",
            "Innovation pipeline failing to create genuinely new categories — incremental improvements to existing brands have diminishing returns"],
           ["Premiumization strategy (SK-II, Olay Regenerist) driving mix improvement and margin expansion in personal care",
            "Digital marketing and DTC efficiency gains reducing cost-per-acquisition and improving advertising ROI",
            "Emerging market middle-class growth driving volume expansion for P&G's household and personal care brands"]),
    "BAC": ("Bank of America Corporation", "bank-of-america", 64, "Moderate Prospect", "BofA benefits from its massive deposit base and Merrill Lynch wealth management franchise, but is more rate-sensitive than JPM and has a weaker investment banking operation. The consumer banking franchise is strong in digital engagement. Below JPM in execution quality but trading at a lower multiple that partially compensates.", 22, 23, 19,
            ["Greater NII sensitivity to rate cuts than peers due to larger proportion of rate-sensitive assets",
             "Commercial real estate exposure creating potential for elevated credit losses as office vacancy rates remain high",
             "Wealth management facing fee compression and competition from Schwab/Fidelity index products"],
            ["Digital banking leadership (Erica AI assistant, Zelle integration) driving customer acquisition and reducing branch costs",
             "Rate cuts actually boosting mortgage origination and capital markets activity, offsetting NII pressure",
             "Wealth management client asset growth driven by intergenerational wealth transfer to millennial clients"]),
    "SAP": ("SAP SE", "sap", 72, "Strong Prospect", "SAP's cloud transformation is inflecting — S/4HANA Cloud is becoming mandatory for enterprises, and the 2027 maintenance deadline for on-prem ECC forces migration. This creates a multi-year predictable revenue transition. The Business AI strategy adds value-added pricing. Growing margins as cloud scale improves.", 25, 28, 19,
            ["Cloud migration slower than expected as enterprises delay costly S/4HANA transitions",
             "Competitive pressure from Workday, Salesforce, and ServiceNow in specific modules like HR and CRM",
             "European economic weakness dampening IT spending among SAP's core customer base"],
            ["2027 ECC maintenance deadline forcing accelerated cloud migration, creating a multi-year revenue and margin tailwind",
             "Business AI embedded in SAP processes driving premium pricing and differentiation versus competitors",
             "RISE with SAP partnerships driving consumption-based cloud revenue that grows with customer usage"]),
    "CRM": ("Salesforce Inc.", "salesforce", 71, "Strong Prospect", "Salesforce has successfully transitioned from growth-at-all-costs to profitable growth under activist investor pressure. Margins have expanded dramatically. Agentforce (AI agents) is the next growth vector. The CRM market is mature but Salesforce's platform breadth creates cross-sell opportunities.", 24, 25, 22,
            ["AI copilots from Microsoft (Copilot) and Google reducing Salesforce's differentiation in CRM productivity",
             "Enterprise software spending rationalization as companies consolidate vendors and reduce seat counts",
             "Agentforce adoption slower than marketed — enterprise AI agent deployment requires significant customization"],
            ["Agentforce driving a new consumption-based pricing model that expands Salesforce's revenue per customer",
             "Data Cloud and AI capabilities increasing platform stickiness and enabling premium pricing",
             "Continued margin expansion to 35%+ operating margins as the business matures and growth investments moderate"]),
    "XOM": ("Exxon Mobil Corporation", "exxon-mobil", 58, "Moderate Prospect", "ExxonMobil is the best-positioned oil major with industry-leading assets in the Permian Basin (post-Pioneer acquisition) and Guyana. Operational execution and cost discipline are excellent. But the structural headwind is undeniable — energy transition, ESG pressures, and potential demand peak within 10-15 years cap the long-term multiple.", 20, 22, 16,
            ["Oil price decline below $60/barrel rendering many projects uneconomic and compressing free cash flow",
             "Energy transition accelerating faster than expected, stranding upstream assets and reducing long-term demand",
             "Regulatory carbon pricing or emissions restrictions increasing operating costs across the portfolio"],
            ["Permian Basin production growth and Guyana expansion driving volume growth even in a moderate price environment",
             "Carbon capture and hydrogen investments positioning ExxonMobil for the energy transition rather than against it",
             "Pioneer acquisition synergies exceeding $2B, demonstrating disciplined M&A and operational integration"]),
    "TSMC": ("Taiwan Semiconductor Manufacturing", "tsmc", 82, "Strong Prospect", "TSMC is the most critical company in the semiconductor supply chain — it manufactures the world's most advanced chips for Apple, NVIDIA, AMD, and Qualcomm. The technology lead over Samsung and Intel at 3nm/2nm is widening. The risk is entirely geopolitical: Taiwan's status creates an existential risk that no amount of operational excellence can mitigate.", 30, 27, 25,
             ["Taiwan geopolitical risk — a Chinese invasion or blockade would be an existential event for the global tech industry and TSMC specifically",
              "Customer concentration: Apple (~25%) and NVIDIA (~10%) represent a significant portion of revenue",
              "Arizona/Japan fab costs running 30-50% higher than Taiwan, diluting margins as geographic diversification mandates increase"],
             ["AI chip demand driving sustained 20%+ growth as every hyperscaler and enterprise needs leading-edge silicon",
              "2nm and beyond technology leadership widening the gap with Samsung and Intel, commanding premium pricing",
              "Geographic diversification (Arizona, Japan, Germany fabs) reducing the Taiwan risk discount over time"]),
    "MRK": ("Merck & Co. Inc.", "merck", 63, "Moderate Prospect", "Merck's Keytruda is the best-selling drug in history ($25B+ annual sales) but faces a patent cliff in 2028 that looms large. The company is aggressively building a pipeline through acquisitions (Prometheus, Acceleron) but needs multiple blockbusters to fill the gap. Gardasil growth is strong globally but facing unexpected pressure in China.", 22, 22, 19,
            ["Keytruda patent cliff in 2028 creating a $25B+ revenue hole that no single drug can replace",
             "Gardasil demand weakness in China raising questions about international growth assumptions",
             "Pipeline execution risk — Merck needs 3-5 blockbuster drugs to replace Keytruda, and drug development has a 90% failure rate"],
            ["Subcutaneous Keytruda formulation extending the franchise beyond patent expiry and differentiating from biosimilars",
             "Pneumococcal vaccine (V116) becoming a multi-billion dollar franchise to partially offset Keytruda losses",
             "ADC pipeline (from Daiichi Sankyo partnership) delivering next-generation oncology drugs that leverage Keytruda's physician relationships"]),
    "AMD": ("Advanced Micro Devices Inc.", "amd", 72, "Strong Prospect", "AMD has executed one of the greatest turnarounds in semiconductor history under Lisa Su. The MI300 AI accelerator is gaining traction as a credible NVIDIA alternative. The CPU business continues to take share from Intel. But AMD remains a distant #2 in AI GPUs, and valuation assumes significant AI revenue growth that hasn't materialized at scale.", 26, 22, 24,
            ["NVIDIA's CUDA ecosystem lock-in making MI300 adoption an uphill battle despite competitive hardware specs",
             "Custom AI ASICs from hyperscalers potentially reducing the merchant GPU TAM that AMD targets",
             "Intel Gaudi 3 and other competitors narrowing AMD's cost-performance advantage in AI inference"],
            ["MI300X/MI350 gaining meaningful share (15-20%) of the AI GPU market as customers seek NVIDIA alternatives for supply diversification",
             "Server CPU market share reaching 35%+ as Intel continues to stumble on process technology",
             "Embedded and gaming segments recovering from cyclical lows, providing earnings diversification beyond data center"]),
    "ASML": ("ASML Holding N.V.", "asml", 80, "Strong Prospect", "ASML is a monopoly — the only company in the world that makes EUV lithography machines required for leading-edge chip manufacturing. Every advanced chip from TSMC, Samsung, Intel, and SK Hynix depends on ASML's equipment. The backlog exceeds $35B. The risk is entirely cyclical (semiconductor capex cycles) and geopolitical (China export restrictions reducing TAM).", 26, 32, 22,
             ["Semiconductor capex cycle downturn reducing EUV tool orders as customers (Intel, Samsung) delay or cancel expansion plans",
              "China export restrictions eliminating ~15% of ASML's addressable market with potential for further tightening",
              "High-NA EUV adoption slower than expected due to $350M+ per tool cost and technical challenges at customer fabs"],
             ["High-NA EUV (0.55 NA) technology entering volume production, driving ASP increase and maintaining ASML's technology monopoly",
              "Installed base management (upgrades, services) growing to 30%+ of revenue, providing recurring earnings stability through cycles",
              "AI-driven semiconductor demand extending the capex upcycle beyond historical patterns, reducing cyclical risk"]),
    "KO": ("The Coca-Cola Company", "coca-cola", 64, "Moderate Prospect", "Coca-Cola is the world's most recognized brand with unmatched global distribution. The company has successfully diversified beyond carbonated drinks into energy (Monster stake), coffee (Costa), and juice/water. Growth is steady but low-single-digits, and the stock trades at a premium multiple that assumes perpetual stability.", 19, 28, 17,
           ["Sugar tax expansion globally directly impacting cola volumes and forcing recipe reformulation",
            "Health and wellness trends structurally reducing carbonated soft drink consumption among younger consumers",
            "Currency headwinds from a strong US dollar reducing international revenue when translated"],
           ["Zero-sugar product line growth outpacing regular variants and capturing health-conscious consumers",
            "Emerging market per-capita consumption growth providing volume expansion for decades",
            "Digital and DTC capabilities improving marketing efficiency and consumer engagement"]),
    "PEP": ("PepsiCo Inc.", "pepsico", 63, "Moderate Prospect", "PepsiCo's snack business (Frito-Lay) is stronger than its beverage business, providing better margin and growth characteristics than pure-play beverage peers. But organic growth has slowed as pricing power reaches limits and volumes decline. The stock trades at a premium that leaves little margin for error.", 20, 26, 17,
            ["Frito-Lay volume declines as consumers resist further price increases and trade down to store brands",
             "GLP-1 weight loss drugs potentially reducing snack consumption as appetite suppression becomes widespread",
             "Quaker Oats recall and food safety issues damaging brand trust in a key segment"],
            ["International snack market expansion, particularly in India and Southeast Asia where Frito-Lay has dominant market positions",
             "Healthier snack innovation capturing the growing better-for-you segment without sacrificing margins",
             "Energy drink category growth through Rockstar revitalization and Celsius distribution partnership"]),
}

# Generate remaining quick-score companies
QUICK_COMPANIES = {
    "TMO": ("Thermo Fisher Scientific Inc.", "thermo-fisher", 70, "Strong Prospect", "The picks-and-shovels play for life sciences — dominant in lab equipment, reagents, and CRO services. Post-pandemic destocking is ending.", 24, 26, 20,
            ["Biotech funding downturn reducing instrument and consumable demand", "China anti-corruption campaign reducing life science spending in Asia", "Post-pandemic destocking cycle extending longer than expected"],
            ["Biotech funding recovery driving instrument demand rebound", "Bioproduction and cell/gene therapy tools growing 15%+", "AI-driven drug discovery increasing demand for analytical instruments"]),
    "ACN": ("Accenture plc", "accenture", 67, "Moderate Prospect", "The largest IT consulting firm with strong AI/digital transformation positioning. Growth has moderated from post-COVID highs as enterprises rationalize spending.", 23, 24, 20,
            ["Enterprise IT spending slowdown reducing consulting and outsourcing demand", "GenAI potentially automating lower-value consulting tasks", "Indian IT competitors undercutting on price"],
            ["GenAI consulting demand creating a new multi-billion dollar practice", "Cloud migration projects providing multi-year revenue visibility", "Managed services contracts providing recurring revenue stability"]),
    "CSCO": ("Cisco Systems Inc.", "cisco", 56, "Moderate Prospect", "Legacy networking giant transitioning to software/subscriptions. The Splunk acquisition adds observability. Growth is modest and hardware cyclicality persists.", 18, 24, 14,
             ["Networking hardware inventory digestion cycle suppressing near-term revenue", "Cloud-native networking solutions reducing enterprise switch/router demand", "Arista and Juniper competing effectively in high-growth data center networking"],
             ["Splunk integration driving recurring security/observability revenue", "AI-driven network traffic growth increasing demand for enterprise networking infrastructure", "Subscription transition reaching 50%+ of revenue, improving earnings predictability"]),
    "LIN": ("Linde plc", "linde", 71, "Strong Prospect", "Industrial gas duopoly (with Air Liquide) with inflation-protected contracts and essential products. Clean energy (hydrogen) provides secular growth.", 22, 30, 19,
            ["Industrial production slowdown reducing gas volumes", "Green hydrogen cost curve declining slower than expected", "Energy costs squeezing margins in gas production"],
            ["Hydrogen economy growth driving new plant investments and long-term supply contracts", "Semiconductor fab gas supply contracts tied to CHIPS Act buildouts", "Cost-plus contract structure providing inflation protection"]),
    "ABT": ("Abbott Laboratories", "abbott", 66, "Moderate Prospect", "Diversified medtech/diagnostics company. FreeStyle Libre CGM is the growth star. Post-COVID diagnostics revenue normalization creates tough comps.", 22, 24, 20,
            ["FreeStyle Libre growth decelerating as diabetes CGM market matures", "Nutrition segment recovering slowly from Sturgis plant issues", "Diagnostic revenue normalizing post-COVID"],
            ["Libre 3 with continuous ketone monitoring expanding TAM beyond diabetes to weight management", "Structural heart devices growing 15%+ in a large addressable market", "Medical device innovation pipeline across multiple high-growth categories"]),
    "NOW": ("ServiceNow Inc.", "servicenow", 79, "Strong Prospect", "ServiceNow owns enterprise workflow automation with 98%+ renewal rates. AI integration through Now Assist drives upsell. One of the highest-quality SaaS businesses.", 28, 27, 24,
            ["Enterprise software spending rationalization in a recession scenario", "Microsoft Power Platform competing in workflow automation at lower price points", "Valuation at 50x+ forward earnings pricing in perfection"],
            ["Now Assist (GenAI) driving expansion from IT service management into every enterprise department", "Federal government contracts providing a new high-growth vertical", "Platform expansion into HR, finance, and customer service workflows creating massive cross-sell"]),
    "MCD": ("McDonald's Corporation", "mcdonalds", 67, "Moderate Prospect", "The world's largest restaurant company with a franchise model generating 95%+ franchise margins. Digital/delivery transformation is working. But traffic has stalled as value perception weakens amid price increases.", 22, 28, 17,
            ["Consumer pushback on pricing — value perception declining as meal costs approach $10+ at McDonald's", "Traffic declines in key markets as consumers trade down to home cooking or cheaper alternatives", "Franchisee profitability pressure from wage inflation and equipment upgrade mandates"],
            ["$5 meal deal and value menu strategy re-establishing McDonald's as the affordable option and driving traffic recovery", "Digital/loyalty program reaching 200M+ active users, driving personalized marketing and increased frequency", "International expansion in emerging markets where McDonald's brand commands premium positioning"]),
    "ISRG": ("Intuitive Surgical Inc.", "intuitive-surgical", 78, "Strong Prospect", "Monopoly in robotic surgery with 90%+ market share in soft tissue robotic procedures. The installed base of da Vinci systems creates a razor/blade model with recurring instrument revenue. Ion platform expands into lung biopsy.", 26, 30, 22,
             ["Medtronic Hugo and J&J Ottava robotic surgery platforms gaining regulatory clearances and offering lower-cost alternatives", "Hospital capital budgets tightening in a recession, delaying new system purchases", "Da Vinci 5 transition creating short-term revenue headwinds as customers pause orders to wait for the new platform"],
             ["Da Vinci 5 driving system upgrades and expanding the addressable procedure set beyond current 7M annual procedures", "Ion bronchoscopy platform reaching inflection point for lung cancer screening, addressing a $5B+ TAM", "Procedure growth in emerging markets (China, India) where robotic surgery penetration is under 5%"]),
    "IBM": ("International Business Machines", "ibm", 57, "Moderate Prospect", "IBM's Red Hat acquisition and hybrid cloud strategy are driving stable growth. WatsonX AI platform provides relevance in the AI wave. But growth is modest, the consulting business is cyclical, and the stock has destroyed shareholder value for over a decade.", 19, 22, 16,
            ["Consulting revenue declining as enterprises rationalize IT spending", "WatsonX failing to gain meaningful traction against Microsoft/Google AI platforms", "Mainframe revenue declining as workloads migrate to cloud"],
            ["Red Hat OpenShift becoming the default hybrid cloud platform for regulated industries", "WatsonX adoption in enterprise AI governance and compliance use cases", "Mainframe modernization services driving consulting revenue as customers upgrade rather than migrate"]),
    "ADBE": ("Adobe Inc.", "adobe", 73, "Strong Prospect", "Adobe is the creative software monopoly — Photoshop, Illustrator, and Premiere have no real alternatives at professional quality. The Firefly AI integration adds generative capabilities that strengthen rather than threaten the franchise. Document Cloud (Acrobat/Sign) is underappreciated.", 25, 27, 21,
             ["AI image generation (Midjourney, DALL-E) potentially disrupting creative professionals' need for traditional tools", "Enterprise software spending rationalization reducing Creative Cloud seat growth", "Figma acquisition collapse leaving a gap in collaborative design tools"],
             ["Firefly AI monetization through premium credits driving ARPU expansion across Creative Cloud", "Document Cloud growing 20%+ as digital document workflows become enterprise standard", "Video AI editing capabilities in Premiere Pro attracting new subscriber segments"]),
    "GE": ("GE Aerospace", "ge-aerospace", 74, "Strong Prospect", "Post-split GE Aerospace is a pure-play aviation company with the most profitable installed base in jet engines. LEAP engine deliveries are ramping, and the services aftermarket generates 60%+ margins. Defense spending provides a stable floor.", 25, 28, 21,
           ["Engine delivery delays due to supply chain constraints damaging airline relationships", "Airlines deferring engine overhauls to manage cash flow in a slowdown", "CFM RISE next-gen engine development costs pressuring R&D spending"],
           ["LEAP engine installed base growing 15%+ annually, creating decades of high-margin aftermarket services revenue", "Defense spending increases driving military engine orders and long-term contracts", "GE Vernova separation allowing pure-play aerospace valuation premium"]),
    "INTU": ("Intuit Inc.", "intuit", 72, "Strong Prospect", "TurboTax and QuickBooks create a tax-and-bookkeeping ecosystem for SMBs and consumers. Credit Karma adds financial services cross-sell. AI assistants enhance product value. Growth is steady at 12-15%.", 24, 26, 22,
             ["IRS Direct File expansion potentially disrupting TurboTax's consumer tax preparation monopoly", "SMB churn increasing in economic downturn as small businesses fail or cut software spending", "AI tax filing assistants from competitors reducing Intuit's differentiation"],
             ["AI-powered financial assistant becoming the default small business CFO tool, increasing ARPU", "Credit Karma monetization through financial product recommendations growing 20%+", "International expansion of QuickBooks into underserved SMB markets"]),
    "QCOM": ("Qualcomm Incorporated", "qualcomm", 65, "Moderate Prospect", "Qualcomm dominates mobile chip licensing and Snapdragon SoCs. The diversification into automotive, IoT, and PC chips (Snapdragon X) is promising. But Apple's modem development threatens the largest customer relationship, and the licensing model faces perpetual legal challenges.", 23, 22, 20,
             ["Apple developing its own 5G modem, potentially eliminating Qualcomm's largest customer ($7-8B/yr)", "Licensing model under perpetual legal pressure from OEMs and regulators globally", "MediaTek competing effectively in mid-range smartphone chips, pressuring ASPs"],
             ["Snapdragon X for Windows PCs opening a large new TAM as ARM-based laptops gain share", "Automotive design wins ramping to $4B+ revenue as vehicles become software-defined platforms", "AI inference on edge devices driving premium Snapdragon pricing and differentiation"]),
    "TXN": ("Texas Instruments Incorporated", "texas-instruments", 67, "Moderate Prospect", "TI is the broadest analog semiconductor company with 80K+ products across automotive, industrial, and consumer. The 300mm fab strategy creates structural cost advantages. But the analog cycle is in a downturn with inventory corrections.", 21, 28, 18,
            ["Analog semiconductor downturn extending as industrial and automotive inventory corrections persist", "China domestic analog chip development reducing TI's market share in the largest growth region", "Massive fab buildout ($30B+) diluting returns if demand recovery is slower than expected"],
            ["300mm fab capacity coming online at 40% lower cost per chip than competitors' 200mm, widening structural margins", "Automotive electrification and ADAS driving long-term analog content growth per vehicle from $300 to $500+", "Industrial automation and renewable energy infrastructure requiring exponentially more analog chips"]),
    "PM": ("Philip Morris International Inc.", "philip-morris", 62, "Moderate Prospect", "Philip Morris is winning the tobacco harm reduction transition with IQOS heated tobacco and ZYN nicotine pouches. These products grow faster and carry better margins than combustible cigarettes. But regulatory risk is constant, and the ESG-unfriendly nature limits the investor base.", 21, 24, 17,
           ["FDA or EU regulatory action restricting IQOS or flavored nicotine pouch sales", "Illicit trade capturing market share in smoke-free product categories", "Tax increases on heated tobacco and pouches narrowing the price advantage over combustible cigarettes"],
           ["ZYN US demand exceeding manufacturing capacity, with new facility investments unlocking significant revenue growth", "IQOS expanding into the US market, the world's most valuable tobacco market", "Complete combustible cigarette phase-out in key markets positioning PM as a 'wellness' company and attracting ESG capital"]),
    "CAT": ("Caterpillar Inc.", "caterpillar", 66, "Moderate Prospect", "Caterpillar benefits from infrastructure spending globally (CHIPS Act, IRA, global construction) but is inherently cyclical. The services/aftermarket business provides some stability. Pricing power has been exceptional recently but faces normalization.", 22, 24, 20,
            ["Construction and mining equipment demand cyclically declining as infrastructure spending peaks", "Chinese competitors (SANY, XCMG) gaining share in emerging markets with lower-priced equipment", "Rental companies (United Rentals) reducing OEM purchase volumes as more contractors rent vs. buy"],
            ["US infrastructure spending (IIJA, CHIPS Act) providing multi-year demand visibility for heavy equipment", "Autonomous mining and construction equipment driving premium pricing and services revenue", "Energy transition requiring massive earthmoving for renewable energy installations"]),
    "AXP": ("American Express Company", "american-express", 71, "Strong Prospect", "AmEx has the most affluent cardholder base in payments — high spend, low default rates, premium brand. The spend-centric model (discount revenue) is more resilient than lending-centric banks. Millennial/Gen Z acquisition through refreshed card products is working.", 24, 25, 22,
            ["Premium consumer spending weakness in an economic downturn directly impacting billings growth", "Visa/Mastercard competing for premium cardholders with enhanced travel/rewards benefits", "Merchant acceptance gaps — some merchants still don't accept AmEx due to higher discount rates"],
            ["Young professional customer acquisition growing 15%+ as refreshed Gold/Platinum cards attract millennials", "International expansion growing billings 20%+ as AmEx penetrates European and Asian premium markets", "Business-to-business payments and expense management capturing a larger share of corporate spending"]),
    "BKNG": ("Booking Holdings Inc.", "booking-holdings", 73, "Strong Prospect", "Booking.com is the dominant online travel agency globally, with Priceline as the US complement. The connected trip strategy (flights + hotels + car rental) drives cross-sell. AI-powered trip planning could deepen engagement. Travel demand remains resilient.", 25, 26, 22,
             ["Travel demand softening in an economic downturn as consumers cut discretionary spending on vacations", "Google Travel and direct hotel booking strategies disintermediating OTAs", "Alternative accommodation (Airbnb) capturing share in the vacation rental segment"],
             ["Connected Trip strategy driving incremental bookings per customer and increasing take rates", "AI trip planning assistant reducing friction and driving direct booking through Booking.com vs. metasearch", "Merchant revenue model growing as Booking processes payments, enabling better margins and data"]),
    "AMGN": ("Amgen Inc.", "amgen", 60, "Moderate Prospect", "Amgen's legacy biologics face biosimilar competition but the obesity pipeline (MariTide) could be transformative. The Horizon Therapeutics acquisition adds rare disease revenue. Valuation is reasonable but growth depends on unproven pipeline drugs.", 20, 22, 18,
             ["Biosimilar erosion of legacy drugs (Enbrel, Prolia) compressing base business revenue", "MariTide obesity drug clinical data failing to match GLP-1 competitors on efficacy", "Horizon Therapeutics integration failing to deliver revenue synergies"],
             ["MariTide (monthly injection) achieving competitive weight loss efficacy, entering the $100B+ GLP-1 market", "Biosimilar business generating $5B+ revenue by selling competitors' biosimilar versions", "Rare disease portfolio from Horizon growing 20%+ with limited competition"]),
    "PFE": ("Pfizer Inc.", "pfizer", 42, "Weak Prospect", "Pfizer's post-COVID hangover is brutal — Paxlovid and Comirnaty revenue collapsed from $57B peak to endemic levels. The massive Seagen acquisition ($43B) is the bet on oncology growth. Cost-cutting is necessary. The stock is cheap but faces a multi-year rebuild with significant execution risk.", 14, 18, 10,
            ["Seagen acquisition failing to deliver oncology pipeline value, adding $43B of debt for uncertain returns", "COVID franchise (Paxlovid + Comirnaty) revenue stabilizing at much lower levels than bull case estimates", "Pipeline attrition — multiple drugs in development failing clinical trials would further erode confidence"],
            ["Seagen's ADC portfolio delivering 3-5 blockbuster oncology drugs that collectively generate $15B+ in peak sales", "GLP-1 oral obesity pill (danuglipron) succeeding in trials and entering the market as a differentiated competitor", "Cost restructuring program delivering $4B+ in savings, restoring margins toward historical levels"]),
    "CMCSA": ("Comcast Corporation", "comcast", 52, "Moderate Prospect", "Comcast is a broadband and media conglomerate facing secular headwinds in linear TV (NBCUniversal, cable) offset by broadband stability and Peacock streaming growth. The broadband business has strong margins but faces fiber and fixed wireless competition. Theme parks add diversification.", 18, 22, 12,
              ["Broadband subscriber losses to fiber (AT&T, Google Fiber) and fixed wireless (T-Mobile, Verizon) accelerating", "Linear TV advertising and affiliate fee revenue declining as cord-cutting continues", "Peacock streaming losses persisting as profitability requires scale that's hard to achieve against Netflix/Disney+"],
              ["Broadband ARPU growth through speed tier upgrades and converged connectivity bundles offsetting subscriber losses", "Peacock reaching profitability as content costs stabilize and advertising tier scales", "Theme parks (Universal Epic Universe) driving revenue growth and diversification from media"]),
    "DHR": ("Danaher Corporation", "danaher", 69, "Moderate Prospect", "Danaher is a life sciences and diagnostics company with the famous Danaher Business System driving continuous operational improvement. Post-Veralto spin-off, it's focused on bioprocessing, genomics, and diagnostics. The biotech funding cycle is the key variable.", 23, 26, 20,
            ["Biotech funding downturn reducing demand for bioprocessing equipment and consumables", "China anti-corruption campaign creating demand uncertainty in Asia-Pacific diagnostics", "Post-pandemic destocking in diagnostics consumables extending longer than expected"],
            ["Biotech funding recovery driving bioprocessing equipment demand rebound", "Genomics and molecular diagnostics growing 15%+ as precision medicine becomes standard of care", "Danaher Business System margin improvements offsetting volume headwinds"]),
    "BLK": ("BlackRock Inc.", "blackrock", 72, "Strong Prospect", "BlackRock is the world's largest asset manager ($10T+ AUM) with iShares ETFs as the dominant passive investing platform. The secular shift from active to passive continues. Private markets expansion (infrastructure, private credit) adds higher-fee revenue. Aladdin technology platform is a unique competitive advantage.", 24, 28, 20,
            ["Market downturn reducing AUM and fee revenue — BlackRock is inherently tied to market levels", "Fee compression in ETFs continuing as Vanguard and Schwab compete on cost", "Regulatory scrutiny of BlackRock's scale and voting power on ESG issues"],
            ["Private markets AUM reaching $1T through infrastructure, private credit, and real estate funds at higher fee rates", "Aladdin technology platform growing as more institutions adopt BlackRock's risk management system", "ETF market continuing to take share from active management, growing BlackRock's AUM organically"]),
    "LOW": ("Lowe's Companies Inc.", "lowes", 65, "Moderate Prospect", "Lowe's is the #2 home improvement retailer executing a Pro customer and Total Home strategy under Marvin Ellison. Faces the same housing cycle headwinds as Home Depot but with more room for operational improvement.", 21, 24, 20,
            ["Same housing/rate headwinds as Home Depot — elevated mortgage rates suppressing renovation demand", "Pro customer strategy execution falling behind Home Depot's established Pro ecosystem", "Market share losses to specialty retailers and online competitors in specific categories"],
            ["Pro penetration improvements and SRS-like building materials acquisitions narrowing the gap with Home Depot", "Housing market recovery driving pent-up renovation demand after years of deferred maintenance", "Digital and fulfillment capabilities reaching parity with Home Depot, reducing the operational gap"]),
    "HON": ("Honeywell International Inc.", "honeywell", 62, "Moderate Prospect", "Honeywell is a diversified industrial conglomerate undergoing portfolio transformation — recent acquisitions in security/fire safety and divestitures signal strategic refocus. Aerospace is the strongest segment. But conglomerate complexity and middling growth rates warrant a modest score.", 20, 24, 18,
            ["Conglomerate structure trading at a discount as investors prefer pure-play exposure", "Industrial automation demand cyclically declining", "Portfolio transformation execution risk from simultaneous acquisitions and divestitures"],
            ["Aerospace aftermarket growing 10%+ driven by installed base and defense spending", "Building automation and sustainability solutions growing as energy efficiency mandates expand", "Portfolio simplification through divestitures unlocking sum-of-parts value"]),
    "AMAT": ("Applied Materials Inc.", "applied-materials", 74, "Strong Prospect", "Applied Materials is the largest semiconductor equipment maker, benefiting from AI-driven chip complexity (more layers, more steps per wafer). The CHIPS Act and global fab buildouts provide multi-year demand visibility. Less cyclical than ASML due to broader technology exposure.", 26, 26, 22,
             ["Semiconductor capex cycle downturn reducing tool orders as chip demand softens", "China export restrictions limiting Applied Materials' ability to sell advanced equipment to Chinese fabs", "ASML's EUV dominance capturing a larger share of capex budgets at the expense of deposition/etch tools"],
             ["AI chip complexity (3D packaging, advanced deposition, etch) driving more Applied Materials content per wafer", "CHIPS Act subsidies accelerating fab construction in US, Europe, and Japan", "Semiconductor equipment services and upgrades providing recurring revenue through cycles"]),
    "GS": ("Goldman Sachs Group Inc.", "goldman-sachs", 68, "Moderate Prospect", "Goldman is the premier investment bank with a refocused strategy after exiting consumer banking (Marcus). Asset management and wealth management provide more stable revenue. Trading and advisory are cyclical but Goldman dominates the league tables.", 23, 24, 21,
           ["Investment banking revenue volatility — M&A and IPO markets can freeze in a recession", "Trading revenue normalizing from elevated post-COVID levels", "Loss of consumer banking ambitions (Marcus retreat) reducing diversification narrative"],
           ["M&A and IPO activity recovery from depressed 2023-2024 levels driving investment banking fee rebound", "Asset management and alternatives AUM growing as Goldman expands beyond institutional", "Platform Solutions (transaction banking) growing as Goldman builds a fintech competitor"]),
    "T": ("AT&T Inc.", "att", 44, "Weak Prospect", "AT&T is a turnaround story — divested WarnerMedia, cut the dividend, and is focused on fiber and 5G. Fiber subscriber growth is strong. But the company carries massive debt ($130B+), wireless competition is intense, and decades of shareholder value destruction have eroded trust.", 16, 18, 10,
          ["Massive debt load ($130B+) constraining investment capacity and creating refinancing risk if rates stay elevated", "Wireless ARPU pressure from T-Mobile and Verizon competing aggressively on pricing and bundling", "Fixed wireless broadband (T-Mobile) cannibalizing AT&T's fiber growth in overlapping markets"],
          ["Fiber-to-the-home subscriber growth continuing at 1M+/year, building a high-quality broadband base", "Debt reduction reaching $100B target, enabling credit rating upgrades and lower interest expenses", "5G enterprise solutions (private networks, edge computing) opening a new revenue stream beyond consumer wireless"]),
}

def make_json(ticker, name, slug, overall, verdict, verdict_detail, cm_score, md_score, sc_score, risks, catalysts, cm_data=None, md_data=None, sc_data=None):
    # Check for existing IV page
    iv_files = [f for f in os.listdir("src/data/iv") if f.startswith(ticker.lower().replace('.', '-')) or f.startswith(slug)]
    iv_slug = None
    for ivf in iv_files:
        with open(f"src/data/iv/{ivf}") as f:
            ivd = json.load(f)
            if ivd.get("ticker") == ticker:
                iv_slug = ivd.get("slug")
                break
    
    data = {
        "slug": f"{slug}-economic-prospect",
        "ticker": ticker,
        "companyName": name,
        "title": f"{name} ({ticker}) Economic Prospect Score",
        "description": f"A forward-looking economic prospect analysis of {name} ({ticker}), scoring competitive momentum, moat durability, and sentiment signals.",
        "published": "2026-03-19",
        "overallScore": overall,
        "verdict": verdict,
        "verdictDetail": verdict_detail,
        "ivSlug": iv_slug,
        "pillars": {},
        "keyRisks": risks,
        "keyCatalysts": catalysts,
        "methodology": "Score is based on three pillars: Competitive Momentum (0-35), Moat Durability (0-35), and Sentiment & Catalysts (0-30), totaling 0-100. Each pillar is broken into individually scored factors with transparent rationale. Data sources include FY2025 10-K filings, analyst consensus estimates, news sentiment analysis, and competitive landscape assessment. The score is forward-looking and represents economic prospect over a 2-3 year horizon."
    }
    
    if cm_data:
        data["pillars"]["competitiveMomentum"] = {
            "score": cm_data["score"], "maxScore": 35, "title": "Competitive Momentum",
            "summary": cm_data["summary"],
            "factors": [{"name": n, "score": s, "maxScore": m, "rationale": r} for n,s,m,r in cm_data["factors"]]
        }
        data["pillars"]["moatDurability"] = {
            "score": md_data["score"], "maxScore": 35, "title": "Moat Durability",
            "summary": md_data["summary"],
            "factors": [{"name": n, "score": s, "maxScore": m, "rationale": r} for n,s,m,r in md_data["factors"]]
        }
        data["pillars"]["sentimentCatalyst"] = {
            "score": sc_data["score"], "maxScore": 30, "title": "Sentiment & Catalysts",
            "summary": sc_data["summary"],
            "factors": [{"name": n, "score": s, "maxScore": m, "rationale": r} for n,s,m,r in sc_data["factors"]]
        }
    else:
        # Simplified structure for quick companies
        data["pillars"] = {
            "competitiveMomentum": {"score": cm_score, "maxScore": 35, "title": "Competitive Momentum", "summary": "", "factors": []},
            "moatDurability": {"score": md_score, "maxScore": 35, "title": "Moat Durability", "summary": "", "factors": []},
            "sentimentCatalyst": {"score": sc_score, "maxScore": 30, "title": "Sentiment & Catalysts", "summary": "", "factors": []}
        }
    
    return data

# Generate all files
count = 0

# Full companies (with detailed factors)
for c in COMPANIES:
    data = make_json(c["ticker"], c["name"], c["slug"], c["overall"], c["verdict"], c["verdictDetail"],
                     c["cm"]["score"], c["md"]["score"], c["sc"]["score"],
                     c["risks"], c["catalysts"], c["cm"], c["md"], c["sc"])
    filepath = f'{OUTPUT_DIR}/{c["ticker"].lower().replace(".", "-")}.json'
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    count += 1
    print(f"✅ {c['ticker']} ({c['overall']}/100)")

# Companies with pillar scores but compact
for ticker, (name, slug, overall, verdict, vd, cm, md, sc, risks, cats) in {**MORE_COMPANIES, **QUICK_COMPANIES}.items():
    data = make_json(ticker, name, slug, overall, verdict, vd, cm, md, sc, risks, cats)
    filepath = f'{OUTPUT_DIR}/{ticker.lower().replace(".", "-")}.json'
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    count += 1
    print(f"✅ {ticker} ({overall}/100)")

print(f"\n=== Generated {count} prospect score files ===")
