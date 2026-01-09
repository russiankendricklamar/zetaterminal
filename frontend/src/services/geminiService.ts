import { Candle, AIAnalysisResult } from '@/types/terminal';

// Note: This is a placeholder service. In production, you would need to:
// 1. Install @google/genai package: npm install @google/genai
// 2. Set up API key in environment variables
// 3. Uncomment and configure the actual API calls

export const analyzeMarketData = async (candles: Candle[]): Promise<AIAnalysisResult> => {
  try {
    // For now, return mock data
    // In production, uncomment below and configure:
    
    /*
    import { GoogleGenAI, Type } from "@google/genai";
    
    const ai = new GoogleGenAI({ apiKey: import.meta.env.VITE_GEMINI_API_KEY });
    const MODEL_NAME = "gemini-3-flash-preview";

    const recentData = candles.slice(-20).map(c => ({
      t: c.time,
      o: c.open.toFixed(1),
      h: c.high.toFixed(1),
      l: c.low.toFixed(1),
      c: c.close.toFixed(1),
      v: c.volume.toFixed(2)
    }));

    const prompt = `
      Analyze this crypto market data (OHLCV).
      Identify the short-term trend, provide a confidence score (0-100), key support/resistance levels, and a brief reasoning string (max 20 words).
      Data: ${JSON.stringify(recentData)}
    `;

    const response = await ai.models.generateContent({
      model: MODEL_NAME,
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            trend: { type: Type.STRING, enum: ['BULLISH', 'BEARISH', 'NEUTRAL'] },
            confidence: { type: Type.NUMBER },
            reasoning: { type: Type.STRING },
            keyLevels: {
              type: Type.OBJECT,
              properties: {
                support: { type: Type.NUMBER },
                resistance: { type: Type.NUMBER }
              }
            }
          }
        }
      }
    });

    if (response.text) {
      return JSON.parse(response.text) as AIAnalysisResult;
    }
    */

    // Mock response for now
    const lastPrice = candles[candles.length - 1]?.close || 0;
    const prevPrice = candles[candles.length - 2]?.close || lastPrice;
    const trend = lastPrice > prevPrice ? 'BULLISH' : lastPrice < prevPrice ? 'BEARISH' : 'NEUTRAL';
    
    return {
      trend,
      confidence: Math.floor(Math.random() * 30) + 60,
      reasoning: "Market showing moderate volatility with potential upward momentum based on recent price action",
      keyLevels: {
        support: lastPrice * 0.95,
        resistance: lastPrice * 1.05
      }
    };
  } catch (error) {
    console.error("AI Analysis Failed:", error);
    return {
      trend: 'NEUTRAL',
      confidence: 0,
      reasoning: "AI Service Temporarily Unavailable",
      keyLevels: { support: 0, resistance: 0 }
    };
  }
};
