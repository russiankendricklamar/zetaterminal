<template>
  <div class="flex-1 glass-panel rounded-3xl overflow-hidden shadow-2xl shadow-black/20 p-6 flex flex-col animate-fade-in relative">
    <!-- Decorative background element -->
    <div class="absolute top-0 right-0 w-96 h-96 bg-gradient-to-b from-orange-500/5 to-transparent rounded-full blur-3xl -z-10 pointer-events-none"></div>

    <div class="flex flex-col gap-4 mb-8">
      <div class="flex justify-between items-center">
        <div>
          <h2 class="text-3xl font-bold text-white tracking-tight mb-1">Криптовалюты</h2>
          <p class="text-sm text-gray-400">Цены и аналитика в реальном времени</p>
        </div>
        <div class="flex gap-2">
          <button 
            v-for="filter in filters" 
            :key="filter"
            @click="activeFilter = filter"
            :class="`px-4 py-2 rounded-xl text-xs font-bold transition-all border border-white/5 hover:border-white/20 ${activeFilter === filter ? 'bg-white/10 text-white' : 'bg-transparent text-gray-400 hover:text-white'}`"
          >
            {{ filter }}
          </button>
        </div>
      </div>
      
      <!-- Фильтры по типу и капитализации -->
      <div class="flex flex-wrap items-center gap-3">
        <!-- Тип криптовалюты Dropdown -->
        <div class="relative" data-dropdown-type>
          <span class="text-xs font-bold text-gray-500 uppercase mb-2 block">Тип</span>
          <div class="relative">
            <button
              @click="isTypeOpen = !isTypeOpen"
              class="px-4 py-2.5 bg-black/20 border border-white/10 rounded-xl text-sm text-white hover:border-indigo-500/50 transition-all flex items-center justify-between gap-3 min-w-[180px]"
            >
              <span>{{ selectedType === 'All' ? 'Все типы' : getTypeName(selectedType) }}</span>
              <ChevronDownIcon :class="`w-4 h-4 transition-transform ${isTypeOpen ? 'rotate-180' : ''}`" />
            </button>
            <div
              v-if="isTypeOpen"
              @click.stop
              class="absolute top-full left-0 mt-2 w-full bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl z-50 max-h-64 overflow-y-auto custom-scrollbar"
            >
              <button
                @click="selectType('All')"
                :class="`w-full px-4 py-3 text-left text-sm transition-colors ${
                  selectedType === 'All' 
                    ? 'bg-indigo-500/20 text-indigo-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                Все типы
              </button>
              <button
                v-for="type in availableTypes"
                :key="type"
                @click="selectType(type)"
                :class="`w-full px-4 py-3 text-left text-sm transition-colors ${
                  selectedType === type 
                    ? 'bg-indigo-500/20 text-indigo-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                {{ getTypeName(type) }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- Капитализация Dropdown -->
        <div class="relative" data-dropdown-cap>
          <span class="text-xs font-bold text-gray-500 uppercase mb-2 block">Капитализация</span>
          <div class="relative">
            <button
              @click="isCapOpen = !isCapOpen"
              class="px-4 py-2.5 bg-black/20 border border-white/10 rounded-xl text-sm text-white hover:border-indigo-500/50 transition-all flex items-center justify-between gap-3 min-w-[180px]"
            >
              <span>{{ selectedCap === 'All' ? 'Все' : getCapName(selectedCap) }}</span>
              <ChevronDownIcon :class="`w-4 h-4 transition-transform ${isCapOpen ? 'rotate-180' : ''}`" />
            </button>
            <div
              v-if="isCapOpen"
              @click.stop
              class="absolute top-full left-0 mt-2 w-full bg-black/90 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl z-50 max-h-64 overflow-y-auto custom-scrollbar"
            >
              <button
                @click="selectCap('All')"
                :class="`w-full px-4 py-3 text-left text-sm transition-colors ${
                  selectedCap === 'All' 
                    ? 'bg-indigo-500/20 text-indigo-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                Все
              </button>
              <button
                v-for="cap in capRanges"
                :key="cap"
                @click="selectCap(cap)"
                :class="`w-full px-4 py-3 text-left text-sm transition-colors ${
                  selectedCap === cap 
                    ? 'bg-indigo-500/20 text-indigo-300' 
                    : 'text-gray-300 hover:bg-white/5 hover:text-white'
                }`"
              >
                {{ getCapName(cap) }}
              </button>
            </div>
          </div>
        </div>
        
        <div class="flex items-end">
          <button 
            v-if="selectedType !== 'All' || selectedCap !== 'All'"
            @click="clearFilters"
            class="px-4 py-2.5 text-xs font-bold text-gray-400 hover:text-white hover:bg-white/5 rounded-xl border border-white/5 hover:border-white/20 transition-all"
          >
            Сбросить
          </button>
        </div>
      </div>
    </div>

    <div class="overflow-auto custom-scrollbar flex-1">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="text-xs text-gray-500 border-b border-white/5 uppercase tracking-wider">
            <th class="font-bold py-4 px-4 pl-0">Инструмент</th>
            <th class="font-bold py-4 px-4 text-right">Цена</th>
            <th class="font-bold py-4 px-4 text-right">Изменение 24ч</th>
            <th class="font-bold py-4 px-4 text-right hidden md:table-cell">Детали</th>
          </tr>
        </thead>
        <tbody class="text-sm font-medium">
          <tr 
            v-for="asset in cryptoAssets" 
            :key="asset.symbol"
            @click="$emit('assetClick', asset)"
            class="border-b border-white/5 hover:bg-white/5 transition-colors group cursor-pointer"
          >
            <td class="py-4 px-4 pl-0">
              <div class="flex items-center gap-4">
                <button 
                  class="text-gray-600 hover:text-yellow-400 transition-colors"
                  @click.stop
                >
                  <StarIcon class="w-4 h-4" />
                </button>
                <div class="w-10 h-10 rounded-xl flex items-center justify-center text-xs font-bold shadow-lg bg-gradient-to-br from-orange-500/20 to-yellow-500/20 text-orange-400">
                  {{ asset.symbol.substring(0, 2) }}
                </div>
                <div>
                  <div class="text-white font-bold text-base">{{ asset.symbol }}</div>
                  <div class="text-xs text-gray-500 flex items-center gap-2">
                    {{ asset.name }}
                    <span class="px-1.5 py-0.5 rounded bg-white/5 text-[10px] uppercase text-gray-400">Крипто</span>
                  </div>
                </div>
              </div>
            </td>
            <td class="py-4 px-4 text-right font-mono text-white text-base">{{ asset.price }}</td>
            <td class="py-4 px-4 text-right">
              <div :class="`inline-flex items-center gap-1 px-2 py-1 rounded-lg ${asset.change.startsWith('+') ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`">
                <component :is="asset.change.startsWith('+') ? 'TrendingUpIcon' : 'TrendingDownIcon'" class="w-3 h-3" />
                <span class="font-mono font-bold">{{ asset.change }}</span>
              </div>
            </td>
            <td class="py-4 px-4 text-right text-gray-400 hidden md:table-cell font-mono">
              {{ asset.cap ? `Кап: ${asset.cap}` : '-' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue';
import { AssetInfo } from '@/types/terminal';

const emit = defineEmits<{
  navigate: [page: string];
  assetClick: [asset: AssetInfo];
}>();

const filters = ['Топ роста', 'Топ падения', 'Высокий объём'];
const activeFilter = ref('Топ роста');
const selectedType = ref('All');
const selectedCap = ref('All');
const isTypeOpen = ref(false);
const isCapOpen = ref(false);

const capRanges = ['Mega', 'Large', 'Mid', 'Small', 'Micro'];

const allCryptoAssets: AssetInfo[] = [
  // Layer 1 - Основные блокчейны
  { name: 'Bitcoin', symbol: 'BTC', price: '64,230.50', change: '+2.45%', cap: '1.2T', vol: '35B', category: 'Crypto', region: 'Layer1' },
  { name: 'Ethereum', symbol: 'ETH', price: '3,450.20', change: '-1.12%', cap: '400B', vol: '15B', category: 'Crypto', region: 'Layer1' },
  { name: 'Solana', symbol: 'SOL', price: '148.50', change: '+5.67%', cap: '65B', vol: '4B', category: 'Crypto', region: 'Layer1' },
  { name: 'Cardano', symbol: 'ADA', price: '0.45', change: '+1.20%', cap: '16B', vol: '400M', category: 'Crypto', region: 'Layer1' },
  { name: 'Avalanche', symbol: 'AVAX', price: '38.50', change: '+4.20%', cap: '14.5B', vol: '320M', category: 'Crypto', region: 'Layer1' },
  { name: 'Polkadot', symbol: 'DOT', price: '7.25', change: '+3.10%', cap: '9.5B', vol: '250M', category: 'Crypto', region: 'Layer1' },
  { name: 'Cosmos', symbol: 'ATOM', price: '8.45', change: '+2.15%', cap: '3.2B', vol: '85M', category: 'Crypto', region: 'Layer1' },
  { name: 'Near Protocol', symbol: 'NEAR', price: '5.80', change: '+1.85%', cap: '6.1B', vol: '120M', category: 'Crypto', region: 'Layer1' },
  { name: 'Algorand', symbol: 'ALGO', price: '0.18', change: '+0.95%', cap: '1.4B', vol: '45M', category: 'Crypto', region: 'Layer1' },
  { name: 'Tezos', symbol: 'XTZ', price: '0.95', change: '-0.25%', cap: '950M', vol: '28M', category: 'Crypto', region: 'Layer1' },
  { name: 'Hedera', symbol: 'HBAR', price: '0.08', change: '+1.45%', cap: '2.8B', vol: '65M', category: 'Crypto', region: 'Layer1' },
  { name: 'Fantom', symbol: 'FTM', price: '0.42', change: '+3.25%', cap: '1.2B', vol: '55M', category: 'Crypto', region: 'Layer1' },
  { name: 'Aptos', symbol: 'APT', price: '9.25', change: '+2.60%', cap: '4.1B', vol: '180M', category: 'Crypto', region: 'Layer1' },
  { name: 'Sui', symbol: 'SUI', price: '1.85', change: '+1.95%', cap: '2.3B', vol: '95M', category: 'Crypto', region: 'Layer1' },
  { name: 'Shiba Inu', symbol: 'SHIB', price: '0.000025', change: '+4.50%', cap: '14.8B', vol: '850M', category: 'Crypto', region: 'Meme' },
  
  // Layer 2 - Решения масштабирования
  { name: 'Polygon', symbol: 'MATIC', price: '0.85', change: '-0.30%', cap: '7.8B', vol: '150M', category: 'Crypto', region: 'Layer2' },
  { name: 'Arbitrum', symbol: 'ARB', price: '1.25', change: '+2.15%', cap: '3.2B', vol: '280M', category: 'Crypto', region: 'Layer2' },
  { name: 'Optimism', symbol: 'OP', price: '2.45', change: '+1.85%', cap: '2.8B', vol: '185M', category: 'Crypto', region: 'Layer2' },
  { name: 'Immutable X', symbol: 'IMX', price: '2.15', change: '+3.40%', cap: '3.1B', vol: '95M', category: 'Crypto', region: 'Layer2' },
  { name: 'Loopring', symbol: 'LRC', price: '0.28', change: '+1.25%', cap: '380M', vol: '25M', category: 'Crypto', region: 'Layer2' },
  { name: 'Starknet', symbol: 'STRK', price: '1.15', change: '+2.85%', cap: '1.6B', vol: '120M', category: 'Crypto', region: 'Layer2' },
  
  // DeFi - Децентрализованные финансы
  { name: 'Uniswap', symbol: 'UNI', price: '6.20', change: '+2.50%', cap: '4.6B', vol: '95M', category: 'Crypto', region: 'DeFi' },
  { name: 'Chainlink', symbol: 'LINK', price: '14.80', change: '+1.85%', cap: '8.2B', vol: '180M', category: 'Crypto', region: 'DeFi' },
  { name: 'Aave', symbol: 'AAVE', price: '95.40', change: '+1.45%', cap: '1.4B', vol: '85M', category: 'Crypto', region: 'DeFi' },
  { name: 'Maker', symbol: 'MKR', price: '2,850.60', change: '+0.95%', cap: '2.7B', vol: '45M', category: 'Crypto', region: 'DeFi' },
  { name: 'Compound', symbol: 'COMP', price: '58.20', change: '+1.25%', cap: '450M', vol: '28M', category: 'Crypto', region: 'DeFi' },
  { name: 'Curve', symbol: 'CRV', price: '0.65', change: '+2.15%', cap: '680M', vol: '42M', category: 'Crypto', region: 'DeFi' },
  { name: 'SushiSwap', symbol: 'SUSHI', price: '1.25', change: '+1.85%', cap: '240M', vol: '35M', category: 'Crypto', region: 'DeFi' },
  { name: 'PancakeSwap', symbol: 'CAKE', price: '2.85', change: '+3.25%', cap: '750M', vol: '95M', category: 'Crypto', region: 'DeFi' },
  { name: '1inch', symbol: '1INCH', price: '0.45', change: '+1.15%', cap: '540M', vol: '38M', category: 'Crypto', region: 'DeFi' },
  { name: 'Yearn Finance', symbol: 'YFI', price: '8,450.20', change: '+0.85%', cap: '280M', vol: '18M', category: 'Crypto', region: 'DeFi' },
  { name: 'Synthetix', symbol: 'SNX', price: '2.95', change: '+2.45%', cap: '950M', vol: '55M', category: 'Crypto', region: 'DeFi' },
  { name: 'Balancer', symbol: 'BAL', price: '4.25', change: '+1.65%', cap: '240M', vol: '15M', category: 'Crypto', region: 'DeFi' },
  { name: 'Convex Finance', symbol: 'CVX', price: '3.85', change: '+2.25%', cap: '380M', vol: '28M', category: 'Crypto', region: 'DeFi' },
  { name: 'Frax', symbol: 'FRAX', price: '0.998', change: '+0.05%', cap: '650M', vol: '45M', category: 'Crypto', region: 'DeFi' },
  { name: 'Lido', symbol: 'LDO', price: '2.15', change: '+1.95%', cap: '1.9B', vol: '85M', category: 'Crypto', region: 'DeFi' },
  
  // Stablecoins
  { name: 'Tether', symbol: 'USDT', price: '1.00', change: '+0.01%', cap: '95B', vol: '45B', category: 'Crypto', region: 'Stablecoin' },
  { name: 'USD Coin', symbol: 'USDC', price: '1.00', change: '+0.01%', cap: '28B', vol: '4.5B', category: 'Crypto', region: 'Stablecoin' },
  { name: 'Dai', symbol: 'DAI', price: '0.999', change: '+0.02%', cap: '5.2B', vol: '280M', category: 'Crypto', region: 'Stablecoin' },
  { name: 'Binance USD', symbol: 'BUSD', price: '1.00', change: '0.00%', cap: '1.8B', vol: '450M', category: 'Crypto', region: 'Stablecoin' },
  { name: 'TrueUSD', symbol: 'TUSD', price: '1.00', change: '+0.01%', cap: '480M', vol: '85M', category: 'Crypto', region: 'Stablecoin' },
  
  // Платежные и переводы
  { name: 'Ripple', symbol: 'XRP', price: '0.62', change: '-0.45%', cap: '34B', vol: '1.2B', category: 'Crypto', region: 'Payment' },
  { name: 'Litecoin', symbol: 'LTC', price: '82.40', change: '+0.95%', cap: '6.1B', vol: '280M', category: 'Crypto', region: 'Payment' },
  { name: 'Bitcoin Cash', symbol: 'BCH', price: '245.60', change: '-0.15%', cap: '4.8B', vol: '120M', category: 'Crypto', region: 'Payment' },
  { name: 'Stellar', symbol: 'XLM', price: '0.12', change: '+0.85%', cap: '3.5B', vol: '95M', category: 'Crypto', region: 'Payment' },
  { name: 'Dash', symbol: 'DASH', price: '28.50', change: '+1.25%', cap: '320M', vol: '28M', category: 'Crypto', region: 'Payment' },
  { name: 'Monero', symbol: 'XMR', price: '145.80', change: '+0.65%', cap: '2.6B', vol: '85M', category: 'Crypto', region: 'Payment' },
  { name: 'Zcash', symbol: 'ZEC', price: '24.85', change: '+1.15%', cap: '380M', vol: '35M', category: 'Crypto', region: 'Payment' },
  
  // NFT и Metaverse
  { name: 'The Sandbox', symbol: 'SAND', price: '0.45', change: '+2.85%', cap: '950M', vol: '85M', category: 'Crypto', region: 'NFT' },
  { name: 'Decentraland', symbol: 'MANA', price: '0.42', change: '+1.95%', cap: '780M', vol: '65M', category: 'Crypto', region: 'NFT' },
  { name: 'Axie Infinity', symbol: 'AXS', price: '7.25', change: '+3.15%', cap: '980M', vol: '95M', category: 'Crypto', region: 'NFT' },
  { name: 'Enjin Coin', symbol: 'ENJ', price: '0.28', change: '+1.45%', cap: '420M', vol: '35M', category: 'Crypto', region: 'NFT' },
  { name: 'Flow', symbol: 'FLOW', price: '0.85', change: '+2.25%', cap: '880M', vol: '55M', category: 'Crypto', region: 'NFT' },
  { name: 'Immutable X', symbol: 'IMX', price: '2.15', change: '+3.40%', cap: '3.1B', vol: '95M', category: 'Crypto', region: 'NFT' },
  { name: 'ApeCoin', symbol: 'APE', price: '1.85', change: '+4.25%', cap: '680M', vol: '120M', category: 'Crypto', region: 'NFT' },
  
  // Meme Coins
  { name: 'Dogecoin', symbol: 'DOGE', price: '0.15', change: '+5.25%', cap: '21.5B', vol: '1.2B', category: 'Crypto', region: 'Meme' },
  { name: 'Shiba Inu', symbol: 'SHIB', price: '0.000025', change: '+4.50%', cap: '14.8B', vol: '850M', category: 'Crypto', region: 'Meme' },
  { name: 'Pepe', symbol: 'PEPE', price: '0.0000085', change: '+8.95%', cap: '3.6B', vol: '450M', category: 'Crypto', region: 'Meme' },
  { name: 'Floki', symbol: 'FLOKI', price: '0.00018', change: '+6.25%', cap: '1.7B', vol: '180M', category: 'Crypto', region: 'Meme' },
  { name: 'Bonk', symbol: 'BONK', price: '0.000025', change: '+12.50%', cap: '1.6B', vol: '280M', category: 'Crypto', region: 'Meme' },
  { name: 'Dogwifhat', symbol: 'WIF', price: '2.85', change: '+9.85%', cap: '2.8B', vol: '380M', category: 'Crypto', region: 'Meme' },
  
  // Exchange Tokens
  { name: 'Binance Coin', symbol: 'BNB', price: '585.40', change: '+1.25%', cap: '88B', vol: '1.8B', category: 'Crypto', region: 'Exchange' },
  { name: 'Cronos', symbol: 'CRO', price: '0.12', change: '+1.85%', cap: '3.2B', vol: '45M', category: 'Crypto', region: 'Exchange' },
  { name: 'KuCoin Token', symbol: 'KCS', price: '10.25', change: '+0.95%', cap: '980M', vol: '18M', category: 'Crypto', region: 'Exchange' },
  { name: 'Huobi Token', symbol: 'HT', price: '4.85', change: '+1.45%', cap: '780M', vol: '25M', category: 'Crypto', region: 'Exchange' },
  { name: 'OKB', symbol: 'OKB', price: '52.40', change: '+0.85%', cap: '3.1B', vol: '35M', category: 'Crypto', region: 'Exchange' },
  { name: 'FTX Token', symbol: 'FTT', price: '1.25', change: '-2.15%', cap: '420M', vol: '15M', category: 'Crypto', region: 'Exchange' },
  
  // Gaming
  { name: 'Gala', symbol: 'GALA', price: '0.042', change: '+3.85%', cap: '1.1B', vol: '95M', category: 'Crypto', region: 'Gaming' },
  { name: 'The Sandbox', symbol: 'SAND', price: '0.45', change: '+2.85%', cap: '950M', vol: '85M', category: 'Crypto', region: 'Gaming' },
  { name: 'Axie Infinity', symbol: 'AXS', price: '7.25', change: '+3.15%', cap: '980M', vol: '95M', category: 'Crypto', region: 'Gaming' },
  { name: 'Illuvium', symbol: 'ILV', price: '85.40', change: '+2.45%', cap: '380M', vol: '28M', category: 'Crypto', region: 'Gaming' },
  { name: 'Star Atlas', symbol: 'ATLAS', price: '0.0085', change: '+1.95%', cap: '180M', vol: '12M', category: 'Crypto', region: 'Gaming' },
  
  // AI & Big Data
  { name: 'Fetch.ai', symbol: 'FET', price: '1.85', change: '+4.25%', cap: '1.5B', vol: '120M', category: 'Crypto', region: 'AI' },
  { name: 'SingularityNET', symbol: 'AGIX', price: '0.42', change: '+3.15%', cap: '540M', vol: '65M', category: 'Crypto', region: 'AI' },
  { name: 'Ocean Protocol', symbol: 'OCEAN', price: '0.85', change: '+2.45%', cap: '480M', vol: '45M', category: 'Crypto', region: 'AI' },
  { name: 'Render', symbol: 'RNDR', price: '8.25', change: '+5.85%', cap: '3.2B', vol: '280M', category: 'Crypto', region: 'AI' },
  { name: 'The Graph', symbol: 'GRT', price: '0.28', change: '+1.85%', cap: '2.6B', vol: '95M', category: 'Crypto', region: 'AI' },
  { name: 'Bittensor', symbol: 'TAO', price: '425.60', change: '+6.25%', cap: '2.8B', vol: '85M', category: 'Crypto', region: 'AI' },
  
  // Privacy
  { name: 'Monero', symbol: 'XMR', price: '145.80', change: '+0.65%', cap: '2.6B', vol: '85M', category: 'Crypto', region: 'Privacy' },
  { name: 'Zcash', symbol: 'ZEC', price: '24.85', change: '+1.15%', cap: '380M', vol: '35M', category: 'Crypto', region: 'Privacy' },
  { name: 'Dash', symbol: 'DASH', price: '28.50', change: '+1.25%', cap: '320M', vol: '28M', category: 'Crypto', region: 'Privacy' },
  { name: 'Horizen', symbol: 'ZEN', price: '8.45', change: '+0.95%', cap: '125M', vol: '8M', category: 'Crypto', region: 'Privacy' },
  
  // Infrastructure
  { name: 'Filecoin', symbol: 'FIL', price: '5.85', change: '+2.15%', cap: '3.1B', vol: '180M', category: 'Crypto', region: 'Infrastructure' },
  { name: 'Arweave', symbol: 'AR', price: '28.50', change: '+3.45%', cap: '1.9B', vol: '65M', category: 'Crypto', region: 'Infrastructure' },
  { name: 'Helium', symbol: 'HNT', price: '4.25', change: '+1.85%', cap: '680M', vol: '35M', category: 'Crypto', region: 'Infrastructure' },
  { name: 'Theta Network', symbol: 'THETA', price: '1.85', change: '+2.25%', cap: '1.8B', vol: '55M', category: 'Crypto', region: 'Infrastructure' },
  { name: 'Basic Attention Token', symbol: 'BAT', price: '0.28', change: '+1.15%', cap: '420M', vol: '28M', category: 'Crypto', region: 'Infrastructure' },
  
  // Дополнительные популярные
  { name: 'Tron', symbol: 'TRX', price: '0.12', change: '+1.45%', cap: '10.5B', vol: '450M', category: 'Crypto', region: 'Layer1' },
  { name: 'Toncoin', symbol: 'TON', price: '6.25', change: '+3.85%', cap: '14.2B', vol: '280M', category: 'Crypto', region: 'Layer1' },
  { name: 'Internet Computer', symbol: 'ICP', price: '12.85', change: '+2.15%', cap: '5.8B', vol: '95M', category: 'Crypto', region: 'Layer1' },
  { name: 'VeChain', symbol: 'VET', price: '0.035', change: '+1.95%', cap: '2.5B', vol: '65M', category: 'Crypto', region: 'Layer1' },
  { name: 'Theta Fuel', symbol: 'TFUEL', price: '0.085', change: '+2.45%', cap: '450M', vol: '18M', category: 'Crypto', region: 'Layer1' },
  { name: 'EOS', symbol: 'EOS', price: '0.75', change: '+0.85%', cap: '850M', vol: '45M', category: 'Crypto', region: 'Layer1' },
  { name: 'Waves', symbol: 'WAVES', price: '2.45', change: '+1.25%', cap: '280M', vol: '25M', category: 'Crypto', region: 'Layer1' },
  { name: 'Zilliqa', symbol: 'ZIL', price: '0.025', change: '+1.65%', cap: '450M', vol: '35M', category: 'Crypto', region: 'Layer1' },
  { name: 'Harmony', symbol: 'ONE', price: '0.018', change: '+2.85%', cap: '240M', vol: '18M', category: 'Crypto', region: 'Layer1' },
  { name: 'Elrond', symbol: 'EGLD', price: '42.50', change: '+1.45%', cap: '1.1B', vol: '45M', category: 'Crypto', region: 'Layer1' },
  { name: 'MultiversX', symbol: 'EGLD', price: '42.50', change: '+1.45%', cap: '1.1B', vol: '45M', category: 'Crypto', region: 'Layer1' },
  { name: 'Celo', symbol: 'CELO', price: '0.85', change: '+1.95%', cap: '450M', vol: '28M', category: 'Crypto', region: 'Layer1' },
  { name: 'Klaytn', symbol: 'KLAY', price: '0.18', change: '+1.25%', cap: '680M', vol: '35M', category: 'Crypto', region: 'Layer1' },
  { name: 'Terra Classic', symbol: 'LUNC', price: '0.00012', change: '+3.25%', cap: '720M', vol: '85M', category: 'Crypto', region: 'Layer1' },
  { name: 'Terra', symbol: 'LUNA', price: '0.65', change: '+2.15%', cap: '450M', vol: '45M', category: 'Crypto', region: 'Layer1' },
];

// Получаем доступные типы
const availableTypes = computed(() => {
  const types = new Set(allCryptoAssets.map(a => a.region).filter(Boolean));
  return Array.from(types).sort();
});

// Фильтрация по типу и капитализации
const cryptoAssets = computed(() => {
  let filtered = [...allCryptoAssets];
  
  // Фильтр по типу
  if (selectedType.value !== 'All') {
    filtered = filtered.filter(a => a.region === selectedType.value);
  }
  
  // Фильтр по капитализации
  if (selectedCap.value !== 'All') {
    filtered = filtered.filter(a => {
      const capValue = parseCapValue(a.cap || '0');
      switch (selectedCap.value) {
        case 'Mega': return capValue >= 100; // >= 100B
        case 'Large': return capValue >= 10 && capValue < 100; // 10B - 100B
        case 'Mid': return capValue >= 1 && capValue < 10; // 1B - 10B
        case 'Small': return capValue >= 0.1 && capValue < 1; // 100M - 1B
        case 'Micro': return capValue < 0.1; // < 100M
        default: return true;
      }
    });
  }
  
  // Сортировка
  if (activeFilter.value === 'Топ роста') {
    filtered = filtered.sort((a, b) => {
      const aChange = parseFloat(a.change.replace('%', ''));
      const bChange = parseFloat(b.change.replace('%', ''));
      return bChange - aChange;
    });
  } else if (activeFilter.value === 'Топ падения') {
    filtered = filtered.sort((a, b) => {
      const aChange = parseFloat(a.change.replace('%', ''));
      const bChange = parseFloat(b.change.replace('%', ''));
      return aChange - bChange;
    });
  } else if (activeFilter.value === 'Высокий объём') {
    filtered = filtered.sort((a, b) => {
      const aVol = parseVolValue(a.vol || '0');
      const bVol = parseVolValue(b.vol || '0');
      return bVol - aVol;
    });
  }
  
  return filtered;
});

const parseCapValue = (cap: string): number => {
  if (cap.includes('T')) return parseFloat(cap.replace('T', '')) * 1000;
  if (cap.includes('B')) return parseFloat(cap.replace('B', ''));
  if (cap.includes('M')) return parseFloat(cap.replace('M', '')) / 1000;
  return 0;
};

const parseVolValue = (vol: string): number => {
  if (vol.includes('B')) return parseFloat(vol.replace('B', '')) * 1000;
  if (vol.includes('M')) return parseFloat(vol.replace('M', ''));
  return 0;
};

const getTypeName = (type: string) => {
  const names: Record<string, string> = {
    'Layer1': 'Layer 1',
    'Layer2': 'Layer 2',
    'DeFi': 'DeFi',
    'Stablecoin': 'Стейблкоины',
    'Payment': 'Платежи',
    'NFT': 'NFT & Metaverse',
    'Meme': 'Мем-коины',
    'Exchange': 'Биржевые токены',
    'Gaming': 'Игровые',
    'AI': 'AI & Big Data',
    'Privacy': 'Приватность',
    'Infrastructure': 'Инфраструктура',
  };
  return names[type] || type;
};

const getCapName = (cap: string) => {
  const names: Record<string, string> = {
    'Mega': 'Мега (>100B)',
    'Large': 'Крупные (10B-100B)',
    'Mid': 'Средние (1B-10B)',
    'Small': 'Малые (100M-1B)',
    'Micro': 'Микро (<100M)',
  };
  return names[cap] || cap;
};

const selectType = (type: string) => {
  selectedType.value = type;
  isTypeOpen.value = false;
};

const selectCap = (cap: string) => {
  selectedCap.value = cap;
  isCapOpen.value = false;
};

const clearFilters = () => {
  selectedType.value = 'All';
  selectedCap.value = 'All';
};

// Закрытие выпадающих меню при клике вне их
let clickOutsideHandler: ((e: MouseEvent) => void) | null = null;

onMounted(() => {
  clickOutsideHandler = (e: MouseEvent) => {
    const target = e.target as HTMLElement;
    if (!target.closest('[data-dropdown-type]') && !target.closest('[data-dropdown-cap]')) {
      isTypeOpen.value = false;
      isCapOpen.value = false;
    }
  };
  document.addEventListener('click', clickOutsideHandler);
});

onBeforeUnmount(() => {
  if (clickOutsideHandler) {
    document.removeEventListener('click', clickOutsideHandler);
  }
});


// Icon components
const StarIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>' };
const TrendingUpIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>' };
const TrendingDownIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>' };
const ChevronDownIcon = { template: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>' };
</script>
