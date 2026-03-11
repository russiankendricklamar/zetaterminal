export type { KnowledgeItem, Category } from './types'
export { categories } from './categories'

import type { KnowledgeItem } from './types'
import { optionsItems } from './options'
import { bondsItems } from './bonds'
import { swapsItems } from './swaps'
import { riskItems } from './risk'
import { simulationItems } from './simulation'
import { regimesItems } from './regimes'
import { portfolioItems } from './portfolio'
import { terminalItems } from './terminal'

export const items: KnowledgeItem[] = [
  ...optionsItems,
  ...bondsItems,
  ...swapsItems,
  ...riskItems,
  ...simulationItems,
  ...regimesItems,
  ...portfolioItems,
  ...terminalItems
]

export { optionsItems } from './options'
export { bondsItems } from './bonds'
export { swapsItems } from './swaps'
export { riskItems } from './risk'
export { simulationItems } from './simulation'
export { regimesItems } from './regimes'
export { portfolioItems } from './portfolio'
export { terminalItems } from './terminal'

export { getCategoryItems, getCategoryById, searchItems, getRelatedItems } from './helpers'
