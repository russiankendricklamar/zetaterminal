// Re-export from split modules for backward compatibility
export type { KnowledgeItem, Category } from './knowledgeBase'
export {
  categories,
  items,
  getCategoryItems,
  getCategoryById,
  searchItems,
  getRelatedItems
} from './knowledgeBase'
