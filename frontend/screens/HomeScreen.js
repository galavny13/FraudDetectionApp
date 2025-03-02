"use client"

import { useState } from "react"
import { View, StyleSheet, Text, SafeAreaView } from "react-native"
import { useAppContext } from "../context/AppContext"
import ImageCapture from "../components/ImageCapture"
import ContactForm from "../components/ContactForm"
import { analyzeBill } from "../utils/api"
import { Button, Card } from "@rneui/themed"
import { LinearGradient } from "expo-linear-gradient"

export default function HomeScreen({ navigation }) {
  const { setAnalysisResult } = useAppContext()
  const [selectedFile, setSelectedFile] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleFileCaptured = (uri, type) => {
    console.log("File captured:", { uri, type })
    setSelectedFile({ uri, type })
  }

  const handleAnalyze = async () => {
    if (!selectedFile) {
      alert("Please capture a photo or upload a file first.")
      return
    }

    setIsAnalyzing(true)
    try {
      const result = await analyzeBill(selectedFile.uri)
      setAnalysisResult(result)
      navigation.navigate("Result")
    } catch (error) {
      console.error("Error analyzing file:", error)
      alert("An error occurred while analyzing the file. Please try again.")
    } finally {
      setIsAnalyzing(false)
      setSelectedFile(null)
    }
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <LinearGradient colors={["rgba(0,60,66,0.02)", "rgba(0,60,66,0.1)"]} style={styles.gradient}>
        <View style={styles.container}>
          <Card containerStyle={styles.card}>
            <Card.Title style={styles.cardTitle}>Capture or Upload File</Card.Title>
            <Card.Divider style={styles.divider} />
            <ImageCapture onFileCaptured={handleFileCaptured} />
            {selectedFile && (
              <Text style={styles.fileStatus}>
                Selected: {selectedFile.type === "image" ? "selected_image.jpg" : "statement.pdf"} ({selectedFile.type})
              </Text>
            )}
          </Card>

          <Card containerStyle={styles.card}>
            <Card.Title style={styles.cardTitle}>Contact Information</Card.Title>
            <Card.Divider style={styles.divider} />
            <ContactForm />
          </Card>

          <View style={styles.buttonContainer}>
            <Button
              title="Analyze"
              onPress={handleAnalyze}
              disabled={!selectedFile || isAnalyzing}
              loading={isAnalyzing}
              buttonStyle={styles.analyzeButton}
              containerStyle={{ width: "100%" }}
              disabledStyle={styles.disabledButton}
              ViewComponent={LinearGradient}
              linearGradientProps={{
                colors: !selectedFile || isAnalyzing ? ["#cccccc", "#bbbbbb"] : ["#7b47e5", "#6b2ee5"],
                start: { x: 0, y: 0 },
                end: { x: 1, y: 0 },
              }}
            />
          </View>
        </View>
      </LinearGradient>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#f0f0f0",
  },
  gradient: {
    flex: 1,
  },
  container: {
    flex: 1,
    padding: 20,
    paddingTop: 50,
  },
  card: {
    borderRadius: 10,
    marginBottom: 20,
    backgroundColor: "#f9f9f9",
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
    padding: 15,
  },
  cardTitle: {
    color: "#003c42",
    fontSize: 20,
    fontWeight: "600",
    letterSpacing: 0.5,
    marginBottom: 5,
  },
  divider: {
    backgroundColor: "rgba(0,60,66,0.1)",
    height: 1,
    marginBottom: 15,
  },
  fileStatus: {
    marginTop: 10,
    color: "#003c42",
    textAlign: "center",
    fontSize: 14,
    opacity: 0.8,
  },
  buttonContainer: {
    width: "78%",
    alignSelf: "center",
    marginBottom: 10,
  },
  analyzeButton: {
    borderRadius: 8,
    height: 50,
    shadowColor: "#6b2ee5",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  disabledButton: {
    opacity: 1, // Override default opacity
  },
  disabledButtonText: {
    color: "#666666",
  },
})

