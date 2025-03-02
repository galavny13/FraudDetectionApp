"use client"
import { View, StyleSheet, Platform } from "react-native"
import * as ImagePicker from "expo-image-picker"
import * as DocumentPicker from "expo-document-picker"
import { Button } from "@rneui/themed"
import { Camera, Image, Upload } from "lucide-react-native"
import { LinearGradient } from "expo-linear-gradient"

export default function ImageCapture({ onFileCaptured }) {
  const requestCameraPermission = async () => {
    if (Platform.OS !== "web") {
      const { status } = await ImagePicker.requestCameraPermissionsAsync()
      if (status !== "granted") {
        alert("Sorry, we need camera permissions to take a photo!")
        return false
      }
    }
    return true
  }

  const takePhoto = async () => {
    if (!(await requestCameraPermission())) return

    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    })

    if (!result.canceled) {
      const file = {
        uri: result.assets[0].uri,
        type: "image",
        name: "selected_image.jpg",
      }
      onFileCaptured(file.uri, file.type)
    }
  }

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    })

    if (!result.canceled) {
      const file = {
        uri: result.assets[0].uri,
        type: "image",
        name: "selected_image.jpg",
      }
      onFileCaptured(file.uri, file.type)
    }
  }

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ["image/*", "application/pdf"],
        copyToCacheDirectory: false,
      })

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const asset = result.assets[0]
        const fileType = asset.mimeType === "application/pdf" ? "pdf" : "image"
        const file = {
          uri: asset.uri,
          type: fileType,
          name: fileType === "pdf" ? "statement.pdf" : "selected_image.jpg",
        }
        onFileCaptured(file.uri, file.type)
      }
    } catch (err) {
      console.error("Error picking document:", err)
    }
  }

  return (
    <View style={styles.container}>
      <View style={styles.buttonWrapper}>
        <Button
          title="Take Photo"
          onPress={takePhoto}
          buttonStyle={styles.button}
          icon={<Camera size={20} color="#fff" style={styles.buttonIcon} />}
          ViewComponent={LinearGradient}
          linearGradientProps={{
            colors: ["#e5d4ff", "#dbcafe"],
            start: { x: 0, y: 0 },
            end: { x: 1, y: 0 },
          }}
        />
      </View>
      <View style={styles.buttonWrapper}>
        <Button
          title="Choose from Photos"
          onPress={pickImage}
          buttonStyle={styles.button}
          icon={<Image size={20} color="#fff" style={styles.buttonIcon} />}
          ViewComponent={LinearGradient}
          linearGradientProps={{
            colors: ["#e5d4ff", "#dbcafe"],
            start: { x: 0, y: 0 },
            end: { x: 1, y: 0 },
          }}
        />
      </View>
      <View style={styles.buttonWrapper}>
        <Button
          title="Choose File (PDF/Image)"
          onPress={pickDocument}
          buttonStyle={styles.purpleButton}
          icon={<Upload size={20} color="#fff" style={styles.buttonIcon} />}
          ViewComponent={LinearGradient}
          linearGradientProps={{
            colors: ["#7b47e5", "#6b2ee5"],
            start: { x: 0, y: 0 },
            end: { x: 1, y: 0 },
          }}
        />
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    width: "100%",
    alignItems: "center",
    paddingHorizontal: 20,
  },
  buttonWrapper: {
    width: "100%",
    marginVertical: 5,
  },
  button: {
    borderRadius: 8,
    height: 50,
    shadowColor: "#dbcafe",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  purpleButton: {
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
  buttonIcon: {
    marginRight: 8,
  },
})

