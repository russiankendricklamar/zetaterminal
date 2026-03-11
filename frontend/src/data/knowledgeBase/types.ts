export interface KnowledgeItem {
  id: string
  code: string
  title: string
  category: string
  description: string
  formula?: string
  formulaExplanation?: string
  features: string[]
  howToUse?: string[]
  path?: string
  relatedItems?: string[]
}

export interface Category {
  id: string
  name: string
  description: string
  color: string
  longDescription: string
}
