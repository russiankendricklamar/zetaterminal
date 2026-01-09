import { Candle, OrderBookItem, Trade, OrderSide } from '@/types/terminal';

export const INITIAL_PRICE = 64230.50;
export const SYMBOL = "BTC/USDT";

export const generateCandles = (count: number): Candle[] => {
  const candles: Candle[] = [];
  let currentPrice = INITIAL_PRICE;
  let timestamp = Date.now() - count * 60 * 1000;

  for (let i = 0; i < count; i++) {
    const move = (Math.random() - 0.5) * 100;
    const open = currentPrice;
    const close = currentPrice + move;
    const high = Math.max(open, close) + Math.random() * 50;
    const low = Math.min(open, close) - Math.random() * 50;
    const volume = Math.random() * 10 + 1;
    
    currentPrice = close;
    timestamp += 60 * 1000;

    candles.push({
      time: new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      timestamp,
      open,
      high,
      low,
      close,
      volume
    });
  }
  return candles;
};

export const generateOrderBook = (basePrice: number): { bids: OrderBookItem[], asks: OrderBookItem[] } => {
  const bids: OrderBookItem[] = [];
  const asks: OrderBookItem[] = [];
  
  for (let i = 1; i <= 15; i++) {
    bids.push({
      price: basePrice - i * 5 - Math.random() * 2,
      amount: Math.random() * 2,
      total: 0 // calc later
    });
    asks.push({
      price: basePrice + i * 5 + Math.random() * 2,
      amount: Math.random() * 2,
      total: 0
    });
  }
  return { bids, asks: asks.reverse() }; // Asks usually sorted ascending, but for UI we might map differently
};

export const generateTrade = (currentPrice: number): Trade => {
  return {
    id: Math.random().toString(36).substring(7),
    price: currentPrice + (Math.random() - 0.5) * 10,
    amount: Math.random() * 0.5,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    side: Math.random() > 0.5 ? OrderSide.BUY : OrderSide.SELL
  };
};
