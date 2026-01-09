<template>
  <div class="h-full bg-transparent flex flex-col flex-shrink-0">
    <div class="flex border-b border-white/5 px-2">
      <button class="px-2 py-1.5 text-xs font-bold text-white border-b-2 border-indigo-500 bg-white/5">Открытые (2)</button>
      <button class="px-2 py-1.5 text-xs font-medium text-gray-500 hover:text-white transition-colors">История</button>
      <button class="px-2 py-1.5 text-xs font-medium text-gray-500 hover:text-white transition-colors">Позиции</button>
    </div>
    
    <div class="flex-1 overflow-x-hidden overflow-y-auto custom-scrollbar">
      <table class="w-full text-left border-collapse table-fixed">
        <thead>
          <tr class="text-[8px] text-gray-500 border-b border-white/5">
            <th class="font-normal py-1.5 px-1.5 w-[10%]">Время</th>
            <th class="font-normal py-1.5 px-1.5 w-[12%]">Актив</th>
            <th class="font-normal py-1.5 px-1.5 w-[8%]">Тип</th>
            <th class="font-normal py-1.5 px-1.5 w-[12%]">Напр.</th>
            <th class="font-normal py-1.5 px-1.5 w-[14%]">Цена</th>
            <th class="font-normal py-1.5 px-1.5 w-[12%]">Объём</th>
            <th class="font-normal py-1.5 px-1.5 w-[10%]">Исп.</th>
            <th class="font-normal py-1.5 px-1.5 w-[12%]">Итого</th>
            <th class="font-normal py-1.5 px-1.5 text-right w-[10%]">Дейст.</th>
          </tr>
        </thead>
        <tbody class="text-[9px] font-mono text-gray-300">
          <tr class="border-b border-white/5 hover:bg-white/5 transition-colors group">
            <td class="py-1.5 px-1.5 text-gray-500">12:30:45</td>
            <td class="py-1.5 px-1.5 font-bold text-white">BTC/USDT</td>
            <td class="py-1.5 px-1.5">Лимит</td>
            <td class="py-1.5 px-1.5 text-emerald-400 font-bold">Покупка</td>
            <td class="py-1.5 px-1.5">63,200</td>
            <td class="py-1.5 px-1.5">0.05</td>
            <td class="py-1.5 px-1.5">0%</td>
            <td class="py-1.5 px-1.5">3,160</td>
            <td class="py-1.5 px-1.5 text-right">
              <button class="text-gray-500 hover:text-rose-400 transition-colors opacity-0 group-hover:opacity-100 text-[8px]">Отменить</button>
            </td>
          </tr>
          <tr class="border-b border-white/5 hover:bg-white/5 transition-colors group">
            <td class="py-1.5 px-1.5 text-gray-500">11:15:22</td>
            <td class="py-1.5 px-1.5 font-bold text-white">ETH/USDT</td>
            <td class="py-1.5 px-1.5">Лимит</td>
            <td class="py-1.5 px-1.5 text-rose-400 font-bold">Продажа</td>
            <td class="py-1.5 px-1.5">2,850</td>
            <td class="py-1.5 px-1.5">1.20</td>
            <td class="py-1.5 px-1.5">12.5%</td>
            <td class="py-1.5 px-1.5">3,420</td>
            <td class="py-1.5 px-1.5 text-right">
              <button class="text-gray-500 hover:text-rose-400 transition-colors opacity-0 group-hover:opacity-100 text-[8px]">Отменить</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
// FooterPanel component - displays order history
</script>
