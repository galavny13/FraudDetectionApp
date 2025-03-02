"use client"

import { createContext, useState, useContext } from "react"

// Create the context
const AppContext = createContext(undefined)

// Create the provider component
export function AppProvider({ children }) {
  const [contactEmail, setContactEmail] = useState("")
  const [analysisResult, setAnalysisResult] = useState(null)

  return (
    <AppContext.Provider value={{ contactEmail, setContactEmail, analysisResult, setAnalysisResult }}>
      {children}
    </AppContext.Provider>
  )
}

// Create the hook to use the context
export function useAppContext() {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error("useAppContext must be used within an AppProvider")
  }
  return context
}



