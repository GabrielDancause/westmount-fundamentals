export interface IVAssumption {
  title: string;
  rate: number;
  rationale: string;
}

export interface IVRisk {
  title: string;
  description: string;
}

export interface IVFaqEntry {
  question: string;
  answer: string;
}

export interface IVData {
  // Metadata
  slug: string;
  ticker: string;
  companyName: string;
  title: string;
  description: string;
  published: string;

  // Header
  subtitle?: string;

  // Financial inputs
  baseFCF: number;
  sharesOut: number;
  currentPrice: number;
  netCash: number;

  // Rates
  fcfGrowthRate: number;
  discountRate: number;
  terminalGrowthRate: number;

  // Sensitivity matrix axes (5 values each)
  sensitivityDiscountRates: number[];
  sensitivityGrowthRates: number[];

  // Content sections
  thesisTitle: string;
  thesisParagraphs: string[];

  assumptions: {
    fcfGrowth: IVAssumption;
    discountRate: IVAssumption;
    terminalGrowth: IVAssumption;
  };

  // DCF intro text overrides (optional)
  dcfIntroText?: string;
  terminalIntroText?: string;
  consolidationText?: string;
  sensitivityIntroText?: string;

  risks: {
    introText: string;
    items: IVRisk[];
  };

  faq: IVFaqEntry[];

  // Verdict footer
  verdictFooter: string;
}
