<template>
  <div class="orderbook">
    <div class="orderbook-header">
      <span class="orderbook-title font-mono">СТАКАН</span>
      <div class="orderbook-dots">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>
    </div>

    <div class="orderbook-content">
      <div class="orderbook-labels font-mono">
        <span>ЦЕНА</span>
        <span>ОБЪЁМ</span>
      </div>

      <!-- Asks (Sells) -->
      <div class="orderbook-asks">
        <OrderBookRow
          v-for="(ask, i) in reversedAsks"
          :key="i"
          :item="ask"
          type="ask"
        />
      </div>

      <!-- Current Price Banner -->
      <div class="orderbook-price">
        <div class="price-info">
          <span class="price-value font-mono">{{ currentPrice.toFixed(2) }}</span>
          <span class="price-usd font-mono">≈ ${{ currentPrice.toFixed(2) }}</span>
        </div>
        <div class="price-indicator"></div>
      </div>

      <!-- Bids (Buys) -->
      <div class="orderbook-bids">
        <OrderBookRow
          v-for="(bid, i) in displayedBids"
          :key="i"
          :item="bid"
          type="bid"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { OrderBookItem } from '@/types/terminal';
import OrderBookRow from './OrderBookRow.vue';
import { useIsMobile } from '@/composables/useIsMobile';

const { isMobile, isSmallMobile } = useIsMobile();

interface Props {
  bids: OrderBookItem[];
  asks: OrderBookItem[];
  currentPrice: number;
}

const props = defineProps<Props>();

// Adjust displayed orders based on screen size
const ordersToShow = computed(() => {
  if (isSmallMobile.value) return 6;
  if (isMobile.value) return 8;
  return 12;
});

const displayedBids = computed(() => props.bids.slice(0, ordersToShow.value));
const reversedAsks = computed(() => [...props.asks.slice(0, ordersToShow.value)].reverse());
</script>

<style scoped>
/* ============================================
   ORDER BOOK - BRUTALIST
   ============================================ */
.orderbook {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background: transparent;
}

.orderbook-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #1a1a1a;
}

.orderbook-title {
  font-size: 10px;
  font-weight: 600;
  color: #525252;
  letter-spacing: 0.1em;
}

.orderbook-dots {
  display: flex;
  gap: 3px;
}

.dot {
  width: 4px;
  height: 4px;
  background: #262626;
}

.orderbook-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.orderbook-labels {
  display: flex;
  justify-content: space-between;
  padding: 6px 8px;
  font-size: 8px;
  font-weight: 600;
  color: #3f3f3f;
  letter-spacing: 0.15em;
  flex-shrink: 0;
}

.orderbook-asks,
.orderbook-bids {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.orderbook-asks {
  justify-content: flex-end;
}

.orderbook-price {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px;
  background: #050505;
  border-top: 1px solid #1a1a1a;
  border-bottom: 1px solid #1a1a1a;
  flex-shrink: 0;
}

.price-info {
  display: flex;
  flex-direction: column;
}

.price-value {
  font-size: 14px;
  font-weight: 700;
  color: #f5f5f5;
}

.price-usd {
  font-size: 9px;
  color: #525252;
}

.price-indicator {
  width: 8px;
  height: 8px;
  background: #22c55e;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ============================================
   RESPONSIVE
   ============================================ */
@media (max-width: 768px) {
  .orderbook-header {
    padding: 6px 8px;
  }

  .orderbook-price {
    padding: 6px;
  }

  .price-value {
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .price-value {
    font-size: 12px;
  }
}

@media (max-width: 375px) {
  .price-value {
    font-size: 11px;
  }
}
</style>
