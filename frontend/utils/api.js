import axios from "axios"
import * as FileSystem from "expo-file-system"

// Update this to match your backend's IP/domain and port.
const API_BASE = "http://localhost:8000"

export const analyzeBill = async (fileUri) => {
  try {
    const fileInfo = await FileSystem.getInfoAsync(fileUri)
    if (!fileInfo.exists) {
      throw new Error("File does not exist")
    }

    const fileExtension = fileUri.split(".").pop().toLowerCase()
    let fileType
    if (fileExtension === "pdf") {
      fileType = "application/pdf"
    } else if (["jpg", "jpeg", "png"].includes(fileExtension)) {
      fileType = `image/${fileExtension}`
    } else {
      throw new Error("Unsupported file type")
    }

    // Prepare multipart/form-data
    const formData = new FormData()
    formData.append("file", {
      uri: fileUri,
      name: fileExtension === "pdf" ? "statement.pdf" : "statement.jpg",
      type: fileType,
    })

    // Send request to /analyze-statement
    const response = await axios.post(`${API_BASE}/analyze-statement`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })

    return response.data // The JSON response from your FastAPI
  } catch (error) {
    console.error("analyzeBill error:", error)
    throw error // Rethrow the error to be handled by the calling function
  }
}

export const validateAnalysisResult = (result) => {
  if (!result || !result.rows) {
    throw new Error("Invalid analysis result format")
  }

  return result
}

