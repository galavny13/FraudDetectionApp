"use client"

import { useState } from "react"
import { View, StyleSheet } from "react-native"
import { useAppContext } from "../context/AppContext"
import { Input, Button } from "@rneui/themed"
import { Mail, ArrowRight } from "lucide-react-native"
import { LinearGradient } from "expo-linear-gradient"

export default function ContactForm() {
  const { contactEmail, setContactEmail } = useAppContext()
  const [email, setEmail] = useState(contactEmail)
  const [isFocused, setIsFocused] = useState(false)

  const handleSubmit = () => {
    setContactEmail(email)
    alert("Contact email updated successfully!")
  }

  return (
    <View style={styles.container}>
      <Input
        value={email}
        onChangeText={setEmail}
        placeholder="Enter contact email"
        keyboardType="email-address"
        autoCapitalize="none"
        leftIcon={<Mail color="#003c42" size={20} />}
        inputStyle={styles.input}
        inputContainerStyle={[styles.inputContainer, isFocused && styles.inputContainerFocused]}
        placeholderTextColor="rgba(0,60,66,0.6)"
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
      />
      <View style={styles.buttonContainer}>
        <Button
          title="Update Contact"
          onPress={handleSubmit}
          buttonStyle={styles.button}
          icon={<ArrowRight size={20} color="#fff" style={styles.buttonIcon} />}
          iconRight
          ViewComponent={LinearGradient}
          linearGradientProps={{
            colors: ["#e5d4ff", "#dbcafe"],
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
  },
  inputContainer: {
    borderBottomWidth: 1,
    borderBottomColor: "rgba(0,60,66,0.3)",
    paddingHorizontal: 0,
    transition: "all 0.3s",
  },
  inputContainerFocused: {
    borderBottomColor: "#dbcafe",
    borderBottomWidth: 2,
  },
  input: {
    color: "#003c42",
    fontSize: 16,
    marginLeft: 10,
  },
  buttonContainer: {
    width: "90%",
    marginBottom: 10,
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
  buttonIcon: {
    marginLeft: 8,
  },
})

