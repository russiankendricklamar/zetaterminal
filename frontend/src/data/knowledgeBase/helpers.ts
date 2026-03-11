import type { KnowledgeItem, Category } from './types'
import { categories } from './categories'
import { optionsItems } from './options'
import { bondsItems } from './bonds'
import { swapsItems } from './swaps'
import { riskItems } from './risk'
import { simulationItems } from './simulation'
import { regimesItems } from './regimes'
import { portfolioItems } from './portfolio'
import { terminalItems } from './terminal'

const allItems: KnowledgeItem[] = [
  ...optionsItems,
  ...bondsItems,
  ...swapsItems,
  ...riskItems,
  ...simulationItems,
  ...regimesItems,
  ...portfolioItems,
  ...terminalItems
]

export const getCategoryItems = (categoryId: string): KnowledgeItem[] => {
  return allItems.filter(item => item.category === categoryId)
}

export const getCategoryById = (categoryId: string): Category | undefined => {
  return categories.find(cat => cat.id === categoryId)
}

export const searchItems = (query: string): KnowledgeItem[] => {
  const q = query.toLowerCase()
  return allItems.filter(item =>
    item.title.toLowerCase().includes(q) ||
    item.code.toLowerCase().includes(q) ||
    item.description.toLowerCase().includes(q) ||
    item.formula?.toLowerCase().includes(q)
  )
}

export const getRelatedItems = (itemId: string): KnowledgeItem[] => {
  const item = allItems.find(i => i.id === itemId)
  if (!item?.relatedItems) return []
  return allItems.filter(i => item.relatedItems?.includes(i.id))
}
